"""流式研报生成（T-110 最小实现）。"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, AsyncIterator

from app.llm.gateway import LLMCostTracker, LLMGateway
from app.pipeline.signals import Signal
from app.scoring.engine import ScoreResult

logger = logging.getLogger(__name__)

_REPORTER_SYSTEM = """你是一名专业的企业风险研究员。请基于提供的信号与文章证据，为指定实体撰写一份简洁的中文风险研报（Markdown）。
要求：
- 结构：## 概述 / ## 风险维度 / ## 关键证据 / ## 结论
- 引用文章用 [n]（n 为证据编号），只可使用提供的编号，不得编造
- 只陈述提供的事实，不确定的措辞用"可能""或"
- 若信息不足（相关文章 <5 篇），在概述中说明原因，结论标记"信息不足"，不给确定等级"""

_REPORTER_USER = """实体：{entity}
综合风险分：{overall}/100，等级：{grade}
样本量：{sample_size} 篇

六维得分：
{dimensions}

风险信号：
{signals}

证据文章：
{articles}
请生成研报。"""

_DIMENSION_LABELS = {
    "judicial": "司法诉讼",
    "finance": "财务信用",
    "regulatory": "监管合规",
    "governance": "经营治理",
    "quality": "产品质量",
    "reputation": "声誉舆情",
}


def _format_articles(articles: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for i, art in enumerate(articles, start=1):
        date = art.get("published_at")
        if isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d")
        else:
            date_str = str(date or "未知")
        lines.append(f"[{i}] {art.get('title', '')}（{art.get('domain', '')}，{date_str}）")
    return "\n".join(lines) or "（无）"


def build_report_prompt(
    *,
    entity: str,
    score: ScoreResult,
    signals: list[Signal],
    articles: list[dict[str, Any]],
) -> list[dict[str, str]]:
    dim_lines = []
    for dim, label in _DIMENSION_LABELS.items():
        ds = score.dimensions.get(dim)
        dim_lines.append(f"- {label}：{ds.score if ds else 0.0}/100")
    signal_lines = []
    for s in signals:
        ev = ", ".join(f"[{i}]" for i in s.article_indices)
        signal_lines.append(
            f"- [{s.dimension}] {s.label}（严重度 {s.severity}/5，置信度 {s.confidence:.2f}，"
            f"提及 {s.mention_count} 次）{s.summary}{' 证据：' + ev if ev else ''}"
        )
    user = _REPORTER_USER.format(
        entity=entity,
        overall=score.overall,
        grade=score.grade,
        sample_size=score.sample_size,
        dimensions="\n".join(dim_lines),
        signals="\n".join(signal_lines) or "（无）",
        articles=_format_articles(articles),
    )
    return [
        {"role": "system", "content": _REPORTER_SYSTEM},
        {"role": "user", "content": user},
    ]


async def stream_report(
    gateway: LLMGateway,
    *,
    entity: str,
    score: ScoreResult,
    signals: list[Signal],
    articles: list[dict[str, Any]],
    cost: LLMCostTracker | None = None,
) -> AsyncIterator[str]:
    messages = build_report_prompt(
        entity=entity, score=score, signals=signals, articles=articles
    )
    async for chunk in gateway.astream_chat(messages, cost=cost):
        yield chunk
