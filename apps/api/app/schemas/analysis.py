"""分析任务 API 模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["zh", "en", "auto"]


class AnalysisCreate(BaseModel):
    query: str = Field(min_length=1, max_length=120)
    days: int = Field(default=30, ge=1, le=365)
    language: Language = "auto"
    region: str | None = None


class AnalysisCreated(BaseModel):
    id: str
    status: str


class AnalysisStatus(BaseModel):
    id: str
    query: str
    entity_name: str | None = None
    entity_type: str | None = None
    status: str
    stage: str | None = None
    message: str | None = None
    sample_size: int = 0
    created_at: datetime
    cost_cny: float = 0.0
