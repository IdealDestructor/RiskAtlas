# 舆图 · 重构待办列表

> 版本：v1.0 · 更新日期：2026-07-28
> 标记说明：`[ ]` 待办 / `[x]` 完成；每个任务尽量对应一次可验证的交付。

## M0 · 地基（工程骨架）

目标：双服务 monorepo 可一键启动，契约与质量基线就位。

- [x] T-001 pnpm workspace 初始化（根 `package.json`、`pnpm-workspace.yaml`、dev 脚本聚合）
- [x] T-002 `apps/api` FastAPI 骨架：`main.py` + `config.py`（pydantic-settings）+ `/health`，ruff/mypy/pytest 配置
- [x] T-003 `apps/web` Next.js 15 骨架（TS strict、Tailwind v4、lucide），eslint/vitest 配置
- [x] T-004 `.env.example`（LLM base_url/key/model、各数据源 key、数据库、Redis、成本预算、限流参数）
- [x] T-005 `docker-compose.yml`（web/api/postgres/redis）+ 双端 Dockerfile（已验证全部构建并启动）
- [x] T-006 OpenAPI → `openapi-typescript` 类型生成脚本
- [ ] T-007 PostgreSQL + SQLAlchemy 2 async 接入、Alembic 初始迁移（ANALYSIS/ARTICLE/SIGNAL/SIGNAL_EVIDENCE）
- [ ] T-008 Redis 接入（任务状态、文章缓存、令牌桶限流中间件）

## M1 · 分析管线后端（核心交付）

目标：`POST /analyses` 创建任务后，管线全阶段可跑通并产出确定性评分与研报（先以单 LLM provider + GDELT + 1 个商业源验证）。

- [x] T-101 LLM 网关：OpenAI + Claude 双协议封装（重试/超时/成本计量/降级）、`llm/schemas.py` 全部结构化输出模型
- [ ] T-102 `pipeline/planner.py` 实体解析 prompt + schema + 消歧候选逻辑（含阈值 0.7）
- [x] T-103 `sources/` 适配器框架（Protocol + 注册表 + 并发编排 + 降级标记）与 `gdelt.py`、`rss.py` 实现
- [x] T-104 商业源适配器 `tavily.py` / `serper.py` / `bocha.py`（有 key 即启用）
- [ ] T-105 `pipeline/extractor.py` 正文抽取（trafilatura 主 + readability 备，并发 10，缓存 24h）
- [ ] T-106 `pipeline/deduper.py` URL 规范化 + MinHash 标题聚簇（阈值 0.7）
- [ ] T-107 `pipeline/analyzer.py` 单篇结构化分析（并发 5、重试 ≤2、失败标记继续）
- [ ] T-108 `pipeline/signals.py` 跨簇信号归并 + 证据挂载
- [x] T-109 `scoring/engine.py` 六维评分 + 络合分 + 等级 + 样本保护 + Top 贡献信号（单测锁定公式）
- [ ] T-110 `pipeline/reporter.py` 流式研报生成 + 引用编号校验剔除
- [ ] T-111 管线编排器与状态机（含取消/超时/部分结果保留）、SSE 事件发射器
- [ ] T-112 路由全集：`/analyses` CRUD、`/events` SSE、`/disambiguate`、`/cancel`、`/signals`、`/articles`
- [ ] T-113 集成测试：全 mock 端到端断言状态机与产出；适配器 respx 单测；评分单测

## M2 · 前端驾驶舱

目标：搜索 → 流式驾驶舱完整可用，视觉对齐交互设计文档。

- [ ] T-201 全局骨架：深色导航 + 浅色工作台主题、风险色阶 token、字体与密度规范落地
- [ ] T-202 搜索首页（大字输入、历史、示例查询、折叠高级选项）
- [ ] T-203 `lib/sse-store.ts`：EventSource 封装 + Zustand 分片 + 断线轮询降级 + 快照恢复
- [ ] T-204 分析步骤条组件（阶段 + 实时计数 + 取消按钮）
- [ ] T-205 ECharts 薄封装与统一主题（`RiskGauge`/`Radar`/`TrendChart`/`Donut`）
- [ ] T-206 面板 A：风险总览（仪表 + 等级徽章 + 六维雷达 + 样本量，雷达点击联动筛选）
- [ ] T-207 面板 B：AI 研报流式渲染（react-markdown + 引用角标定位证据）
- [ ] T-208 面板 C：声量×情绪双轴时间线（事件旗帜标注 + hover Top 标题）
- [ ] T-209 面板 D：风险事件流（维度筛选、严重度排序、证据展开外链）
- [ ] T-210 面板 E：来源域名 Top10 + 正负面占比 + 媒体类型
- [ ] T-211 状态全覆盖：骨架屏/空态/降级提示条/错误态重试/insufficient_data 展示
- [ ] T-212 消歧候选交互（"您是指…"卡片）与重新分析入口
- [ ] T-213 vitest 单测（store 归约、数据映射）+ Playwright e2e（fixture 后端）
- [ ] T-214 响应式（≥1280 / 768-1280 / <768 三档）与可访问性走查

## M3 · 产品化（P1）

- [ ] T-301 分析历史列表 + 快照详情 + 只读分享链接（share_token）
- [ ] T-302 报告导出（Markdown 直出 + PDF 打印样式）
- [ ] T-303 上下文追问（RAG 式，答案引用校验，SSE）
- [ ] T-304 监控列表 CRUD + 定时重分析（APScheduler）+ 阈值/新高严重度预警（站内 + Webhook）
- [ ] T-305 历史分数曲线（F-404）+ 关联图谱（F-505）+ 地域地图（F-506，ECharts map）
- [ ] T-306 邮箱登录与配额绑定、管理端源/模型配置（F-702/F-703）
- [ ] T-307 垂直数据源适配器接入（监管/司法，视授权情况）
- [ ] T-308 pgvector 语义聚类（升级 T-106 聚簇质量）

## M4 · 增强（P2）

- [ ] T-401 多实体对比页（雷达叠加 + 信号差异）
- [ ] T-402 监控预警邮件通道与通知偏好
- [ ] T-403 OpenTelemetry 全链路追踪接入
- [ ] T-404 中英双语界面切换

## 当前冲刺

> 下一步执行：**M0 全部 → M1**。完成后以真实查询词（如知名上市公司）做一次端到端验收：完成率、耗时、成本、证据可点通。

## 验收对照

- M1 完成 = PRD F-101~F-403、F-305 可用（无前端或仅有调试页亦可）；
- M2 完成 = PRD 全部 P0 功能需求可交互演示；
- M3 完成 = P1 需求交付；M4 = P2。
- [x] T-109 `scoring/engine.py` 六维评分 + 络合分 + 等级 + 样本保护 + Top 贡献信号（单测锁定公式）
- [x] T-109 `scoring/engine.py` 六维评分 + 综合分 + 等级 + 样本保护 + Top 贡献信号（单测锁定公式，已通过）
