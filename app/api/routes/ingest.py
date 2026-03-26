from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks

from app.models.schemas import IngestResponse
from app.services.ingest_service import ingest_service
from app.state import ingest_state

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def trigger_ingest(background_tasks: BackgroundTasks) -> IngestResponse:
    if ingest_state.is_running:
        return IngestResponse(status="running", message="Ingest is already running")

    ingest_state.is_running = True
    ingest_state.last_status = "running"
    ingest_state.last_message = "Ingest job started"
    background_tasks.add_task(ingest_service.run_ingest)
    return IngestResponse(status="accepted", message="Ingest job triggered")
