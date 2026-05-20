from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RAG_",
        extra="ignore",
    )

    app_name: str = "rag-local-api"
    app_version: str = "0.1.0"
    top_k: int = 1
    raw_docs_dir: Path = Path("raw_docs")
    index_path: Path = Path("data/index/faiss.index")
    metadata_path: Path = Path("data/meta/metadata.json")
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 16
    chunk_size: int = 500
    chunk_overlap: int = 80
    system_meta_path: Path = Path("data/system/system_meta.json")
    prompt_template_path: Path = Path("data/prompts/query_prompt_v3.txt")
    final_prompt_path: Path = Path("data/prompts/final_prompt.txt")
    gemini_api_key: str | None = None
    gemini_model: str = "models/gemini-2.0-flash-lite"
    gemini_timeout_seconds: int = 30
    llm_max_output_tokens: int = 256


settings = Settings()
