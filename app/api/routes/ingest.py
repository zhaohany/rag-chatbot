from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models.schemas import IngestResponse
from app.services.ingest_queue_service import (
    IngestJobAlreadyRunningError,
    ingest_queue_service,
)

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def trigger_ingest(background_tasks: BackgroundTasks) -> IngestResponse:
    try:
        payload = ingest_queue_service.submit_ingest_job(background_tasks)
        return IngestResponse.model_validate(payload)
    except IngestJobAlreadyRunningError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
