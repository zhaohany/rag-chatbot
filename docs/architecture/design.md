### A. Local Architecture（本地开发架构）

配图：`docs/architecture/5-class-system-design-local-graph.png`

目标：快速验证、低成本、可 debug（调试）。

推荐组件：

- FastAPI（API 服务）
- sentence-transformers（embedding）
- FAISS（本地向量检索）
- 本地文件（raw docs）
- metadata.json（映射与追溯）

数据流（简版）：

1. `POST /ingest`：异步触发读取 `raw_docs/*.md` -> chunking -> embedding -> 写入 FAISS + metadata
2. `POST /query`：query embedding -> Top-K retrieval -> prompt assembly -> generation

说明：

- Local 课堂版本不要求前端上传文件，文档由你提前放在本地 `raw_docs` 目录。
- `POST /ingest` 只负责 trigger，不负责承载大文本 payload。
- `doc_id`、`chunk_id`、`vector_id` 由系统在入库时自动分配。
- `chunk_size`、`chunk_overlap` 先写在代码默认配置中，保持课堂一致性。

### B. Design Decisions（工程权衡）

#### 1) Top-K 的工程权衡

- Top-K 太小：recall（召回率）下降，容易漏信息。
- Top-K 太大：噪声上升，latency（延迟）和 token 成本上升。

建议：

- 从 `Top-K=3` 起步，做 `1/3/5` 对比实验，再定默认值。

#### 2) chunk size 的工程权衡

- chunk 太小：语义被切碎，上下文不完整。
- chunk 太大：检索粒度过粗，噪声增加。

建议：

- 不先固定死一个数字模板。
- 对 Markdown 文档优先 `header-aware + 小 overlap`。
- 当文档结构不稳定时，再回退到 fixed-length（例如 `chunk_size=120`, `overlap=20`，按词）。

### C. UI Decision（轻量前端决策）

- 采用 `React + Vite + TypeScript`：兼顾 Node/JS 技术栈、简历可见度和工程轻量性。
- UI 用于本地演示和联调，优先复用现有 API，而不是在前端重复业务逻辑。
- UI 范围控制为三项能力：服务状态查看（`/health`）、触发入库（`/ingest`）、提问与结果展示（`/query`）。
