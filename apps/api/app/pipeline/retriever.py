"""多源检索 + URL 去重（T-103/T-106 最小实现）。"""

from __future__ import annotations

from urllib.parse import urlparse

from app.sources.base import RawArticle
from app.sources.registry import search_all


def _normalize_url(url: str) -> str:
    p = urlparse(url)
    host = (p.netloc or "").lower()
    path = (p.path or "").rstrip("/") or "/"
    return f"{p.scheme}://{host}{path}"


def dedupe_articles(articles: list[RawArticle]) -> list[RawArticle]:
    """按规范化 URL 去重，保持原顺序。"""
    seen: set[str] = set()
    out: list[RawArticle] = []
    for art in articles:
        key = _normalize_url(art.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(art)
    return out


async def retrieve(
    query: str, *, days: int, lang: str, limit_per_source: int = 25
) -> list[RawArticle]:
    """并发检索全部启用源并去重；单源失败由注册表降级，不阻断整体。"""
    results = await search_all(query, days=days, lang=lang, limit_per_source=limit_per_source)
    raw = [art for r in results if r.status == "ok" for art in r.articles]
    return dedupe_articles(raw)
