"""LLM 网关：统一封装 OpenAI 兼容与 Anthropic Claude 两种协议。

对外暴露统一的 LLMGateway 接口：
- achat_structured: 结构化输出，返回与 schema 对应的 dict。
- astream_chat: 流式文本生成（研报用）。

OpenAI 协议（DeepSeek/Qwen/OpenAI 一族）走 response_format=json_schema；
Claude 协议走原生 messages API + tool_use 强制结构化。
provider/model/base_url/api_key 完全由环境变量驱动。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Literal, TypedDict

import anthropic
import openai

from app.config import get_settings

logger = logging.getLogger(__name__)

Role = Literal["system", "user", "assistant"]


class Message(TypedDict, total=False):
    role: Role
    content: str


_PRICE_CNY: dict[str, tuple[float, float]] = {
    "deepseek-chat": (0.001, 0.002),
    "qwen-plus": (0.004, 0.012),
    "qwen-max": (0.02, 0.06),
    "gpt-4o-mini": (0.00107, 0.00429),
    "gpt-4o": (0.0175, 0.07),
    "claude-sonnet-4-20250514": (0.022, 0.088),
    "claude-haiku-4-20250228": (0.0085, 0.0425),
}
_DEFAULT_PRICE = (0.004, 0.012)


@dataclass
class LLMUsage:
    input_tokens: int
    output_tokens: int
    model: str
    cost_cny: float = 0.0


@dataclass
class LLMResponse:
    content: str
    parsed: dict[str, Any] | None
    usage: LLMUsage
    model: str
    raw_provider: str


@dataclass
class LLMCostTracker:
    total_cny: float = 0.0
    calls: int = 0
    histories: list[LLMUsage] = field(default_factory=list)

    def add(self, u: LLMUsage) -> None:
        self.total_cny += u.cost_cny
        self.calls += 1
        self.histories.append(u)

    def remaining(self, budget: float) -> float:
        return max(0.0, budget - self.total_cny)


class LLMGateway:
    """统一 LLM 网关，支持 openai / claude 两种 provider。"""

    def __init__(self, provider: str | None = None, model: str | None = None) -> None:
        s = get_settings()
        self.provider = (provider or s.analysis_llm_provider).lower()
        self.model = model or (
            s.claude_llm_model if self.provider == "claude" else s.analysis_llm_model
        )
        if self.provider == "openai":
            self._client = openai.AsyncOpenAI(
                api_key=s.analysis_llm_api_key or s.openai_llm_api_key or "EMPTY",
                base_url=s.analysis_llm_base_url,
                timeout=s.llm_request_timeout_seconds,
                max_retries=s.llm_max_retries,
            )
        elif self.provider == "claude":
            self._client = anthropic.AsyncAnthropic(
                api_key=s.claude_llm_api_key,
                timeout=s.llm_request_timeout_seconds,
                max_retries=s.llm_max_retries,
            )
        else:
            raise ValueError(f"未知 LLM provider: {self.provider}")

    async def achat_structured(
        self,
        messages: list[Message],
        schema: dict[str, Any],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1536,
        cost: LLMCostTracker | None = None,
    ) -> LLMResponse:
        if self.provider == "openai":
            return await self._openai_structured(messages, schema, temperature, max_tokens, cost)
        return await self._claude_structured(messages, schema, temperature, max_tokens, cost)

    async def astream_chat(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.4,
        max_tokens: int = 1800,
        cost: LLMCostTracker | None = None,
    ) -> AsyncIterator[str]:
        if self.provider == "openai":
            stream = await self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self.model,
                messages=_normalize_openai_messages(messages),
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                stream_options={"include_usage": True},
            )
            usage = LLMUsage(0, 0, self.model)
            assert stream is not None
            async for chunk in stream:  # type: ignore[union-attr]
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
                if getattr(chunk, "usage", None):
                    usage.input_tokens = chunk.usage.prompt_tokens
                    usage.output_tokens = chunk.usage.completion_tokens
                    usage.cost_cny = _calc_cost(usage)
                    if cost:
                        cost.add(usage)
        else:
            async with self._client.messages.stream(  # type: ignore[union-attr]
                model=self.model,
                system=_extract_system(messages),
                messages=_normalize_claude_messages(messages),
                max_tokens=max_tokens,
                temperature=temperature,
            ) as stream:
                usage = LLMUsage(0, 0, self.model)
                async for text in stream.text_stream:  # type: ignore[union-attr]
                    yield text
                final = await stream.get_final_message()
                usage.input_tokens = final.usage.input_tokens
                usage.output_tokens = final.usage.output_tokens
                usage.cost_cny = _calc_cost(usage)
                if cost:
                    cost.add(usage)

    async def _openai_structured(
        self, messages, schema, temperature, max_tokens, cost
    ) -> LLMResponse:
        resp = await self._client.chat.completions.create(  # type: ignore[union-attr]
            model=self.model,
            messages=_normalize_openai_messages(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "structured_output", "schema": schema, "strict": True},
            },
        )
        content = resp.choices[0].message.content or "{}"
        parsed = json.loads(content)
        usage = LLMUsage(
            resp.usage.prompt_tokens if resp.usage else 0,
            resp.usage.completion_tokens if resp.usage else 0,
            self.model,
        )
        usage.cost_cny = _calc_cost(usage)
        if cost:
            cost.add(usage)
        return LLMResponse(content, parsed, usage, self.model, "openai")

    async def _claude_structured(
        self, messages, schema, temperature, max_tokens, cost
    ) -> LLMResponse:
        tool_name = "emit_structured_result"
        tool_input_schema = {k: v for k, v in schema.items() if k != "type"}
        resp = await self._client.messages.create(  # type: ignore[union-attr]
            model=self.model,
            system=_extract_system(messages),
            messages=_normalize_claude_messages(messages),
            max_tokens=max_tokens,
            temperature=temperature,
            tools=[{
                "name": tool_name,
                "description": "输出符合规范的结构化结果",
                "input_schema": tool_input_schema,
            }],
            tool_choice={"type": "tool", "name": tool_name},
        )
        parsed: dict[str, Any] = {}
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use" and block.name == tool_name:
                parsed = block.input  # type: ignore[assignment]
                break
        content = json.dumps(parsed, ensure_ascii=False)
        usage = LLMUsage(resp.usage.input_tokens, resp.usage.output_tokens, self.model)
        usage.cost_cny = _calc_cost(usage)
        if cost:
            cost.add(usage)
        return LLMResponse(content, parsed, usage, self.model, "claude")


def _extract_system(messages: list[Message]) -> str:
    return "\n\n".join(m["content"] for m in messages if m.get("role") == "system")


def _normalize_openai_messages(messages: list[Message]) -> list[dict[str, str]]:
    out = []
    for m in messages:
        out.append({"role": m.get("role", "user"), "content": m.get("content", "")})
    return out


def _normalize_claude_messages(messages: list[Message]) -> list[dict[str, str]]:
    return [
        {"role": m.get("role", "user"), "content": m.get("content", "")}
        for m in messages
        if m.get("role") != "system"
    ]


def _calc_cost(u: LLMUsage) -> float:
    p_in, p_out = _PRICE_CNY.get(u.model, _DEFAULT_PRICE)
    return round(u.input_tokens / 1000 * p_in + u.output_tokens / 1000 * p_out, 6)
