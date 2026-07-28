"""博查搜索适配器（中文网页搜索优化），需 key。"""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

import httpx

from app.sources.base import RawArticle

_BASE = "https://api.bochaai.com/v1/web-search"


class BochaSource:
    name = "bocha"

    def __init__(self, api_key: str) -> None:
        self._key = api_key
        self._client = httpx.AsyncClient(
            timeout=12,
            headers={"Authorization": f"Bearer {api_key}", "User-Agent": "RiskAtlas/1.0"},
        )

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]:
        payload = {"query": query, "count": limit, "freshness": f"oneMonth" if days <= 30 else "oneYear"}
        resp = await self._client.post(_BASE, json=payload)
        resp.raise_for_status()
        data = resp.json()
        out: list[RawArticle] = []
        pages = data.get("data", {}).get("webPages", {}).get("value", [])
        for item in pages[:limit]:
            url = item.get("url", "")
            if not url:
                continue
            out.append(
                RawArticle(
                    source=self.name,
                    url=url,
                    title=item.get("name", "")[:300],
                    snippet=item.get("summary", "")[:500] or None,
                    published_at=_parse(item.get("dateLastCrawled")),
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
