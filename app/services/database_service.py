from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_path TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_deleted INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL,
    vector_id INTEGER NOT NULL UNIQUE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    source_path TEXT NOT NULL,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
);

CREATE INDEX IF NOT EXISTS idx_documents_status
ON documents (status);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_id
ON chunks (doc_id);

CREATE INDEX IF NOT EXISTS idx_chunks_vector_id
ON chunks (vector_id);

CREATE TABLE IF NOT EXISTS ingest_jobs (
    job_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ingest_jobs_status
ON ingest_jobs (status);
"""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DatabaseService:
    """SQLite-backed metadata store for the local RAG app.

    SQL fill-in areas:
    - The app code already calls this class instead of reading/writing JSON metadata.
    - Marked SQL strings can be completed without changing the route/service flow.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def set_system_state(self, key: str, value: str | None) -> None:
        self.initialize()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO system_state (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def get_system_state(self, key: str) -> str | None:
        self.initialize()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT value
                FROM system_state
                WHERE key = ?
                """,
                (key,),
            ).fetchone()
        if row is None:
            return None
        value = row["value"]
        return value if isinstance(value, str) else None

    def set_ingestion_status(
        self,
        ingestion_status: str,
        last_success_ingestion_time: str | None,
        total_docs: int,
    ) -> None:
        self.set_system_state("ingestion_status", ingestion_status)
        self.set_system_state("last_success_ingestion_time", last_success_ingestion_time)
        self.set_system_state("total_docs", str(total_docs))

    def get_ingestion_meta(self) -> dict[str, str | None | int]:
        total_docs_raw = self.get_system_state("total_docs")
        try:
            total_docs = int(total_docs_raw or "0")
        except ValueError:
            total_docs = 0

        return {
            "ingestion_status": self.get_system_state("ingestion_status") or "idle",
            "last_success_ingestion_time": self.get_system_state(
                "last_success_ingestion_time"
            ),
            "total_docs": max(total_docs, 0),
        }

    def create_ingest_job(self, job_id: str, message: str) -> None:
        """Create one queued ingestion job record.

        中文说明：
          在 /ingest API 接收到请求后，先写入一条 job record。
          这条记录表示任务已经进入 queued 状态，后台任务稍后会继续处理。

        English keywords:
          SQL INSERT, job record, queued status, timestamp

        Input:
          job_id: ingestion job id, e.g. "ingest_20260628_123456_000000"
          message: readable job message, e.g. "Ingestion job submitted"

        Output:
          None. The job row is written to SQLite table `ingest_jobs`.

        TODO(sql):
          Fill in the SQL statement below. It should insert one row into
          `ingest_jobs` with:
          - job_id from input
          - status = "queued"
          - message from input
          - created_at = current UTC timestamp
          - started_at = NULL
          - finished_at = NULL
        """
        self.initialize()
        with self.connect() as conn:
            sql = """
                INSERT INTO ingest_jobs (
                    -- TODO(sql): fill in the column list.
                    -- Expected columns:
                    -- job_id, status, message, created_at, started_at, finished_at
                )
                VALUES (?, 'queued', ?, ?, NULL, NULL)
                """
            conn.execute(
                sql,
                (job_id, message, utc_now_iso()),
            )

    def mark_ingest_job_running(self, job_id: str) -> None:
        """Mark an ingestion job as running."""
        self.initialize()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE ingest_jobs
                SET status = 'running',
                    message = 'Ingestion job is running',
                    started_at = ?
                WHERE job_id = ?
                """,
                (utc_now_iso(), job_id),
            )

    def mark_ingest_job_succeeded(self, job_id: str, message: str) -> None:
        """Mark an ingestion job as succeeded."""
        self.initialize()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE ingest_jobs
                SET status = 'succeeded',
                    message = ?,
                    finished_at = ?
                WHERE job_id = ?
                """,
                (message, utc_now_iso(), job_id),
            )

    def mark_ingest_job_failed(self, job_id: str, message: str) -> None:
        """Mark an ingestion job as failed."""
        self.initialize()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE ingest_jobs
                SET status = 'failed',
                    message = ?,
                    finished_at = ?
                WHERE job_id = ?
                """,
                (message, utc_now_iso(), job_id),
            )

    def replace_ingested_metadata(self, records: list[dict[str, Any]]) -> None:
        """Replace document/chunk metadata after a successful local ingest."""
        self.initialize()
        with self.connect() as conn:
            conn.execute("DELETE FROM chunks")
            conn.execute("DELETE FROM documents")

            seen_docs: set[str] = set()
            for record in records:
                doc_id = str(record["doc_id"])
                source_path = str(record["source"])
                if doc_id not in seen_docs:
                    conn.execute(
                        """
                        INSERT INTO documents (
                            doc_id,
                            title,
                            source_path,
                            status,
                            created_at,
                            is_deleted
                        )
                        VALUES (?, ?, ?, 'indexed', CURRENT_TIMESTAMP, 0)
                        """,
                        (doc_id, source_path, source_path),
                    )
                    seen_docs.add(doc_id)

                conn.execute(
                    """
                    INSERT INTO chunks (
                        chunk_id,
                        doc_id,
                        vector_id,
                        chunk_index,
                        chunk_text,
                        source_path
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["chunk_id"],
                        doc_id,
                        record["vector_id"],
                        record["chunk_index"],
                        record["chunk_text"],
                        source_path,
                    ),
                )

    def load_chunk_metadata(self) -> list[dict[str, Any]]:
        """Load chunk rows ordered by FAISS vector id."""
        self.initialize()
        with self.connect() as conn:
            # TODO(homework): 补完整这个函数要用的 SQL query。
            # 目标：
            # 1. 从 `chunks` 表读取 chunk metadata。
            # 2. 用 `doc_id` JOIN 到 `documents` 表。
            # 3. 用 `documents.is_deleted = 0` 排除 soft-deleted documents。
            # 4. 按 `chunks.vector_id ASC` 排序，这样 FAISS vector id
            #    才能映射回正确的 chunk row。
            #
            # 必须返回这些字段：
            # - chunks.vector_id
            # - chunks.chunk_id
            # - chunks.doc_id
            # - chunks.chunk_text
            # - chunks.source_path
            # - documents.title AS document_title
            # - documents.status AS document_status
            # - documents.is_deleted
            #
            # 请替换下面 placeholder SQL。
            rows = conn.execute(
                """
                SELECT
                    chunks.vector_id,
                    chunks.chunk_id,
                    chunks.doc_id,
                    chunks.chunk_text,
                    chunks.source_path,
                    documents.title AS document_title,
                    documents.status AS document_status,
                    documents.is_deleted
                FROM chunks
                JOIN documents ON chunks.doc_id = documents.doc_id
                WHERE documents.is_deleted = 0
                ORDER BY chunks.vector_id ASC
                """
            ).fetchall()

        return [dict(row) for row in rows]


def create_database_service(db_path: Path) -> DatabaseService:
    database = DatabaseService(db_path)
    database.initialize()
    return database
