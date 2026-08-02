"""实体解析：LLM 判定实体画像与扩展查询词（T-102 最小实现，失败降级为原文）。"""

from __future__ import annotations

import logging
from typing import Any

from app.llm.gateway import LLMCostTracker, LLMGateway
from app.llm.schemas import ENTITY_RESOLVE_SCHEMA

logger = logging.getLogger(__name__)

_RESOLVE_SYSTEM = (
    "你是企业情报检索的实体解析器。从用户查询中识别目标实体，给出规范化名称、类型、"
    "别名、英文名、扩展查询词与消歧置信度。输出必须符合 JSON Schema 约束。"
)

_RESOLVE_USER = (
    "用户查询：{query}\n"
    "请返回 entity_name / entity_type / aliases / english_name / expanded_queries / "
    "confidence / disambiguation_candidates。"
)


async def resolve_entity(
    gateway: LLMGateway, query: str, *, cost: LLMCostTracker | None = None
) -> dict[str, Any] | None:
    """解析实体画像；LLM 失败时返回 None，由调用方降级为原文。"""
    try:
        resp = await gateway.achat_structured(
            [
                {"role": "system", "content": _RESOLVE_SYSTEM},
                {"role": "user", "content": _RESOLVE_USER.format(query=query)},
            ],
            ENTITY_RESOLVE_SCHEMA,
            max_tokens=1024,
            cost=cost,
        )
        return resp.parsed
    except Exception as e:  # noqa: BLE001
        logger.warning("entity resolve failed: %s", e)
        return None
