# RAG Chatbot (Local)

本项目当前只聚焦本地开发版本：快速验证、低成本、可调试。

核心组件：

- FastAPI（API 服务）
- 三个教学接口骨架：`/health`、`/ingest`、`/query`
- 分层目录：`api / services / models / shared / core`
- 系统状态元数据：`data/system/system_meta.json`

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
│   ├── index/                   # 后续阶段预留
│   ├── meta/                    # 后续阶段预留
│   └── system/                  # 系统状态元数据（当前使用）
├── docs/
│   ├── architecture/
│   ├── setup/
│   ├── api/
├── ui/                          # React + Vite + TypeScript demo UI
├── requirements.txt
└── README.md
```

## 当前状态

- 当前是 local MVP：`/health` 与 `/ingest` 可用，`/query` 已支持 retrieval（仅返回 top-k 检索结果，不做生成）。
- 每次调用 `POST /query` 会生成 prompt 产物并写入 `data/prompts/final_prompt.txt`，用于下节课接入 generation。
- `POST /ingest` 为同步流程：读取 `raw_docs/*.md`，执行 chunking/embedding，并写入本地 FAISS 与 metadata。
- 目录结构保持分层（`api/`、`services/`、`models/`、`shared/`、`core/`），便于后续演进 async 版本。
- 目标仍是课堂分阶段实现，优先保证链路清晰与可调试。

## 接口

- `GET /health`：健康检查（返回服务状态与 ingest 元数据）
- `POST /ingest`：同步入库流程入口（本地重建索引）
- `POST /query`：查询流程入口（retrieval-only，返回 `retrieved_chunks`；同时本地落盘 final prompt）

接口示例见 `docs/api/local-endpoints.md`。

## 环境配置与启动

请按你的系统看详细文档：

- macOS: `docs/setup/mac.md`
- Windows: `docs/setup/windows.md`

通用最短启动：

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip3 install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```

可选环境变量模板：`.env.example`（按需复制为 `.env`）

Swagger: `http://127.0.0.1:8000/docs`

启动 UI（可选）：

```bash
cd ui
cp .env.example .env  # 可选
npm install
npm run dev
```

UI 默认地址：`http://127.0.0.1:5173`

## 团队协作建议

- 架构说明统一放 `docs/architecture/local.md`
- 初始设计文档放 `docs/architecture/design.md`
- 架构图放 `docs/architecture/5-class-system-design-local-graph.png`
- 里程碑统一放 `docs/roadmap.md`

如果后续上云，再从当前 local 结构演进即可，不影响现在开发节奏。
