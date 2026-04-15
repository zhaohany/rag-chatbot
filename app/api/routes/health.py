from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import HealthResponse
from app.services.health_service import health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    ingestion_meta = health_service.get_ingestion_meta()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        ingestion_status=ingestion_meta["ingestion_status"] or "idle",
        last_success_ingestion_time=ingestion_meta["last_success_ingestion_time"],
        total_docs=int(ingestion_meta["total_docs"] or 0),
    )
