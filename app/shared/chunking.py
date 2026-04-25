from __future__ import annotations

import re


def _contains_header_level(text: str, level: int) -> bool:
    pattern = re.compile(rf"(?m)^{'#' * level}(?!#)\s+.+$")
    return pattern.search(text) is not None


def _split_by_header_level(text: str, level: int) -> list[str]:
    pattern = re.compile(rf"(?m)^{'#' * level}(?!#)\s+.+$")
    matches = list(pattern.finditer(text))
    if not matches:
        return [text]

    sections: list[str] = []
    first_start = matches[0].start()
    if first_start > 0:
        intro = text[:first_start].strip()
        if intro:
            sections.append(intro)

    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if section:
            sections.append(section)

    return sections


def split_markdown_into_chunks(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """Split markdown by H2, then H3, then length.

    Input:
      text: markdown text
      chunk_size: max characters per chunk
      chunk_overlap: overlap characters between adjacent length-based chunks

    Output:
      list[str]
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

    if not _contains_header_level(normalized, 2):
        return split_into_chunks(normalized, chunk_size, chunk_overlap)

    chunks: list[str] = []
    h2_sections = _split_by_header_level(normalized, 2)

    for h2_section in h2_sections:
        if len(h2_section) <= chunk_size:
            chunks.append(h2_section)
            continue

        if not _contains_header_level(h2_section, 3):
            chunks.extend(split_into_chunks(h2_section, chunk_size, chunk_overlap))
            continue

        h3_sections = _split_by_header_level(h2_section, 3)
        for h3_section in h3_sections:
            if len(h3_section) <= chunk_size:
                chunks.append(h3_section)
            else:
                chunks.extend(split_into_chunks(h3_section, chunk_size, chunk_overlap))

    return chunks


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
