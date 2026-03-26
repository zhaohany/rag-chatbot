from __future__ import annotations

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    status: str
    message: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)


class RetrievedChunk(BaseModel):
    vector_id: int
    chunk_id: str
    doc_id: str
    score: float
    text: str
    source_path: str


class QueryResponse(BaseModel):
    answer: str
    used_top_k: int
    retrieved_chunks: list[RetrievedChunk]


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    index_exists: bool
    metadata_exists: bool
    last_success_ingestion_time: str | None
