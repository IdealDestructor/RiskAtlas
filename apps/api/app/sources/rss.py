"""RSS 源适配器（feedparser，免 key）。源列表可经 RSS_FEEDS 配置覆盖。"""

from __future__ import annotations

import logging
from datetime import datetime
from urllib.parse import urlparse

import feedparser

from app.sources.base import RawArticle

logger = logging.getLogger(__name__)

_DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.zhihu.com/rss",
]


class RSSSource:
    name = "rss"

    def __init__(self, feeds_cfg: str = "") -> None:
        self._feeds = [f.strip() for f in (feeds_cfg or "").splitlines() if f.strip()] or _DEFAULT_FEEDS

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]:
        q = query.lower()
        out: list[RawArticle] = []
        for feed_url in self._feeds:
            try:
                parsed = feedparser.parse(feed_url)
                for e in parsed.entries:
                    title = e.get("title", "")
                    summary = e.get("summary", "")
                    if q not in title.lower() and q not in summary.lower():
                        continue
                    url = e.get("link", "")
                    if not url:
                        continue
                    out.append(
                        RawArticle(
                            source=self.name,
                            url=url,
                            title=title[:300],
                            snippet=summary[:500] or None,
                            published_at=_parse_feed_date(e.get("published_parsed")),
                            language=lang if lang != "auto" else None,
                            domain=urlparse(url).netloc,
                        )
                    )
                    if len(out) >= limit:
                        return out
            except Exception:  # noqa: BLE001
                logger.debug("rss feed parse failed: %s", feed_url)
        return out


def _parse_feed_date(tp) -> datetime | None:
    if not tp:
        return None
    try:
        from time import mktime
        return datetime.fromtimestamp(mktime(tp))
    except Exception:  # noqa: BLE001
        return None
