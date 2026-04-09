from __future__ import annotations

from pydantic import BaseModel


class IngestResponse(BaseModel):
    pass


class QueryRequest(BaseModel):
    pass


class RetrievedChunk(BaseModel):
    pass


class QueryResponse(BaseModel):
    pass


class HealthResponse(BaseModel):
    status: str
    version: str
    ingestion_status: str
    last_success_ingestion_time: str | None
