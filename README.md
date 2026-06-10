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

- 当前是 local MVP：`/health` 与 `/ingest` 可用，`/query` 已支持 retrieval + Gemini generation。
- 每次调用 `POST /query` 会生成 prompt 产物并写入 `data/prompts/final_prompt.txt`，并返回最终 `answer`。
- `POST /ingest` 为同步流程：读取 `raw_docs/*.md`，执行 chunking/embedding，并写入本地 FAISS 与 metadata。
- 目录结构保持分层（`api/`、`services/`、`models/`、`shared/`、`core/`），便于后续演进 async 版本。
- 目标仍是课堂分阶段实现，优先保证链路清晰与可调试。

## 接口

- `GET /health`：健康检查（返回服务状态与 ingest 元数据）
- `POST /ingest`：同步入库流程入口（本地重建索引）
- `POST /query`：查询流程入口（retrieval + generation，返回 `answer` 与 `retrieved_chunks`；同时本地落盘 final prompt）

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

环境变量快速准备：

```bash
cp .env.example .env
```

如需本地启用 Gemini，请在 `.env` 中替换：

```bash
RAG_GEMINI_API_KEY=your_gemini_api_key_here
```

可选：列出当前账号可用的 Gemini models：

```bash
python3 scripts/list_gemini_models.py
```

Swagger: `http://127.0.0.1:8000/docs`

### Docker 启动后端

构建并启动 FastAPI backend：

```bash
docker compose up --build backend
```

访问：

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

如需启用 Gemini，可在宿主机环境变量或 `.env` 中配置：

```bash
RAG_GEMINI_API_KEY=your_gemini_api_key_here
```

Compose 会挂载本地目录：

- `./data:/app/data`：保留 FAISS index、metadata、prompt 输出
- `./raw_docs:/app/raw_docs:ro`：作为只读文档输入
- `backend_hf_cache:/app/.cache/huggingface`：缓存 sentence-transformers 模型，避免每次重下

不使用 Compose 时，也可以直接用 Docker CLI：

```bash
docker build -t rag-chatbot-backend:local .
docker run --rm \
  -p 8000:8000 \
  -e RAG_GEMINI_API_KEY="$RAG_GEMINI_API_KEY" \
  -e RAG_PROMPT_TEMPLATE_PATH="data/prompts/query_prompt_v3.txt" \
  -e RAG_FINAL_PROMPT_PATH="data/prompts/final_prompt.txt" \
  -v "$PWD/data:/app/data" \
  -v "$PWD/raw_docs:/app/raw_docs:ro" \
  -v rag_chatbot_hf_cache:/app/.cache/huggingface \
  rag-chatbot-backend:local
```

其中：

- `-p 8000:8000`：把宿主机 8000 端口映射到容器内 8000 端口
- `-v "$PWD/data:/app/data"`：挂载本地 `data` 目录
- `-v "$PWD/raw_docs:/app/raw_docs:ro"`：只读挂载本地 `raw_docs` 目录
- `-v rag_chatbot_hf_cache:/app/.cache/huggingface`：使用 Docker named volume 缓存模型

启动 UI（可选）：

```bash
cd ui
cp .env.example .env  # 可选
npm install
npm run dev
```

UI 默认地址：`http://127.0.0.1:5173`

### Docker 启动前端作业版

前端 Docker 作业文件见：`ui/Dockerfile`，详细说明见：`docs/setup/frontend-docker-assignment.md`。

学生需要先填写 `ui/Dockerfile` 里的 3 个 TODO：

- `COPY TODO_STUDENT_PACKAGE_FILES ./`
- `RUN TODO_STUDENT_INSTALL_COMMAND`
- `CMD TODO_STUDENT_START_COMMAND`

不使用 Compose 时，在 `ui/` 目录直接构建并运行：

```bash
cd ui
docker build -t rag-chatbot-ui:student .
docker run --rm \
  -p 5173:5173 \
  -e VITE_API_BASE_URL="http://127.0.0.1:8000" \
  rag-chatbot-ui:student
```

使用 Compose 时，在仓库根目录运行：

```bash
docker compose up --build frontend
```

因为 `compose.yaml` 里配置了 `frontend` 依赖 `backend`，所以上面这条命令会同时启动后端。

也可以显式写出两个服务：

```bash
docker compose up --build backend frontend
```

访问前端：`http://127.0.0.1:5173`

前端会通过 `VITE_API_BASE_URL` 调用后端，默认是：`http://127.0.0.1:8000`。

## 团队协作建议

- 架构说明统一放 `docs/architecture/local.md`
- 初始设计文档放 `docs/architecture/design.md`
- 架构图放 `docs/architecture/5-class-system-design-local-graph.png`
- 里程碑统一放 `docs/roadmap.md`

如果后续上云，再从当前 local 结构演进即可，不影响现在开发节奏。
