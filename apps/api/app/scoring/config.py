"""评分引擎参数（可经环境变量调整）。"""

from __future__ import annotations

from app.llm.schemas import DIMENSION_WEIGHTS

HALF_LIFE_DAYS: int = 30
SATURATION_K: float = 8.0
MIN_RELEVANT_ARTICLES: int = 5
DEFAULT_CREDIBILITY: float = 0.6
GRADE_THRESHOLDS: tuple[int, int, int, int] = (20, 40, 60, 80)
WEIGHTS: dict[str, float] = dict(DIMENSION_WEIGHTS)
