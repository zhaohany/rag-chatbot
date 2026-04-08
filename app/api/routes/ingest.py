from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import IngestResponse

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def trigger_ingest() -> IngestResponse:
    return IngestResponse()
