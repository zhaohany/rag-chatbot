# Local API Endpoints

Base URL: `http://127.0.0.1:8000`

说明：当前是 local MVP 阶段，`/health` 与 `/ingest` 已提供可用响应结构，`/query` 仍是占位结构。

## GET /health

Response example:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "ingestion_status": "idle",
  "last_success_ingestion_time": null,
  "total_docs": 0
}
```

## POST /ingest

用途：同步触发本地 ingest（读取 `raw_docs/*.md`，并写入本地索引与元数据）

Request body: none

Response example:

```json
{
  "status": "success",
  "total_docs": 3,
  "total_chunks": 18,
  "message": "Ingestion completed"
}
```

## POST /query

Request example:

```json
{}
```

Query test prompts: `docs/api/sample-test-queries-it-support.md`

Response example:

```json
{}
```
