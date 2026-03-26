# RAG Chatbot (Local)

本项目当前只聚焦本地开发版本：快速验证、低成本、可调试。

核心组件：

- FastAPI（API 服务）
- sentence-transformers（embedding）
- FAISS（本地向量检索）
- `raw_docs/*.md`（本地原始文档）
- `data/meta/metadata.json`（映射与追溯）

## 目录结构

```text
.
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── models/
│   ├── shared/                   # chunking / id 生成
│   └── services/
├── raw_docs/                    # 课堂文档输入（你手动放 .md）
├── data/
│   ├── index/                   # faiss.index 输出
│   └── meta/                    # metadata.json 输出
├── docs/
│   ├── architecture/
│   ├── setup/
│   ├── api/
│   └── collaboration/
├── requirements.txt
└── README.md
```

## 当前状态

- 已实现本地 FastAPI 三个接口：`/health`、`/ingest`、`/query`
- 已实现本地入库流程：读取 markdown -> chunking -> embedding -> FAISS + metadata
- 已实现本地检索与回答：Top-K 检索 + prompt 组装 + mock/HF 生成适配
- 已实现本地持久化：`data/index/faiss.index` 与 `data/meta/metadata.json`
- 当前以本地开发为唯一目标，暂不引入云端目录或部署逻辑

## 数据流

1. `POST /ingest`：异步触发读取 `raw_docs/*.md` -> chunking -> embedding -> 写入 FAISS + metadata
2. `POST /query`：query embedding -> top-k retrieval -> prompt assembly -> generation

说明：

- `POST /ingest` 只负责 trigger，不承载大文本 payload
- `doc_id`、`chunk_id`、`vector_id` 在入库时自动分配
- `chunk_size`、`chunk_overlap` 使用代码默认配置（便于课堂一致）

工程权衡（Design Decisions）：

- Top-K：太小会降低召回，太大会提高噪声、延迟和 token 成本；建议从 `Top-K=3` 起，做 `1/3/5` 对比实验。
- chunk size：太小会打碎语义，太大会让检索粒度变粗；Markdown 优先 `header-aware + 小 overlap`，结构不稳定时回退 fixed-length（如 `chunk_size=120`, `overlap=20`）。

## 接口

- `GET /health`：服务状态与索引存在性
- `POST /ingest`：触发异步入库
- `POST /query`：检索并生成回答

接口示例见 `docs/api/local-endpoints.md`。

## 环境配置与启动

请按你的系统看详细文档：

- macOS: `docs/setup/mac.md`
- Windows: `docs/setup/windows.md`

通用最短启动：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

可选环境变量模板：`.env.example`（按需复制为 `.env`）

Swagger: `http://127.0.0.1:8000/docs`

## 团队协作建议

- 架构说明统一放 `docs/architecture/local.md`
- 初始设计文档放 `docs/architecture/design.md`
- 架构图放 `docs/architecture/5-class-system-design-local-graph.png`
- 协作分工放 `docs/collaboration/roles.md`
- 里程碑统一放 `docs/roadmap.md`

如果后续上云，再从当前 local 结构演进即可，不影响现在开发节奏。
