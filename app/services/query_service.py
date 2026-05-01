from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.core.config import settings
from app.services.generation_service import generation_service
from app.shared.embedding import get_embedding_model, preload_embedding_model


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
    model = get_embedding_model()
    vector = model.encode([question], convert_to_numpy=True)
    return np.ascontiguousarray(vector, dtype=np.float32)


def retrieve_topk(
    index: faiss.Index,
    query_vector: np.ndarray,
    top_k: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Search FAISS and return top-k distances and vector ids.

    Output format:
      - distances: shape (1, k), float scores from L2 distance
      - indices: shape (1, k), int vector ids in FAISS

    Example:
      distances = [[0.22, 0.41, 0.97]]
      indices = [[5, 2, 9]]

      Meaning:
        rank 1 -> vector_id 5, score 0.22
        rank 2 -> vector_id 2, score 0.41
        rank 3 -> vector_id 9, score 0.97
    """
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    faiss.omp_set_num_threads(1)

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
    """Build retrieval rows from FAISS output.

    We align by position:
      indices[0][i] is the vector id from FAISS,
      metadata[vector_id] is the metadata for that vector.

    Students can fill real `text` and `source_path` later.
    """
    chunks: list[dict[str, Any]] = []

    if distances.size == 0 or indices.size == 0:
        return chunks

    scores_row = distances[0]
    vector_ids_row = indices[0]

    for rank, raw_vector_id in enumerate(vector_ids_row):
        vector_id = int(raw_vector_id)
        if vector_id < 0 or vector_id >= len(metadata):
            continue

        score = float(scores_row[rank])
        record: dict[str, Any] = metadata[vector_id]

        chunks.append(
            {
                "vector_id": vector_id,
                "chunk_id": record.get("chunk_id"),
                "doc_id": record.get("doc_id"),
                "score": score,
                # TODO(): fill real content from metadata/storage.
                "text": None,
                "source_path": None,
            }
        )

    return chunks


class QueryService:
    def preload_embedding_model(self) -> None:
        preload_embedding_model()

    def query(self, question: str) -> dict[str, Any]:
        index = load_index(settings.index_path)
        query_vector = embed_question(question)
        distances, indices = retrieve_topk(index, query_vector, settings.top_k)
        metadata = load_metadata(settings.metadata_path)
        retrieved_chunks = build_retrieved_chunks(distances, indices, metadata)
        final_prompt = generation_service.build_prompt(question, retrieved_chunks)
        generation_service.save_prompt(final_prompt)

        return {
            "answer": None,
            "used_top_k": len(retrieved_chunks),
            "retrieved_chunks": retrieved_chunks,
        }


query_service = QueryService()
