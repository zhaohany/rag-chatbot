from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import QueryRequest, QueryResponse
from app.services.generation_service import PromptSaveError, PromptTemplateError
from app.services.query_service import query_service

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    try:
        result = query_service.query(payload.question)
        return QueryResponse.model_validate(result)
    except (PromptTemplateError, PromptSaveError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
