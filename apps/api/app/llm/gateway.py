"""LLM 网关：统一封装 OpenAI 兼容与 Anthropic Claude 两种协议。

对外暴露统一的 LLMGateway 接口：
- achat_structured: 结构化输出，返回与 schema 对应的 dict。
- astream_chat: 流式文本生成（研报用）。

OpenAI 协议（DeepSeek/Qwen/OpenAI 一族）走 response_format=json_schema；
Claude 协议走原生 messages API + tool_use 强制结构化。
provider/model/base_url/api_key 完全由环境变量驱动。
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict

import anthropic
import openai

from app.config import get_settings

logger = logging.getLogger(__name__)

# 429 限流/瞬态错误的应用层退避参数：SDK 自带重试间隔太短（<2s），
# 跨不过服务商按分钟统计的限流窗口，故在网关层做 5s 起步的指数退避。
_RATE_LIMIT_BASE_DELAY = 5.0
_RATE_LIMIT_MAX_DELAY = 60.0

_RETRYABLE_ERRORS = (
    openai.RateLimitError,
    openai.APITimeoutError,
    openai.APIConnectionError,
    openai.InternalServerError,
    anthropic.RateLimitError,
    anthropic.APITimeoutError,
    anthropic.APIConnectionError,
    anthropic.InternalServerError,
)


async def _with_backoff[T](fn: Callable[[], Awaitable[T]], *, retries: int) -> T:
    """对 429/瞬态错误做指数退避重试；fn 为无参协程工厂（每次重试重新调用）。"""
    for attempt in range(retries + 1):
        try:
            return await fn()
        except _RETRYABLE_ERRORS as e:
            if attempt >= retries:
                raise
            delay = min(_RATE_LIMIT_MAX_DELAY, _RATE_LIMIT_BASE_DELAY * (2**attempt))
            delay += random.uniform(0, 1)
            logger.warning(
                "LLM 调用被限流/瞬态错误，%.1fs 后重试（第 %d/%d 次）: %s",
                delay, attempt + 1, retries, e,
            )
            await asyncio.sleep(delay)
    raise AssertionError("unreachable")


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
        self._rl_retries = s.llm_rate_limit_retries
        # 优先走 OpenAI 兼容服务商注册表（任意 OpenAI 规范服务商）
        entry = s.resolve_llm_provider(self.provider)
        if entry is not None:
            self.protocol = "openai"
            self.model = model or entry.model or s.analysis_llm_model
            self._price = (
                (entry.price_input_cny, entry.price_output_cny)
                if entry.price_input_cny is not None and entry.price_output_cny is not None
                else None
            )
            self._client = openai.AsyncOpenAI(
                api_key=entry.api_key or s.analysis_llm_api_key or s.openai_llm_api_key or "EMPTY",
                base_url=entry.base_url or s.analysis_llm_base_url,
                timeout=s.llm_request_timeout_seconds,
                max_retries=s.llm_max_retries,
            )
            return
        self.model = model or (
            s.claude_llm_model if self.provider == "claude" else s.analysis_llm_model
        )
        self._price = None
        if self.provider == "openai":
            self.protocol = "openai"
            self._client = openai.AsyncOpenAI(
                api_key=s.analysis_llm_api_key or s.openai_llm_api_key or "EMPTY",
                base_url=s.analysis_llm_base_url,
                timeout=s.llm_request_timeout_seconds,
                max_retries=s.llm_max_retries,
            )
        elif self.provider == "claude":
            self.protocol = "claude"
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
        if self.protocol == "openai":
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
        if self.protocol == "openai":
            stream = await _with_backoff(
                lambda: self._client.chat.completions.create(  # type: ignore[union-attr]
                    model=self.model,
                    messages=_normalize_openai_messages(messages),
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                    stream_options={"include_usage": True},
                ),
                retries=self._rl_retries,
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
                    usage.cost_cny = _calc_cost(usage, self._price)
                    if cost:
                        cost.add(usage)
        else:
            # 仅在尚未产出任何文本前允许退避重试，避免重复输出
            attempt = 0
            while True:
                emitted = False
                try:
                    async with self._client.messages.stream(  # type: ignore[union-attr]
                        model=self.model,
                        system=_extract_system(messages),
                        messages=_normalize_claude_messages(messages),
                        max_tokens=max_tokens,
                        temperature=temperature,
                    ) as stream:
                        usage = LLMUsage(0, 0, self.model)
                        async for text in stream.text_stream:  # type: ignore[union-attr]
                            emitted = True
                            yield text
                        final = await stream.get_final_message()
                        usage.input_tokens = final.usage.input_tokens
                        usage.output_tokens = final.usage.output_tokens
                        usage.cost_cny = _calc_cost(usage, self._price)
                        if cost:
                            cost.add(usage)
                    return
                except _RETRYABLE_ERRORS as e:
                    if emitted or attempt >= self._rl_retries:
                        raise
                    attempt += 1
                    delay = min(_RATE_LIMIT_MAX_DELAY, _RATE_LIMIT_BASE_DELAY * (2 ** (attempt - 1)))
                    delay += random.uniform(0, 1)
                    logger.warning(
                        "Claude 流式调用被限流/瞬态错误，%.1fs 后重试（第 %d/%d 次）: %s",
                        delay, attempt, self._rl_retries, e,
                    )
                    await asyncio.sleep(delay)

    async def _openai_structured(
        self, messages, schema, temperature, max_tokens, cost
    ) -> LLMResponse:
        mode = get_settings().llm_structured_mode
        content, usage = await self._openai_structured_fallback(
            mode, messages, schema, temperature, max_tokens
        )
        parsed = _extract_json(content)
        usage.cost_cny = _calc_cost(usage, self._price)
        if cost:
            cost.add(usage)
        return LLMResponse(content, parsed, usage, self.model, self.provider)

    async def _openai_structured_fallback(
        self, mode, messages, schema, temperature, max_tokens
    ) -> tuple[str, LLMUsage]:
        """按模式调用 OpenAI 兼容接口；auto 时对不支持 response_format 的服务商逐级降级。"""
        if mode == "auto":
            candidates = ("json_schema", "json_object", "prompt")
        elif mode in ("json_schema", "json_object", "prompt"):
            candidates = (mode,)
        else:
            raise ValueError(f"未知 llm_structured_mode: {mode}")

        last_err: Exception | None = None
        for i, cand in enumerate(candidates):
            try:
                return await self._openai_structured_call(
                    cand, messages, schema, temperature, max_tokens
                )
            except openai.BadRequestError as e:
                last_err = e
                if i < len(candidates) - 1:
                    logger.warning(
                        "response_format=%s 不受支持（%s），降级为 %s",
                        cand, e, candidates[i + 1],
                    )
        assert last_err is not None
        raise last_err

    async def _openai_structured_call(
        self, mode, messages, schema, temperature, max_tokens
    ) -> tuple[str, LLMUsage]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": _normalize_openai_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if mode == "json_schema":
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "structured_output", "schema": schema, "strict": True},
            }
        elif mode == "json_object":
            kwargs["response_format"] = {"type": "json_object"}
        resp = await _with_backoff(
            lambda: self._client.chat.completions.create(**kwargs),  # type: ignore[union-attr]
            retries=self._rl_retries,
        )
        content = resp.choices[0].message.content or "{}"
        usage = LLMUsage(
            resp.usage.prompt_tokens if resp.usage else 0,
            resp.usage.completion_tokens if resp.usage else 0,
            self.model,
        )
        return content, usage

    async def _claude_structured(
        self, messages, schema, temperature, max_tokens, cost
    ) -> LLMResponse:
        tool_name = "emit_structured_result"
        tool_input_schema = {k: v for k, v in schema.items() if k != "type"}
        resp = await _with_backoff(
            lambda: self._client.messages.create(  # type: ignore[union-attr]
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
            ),
            retries=self._rl_retries,
        )
        parsed: dict[str, Any] = {}
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use" and block.name == tool_name:
                parsed = block.input  # type: ignore[assignment]
                break
        content = json.dumps(parsed, ensure_ascii=False)
        usage = LLMUsage(resp.usage.input_tokens, resp.usage.output_tokens, self.model)
        usage.cost_cny = _calc_cost(usage, self._price)
        if cost:
            cost.add(usage)
        return LLMResponse(content, parsed, usage, self.model, self.provider)


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


def _calc_cost(u: LLMUsage, price: tuple[float, float] | None = None) -> float:
    p_in, p_out = price or _PRICE_CNY.get(u.model, _DEFAULT_PRICE)
    return round(u.input_tokens / 1000 * p_in + u.output_tokens / 1000 * p_out, 6)


def _extract_json(content: str) -> dict[str, Any]:
    """从 LLM 输出中稳健解析 JSON 对象（容忍代码围栏与首尾杂质）。"""
    text = content.strip()
    if text.startswith("```"):
        fence_end = text.find("\n")
        text = text[fence_end + 1 :] if fence_end != -1 else ""
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"LLM 输出无法解析为 JSON: {content[:300]!r}")
