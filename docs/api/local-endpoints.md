# Local API Endpoints

Base URL: `http://127.0.0.1:8000`

## GET /health

`last_success_ingestion_time` 为最近一次成功入库时间（UTC ISO-8601），未成功入库前为 `null`。

Response example:

```json
{
  "status": "ok",
  "app": "rag-local-api",
  "version": "0.1.0",
  "index_exists": false,
  "metadata_exists": false,
  "last_success_ingestion_time": null
}
```

## POST /ingest

用途：触发异步入库任务（不会上传大文本）

Request body: none

Response example:

```json
{
  "status": "accepted",
  "message": "Ingest job triggered"
}
```

若已有入库任务在执行中：

```json
{
  "status": "running",
  "message": "Ingest is already running"
}
```

## POST /query

Request example:

```json
{
  "question": "What is this document about?",
  "top_k": 3
}
```

Response example:

```json
{
  "answer": "(Mock answer) ...",
  "used_top_k": 3,
  "retrieved_chunks": [
    {
      "vector_id": 0,
      "chunk_id": "doc_1_chunk_1",
      "doc_id": "doc_1",
      "score": 0.73,
      "text": "...",
      "source_path": "raw_docs/example.md"
    }
  ]
}
```

常见错误（未先 ingest）：

```json
{
  "detail": "Index or metadata not found. Please run /ingest first."
}
```
