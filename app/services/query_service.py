from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.core.config import settings
from app.services.ingest_service import ingest_service


def load_index(index_path: Path) -> faiss.Index:
    if not index_path.exists():
        raise RuntimeError("Index not found. Please run /ingest first.")
    return faiss.read_index(str(index_path))


def load_metadata(metadata_path: Path) -> list[dict[str, Any]]:
    if not metadata_path.exists():
        return []

    try:
        with metadata_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to read metadata: {exc}") from exc

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def embed_question(question: str) -> np.ndarray:
    model = ingest_service.get_embedding_model()
    vector = model.encode([question], convert_to_numpy=True)
    return np.ascontiguousarray(vector, dtype=np.float32)


def retrieve_topk(
    index: faiss.Index,
    query_vector: np.ndarray,
    top_k: int,
) -> tuple[np.ndarray, np.ndarray]:
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    total_vectors = int(index.ntotal)
    if total_vectors == 0:
        empty = np.empty((1, 0), dtype=np.float32)
        return empty, empty.astype(np.int64)

    k = min(top_k, total_vectors)
    distances, indices = index.search(query_vector, k)  # type: ignore[call-arg]
    return distances, indices


def build_retrieved_chunks(
    distances: np.ndarray,
    indices: np.ndarray,
    metadata: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []

    for score, vector_id in zip(distances[0], indices[0]):
        if int(vector_id) < 0:
            continue

        record = metadata[int(vector_id)] if int(vector_id) < len(metadata) else {}
        chunks.append(
            {
                "vector_id": int(vector_id),
                "chunk_id": record.get("chunk_id") if isinstance(record, dict) else None,
                "doc_id": record.get("doc_id") if isinstance(record, dict) else None,
                "score": float(score),
                # Reserved for students to fill real content later.
                "text": None,
                "source_path": None,
            }
        )

    return chunks


class QueryService:
    def query(self, question: str) -> dict[str, Any]:
        index = load_index(settings.index_path)
        query_vector = embed_question(question)
        distances, indices = retrieve_topk(index, query_vector, settings.top_k)
        metadata = load_metadata(settings.metadata_path)
        retrieved_chunks = build_retrieved_chunks(distances, indices, metadata)

        return {
            "answer": None,
            "used_top_k": len(retrieved_chunks),
            "retrieved_chunks": retrieved_chunks,
        }


query_service = QueryService()
