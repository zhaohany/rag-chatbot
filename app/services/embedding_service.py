from __future__ import annotations

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self._model = SentenceTransformer(settings.embedding_model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()


embedding_service = EmbeddingService()
