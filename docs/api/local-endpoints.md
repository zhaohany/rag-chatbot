# Local API Endpoints

Base URL: `http://127.0.0.1:8000`

说明：当前是 local MVP 阶段，`/health` 与 `/ingest` 已提供可用响应结构，`/query` 执行 retrieval + Gemini generation。
另外，`/query` 会在本地写入 prompt 产物：`data/prompts/final_prompt.txt`（不通过 API 返回）。

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

Prompt artifact behavior:

- Template file: `data/prompts/query_prompt_v3.txt`
- Final prompt output: `data/prompts/final_prompt.txt`
- 如果模板缺失或落盘失败，接口会返回可读的错误信息，便于本地排查。

## POST /ingest

用途：提交一个本地 ingest job。API 会立刻返回 `queued`，实际 embedding / FAISS / SQLite 写入由 FastAPI `BackgroundTasks` 在 response 返回后继续执行。

说明：这是教学版 queue-based ingestion。它不是定时任务，也不是 Redis/Celery 分布式队列。一次 `/ingest` 请求对应一个 job，这个 job 会处理所有 `raw_docs/*.md` 并全量重建本地索引。

Request body: none

Response example:

```json
{
  "status": "queued",
  "total_docs": 0,
  "total_chunks": 0,
  "message": "Ingestion job submitted",
  "job_id": "ingest_20260628_123456_000000"
}
```

If another ingest job is already `queued` or `running`, the API returns `409 Conflict`.

Use `GET /health` to observe app-level ingestion status:

```text
queued -> running -> idle
queued -> running -> failed
```

## POST /query

Request example:

```json
{
  "question": "How to reset password?"
}
```

Query test prompts: `docs/api/sample-test-queries-it-support.md`

Response example:

```json
{
  "answer": "Complete MFA enrollment first, then submit a VPN access request in the Service Portal.",
  "used_top_k": 1,
  "retrieved_chunks": [
    {
      "vector_id": 10,
      "chunk_id": "doc_4_chunk_2",
      "doc_id": "doc_4",
      "score": 0.42,
      "text": null,
      "source_path": null
    }
  ]
}
```
