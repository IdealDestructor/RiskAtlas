"""数据源统一接口与数据模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel


class RawArticle(BaseModel):
    source: str
    url: str
    title: str
    snippet: str | None = None
    published_at: datetime | None = None
    language: str | None = None
    domain: str


@runtime_checkable
class NewsSource(Protocol):
    name: str

    async def search(
        self, query: str, *, days: int, lang: str, limit: int
    ) -> list[RawArticle]: ...


class SourceResult(BaseModel):
    name: str
    status: str
    count: int
    error: str | None = None
    articles: list[RawArticle] = []
