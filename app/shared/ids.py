from __future__ import annotations


def make_doc_id(doc_number: int) -> str:
    return f"doc_{doc_number}"


def make_chunk_id(doc_id: str, chunk_number: int) -> str:
    return f"{doc_id}_chunk_{chunk_number}"
