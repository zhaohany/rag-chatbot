from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.ingest import router as ingest_router
from app.api.routes.query import router as query_router
from app.core.config import settings
from app.shared.embedding import preload_embedding_model

app = FastAPI(title=settings.app_name, version=settings.app_version)
# Configure CORS so the browser-based UI (Vite dev server) can call this API.
# - allow_origins: only allow requests from these frontend origins.
# - allow_credentials: allow cookies/auth headers when needed.
# - allow_methods/allow_headers: accept all HTTP methods and headers for development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def preload_models() -> None:
    preload_embedding_model()


app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(query_router)
