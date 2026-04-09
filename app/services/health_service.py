from __future__ import annotations

import json
from pathlib import Path

from app.core.config import settings


class HealthService:
    def __init__(self, meta_path: Path | None = None) -> None:
        self.meta_path = meta_path or settings.system_meta_path

    def get_ingestion_meta(self) -> dict[str, str | None]:
        if self.meta_path.exists():
            try:
                with self.meta_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return {
                        "ingestion_status": str(data.get("ingestion_status", "idle")),
                        "last_success_ingestion_time": data.get("last_success_ingestion_time"),
                    }
            except (OSError, json.JSONDecodeError):
                pass

        return {
            "ingestion_status": "idle",
            "last_success_ingestion_time": None,
        }


health_service = HealthService()
