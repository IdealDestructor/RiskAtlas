
# RiskAtlas 舆图 · LLM 驱动的实时实体风险情报平台

输入一个名字（公司 / 品牌 / 人物 / 关键词），RiskAtlas 实时检索多源新闻舆情，由大模型完成实体消歧、事件抽取、情感研判与风险归类，经可解释的确定性评分引擎聚合，以流式驾驶舱呈现六维风险画像与 AI 风险研报——辅助金融机构完成授信尽调、投后监控与风险预警。
> 本项目是对原「舆图」（Vue 2 + ECharts 静态数据可视化，存档于 [`backup/`](./backup/)）的全面重构：从"静态库查数"升级为"查询词驱动的实时多源情报 + LLM 分析 + 流式可视化"。

## 核心能力

- **实体解析**：LLM 消歧 + 别名/扩展查询词生成，中英文查询均可
- **多源实时检索**：GDELT、RSS、Tavily / Serper / 博查等适配器并行，单源故障自动降级
- **AI 结构化分析**：逐篇情感研判与风险事件抽取（JSON Schema 强约束 + 幻觉防护）
- **六维风险评分**：司法诉讼 / 财务信用 / 监管合规 / 经营治理 / 产品质量 / 声誉舆情，确定性公式、可下钻到证据
- **流式驾驶舱**：风险总览、舆情走势、事件流、来源分布渐进渲染；AI 研报逐字生成、引用可溯源
- **持续监控（P1）**：Watchlist 定时重分析 + 阈值预警

## 技术栈

| 端 | 技术 |
| --- | --- |
| 前端 `apps/web` | Next.js 15 · React 19 · TypeScript · Tailwind v4 · shadcn/ui · ECharts 5 · Zustand（SSE） |
| 后端 `apps/api` | FastAPI · Python 3.12 · pydantic · httpx/asyncio · OpenAI 兼容 LLM 网关 · trafilatura · datasketch |
| 数据 | PostgreSQL 16（SQLAlchemy 2 async + Alembic） · Redis 7 |
| 部署 | docker-compose 一键编排 |

## 快速开始（脚手架就位后）

```bash
cp .env.example .env        # 填入 LLM 与数据源 key（GDELT/RSS 免 key 可直接跑）
docker compose up -d postgres redis
pnpm install && pnpm dev    # web :3000 / api :8000
```

## 文档

- [产品需求 PRD](./docs/PRD.md) — 场景、功能需求（P0/P1/P2）、风险指标体系
- [交互设计](./docs/INTERACTION_DESIGN.md) — 驾驶舱布局、流式状态、视觉规范
- [技术架构](./docs/ARCHITECTURE.md) — 管线状态机、SSE 协议、评分公式、数据模型、API 契约
- [重构待办](./docs/TODO.md) — M0-M4 分阶段任务清单与验收标准

## 路线图

- **M0 地基**：monorepo 骨架、契约生成、基础设施
- **M1 管线后端**：检索 → 去重 → LLM 分析 → 评分 → 研报全链路
- **M2 前端驾驶舱**：搜索 + 流式可视化面板
- **M3 产品化**：历史/分享/导出/追问/监控预警
- **M4 增强**：多实体对比、双语、全链路追踪

## 免责声明

平台输出由公开信息与 AI 分析生成，仅供风险研判参考，不构成任何投资建议或信贷决策依据。
