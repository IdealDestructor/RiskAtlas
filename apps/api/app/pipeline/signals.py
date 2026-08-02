"""跨文章风险事件归并为信号（T-108 最小实现）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

DEFAULT_NOW = datetime.now(tz=timezone.utc)


def _ensure_aware(dt: datetime | None, fallback: datetime) -> datetime:
    if dt is None:
        return fallback
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class AnalyzedEvent:
    """单篇文章抽取出的一条风险事件（供归并）。"""

    dimension: str
    label: str
    severity: int
    confidence: float
    summary: str
    published_at: datetime | None = None
    article_index: int = -1


@dataclass
class Signal:
    """归并后的风险信号。"""

    signal_id: str
    dimension: str
    label: str
    severity: int
    confidence: float
    summary: str
    first_seen: datetime
    last_seen: datetime
    mention_count: int
    article_indices: list[int] = field(default_factory=list)

    def to_emit(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "dimension": self.dimension,
            "label": self.label,
            "severity": self.severity,
            "confidence": self.confidence,
            "summary": self.summary,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "mention_count": self.mention_count,
            "article_indices": self.article_indices,
        }


def merge_signals(events: list[AnalyzedEvent], *, now: datetime | None = None) -> list[Signal]:
    """同类事件（同维度 + 标签忽略大小写）合并为信号，按严重度×置信度×次数排序。"""
    now = now or DEFAULT_NOW
    buckets: dict[tuple[str, str], list[AnalyzedEvent]] = {}
    for ev in events:
        key = (ev.dimension, ev.label.strip().lower())
        buckets.setdefault(key, []).append(ev)

    out: list[Signal] = []
    for (dim, _), group in buckets.items():
        group.sort(key=lambda e: e.severity * e.confidence, reverse=True)
        top = group[0]
        first = min(_ensure_aware(e.published_at, now) for e in group)
        last = max(_ensure_aware(e.published_at, now) for e in group)
        out.append(
            Signal(
                signal_id=f"{dim}-{len(out) + 1}",
                dimension=dim,
                label=top.label,
                severity=top.severity,
                confidence=top.confidence,
                summary=top.summary,
                first_seen=first,
                last_seen=last,
                mention_count=len(group),
                article_indices=sorted(e.article_index for e in group if e.article_index >= 0),
            )
        )
    out.sort(key=lambda s: s.severity * s.confidence * s.mention_count, reverse=True)
    return out
