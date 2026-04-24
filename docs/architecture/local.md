# Local Architecture

## Goal

- 快速验证
- 低成本
- 易于 debug

## Components

- FastAPI API (`app/main.py`)
- API routes (`/health`, `/ingest`, `/query`)
- Service skeletons (`health_service`, `ingest_service`, `query_service`)
- System meta (`data/system/system_meta.json`)
- Lightweight UI (`ui/`, React + Vite + TypeScript)

## Current Code Layout

- `app/api/routes/`: API 路由层（health / ingest / query）
- `app/services/`: 业务流程层（health / ingest / query skeleton）
- `app/shared/`: 可复用工具层（预留）
- `app/core/config.py`: 本地默认配置
- `data/system/system_meta.json`: 系统状态元数据（ingestion_status / last_success_ingestion_time）

## Data Flow

1. `POST /ingest`
   - 当前实现为同步 ingest：文档读取 -> chunking -> embedding -> 向量/元数据写入
   - 每次调用默认执行本地全量重建，便于教学和调试

2. `POST /query`
   - 当前实现 retrieval-only：问题向量化 -> FAISS top-k 检索 -> 返回 `retrieved_chunks`
   - 暂不做答案生成，`answer` 字段保留为 `null`

## Notes

- Local 版本不做前端上传
- 当前实现保持 local MVP，优先保证流程可观察和可调试
- 系统状态先只维护两个字段：`ingestion_status`、`last_success_ingestion_time`
- lightweight UI 作为本地演示层，直接调用现有 API（`/health`、`/ingest`、`/query`）

## Design Decisions

- 本阶段优先教学节奏与可读性，不追求一次性完整功能。
- 先保留接口与分层骨架，再按课堂顺序逐步实现每个环节。
