from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.schemas import QueryRequest, QueryResponse, RetrievedChunk
from app.services.generation_service import generation_service
from app.services.retrieval_service import retrieval_service

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    top_k = payload.top_k or settings.top_k
    try:
        contexts = retrieval_service.retrieve(payload.question, top_k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}") from exc

    answer = generation_service.generate(payload.question, contexts)
    return QueryResponse(
        answer=answer,
        used_top_k=top_k,
        retrieved_chunks=[RetrievedChunk(**item) for item in contexts],
    )
