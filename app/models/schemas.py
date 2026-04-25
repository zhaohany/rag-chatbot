from __future__ import annotations

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    status: str
    total_docs: int
    total_chunks: int
    message: str | None = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class RetrievedChunk(BaseModel):
    vector_id: int
    chunk_id: str | None = None
    doc_id: str | None = None
    score: float
    text: str | None = None
    source_path: str | None = None


class QueryResponse(BaseModel):
    answer: str | None = None
    used_top_k: int
    retrieved_chunks: list[RetrievedChunk]


class HealthResponse(BaseModel):
    status: str
    version: str
    ingestion_status: str
    last_success_ingestion_time: str | None
    total_docs: int
