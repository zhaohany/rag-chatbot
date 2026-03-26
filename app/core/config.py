from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RAG_")

    app_name: str = "rag-local-api"
    app_version: str = "0.1.0"

    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 3

    raw_docs_dir: Path = Path("raw_docs")
    faiss_index_path: Path = Path("data/index/faiss.index")
    metadata_path: Path = Path("data/meta/metadata.json")

    llm_provider: str = "mock"
    huggingface_model: str = "HuggingFaceH4/zephyr-7b-beta"
    huggingface_token: str | None = None


settings = Settings()
