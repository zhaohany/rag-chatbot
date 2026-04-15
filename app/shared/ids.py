from __future__ import annotations


def make_doc_id(doc_index: int) -> str:
    """Return doc id in format `doc_{n}`.

    Example:
      make_doc_id(3) -> "doc_3"
    """
    if doc_index <= 0:
        raise ValueError("doc_index must be greater than 0")
    return f"doc_{doc_index}"


def make_chunk_id(doc_id: str, chunk_index: int) -> str:
    """Return chunk id in format `{doc_id}_chunk_{n}`.

    Example:
      make_chunk_id("doc_3", 2) -> "doc_3_chunk_2"
    """
    if not doc_id:
        raise ValueError("doc_id must not be empty")
    if chunk_index <= 0:
        raise ValueError("chunk_index must be greater than 0")
    return f"{doc_id}_chunk_{chunk_index}"
