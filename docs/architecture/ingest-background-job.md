# Ingest Background Job Implementation Notes

## Goal

`/ingest` no longer waits for embedding / FAISS / SQLite writes before returning.

The API now submits one ingestion job and returns immediately:

```text
POST /ingest
-> create job id
-> write SQLite job record
-> return queued response
-> FastAPI BackgroundTasks continues the ingestion pipeline
```

FastAPI `BackgroundTasks` is request-triggered background work. It is not a scheduled cron job and it is not a distributed queue such as Redis/Celery.

## Flow

One `/ingest` request creates one job.

That job processes all markdown files:

```text
raw_docs/*.md
```

The ingestion pipeline remains a full local rebuild:

```text
all markdown docs -> chunks -> embeddings -> one FAISS index -> SQLite metadata
```

## Code Path

```text
app/api/routes/ingest.py
-> IngestQueueService.submit_ingest_job(...)
-> DatabaseService.create_ingest_job(...)
-> BackgroundTasks.add_task(...)
-> IngestQueueService.process_ingest_job(...)
-> IngestService.run_sync_ingest()
```

`IngestQueueService` owns job submission and job state.

`IngestService` owns the actual ingestion pipeline:

```text
read markdown -> chunking -> embeddings -> FAISS index -> SQLite metadata
```

## Remaining Implementation Points

### 1. Insert The Initial Job Record

Complete the SQL statement in:

```text
app/services/database_service.py
DatabaseService.create_ingest_job(...)
```

Complete the `INSERT` column list so the method writes one row into `ingest_jobs`:

```text
job_id
status = queued
message
created_at
started_at = NULL
finished_at = NULL
```

Keywords: `SQL INSERT`, `job record`, `queued status`, `timestamp`.

Expected SQL shape:

```sql
INSERT INTO ingest_jobs (
    job_id,
    status,
    message,
    created_at,
    started_at,
    finished_at
)
VALUES (?, 'queued', ?, ?, NULL, NULL)
```

The Python parameters are already wired:

```python
(job_id, message, utc_now_iso())
```

No queue logic needs to be written in this method. It only inserts the initial job record.

### 2. Call The Existing Ingest Pipeline

Complete the TODO in:

```text
app/services/ingest_queue_service.py
IngestQueueService.process_ingest_job(...)
```

The method already marks the job as `running` before the TODO and marks the job as `succeeded` / `failed` after it.

Fill in the existing sync ingest call and success message:

```python
result = self.ingest_service.run_sync_ingest()
message = (
    "Ingestion completed: "
    f"docs={result['total_docs']}, chunks={result['total_chunks']}"
)
```

Keywords: `call existing sync ingest`, `reuse pipeline`, `success message`.

## What `process_ingest_job` Does

`process_ingest_job(job_id)` is the function FastAPI runs after the `/ingest` response has been sent.

It does not implement embedding itself. It wraps the existing ingestion pipeline with job-status updates:

```text
mark job running
-> call IngestService.run_sync_ingest()
-> mark job succeeded or failed
```

The real ingestion work still happens here:

```python
self.ingest_service.run_sync_ingest()
```

That existing service call performs markdown reading, chunking, embeddings, FAISS index writing, and SQLite metadata replacement.

## Local Checks

Compile Python:

```bash
python3 -m compileall app
```

Start API:

```bash
python3 -m uvicorn app.main:app --reload
```

Submit ingest job:

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

Expected queued response:

```json
{
  "status": "queued",
  "job_id": "ingest_...",
  "total_docs": 0,
  "total_chunks": 0,
  "message": "Ingestion job submitted"
}
```

Check health:

```bash
curl -X GET http://127.0.0.1:8000/health
```

Status flow:

```text
queued -> running -> idle
queued -> running -> failed
```

## Non-Goals

Do not split this into one message per document.

Do not store embedding vectors in SQLite.

Do not introduce Redis / Celery / RabbitMQ for this local flow.

Do not rewrite `IngestService.run_sync_ingest()`.
