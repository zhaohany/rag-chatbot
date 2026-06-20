from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.services.database_service import DatabaseService, create_database_service


class HealthService:
    def __init__(
        self,
        meta_path: Path | None = None,
        database: DatabaseService | None = None,
    ) -> None:
        self.meta_path = meta_path or settings.system_meta_path
        self.database = database or create_database_service(settings.metadata_db_path)

    def get_ingestion_meta(self) -> dict[str, str | None | int]:
        return self.database.get_ingestion_meta()


health_service = HealthService()
