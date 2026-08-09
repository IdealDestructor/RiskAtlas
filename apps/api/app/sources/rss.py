"""RSS 与无 key 新闻搜索适配器。"""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from time import mktime
from urllib.parse import urlencode, urlparse

import feedparser
import httpx

from app.sources.base import RawArticle

logger = logging.getLogger(__name__)

_DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.theguardian.com/business/rss",
    "https://www.theguardian.com/technology/rss",
]

_HEADERS = {
    "User-Agent": "RiskAtlas/1.0 (+https://riskatlas.local)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
}


class RSSSource:
    """抓取配置的静态 RSS，并按查询词进行本地过滤。"""

    name = "rss"

    def __init__(self, feeds_cfg: str = "", *, use_proxy: bool = False) -> None:
        self._feeds = [
            line.split("#", 1)[0].strip()
            for line in (feeds_cfg or "").splitlines()
            if line.split("#", 1)[0].strip()
        ] or _DEFAULT_FEEDS
        self._use_proxy = use_proxy

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]:
        return await _search_feeds(
            self._feeds,
            source=self.name,
            query=query,
            days=days,
            lang=lang,
            limit=limit,
            filter_query=True,
            use_proxy=self._use_proxy,
        )


class QueryRSSSource:
    """将查询直接交给新闻 RSS 搜索引擎，作为无 key 兜底源。"""

    def __init__(
        self,
        name: str,
        url_builder: Callable[[str], str],
        *,
        use_proxy: bool = False,
    ) -> None:
        self.name = name
        self._url_builder = url_builder
        self._use_proxy = use_proxy

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]:
        return await _search_feeds(
            [self._url_builder(query)],
            source=self.name,
            query=query,
            days=days,
            lang=lang,
            limit=limit,
            filter_query=False,
            use_proxy=self._use_proxy,
        )


def google_news_url(query: str) -> str:
    # Google News RSS accepts ordinary terms and the when:N d operator.
    params = {
        "q": f"{query} when:{max(1, min(30, 30))}d",
        "hl": "zh-CN" if _looks_chinese(query) else "en-US",
        "gl": "CN" if _looks_chinese(query) else "US",
        "ceid": "CN:zh-Hans" if _looks_chinese(query) else "US:en",
    }
    return "https://news.google.com/rss/search?" + urlencode(params)


def bing_news_url(query: str) -> str:
    return "https://www.bing.com/news/search?" + urlencode({"q": query, "format": "rss"})


async def _search_feeds(
    feeds: list[str],
    *,
    source: str,
    query: str,
    days: int,
    lang: str,
    limit: int,
    filter_query: bool,
    use_proxy: bool,
) -> list[RawArticle]:
    timeout = httpx.Timeout(12.0, connect=8.0)
    async with httpx.AsyncClient(
        timeout=timeout,
        headers=_HEADERS,
        follow_redirects=True,
        trust_env=use_proxy,
    ) as client:
        results = await asyncio.gather(
            *(_fetch_feed(client, feed_url) for feed_url in feeds),
            return_exceptions=True,
        )

    cutoff = datetime.now(tz=UTC) - timedelta(days=max(days, 1))
    terms = _query_terms(query)
    out: list[RawArticle] = []
    seen_urls: set[str] = set()
    for feed_url, parsed in zip(feeds, results, strict=False):
        if isinstance(parsed, Exception):
            logger.warning("rss feed failed source=%s url=%s error=%s", source, feed_url, parsed)
            continue
        for entry in parsed.entries:
            title = str(entry.get("title", "")).strip()
            summary = str(entry.get("summary", entry.get("description", ""))).strip()
            content = " ".join(
                str(item.get("value", "")) for item in entry.get("content", []) if isinstance(item, dict)
            )
            searchable = f"{title} {summary} {content}".lower()
            if filter_query and terms and not any(term in searchable for term in terms):
                continue
            published = _parse_feed_date(
                entry.get("published_parsed") or entry.get("updated_parsed")
            )
            if published and published < cutoff:
                continue
            url = str(entry.get("link", "")).strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            out.append(
                RawArticle(
                    source=source,
                    url=url,
                    title=title[:300] or url,
                    snippet=_strip_markup(summary or content)[:500] or None,
                    published_at=published,
                    language=lang if lang != "auto" else None,
                    domain=urlparse(url).netloc,
                )
            )
            if len(out) >= limit:
                return out
    return out


async def _fetch_feed(client: httpx.AsyncClient, url: str):
    response = await client.get(url)
    response.raise_for_status()
    parsed = feedparser.parse(response.content)
    if getattr(parsed, "bozo", False) and not parsed.entries:
        raise ValueError(f"invalid RSS/Atom response: {url}")
    return parsed


def _query_terms(query: str) -> list[str]:
    terms = [term.lower() for term in re.split(r"\s+|[,，。；;:：/]+", query) if term.strip()]
    return [term for term in terms if len(term) >= 2]


def _looks_chinese(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)


def _strip_markup(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value).replace("&nbsp;", " ").strip()


def _parse_feed_date(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromtimestamp(mktime(value), tz=UTC)
    except (TypeError, ValueError, OverflowError, OSError):
        return None