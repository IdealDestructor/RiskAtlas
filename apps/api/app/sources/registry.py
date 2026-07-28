"""数据源注册表：按配置启停，并发编排，单源失败降级。"""

from __future__ import annotations

import asyncio
import logging

from app.config import get_settings
from app.sources.base import NewsSource, SourceResult

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, NewsSource] = {}


def register_source(name: str, source: NewsSource) -> None:
    _REGISTRY[name] = source


def _bootstrap() -> None:
    """按配置懒加载内置适配器。"""
    s = get_settings()
    if s.gdelt_enabled and "gdelt" not in _REGISTRY:
        from app.sources.gdelt import GDELTSource

        register_source("gdelt", GDELTSource())
    if s.rss_enabled and "rss" not in _REGISTRY:
        from app.sources.rss import RSSSource

        register_source("rss", RSSSource(s.rss_feeds))
    if s.tavily_enabled and s.tavily_api_key and "tavily" not in _REGISTRY:
        from app.sources.tavily import TavilySource

        register_source("tavily", TavilySource(s.tavily_api_key))
    if s.serper_enabled and s.serper_api_key and "serper" not in _REGISTRY:
        from app.sources.serper import SerperSource

        register_source("serper", SerperSource(s.serper_api_key))
    if s.bocha_enabled and s.bocha_api_key and "bocha" not in _REGISTRY:
        from app.sources.bocha import BochaSource

        register_source("bocha", BochaSource(s.bocha_api_key))


def get_enabled_sources() -> list[NewsSource]:
    _bootstrap()
    return list(_REGISTRY.values())


async def search_all(
    query: str, *, days: int, lang: str, limit_per_source: int = 25
) -> list[SourceResult]:
    """并发调用所有启用源；单源超时/异常降级为 degraded，不阻断整体。"""
    sources = get_enabled_sources()
    if not sources:
        return []

    async def _run(src: NewsSource) -> SourceResult:
        try:
            articles = await asyncio.wait_for(
                src.search(query, days=days, lang=lang, limit=limit_per_source), timeout=15
            )
            return SourceResult(name=src.name, status="ok", count=len(articles), articles=articles)
        except asyncio.TimeoutError:
            logger.warning("source %s timeout", src.name)
            return SourceResult(name=src.name, status="degraded", count=0, error="timeout")
        except Exception as e:  # noqa: BLE001
            logger.warning("source %s failed: %s", src.name, e)
            return SourceResult(name=src.name, status="degraded", count=0, error=str(e))

    return await asyncio.gather(*[_run(s) for s in sources])
