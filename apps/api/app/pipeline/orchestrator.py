"""分析管线编排器：状态机 + SSE 事件发射。

M0 提供可跑通的最小管线骨架：实体解析→检索→去重→分析→评分→研报。
各阶段逻辑在 M1 逐步充实；本文件先保证阶段切换与事件协议正确。
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import AsyncIterator, Literal

from app.schemas.analysis import AnalysisCreate

logger = logging.getLogger(__name__)

Stage = Literal[
    "pending", "resolving", "awaiting_disambiguation",
    "retrieving", "analyzing", "scoring", "reporting", "completed", "failed", "cancelled",
]


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
    """管线主体：M0 骨架版，逐步切阶段并发事件；M1 替换为真实逻辑。"""
    try:
        await _set_stage(task, "resolving", "实体解析中")
        await asyncio.sleep(0.3)
        # M1: LLM 实体解析
        task.entity_name = task.query
        task.entity_type = "company"
        task.emit("entity", {"entity_name": task.entity_name, "entity_type": task.entity_type, "expanded_queries": [task.query]})

        await _set_stage(task, "retrieving", "多源检索中")
        await asyncio.sleep(0.5)
        # M1: sources.search_all + extractor + deduper
        task.emit("retrieval_stats", {"fetched": 0, "after_dedup": 0, "clusters": 0, "sources": []})

        await _set_stage(task, "analyzing", "AI 结构化分析中")
        await asyncio.sleep(0.5)
        # M1: analyzer 并发 LLM 分析

        await _set_stage(task, "scoring", "风险评分中")
        await asyncio.sleep(0.3)
        # M1: scoring.engine.score_signals
        task.sample_size = 0
        task.emit("scores", {"overall": 0, "grade": "insufficient", "dimensions": {}, "insufficient_data": True, "sample_size": 0})

        await _set_stage(task, "reporting", "生成研报中")
        # M1: reporter astream_chat
        task.emit("report_chunk", {"text": "（研报骨架占位：M1 将由 LLM 流式生成。）\n\n本次为工程骨架版本，尚未接入真实数据与模型，风险结论标记为信息不足。"})

        task.status = "completed"
        task.stage = "completed"
        task.message = "完成（骨架）"
        task.emit("completed", {"status": "completed", "sample_size": task.sample_size, "note": "M0 骨架：真实管线在 M1 接入"})
    except asyncio.CancelledError:
        task.status = "cancelled"
        task.emit("error", {"message": "cancelled"})
        raise
    except Exception as e:  # noqa: BLE001
        logger.exception("pipeline failed")
        task.status = "failed"
        task.emit("error", {"message": str(e)})
    finally:
        task.done()


async def _set_stage(task: AnalysisTask, stage: Stage, message: str) -> None:
    if task._cancelled:
        raise asyncio.CancelledError()
    task.stage = stage
    task.message = message
    task.emit("status", {"stage": stage, "message": message})


async def event_stream(task: AnalysisTask) -> AsyncIterator[str]:
    """SSE 事件流生成器。"""
    while True:
        item = await task._queue.get()
        ev = item["event"]
        if ev == "__done__":
            yield "event: __eof__\ndata: {}\n\n"
            break
        yield f"event: {ev}\ndata: {json.dumps(item['data'], ensure_ascii=False)}\n\n"
