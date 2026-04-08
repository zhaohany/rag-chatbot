from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import QueryRequest, QueryResponse

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(_payload: QueryRequest) -> QueryResponse:
    return QueryResponse()
