"""风险评分引擎：LLM 输出原料，代码计算分数（确定性、可解释、可测试）。

公式见 docs/ARCHITECTURE.md 第 6 节：
  weight(s) = severity × confidence × credibility × decay
  decay(s)  = 0.5 ^ (days_since_first_seen / half_life)
  raw_d     = Σ weight(s)
  score_d   = 100 × (1 − e^(−raw_d / k))
  overall   = Σ w_d × score_d
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from app.scoring import config as C

Dimension = Literal["judicial", "finance", "regulatory", "governance", "quality", "reputation"]
Grade = Literal["low", "low_mid", "mid", "mid_high", "high", "insufficient"]


@dataclass
class SignalIn:
    """评分输入：一条已归并的风险信号。"""
    signal_id: str
    dimension: str
    severity: int          # 1-5
    confidence: float      # 0-1
    credibility: float     # 0-1 来源可信度
    first_seen: datetime


@dataclass
class DimensionScore:
    dimension: str
    score: float
    raw: float
    top_signal_ids: list[str] = field(default_factory=list)


@dataclass
class ScoreResult:
    overall: float
    grade: Grade
    dimensions: dict[str, DimensionScore]
    insufficient_data: bool
    sample_size: int


def _decay(first_seen: datetime, now: datetime, half_life: int) -> float:
    days = max((now - first_seen).total_seconds() / 86400, 0.0)
    return 0.5 ** (days / half_life)


def _signal_weight(s: SignalIn, now: datetime) -> float:
    return s.severity * s.confidence * s.credibility * _decay(s.first_seen, now, C.HALF_LIFE_DAYS)


def _grade_from_score(score: float) -> Grade:
    t = C.GRADE_THRESHOLDS
    if score < t[0]:
        return "low"
    if score < t[1]:
        return "low_mid"
    if score < t[2]:
        return "mid"
    if score < t[3]:
        return "mid_high"
    return "high"


def score_signals(
    signals: list[SignalIn], *, sample_size: int, now: datetime | None = None
) -> ScoreResult:
    """对全部信号做六维评分与综合分。"""
    now = now or datetime.now(tz=timezone.utc)
    by_dim: dict[str, list[SignalIn]] = {d: [] for d in C.WEIGHTS}
    for s in signals:
        if s.dimension in by_dim:
            by_dim[s.dimension].append(s)

    dimensions: dict[str, DimensionScore] = {}
    for dim, sigs in by_dim.items():
        if not sigs:
            dimensions[dim] = DimensionScore(dimension=dim, score=0.0, raw=0.0)
            continue
        weighted = sorted(
            ((s, _signal_weight(s, now)) for s in sigs), key=lambda x: x[1], reverse=True
        )
        raw = sum(w for _, w in weighted)
        score = 100.0 * (1.0 - math.exp(-raw / C.SATURATION_K))
        dimensions[dim] = DimensionScore(
            dimension=dim,
            score=round(score, 1),
            raw=round(raw, 4),
            top_signal_ids=[s.signal_id for s, _ in weighted[:3]],
        )

    overall = sum(C.WEIGHTS[d] * dimensions[d].score for d in C.WEIGHTS)
    overall = round(overall, 1)
    insufficient = sample_size < C.MIN_RELEVANT_ARTICLES
    grade: Grade = "insufficient" if insufficient else _grade_from_score(overall)
    return ScoreResult(overall=overall, grade=grade, dimensions=dimensions, insufficient_data=insufficient, sample_size=sample_size)
