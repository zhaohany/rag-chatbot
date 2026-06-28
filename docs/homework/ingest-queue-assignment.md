# Ingest Queue 作业：用 BackgroundTasks 提交后台入库任务

## 目标

本项目原来的 `/ingest` 是同步执行：API 会一直等到 embedding / FAISS / SQLite 全部完成才返回。

现在改成教学版 queue-based ingestion：

```text
POST /ingest
-> 创建 job
-> 写入 SQLite job record
-> 返回 queued response
-> FastAPI BackgroundTasks 后台继续执行 embedding
```

这不是 Redis/Celery 生产队列，也不是 scheduled cron。它是 request-triggered background work。

## 已经写好的部分

以下部分已经帮你写好：

1. `IngestQueueService` class。
2. `submit_ingest_job(...)`。
3. SQLite `ingest_jobs` table。
4. job status 更新：`queued` / `running` / `succeeded` / `failed`。
5. duplicate job guard：已有 job `queued` 或 `running` 时返回 `409 Conflict`。
6. 原来的 embedding pipeline：`ingest_service.run_sync_ingest()`。

## 你要理解的流程

一次 `/ingest` 请求只创建一个 job。

这个 job 会处理所有：

```text
raw_docs/*.md
```

不要改成一个文档一个 message。当前项目是全量重建 index：

```text
all markdown docs -> chunks -> embeddings -> one FAISS index -> SQLite metadata
```

## 作业 1：queued response

打开：

```text
app/services/ingest_queue_service.py
```

找到：

```python
build_queued_ingest_response(job_id: str) -> dict[str, Any]
```

这个函数负责返回 `/ingest` 提交成功后的 payload。

Expected output example:

```python
{
    "status": "queued",
    "job_id": job_id,
    "total_docs": 0,
    "total_chunks": 0,
    "message": "Ingestion job submitted",
}
```

关键词：`queued response`, `async API`, `job id`

## 作业 2：worker 调用现有 ingestion pipeline

还是在：

```text
app/services/ingest_queue_service.py
```

找到：

```python
process_ingest_job(...)
```

你只需要理解这一行：

```python
result = self.ingest_service.run_sync_ingest()
```

它会真正执行：

```text
read markdown -> chunking -> embeddings -> FAISS index -> SQLite metadata
```

关键词：`background task`, `worker`, `reuse existing sync service`, `embedding pipeline`

## 本地验证

检查 Python 编译：

```bash
python3 -m compileall app
```

启动 API：

```bash
python3 -m uvicorn app.main:app --reload
```

提交 ingest job：

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

你应该先看到：

```json
{
  "status": "queued",
  "job_id": "ingest_...",
  "total_docs": 0,
  "total_chunks": 0,
  "message": "Ingestion job submitted"
}
```

然后查看 health：

```bash
curl -X GET http://127.0.0.1:8000/health
```

状态会经历：

```text
queued -> running -> idle
```

如果失败，会变成：

```text
queued -> running -> failed
```

## 不要改的东西

不要把 embedding vector 存进 SQLite。

不要把 job 拆成一个文档一个 message。

不要引入 Redis / Celery / RabbitMQ。

不要重写 `ingest_service.run_sync_ingest()`。
