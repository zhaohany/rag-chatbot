from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np


class FaissVectorStore:
    def __init__(self, index_path: Path) -> None:
        self.index_path = index_path
        self.index: faiss.Index | None = None

    def exists(self) -> bool:
        return self.index_path.exists()

    def load(self) -> None:
        if not self.exists():
            raise FileNotFoundError(f"FAISS index not found: {self.index_path}")
        self.index = faiss.read_index(str(self.index_path))

    def create(self, dimension: int) -> None:
        self.index = faiss.IndexFlatIP(dimension)

    def add(self, vectors: list[list[float]]) -> tuple[int, int]:
        if self.index is None:
            raise RuntimeError("FAISS index is not initialized")
        arr = np.array(vectors, dtype="float32")
        start = self.index.ntotal
        self.index.add(arr)
        end = self.index.ntotal
        return int(start), int(end)

    def search(self, query_vector: list[float], k: int) -> tuple[list[float], list[int]]:
        if self.index is None:
            raise RuntimeError("FAISS index is not initialized")
        query = np.array([query_vector], dtype="float32")
        scores, ids = self.index.search(query, k)
        return scores[0].tolist(), ids[0].tolist()

    def save(self) -> None:
        if self.index is None:
            raise RuntimeError("FAISS index is not initialized")
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
