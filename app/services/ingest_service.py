from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings


class IngestService:
    def __init__(self, meta_path: Path | None = None) -> None:
        self.meta_path = meta_path or settings.system_meta_path

    def trigger(self) -> None:
        return None

    def set_status(self, ingestion_status: str, last_success_ingestion_time: str | None) -> None:
        payload = {
            "ingestion_status": ingestion_status,
            "last_success_ingestion_time": last_success_ingestion_time,
        }
        self.meta_path.parent.mkdir(parents=True, exist_ok=True)
        with self.meta_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)


ingest_service = IngestService()
