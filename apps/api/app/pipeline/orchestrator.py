"""分析管线编排器：状态机 + SSE 事件发射。

M1 真实管线：实体解析 → 多源检索去重 → 逐篇 LLM 结构化分析 →
信号归并 → 确定性评分 → 流式研报。各阶段产出通过 SSE 增量推送。
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import AsyncIterator, Literal

from app.llm.gateway import LLMCostTracker, LLMGateway
from app.pipeline.analyzer import analyze_all
from app.pipeline.planner import resolve_entity
from app.pipeline.reporter import stream_report
from app.pipeline.retriever import dedupe_articles
from app.pipeline.signals import AnalyzedEvent, merge_signals
from app.schemas.analysis import AnalysisCreate
from app.scoring import config as SC
from app.scoring.engine import SignalIn, score_signals
from app.sources.registry import search_all

logger = logging.getLogger(__name__)

Stage = Literal[
    "pending", "resolving", "awaiting_disambiguation",
    "retrieving", "analyzing", "scoring", "reporting", "completed", "failed", "cancelled",
]

# 单次分析的文章上限与相关度门槛（相关 <MIN_RELEVANT_ARTICLES 篇判为信息不足）
MAX_ANALYZE_ARTICLES = 40
RELEVANCE_THRESHOLD = 0.3
ANALYZE_CONCURRENCY = 5


@dataclass
class AnalysisTask:
    id: str
    query: str
    params: AnalysisCreate
    status: Stage = "pending"
    stage: str | None = None
    message: str | None = None
    entity_name: str | None = None
    entity_type: str | None = None
    sample_size: int = 0
    cost_cny: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    _queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    _cancelled: bool = False

    def emit(self, event: str, data: dict) -> None:
        self._queue.put_nowait({"event": event, "data": data})

    def done(self) -> None:
        self._queue.put_nowait({"event": "__done__", "data": {}})


_TASKS: dict[str, AnalysisTask] = {}


def get_task(task_id: str) -> AnalysisTask | None:
    return _TASKS.get(task_id)


def create_task(req: AnalysisCreate) -> AnalysisTask:
    tid = str(uuid.uuid4())
    task = AnalysisTask(id=tid, query=req.query, params=req)
    _TASKS[tid] = task
    return task


async def run_pipeline(task: AnalysisTask) -> None:
    """管线主体：解析→检索→分析→评分→研报，逐阶段发射 SSE 事件。"""
    gateway = LLMGateway()
    cost = LLMCostTracker()
    try:
        # --- 阶段 1：实体解析 ---
        await _set_stage(task, "resolving", "实体解析中")
        resolved = await resolve_entity(gateway, task.query, cost=cost)
        if resolved and resolved.get("entity_name"):
            task.entity_name = resolved.get("entity_name")
            task.entity_type = resolved.get("entity_type") or "unknown"
            expanded = list(resolved.get("expanded_queries") or [])
        else:
            task.entity_name = task.query
            task.entity_type = "company"
            expanded = []
        if task.query not in expanded:
            expanded.insert(0, task.query)
        task.emit(
            "entity",
            {
                "entity_name": task.entity_name,
                "entity_type": task.entity_type,
                "expanded_queries": expanded[:6],
            },
        )

        # --- 阶段 2：多源检索 + 去重 ---
        await _set_stage(task, "retrieving", "多源检索中")
        results = await search_all(
            task.entity_name,
            days=task.params.days,
            lang=task.params.language,
            limit_per_source=25,
        )
        articles = dedupe_articles(
            [art for r in results if r.status == "ok" for art in r.articles]
        )[:MAX_ANALYZE_ARTICLES]
        task.emit(
            "retrieval_stats",
            {
                "fetched": sum(r.count for r in results),
                "after_dedup": len(articles),
                "clusters": len(articles),
                "sources": [
                    {"name": r.name, "status": r.status, "count": r.count} for r in results
                ],
            },
        )

        # --- 阶段 3：逐篇 LLM 结构化分析 ---
        await _set_stage(task, "analyzing", "AI 结构化分析中")
        analyses = await analyze_all(
            gateway, task.entity_name, articles, cost=cost, concurrency=ANALYZE_CONCURRENCY
        )
        events: list[AnalyzedEvent] = []
        relevant = 0
        for i, (art, an) in enumerate(zip(articles, analyses)):
            if not an:
                continue
            relevance = float(an.get("relevance", 0.0))
            relevant += 1 if relevance >= RELEVANCE_THRESHOLD else 0
            for ev in an.get("events") or []:
                events.append(
                    AnalyzedEvent(
                        dimension=ev.get("dimension", "reputation"),
                        label=ev.get("label") or "未知风险",
                        severity=int(ev.get("severity", 1)),
                        confidence=float(ev.get("confidence", 0.5)),
                        summary=ev.get("summary") or "",
                        published_at=art.published_at,
                        article_index=i,
                    )
                )
            task.emit(
                "article_analyzed",
                {
                    "done": i + 1,
                    "total": len(articles),
                    "current": {
                        "title": art.title,
                        "relevance": relevance,
                        "sentiment": an.get("sentiment", {}).get("label", "neutral"),
                    },
                },
            )
        signals = merge_signals(events)

        # --- 阶段 4：确定性评分 ---
        await _set_stage(task, "scoring", "风险评分中")
        signal_in = [
            SignalIn(
                signal_id=s.signal_id,
                dimension=s.dimension,
                severity=s.severity,
                confidence=s.confidence,
                credibility=SC.DEFAULT_CREDIBILITY,
                first_seen=s.first_seen,
            )
            for s in signals
        ]
        score = score_signals(signal_in, sample_size=relevant)
        task.sample_size = relevant
        task.cost_cny = round(cost.total_cny, 4)
        task.emit(
            "scores",
            {
                "overall": score.overall,
                "grade": score.grade,
                "dimensions": {
                    d: {"score": ds.score, "raw": ds.raw}
                    for d, ds in score.dimensions.items()
                },
                "insufficient_data": score.insufficient_data,
                "sample_size": relevant,
            },
        )
        task.emit(
            "articles",
            {
                "articles": [
                    {
                        "index": i,
                        "title": art.title,
                        "url": art.url,
                        "domain": art.domain,
                        "snippet": art.snippet,
                        "published_at": (
                            art.published_at.isoformat() if art.published_at else None
                        ),
                    }
                    for i, art in enumerate(articles)
                ]
            },
        )
        for s in signals:
            task.emit("signal", s.to_emit())

        # --- 阶段 5：流式研报 ---
        await _set_stage(task, "reporting", "生成研报中")
        if not articles:
            task.emit(
                "report_chunk",
                {
                    "text": (
                        "## 概述\n\n本次分析未从任何已启用数据源检索到相关文章，"
                        "无法生成风险结论。可尝试更换查询词、扩大时间窗或检查数据源配置。"
                    )
                },
            )
        else:
            report_articles = [
                {
                    "title": art.title,
                    "domain": art.domain,
                    "published_at": art.published_at,
                    "snippet": art.snippet,
                }
                for art in articles
            ]
            async for chunk in stream_report(
                gateway,
                entity=task.entity_name,
                score=score,
                signals=signals,
                articles=report_articles,
                cost=cost,
            ):
                task.emit("report_chunk", {"text": chunk})
        task.cost_cny = round(cost.total_cny, 4)

        task.status = "completed"
        task.stage = "completed"
        task.message = "完成"
        task.emit(
            "completed",
            {
                "status": "completed",
                "sample_size": relevant,
                "cost_cny": task.cost_cny,
            },
        )
    except asyncio.CancelledError:
        task.status = "cancelled"
        task.emit("error", {"message": "cancelled"})
        raise
    except Exception as e:  # noqa: BLE001
        logger.exception("pipeline failed")
        task.status = "failed"
        msg = str(e)
        if "429" in msg:
            msg = "模型服务限流（429）：请求超出服务商速率上限，已自动重试仍失败，请稍后重新发起分析。"
        task.emit("error", {"message": msg})
    finally:
        task.done()


async def _set_stage(task: AnalysisTask, stage: Stage, message: str) -> None:
    if task._cancelled:
        raise asyncio.CancelledError()
    task.stage = stage
    task.message = message
    task.emit("status", {"stage": stage, "message": message})


async def event_stream(task: AnalysisTask) -> AsyncIterator[dict]:
    """SSE 事件流生成器：data 预序列化为 JSON，事件名由 sse_starlette 输出。"""
    while True:
        item = await task._queue.get()
        ev = item["event"]
        if ev == "__done__":
            yield {"event": "__eof__", "data": {}}
            break
        yield {"event": ev, "data": json.dumps(item["data"], ensure_ascii=False)}
