"""应用配置，全部由环境变量注入。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（apps/api/app/config.py -> 仓库根），.env 固定在根目录
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class OpenAICompatProvider(BaseModel):
    """OpenAI 兼容协议的服务商配置（DeepSeek / Qwen / OpenAI / 任意自建网关）。"""

    base_url: str = ""
    api_key: str = ""
    model: str = ""
    price_input_cny: float | None = None  # 元/千 token
    price_output_cny: float | None = None  # 元/千 token


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    # --- LLM ---
    analysis_llm_provider: str = "openai"
    analysis_llm_model: str = "deepseek-chat"
    analysis_llm_base_url: str = "https://api.deepseek.com/v1"
    analysis_llm_api_key: str = ""

    # OpenAI 兼容服务商注册表（JSON）：任意多家，provider 名称即键，切换仅改 ANALYSIS_LLM_PROVIDER
    llm_providers: dict[str, OpenAICompatProvider] = Field(default_factory=dict)

    @field_validator("llm_providers", mode="before")
    @classmethod
    def _parse_llm_providers(cls, v: Any) -> Any:
        if isinstance(v, str):
            return json.loads(v)
        return v

    def resolve_llm_provider(self, name: str) -> OpenAICompatProvider | None:
        return self.llm_providers.get((name or "").lower())

    # OpenAI 兼容（备选）
    openai_llm_base_url: str = "https://api.openai.com/v1"
    openai_llm_api_key: str = ""

    # Claude 原生（备选）
    claude_llm_api_key: str = ""
    claude_llm_model: str = "claude-sonnet-4-20250514"

    llm_request_timeout_seconds: int = 30
    llm_max_retries: int = 2
    # 429 限流/瞬态错误的应用层退避重试次数（网关层指数退避，5s 起步封顶 60s）
    llm_rate_limit_retries: int = 4
    analysis_budget_cny: float = 0.5

    # 代理（LLM / 数据源外呼需要走代理时设置；httpx 自动读取 HTTP(S)_PROXY）
    http_proxy: str = ""
    https_proxy: str = ""

    # --- 数据源 ---
    gdelt_enabled: bool = True
    rss_enabled: bool = True
    rss_feeds: str = ""
    tavily_enabled: bool = False
    tavily_api_key: str = ""
    serper_enabled: bool = False
    serper_api_key: str = ""
    bocha_enabled: bool = False
    bocha_api_key: str = ""

    # --- 基础设施 ---
    database_url: str = "postgresql+asyncpg://riskatlas:riskatlas@localhost:5432/riskatlas"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # --- 限流 ---
    rate_limit_requests: int = 10
    rate_limit_window_seconds: int = 3600

    @field_validator("cors_origins")
    @classmethod
    def _split_cors(cls, v: str) -> str:
        return ",".join(s.strip() for s in v.split(",") if s.strip())

    def apply_proxy_env(self) -> None:
        """把配置的代理写入进程环境变量，供 httpx/openai SDK 自动读取。"""
        import os

        if self.http_proxy and not os.environ.get("HTTP_PROXY"):
            os.environ["HTTP_PROXY"] = self.http_proxy
        if self.https_proxy and not os.environ.get("HTTPS_PROXY"):
            os.environ["HTTPS_PROXY"] = self.https_proxy

    @property
    def cors_origin_list(self) -> list[str]:
        return [s.strip() for s in self.cors_origins.split(",") if s.strip()]


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.apply_proxy_env()
    return s
