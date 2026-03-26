from __future__ import annotations

from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.metadata_store import MetadataStore
from app.services.vector_store import FaissVectorStore


class RetrievalService:
    def __init__(self) -> None:
        self.metadata_store = MetadataStore(settings.metadata_path)
        self.vector_store = FaissVectorStore(settings.faiss_index_path)

    def retrieve(self, question: str, top_k: int) -> list[dict]:
        if not self.vector_store.exists() or not self.metadata_store.exists():
            raise FileNotFoundError("Index or metadata not found. Please run /ingest first.")

        self.vector_store.load()
        vector = embedding_service.encode([question])[0]
        scores, ids = self.vector_store.search(vector, top_k)
        mapping = self.metadata_store.by_vector_id()

        results: list[dict] = []
        for score, vector_id in zip(scores, ids):
            if vector_id < 0:
                continue
            item = mapping.get(vector_id)
            if not item:
                continue
            results.append(
                {
                    "vector_id": vector_id,
                    "chunk_id": item["chunk_id"],
                    "doc_id": item["doc_id"],
                    "score": float(score),
                    "text": item["text"],
                    "source_path": item["source_path"],
                }
            )
        return results


retrieval_service = RetrievalService()
