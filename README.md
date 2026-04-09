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

- 当前是教学用 skeleton：保留 `FastAPI + 3 个接口` 的最小骨架。
- `GET /health` 可用；`POST /ingest`、`POST /query` 目前返回 TODO 占位响应。
- 目录结构已预留（`services/`、`shared/`、`data/`、`raw_docs/`），但暂不包含实际 RAG 实现。
- 目标是和学生按阶段逐步实现，而不是一次性给出完整方案。

## 接口

- `GET /health`：健康检查（当前 skeleton 返回空结构）
- `POST /ingest`：入库流程入口（当前 skeleton）
- `POST /query`：查询流程入口（当前 skeleton）

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
