from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import BackgroundTasks

from app.core.config import settings
from app.services.database_service import DatabaseService, create_database_service
from app.services.ingest_service import IngestService, ingest_service


class IngestJobAlreadyRunningError(RuntimeError):
    pass


@dataclass(frozen=True)
class IngestJob:
    job_id: str


def build_queued_ingest_response(job_id: str) -> dict[str, Any]:
    """Homework function: build response after ingestion job is queued.

    中文说明:
      /ingest API 不再同步执行 embedding。
      它只把任务交给 IngestQueueService，然后立刻返回。
      这个函数负责组装 API response。

    English keywords:
      queued response, async API, job id

    Input:
      job_id: ingestion job id, for example "ingest_20260628_123456"

    Output:
      dict with keys:
        - status: "queued"
        - job_id: same job_id from input
        - total_docs: 0
        - total_chunks: 0
        - message: "Ingestion job submitted"

    Example:
      build_queued_ingest_response("ingest_20260628_123456")
      -> {
           "status": "queued",
           "job_id": "ingest_20260628_123456",
           "total_docs": 0,
           "total_chunks": 0,
           "message": "Ingestion job submitted",
         }

    Student TODO:
      Return the dictionary shown in the example.
    """
    return {
        "status": "queued",
        "job_id": job_id,
        "total_docs": 0,
        "total_chunks": 0,
        "message": "Ingestion job submitted",
    }


class IngestQueueService:
    """Small teaching queue wrapper for ingestion jobs.

    This class uses FastAPI BackgroundTasks as the lightweight local worker.
    One POST /ingest request creates one job that rebuilds the full local index.
    """

    def __init__(
        self,
        ingest: IngestService | None = None,
        database: DatabaseService | None = None,
    ) -> None:
        self.ingest_service = ingest or ingest_service
        self.database = database or create_database_service(settings.metadata_db_path)

    def submit_ingest_job(self, background_tasks: BackgroundTasks) -> dict[str, Any]:
        """Create one queued job and ask FastAPI to run it after response."""
        current_status = str(
            self.database.get_ingestion_meta()["ingestion_status"] or "idle"
        )
        if current_status in {"queued", "running"}:
            raise IngestJobAlreadyRunningError(
                f"Ingestion is already {current_status}. Please wait."
            )

        job = self.create_job()
        self.database.create_ingest_job(job.job_id, "Ingestion job submitted")
        self.ingest_service.set_status(
            "queued",
            self.ingest_service.get_last_success_ingestion_time(),
            self.ingest_service.get_total_docs(),
        )
        background_tasks.add_task(self.process_ingest_job, job.job_id)
        return build_queued_ingest_response(job.job_id)

    def create_job(self) -> IngestJob:
        now = datetime.now(timezone.utc)
        job_id = now.strftime("ingest_%Y%m%d_%H%M%S_%f")
        return IngestJob(job_id=job_id)

    def process_ingest_job(self, job_id: str) -> None:
        """Run one queued ingestion job.

        中文说明:
          这个函数由 FastAPI BackgroundTasks 在 API response 返回后执行。
          它会真正执行 ingestion，包括:
          read markdown -> chunking -> embeddings -> FAISS index -> SQLite metadata。

        English keywords:
          background task, ingestion worker, embedding processing, reuse sync service

        Input:
          job_id: ingestion job id

        Output:
          None. Results are persisted to FAISS index and SQLite metadata.

        Student TODO:
          In the marked line below, call the existing sync ingest pipeline.
          Hint: self.ingest_service.run_sync_ingest()
        """
        self.database.mark_ingest_job_running(job_id)

        try:
            # TODO(homework): call existing sync ingest pipeline.
            result = self.ingest_service.run_sync_ingest()
            message = (
                "Ingestion completed: "
                f"docs={result['total_docs']}, chunks={result['total_chunks']}"
            )
            self.database.mark_ingest_job_succeeded(job_id, message)
        except RuntimeError as exc:
            self.database.mark_ingest_job_failed(job_id, str(exc))
        except Exception as exc:
            self.ingest_service.set_status(
                "failed",
                self.ingest_service.get_last_success_ingestion_time(),
                self.ingest_service.get_total_docs(),
            )
            self.database.mark_ingest_job_failed(job_id, f"Unexpected error: {exc}")
            raise


ingest_queue_service = IngestQueueService()
