"""评分引擎公式锁定测试。"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from app.scoring import config as C
from app.scoring.engine import SignalIn, score_signals

NOW = datetime(2026, 7, 28, tzinfo=timezone.utc)


def _sig(dim, sev, conf, cred, days_ago=0):
    return SignalIn(
        signal_id=f"s-{dim}-{sev}",
        dimension=dim,
        severity=sev,
        confidence=conf,
        credibility=cred,
        first_seen=NOW - timedelta(days=days_ago),
    )


def test_empty_signals_zero_score():
    r = score_signals([], sample_size=0, now=NOW)
    assert r.overall == 0.0
    assert r.grade == "insufficient"
    assert r.insufficient_data is True


def test_single_signal_score_formula():
    sig = _sig("judicial", sev=5, conf=1.0, cred=1.0, days_ago=0)
    r = score_signals([sig], sample_size=10, now=NOW)
    raw = 5 * 1.0 * 1.0 * 1.0
    expected = 100.0 * (1 - math.exp(-raw / C.SATURATION_K))
    assert abs(r.dimensions["judicial"].score - round(expected, 1)) < 0.05
    assert r.grade != "insufficient"
    assert r.dimensions["judicial"].top_signal_ids == ["s-judicial-5"]


def test_time_decay_reduces_score():
    fresh = score_signals([_sig("finance", 5, 1.0, 1.0, days_ago=0)], sample_size=10, now=NOW)
    old = score_signals([_sig("finance", 5, 1.0, 1.0, days_ago=C.HALF_LIFE_DAYS)], sample_size=10, now=NOW)
    assert old.dimensions["finance"].score < fresh.dimensions["finance"].score
    assert abs(old.dimensions["finance"].raw - fresh.dimensions["finance"].raw / 2) < 0.01


def test_saturation_caps_score():
    sigs = [_sig("quality", 5, 1.0, 1.0) for _ in range(10)]
    r = score_signals(sigs, sample_size=10, now=NOW)
    assert r.dimensions["quality"].score < 100.0
    assert r.dimensions["quality"].score > 50.0


def test_overall_weighted():
    sigs = [_sig("judicial", 5, 1.0, 1.0), _sig("finance", 4, 1.0, 1.0)]
    r = score_signals(sigs, sample_size=10, now=NOW)
    expected = round(
        C.WEIGHTS["judicial"] * r.dimensions["judicial"].score
        + C.WEIGHTS["finance"] * r.dimensions["finance"].score
        + sum(C.WEIGHTS[d] * 0.0 for d in C.WEIGHTS if d not in ("judicial", "finance")),
        1,
    )
    assert abs(r.overall - expected) < 0.05


def test_grade_thresholds():
    r = score_signals([], sample_size=3, now=NOW)
    assert r.grade == "insufficient"
    r2 = score_signals([_sig("judicial", 1, 0.1, 0.1)], sample_size=6, now=NOW)
    assert r2.grade in ("low", "low_mid", "mid", "mid_high", "high")


def test_sample_size_insufficient_threshold():
    r = score_signals([_sig("judicial", 5, 1.0, 1.0)], sample_size=4, now=NOW)
    assert r.insufficient_data is True
    assert r.grade == "insufficient"
    r2 = score_signals([_sig("judicial", 5, 1.0, 1.0)], sample_size=5, now=NOW)
    assert r2.insufficient_data is False
