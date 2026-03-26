from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.models.schemas import HealthResponse
from app.state import ingest_state

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        index_exists=settings.faiss_index_path.exists(),
        metadata_exists=settings.metadata_path.exists(),
        last_success_ingestion_time=ingest_state.last_success_ingestion_time,
    )
