# Local API Endpoints

Base URL: `http://127.0.0.1:8000`

说明：当前是教学 skeleton 阶段，先实现 health 的清晰状态响应，其他接口仍为占位结构。

## GET /health

Response example:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "ingestion_status": "idle",
  "last_success_ingestion_time": null
}
```

## POST /ingest

用途：预留入库流程入口（后续课堂逐步实现）

Request body: none

Response example:

```json
{}
```

## POST /query

Request example:

```json
{}
```

Response example:

```json
{}
```
