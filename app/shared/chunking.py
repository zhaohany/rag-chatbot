from __future__ import annotations


def split_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into overlapping chunks.

    Input:
      text: original text
      chunk_size: max characters per chunk
      chunk_overlap: overlap characters between adjacent chunks

    Output:
      list[str]

    Example:
      split_into_chunks("abcdef", chunk_size=4, chunk_overlap=1)
      -> ["abcd", "def"]
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    normalized = text.strip()
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    step = chunk_size - chunk_overlap

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks
