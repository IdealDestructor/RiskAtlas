from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.pipeline.orchestrator import (
    create_task,
    event_stream,
    get_task,
    run_pipeline,
)
from app.schemas.analysis import AnalysisCreate, AnalysisCreated, AnalysisStatus

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisCreated)
async def create_analysis(req: AnalysisCreate) -> AnalysisCreated:
    task = create_task(req)
    asyncio.create_task(run_pipeline(task))
    return AnalysisCreated(id=task.id, status=task.status)


@router.get("/{task_id}", response_model=AnalysisStatus)
async def get_analysis(task_id: str) -> AnalysisStatus:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="analysis not found")
    return AnalysisStatus(
        id=task.id,
        query=task.query,
        entity_name=task.entity_name,
        entity_type=task.entity_type,
        status=task.status,
        stage=task.stage,
        message=task.message,
        sample_size=task.sample_size,
        created_at=task.created_at,
        cost_cny=task.cost_cny,
    )


@router.get("/{task_id}/events")
async def analysis_events(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="analysis not found")
    return EventSourceResponse(event_stream(task))
