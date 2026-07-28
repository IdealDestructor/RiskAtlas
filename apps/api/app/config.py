"""应用配置，全部由环境变量注入。"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- LLM ---
    analysis_llm_provider: Literal["openai", "claude"] = "openai"
    analysis_llm_model: str = "deepseek-chat"
    analysis_llm_base_url: str = "https://api.deepseek.com/v1"
    analysis_llm_api_key: str = ""

    # OpenAI 兼容（备选）
    openai_llm_base_url: str = "https://api.openai.com/v1"
    openai_llm_api_key: str = ""

    # Claude 原生（备选）
    claude_llm_api_key: str = ""
    claude_llm_model: str = "claude-sonnet-4-20250514"

    llm_request_timeout_seconds: int = 30
    llm_max_retries: int = 2
    analysis_budget_cny: float = 0.5

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

    @property
    def cors_origin_list(self) -> list[str]:
        return [s.strip() for s in self.cors_origins.split(",") if s.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
