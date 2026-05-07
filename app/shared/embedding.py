from __future__ import annotations

import os

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from sentence_transformers import SentenceTransformer
import torch

from app.core.config import settings

_embedding_model: SentenceTransformer | None = None


def preload_embedding_model() -> None:
    global _embedding_model
    if _embedding_model is None:
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        _embedding_model = SentenceTransformer(settings.embedding_model_name)


def get_embedding_model() -> SentenceTransformer:
    if _embedding_model is None:
        raise RuntimeError("Embedding model is not preloaded")
    return _embedding_model
