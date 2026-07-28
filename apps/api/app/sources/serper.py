"""Serper（Google 结果）搜索适配器，需 key。"""

from __future__ import annotations

from urllib.parse import urlparse

import httpx

from app.sources.base import RawArticle

_BASE = "https://google.serper.dev/news"


class SerperSource:
    name = "serper"

    def __init__(self, api_key: str) -> None:
        self._key = api_key
        self._client = httpx.AsyncClient(
            timeout=12,
            headers={"X-API-KEY": api_key, "User-Agent": "Yutu/1.0"},
        )

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]:
        payload = {"q": query, "num": limit, "gl": "cn" if lang == "zh" else "us"}
        resp = await self._client.post(_BASE, json=payload)
        resp.raise_for_status()
        data = resp.json()
        out: list[RawArticle] = []
        for item in data.get("news", [])[:limit]:
            url = item.get("link", "")
            if not url:
                continue
            out.append(
                RawArticle(
                    source=self.name,
                    url=url,
                    title=item.get("title", "")[:300],
                    snippet=item.get("snippet", "")[:500] or None,
                    language=lang if lang != "auto" else None,
                    domain=urlparse(url).netloc,
                )
            )
        return out
