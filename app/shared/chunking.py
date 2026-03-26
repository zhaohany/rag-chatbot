from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    start_char: int
    end_char: int


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    cleaned = text.strip()
    if not cleaned:
        return []

    chunks: list[Chunk] = []
    step = chunk_size - chunk_overlap
    cursor = 0
    length = len(cleaned)

    while cursor < length:
        end = min(cursor + chunk_size, length)
        segment = cleaned[cursor:end].strip()
        if segment:
            chunks.append(Chunk(text=segment, start_char=cursor, end_char=end))
        if end == length:
            break
        cursor += step

    return chunks
