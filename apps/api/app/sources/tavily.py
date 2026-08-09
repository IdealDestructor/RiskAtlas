"""Tavily 搜索适配器（中英文网页搜索，需 key）。"""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

import httpx

from app.sources.base import RawArticle

_BASE = "https://api.tavily.com/search"


class TavilySource:
    name = "tavily"

    def __init__(self, api_key: str, *, use_proxy: bool = False) -> None:
        self._key = api_key
        self._client = httpx.AsyncClient(
            timeout=12,
            headers={"User-Agent": "RiskAtlas/1.0"},
            trust_env=use_proxy,
        )

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]:
        payload = {
            "api_key": self._key,
            "query": query,
            "search_depth": "advanced",
            "max_results": limit,
            "topic": "news",
            "days": max(days, 1),
        }
        resp = await self._client.post(_BASE, json=payload)
        resp.raise_for_status()
        data = resp.json()
        out: list[RawArticle] = []
        for item in data.get("results", [])[:limit]:
            url = item.get("url", "")
            if not url:
                continue
            out.append(
                RawArticle(
                    source=self.name,
                    url=url,
                    title=item.get("title", "")[:300],
                    snippet=item.get("content", "")[:500] or None,
                    published_at=_parse(item.get("published_date")),
                    language=lang if lang != "auto" else None,
                    domain=urlparse(url).netloc,
                )
            )
        return out


def _parse(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
