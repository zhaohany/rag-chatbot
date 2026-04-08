from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RAG_")

    app_name: str = "rag-local-api"
    app_version: str = "0.1.0"
    top_k: int = 3
    system_meta_path: Path = Path("data/system/system_meta.json")


settings = Settings()
