"""FastAPI 应用入口。"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analyses, health

settings = get_settings()

app = FastAPI(title="RiskAtlas API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(analyses.router, prefix=API_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": "舆图 Yutu API", "docs": f"{API_PREFIX}/docs"}
