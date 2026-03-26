from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IngestState:
    is_running: bool = False
    last_status: str = "idle"
    last_message: str = "No ingest run yet"
    last_success_ingestion_time: str | None = None


ingest_state = IngestState()
