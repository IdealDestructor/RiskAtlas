"""LLM 结构化输出的 JSON Schema 定义与维度常量。"""

from __future__ import annotations

from typing import Any

SENTIMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "label": {"type": "string", "enum": ["negative", "neutral", "positive"]},
        "score": {"type": "number", "minimum": -1, "maximum": 1},
    },
    "required": ["label", "score"],
    "additionalProperties": False,
}

EVENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "dimension": {
            "type": "string",
            "enum": ["judicial", "finance", "regulatory", "governance", "quality", "reputation"],
        },
        "label": {"type": "string"},
        "severity": {"type": "integer", "minimum": 1, "maximum": 5},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "summary": {"type": "string"},
    },
    "required": ["dimension", "label", "severity", "confidence", "summary"],
    "additionalProperties": False,
}

ARTICLE_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "relevance": {"type": "number", "minimum": 0, "maximum": 1},
        "sentiment": SENTIMENT_SCHEMA,
        "events": {"type": "array", "items": EVENT_SCHEMA},
        "mentioned_entities": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["relevance", "sentiment", "events", "mentioned_entities"],
    "additionalProperties": False,
}

ENTITY_RESOLVE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "entity_name": {"type": "string"},
        "entity_type": {
            "type": "string",
            "enum": ["company", "person", "product", "industry", "unknown"],
        },
        "aliases": {"type": "array", "items": {"type": "string"}},
        "english_name": {"type": "string"},
        "expanded_queries": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "disambiguation_candidates": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["entity_name", "entity_type", "expanded_queries", "confidence"],
    "additionalProperties": False,
}

DIMENSION_LABELS: dict[str, str] = {
    "judicial": "司法诉讼",
    "finance": "财务信用",
    "regulatory": "监管合规",
    "governance": "经营治理",
    "quality": "产品质量",
    "reputation": "声誉舆情",
}

DIMENSION_WEIGHTS: dict[str, float] = {
    "judicial": 0.22,
    "finance": 0.22,
    "regulatory": 0.18,
    "governance": 0.14,
    "quality": 0.12,
    "reputation": 0.12,
}
