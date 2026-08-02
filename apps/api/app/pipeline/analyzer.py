"""单篇文章结构化分析：LLM 抽取风险事件（T-107 最小实现）。

文章分析以上游检索返回的标题+摘要为输入（正文抽取见 T-105，后续接入）。
"""

from __future__ import annotations

import asyncio
import logging

from app.config import get_settings
from app.llm.gateway import LLMCostTracker, LLMGateway
from app.llm.schemas import ARTICLE_ANALYSIS_SCHEMA
from app.sources.base import RawArticle

logger = logging.getLogger(__name__)

_ANALYSIS_SYSTEM = (
    "你是一名严谨的企业风险情报分析师。根据给定的文章标题与摘要，判断其与目标实体的相关性，"
    "并抽取其中反映的风险事件。六维分类：judicial 司法诉讼、finance 财务信用、"
    "regulatory 监管合规、governance 经营治理、quality 产品质量、reputation 声誉舆情。"
    "输出必须完全符合 JSON Schema 约束。"
)

_ANALYSIS_USER = """目标实体：{entity}
标题：{title}
摘要：{snippet}
请返回 relevance / sentiment / events / mentioned_entities 四字段的 JSON。若无风险事件，events 为空数组。"""


async def analyze_article(
    gateway: LLMGateway,
    entity: str,
    article: RawArticle,
    *,
    cost: LLMCostTracker | None = None,
) -> dict | None:
    """分析单篇文章，返回 ARTICLE_ANALYSIS_SCHEMA 结构；失败返回 None。"""
    snippet = (article.snippet or "").strip() or "（无摘要）"
    try:
        resp = await gateway.achat_structured(
            [
                {"role": "system", "content": _ANALYSIS_SYSTEM},
                {
                    "role": "user",
                    "content": _ANALYSIS_USER.format(
                        entity=entity, title=article.title, snippet=snippet
                    ),
                },
            ],
            ARTICLE_ANALYSIS_SCHEMA,
            max_tokens=1536,
            cost=cost,
        )
        return resp.parsed
    except Exception as e:  # noqa: BLE001
        logger.warning("article analyze failed: %s", e)
        return None


async def analyze_all(
    gateway: LLMGateway,
    entity: str,
    articles: list[RawArticle],
    *,
    cost: LLMCostTracker | None = None,
    concurrency: int = 5,
    max_retries: int = 2,
) -> list[dict | None]:
    """并发分析全部文章，返回与入参等长的结果列表；失败或跳过为 None。"""
    settings = get_settings()
    sem = asyncio.Semaphore(concurrency)
    results: list[dict | None] = [None] * len(articles)

    async def _run(i: int) -> None:
        async with sem:
            if cost is not None and cost.remaining(settings.analysis_budget_cny) <= 0:
                return
            for attempt in range(max_retries + 1):
                result = await analyze_article(gateway, entity, articles[i], cost=cost)
                if result is not None:
                    results[i] = result
                    return
                if attempt < max_retries:
                    # 失败后稍作退避再重试，避免并发任务一起瞬时重打服务商限流
                    await asyncio.sleep(min(2.0 * (2**attempt), 10.0))
            results[i] = None

    await asyncio.gather(*[_run(i) for i in range(len(articles))])
    return results
