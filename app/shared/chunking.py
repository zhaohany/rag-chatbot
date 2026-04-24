from __future__ import annotations

def split_markdown_into_chunks(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """Split markdown by H2/H3, then fallback to length-based chunking."""
    _validate_chunk_config(chunk_size, chunk_overlap)

    normalized = text.strip()
    if not normalized:
        return []

    chunks: list[str] = []
    sections_h2 = _split_by_h2(normalized)

    for section in sections_h2:
        if len(section) <= chunk_size:
            chunks.append(section)
            continue

        sections_h3 = _split_by_h3(section)
        if len(sections_h3) > 1:
            for sub_section in sections_h3:
                if len(sub_section) <= chunk_size:
                    chunks.append(sub_section)
                else:
                    chunks.extend(
                        _split_by_length(sub_section, chunk_size, chunk_overlap)
                    )
            continue

        chunks.extend(_split_by_length(section, chunk_size, chunk_overlap))

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
    _validate_chunk_config(chunk_size, chunk_overlap)

    normalized = text.strip()
    if not normalized:
        return []

    chunks: list[str] = []
    step = chunk_size - chunk_overlap
    start = 0

    while start < len(normalized):
        chunk = normalized[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def _validate_chunk_config(chunk_size: int, chunk_overlap: int) -> None:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")


def _split_by_h2(text: str) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []

    lines = normalized.splitlines()
    sections: list[str] = []
    current: list[str] = []

    for line in lines:
        stripped = line.lstrip()
        is_h2 = stripped.startswith("## ")
        if is_h2 and current:
            section = "\n".join(current).strip()
            if section:
                sections.append(section)
            current = [line]
            continue
        current.append(line)

    if current:
        section = "\n".join(current).strip()
        if section:
            sections.append(section)

    return sections if sections else [normalized]


def _split_by_h3(text: str) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []

    lines = normalized.splitlines()
    sections: list[str] = []
    current: list[str] = []

    for line in lines:
        stripped = line.lstrip()
        is_h3 = stripped.startswith("### ")
        if is_h3 and current:
            section = "\n".join(current).strip()
            if section:
                sections.append(section)
            current = [line]
            continue
        current.append(line)

    if current:
        section = "\n".join(current).strip()
        if section:
            sections.append(section)

    return sections if sections else [normalized]


def _split_by_length(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    return split_into_chunks(normalized, chunk_size, chunk_overlap)
