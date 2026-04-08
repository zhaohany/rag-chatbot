### A. Local Architecture（本地开发架构）

配图：`docs/architecture/5-class-system-design-local-graph.png`

目标：快速验证、低成本、可 debug（调试）。

推荐组件：

- FastAPI（API 服务）
- 三个接口骨架（health / ingest / query）
- 分层目录（api / services / models / shared / core）
- 系统状态元数据文件（data/system/system_meta.json）

数据流（简版）：

1. `POST /ingest`：先保留入口骨架，后续逐步实现完整入库流程
2. `POST /query`：先保留入口骨架，后续逐步实现检索与生成流程

说明：

- Local 课堂版本当前以 skeleton 为主，先讲清分层与接口边界。
- 系统元数据当前只保留两个字段：`ingestion_status`、`last_success_ingestion_time`。
- 具体算法与存储实现在后续里程碑逐步加入。

### B. Design Decisions（工程权衡）

- 本阶段优先“结构先行”：接口和目录先稳定，再补内部实现。
- 复杂参数（Top-K、chunk size 等）放到后续课堂单独展开。

### C. UI Decision（轻量前端决策）

- 采用 `React + Vite + TypeScript`：兼顾 Node/JS 技术栈、简历可见度和工程轻量性。
- UI 用于本地演示和联调，优先复用现有 API，而不是在前端重复业务逻辑。
- UI 范围控制为三项能力：服务状态查看（`/health`）、触发入库（`/ingest`）、提问与结果展示（`/query`）。
