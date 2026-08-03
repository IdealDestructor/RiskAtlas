"""GDELT 2.1 DOC API 适配器（免 key）。

API: https://api.gdeltproject.org/api/v2/doc/doc
参数: query (简化布尔), mode=ArtList, maxrecords, timespan (PnD), sort=DateDesc
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx

from app.sources.base import RawArticle

logger = logging.getLogger(__name__)
_BASE = "https://api.gdeltproject.org/api/v2/doc/doc"


class GDELTSource:
    name = "gdelt"

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=12, headers={"User-Agent": "RiskAtlas/1.0"})

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]:
        # GDELT timespan: 最小 5 分钟，用 PnD
        timespan = f"P{max(days, 1)}D"
        params = {
            "query": query,
            "mode": "ArtList",
            "maxrecords": str(min(limit, 250)),
            "timespan": timespan,
            "sort": "DateDesc",
            "format": "json",
        }
        resp = await self._client.get(_BASE, params=params)
        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError:
            logger.warning("gdelt 返回非 JSON 响应（可能是限流/临时故障）: %s", resp.text[:200])
            return []
        articles: list[RawArticle] = []
        for item in data.get("articles", [])[:limit]:
            url = item.get("url", "")
            if not url:
                continue
            domain = urlparse(url).netloc
            published = _parse_dt(item.get("seendate") or item.get("date"))
            articles.append(
                RawArticle(
                    source=self.name,
                    url=url,
                    title=item.get("title", "")[:300],
                    snippet=item.get("socialimage") or None,
                    published_at=published,
                    language=item.get("language"),
                    domain=domain,
                )
            )
        return articles


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    # GDELT seendate 形如 20240115T120000Z
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None
