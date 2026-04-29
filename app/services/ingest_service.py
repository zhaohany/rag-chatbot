from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.shared.chunking import split_into_chunks
from app.shared.embedding import get_embedding_model, preload_embedding_model
from app.shared.ids import make_chunk_id, make_doc_id


def discover_markdown_files(raw_docs_dir: Path) -> list[Path]:
    """Return sorted markdown file paths.

    Input:
      raw_docs_dir: Path, e.g. Path("raw_docs")

    Output:
      list[Path], sorted .md paths

    Example:
      discover_markdown_files(Path("raw_docs"))
      -> [Path("raw_docs/employee_handbook.md"), Path("raw_docs/product_faq.md")]
    """
    if not raw_docs_dir.exists():
        return []
    return sorted(path for path in raw_docs_dir.glob("*.md") if path.is_file())


def read_markdown(path: Path) -> str:
    """Read one markdown file in UTF-8 and return full text.

    Input:
      path: markdown file path

    Output:
      str text

    Example:
      read_markdown(Path("raw_docs/product_faq.md")) -> "# Product FAQ\n..."
    """
    return path.read_text(encoding="utf-8")


def embed_chunks(
    texts: list[str],
    batch_size: int,
    model: SentenceTransformer,
) -> np.ndarray:
    """Generate embeddings for chunk texts.

    Input:
      texts: list of chunk text
      batch_size: embedding batch size
      model: preloaded sentence-transformers model

    Output:
      2D float32 array-like, shape=(num_chunks, dim)

    Example:
      embed_chunks(["hello", "world"], 16, model)
      -> ndarray with shape (2, 384)
    """
    vectors = model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
    return np.asarray(vectors, dtype=np.float32)


def build_faiss_index(vectors: np.ndarray) -> faiss.IndexFlatL2:
    """Build and return a FAISS index from vectors.

    Input:
      vectors: 2D float32 vectors

    Output:
      FAISS index object

    Example:
      build_faiss_index(vectors) -> <faiss.IndexFlatL2>
    """
    if vectors.ndim != 2:
        raise ValueError("vectors must be 2-dimensional")
    if vectors.shape[0] == 0:
        raise ValueError("vectors must not be empty")

    faiss.omp_set_num_threads(1)
    vectors = np.ascontiguousarray(vectors, dtype=np.float32)
    dimension = int(vectors.shape[1])
    index = faiss.IndexFlatL2(dimension)  # type: ignore[call-arg]
    index.add(vectors)  # type: ignore[call-arg]
    return index


def write_faiss_index(index: faiss.Index, index_path: Path) -> None:
    """Persist FAISS index to disk.

    Input:
      index: FAISS index
      index_path: e.g. Path("data/index/faiss.index")
    """
    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))


def write_metadata(records: list[dict[str, Any]], metadata_path: Path) -> None:
    """Persist chunk metadata records to JSON.

    Input:
      records: list of chunk metadata dicts
      metadata_path: e.g. Path("data/meta/metadata.json")

    Example record:
      {
        "doc_id": "doc_1",
        "chunk_id": "doc_1_chunk_1",
        "source": "employee_handbook.md",
        "chunk_index": 1,
        "chunk_text": "..."
      }
    """
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


class IngestService:
    def __init__(
        self,
        meta_path: Path | None = None,
        raw_docs_dir: Path | None = None,
        index_path: Path | None = None,
        metadata_path: Path | None = None,
    ) -> None:
        self.meta_path = meta_path or settings.system_meta_path
        self.raw_docs_dir = raw_docs_dir or settings.raw_docs_dir
        self.index_path = index_path or settings.index_path
        self.metadata_path = metadata_path or settings.metadata_path

    def preload_embedding_model(self) -> None:
        preload_embedding_model()

    def get_embedding_model(self) -> SentenceTransformer:
        return get_embedding_model()

    def set_status(
        self,
        ingestion_status: str,
        last_success_ingestion_time: str | None,
        total_docs: int,
    ) -> None:
        payload = {
            "ingestion_status": ingestion_status,
            "last_success_ingestion_time": last_success_ingestion_time,
            "total_docs": total_docs,
        }
        self.meta_path.parent.mkdir(parents=True, exist_ok=True)
        with self.meta_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def get_last_success_ingestion_time(self) -> str | None:
        if not self.meta_path.exists():
            return None
        try:
            with self.meta_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(data, dict):
            return None
        timestamp = data.get("last_success_ingestion_time")
        if timestamp is None or isinstance(timestamp, str):
            return timestamp
        return None

    def get_total_docs(self) -> int:
        if not self.meta_path.exists():
            return 0
        try:
            with self.meta_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return 0
        if not isinstance(data, dict):
            return 0
        total_docs = data.get("total_docs")
        if isinstance(total_docs, int) and total_docs >= 0:
            return total_docs
        return 0

    def run_sync_ingest(self) -> dict[str, Any]:
        """Run sync ingest orchestration and return summary payload.

        Output example:
          {
            "status": "success",
            "total_docs": 3,
            "total_chunks": 18,
            "message": "Ingestion completed"
          }
        """
        last_success_time = self.get_last_success_ingestion_time()
        previous_total_docs = self.get_total_docs()
        self.set_status("running", last_success_time, previous_total_docs)

        try:
            markdown_files = discover_markdown_files(self.raw_docs_dir)

            records: list[dict[str, Any]] = []
            chunk_texts: list[str] = []

            for file_index, file_path in enumerate(markdown_files, start=1):
                doc_id = make_doc_id(file_index)
                text = read_markdown(file_path)
                chunks = split_into_chunks(
                    text,
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap,
                )

                for chunk_index, chunk_text in enumerate(chunks, start=1):
                    chunk_id = make_chunk_id(doc_id, chunk_index)
                    chunk_texts.append(chunk_text)
                    records.append(
                        {
                            "doc_id": doc_id,
                            "chunk_id": chunk_id,
                            "source": file_path.name,
                            "chunk_index": chunk_index,
                            "chunk_text": chunk_text,
                        }
                    )

            if chunk_texts:
                model = self.get_embedding_model()
                vectors = embed_chunks(
                    chunk_texts,
                    batch_size=settings.embedding_batch_size,
                    model=model,
                )
                index = build_faiss_index(vectors)
                write_faiss_index(index, self.index_path)
            elif self.index_path.exists():
                self.index_path.unlink()

            write_metadata(records, self.metadata_path)

            finished_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            total_docs = len(markdown_files)
            self.set_status("idle", finished_at, total_docs)
            return {
                "status": "success",
                "total_docs": total_docs,
                "total_chunks": len(records),
                "message": "Ingestion completed",
            }
        except (OSError, ValueError, RuntimeError) as exc:
            self.set_status("failed", last_success_time, previous_total_docs)
            raise RuntimeError(f"Ingestion failed: {exc}") from exc


ingest_service = IngestService()
