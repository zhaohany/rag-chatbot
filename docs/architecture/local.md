# Local Architecture

## Goal

- 快速验证
- 低成本
- 易于 debug

## Components

- FastAPI API (`app/main.py`)
- Embedding (`sentence-transformers/all-MiniLM-L6-v2`)
- Vector store (FAISS)
- Raw docs (`raw_docs/*.md`)
- Metadata (`data/meta/metadata.json`)

## Current Code Layout

- `app/api/routes/`: API 路由层（health / ingest / query）
- `app/services/`: 业务流程层（ingest / retrieval / generation / stores）
- `app/shared/`: 可复用工具（chunking / id 生成）
- `app/core/config.py`: 本地默认配置

## Data Flow

1. `POST /ingest`
   - 异步触发任务
   - 扫描 `raw_docs/*.md`
   - chunking（默认 `chunk_size=500`, `chunk_overlap=100`）
   - embedding
   - 写入 `data/index/faiss.index` + `data/meta/metadata.json`

2. `POST /query`
   - 对 query 做 embedding
   - FAISS top-k 检索
   - 拼接 prompt
   - 调用生成器（默认 mock，可切 HF）

## ID Rules

- `doc_id`: `doc_{n}`
- `chunk_id`: `{doc_id}_chunk_{n}`
- `vector_id`: FAISS 内部行号（add 时分配）

## Notes

- Local 版本不做前端上传
- 文档由团队提前放入 `raw_docs/`
- `/ingest` 只做 trigger，不承载大 payload
- 配置默认值在 `app/core/config.py`，可用 `.env` 覆盖

## Design Decisions

- Top-K 取值存在质量/成本权衡：太小会降低召回，太大会增加噪声与延迟；建议从 `Top-K=3` 起，做 `1/3/5` 对比实验。
- chunk size 取值存在语义完整性/检索粒度权衡：优先对 Markdown 使用 `header-aware + 小 overlap`，文档结构不稳定时回退 fixed-length（如 `chunk_size=120`, `overlap=20`）。
