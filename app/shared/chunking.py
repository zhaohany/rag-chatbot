from __future__ import annotations

def split_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    '''
    Split Markdown text recursively into overlapping chunks.

    Input:
      text: original markdown text
      chunk_size: max characters per chunk
      chunk_overlap: overlap characters between adjacent chunks

    Output:
      list[str]

    Example:
    '''
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    # ensure that the first-line heading (`# Title`) can correctly detected.
    normalized = "\n" + text.strip()
    if not normalized.strip():
        return []

    # \n\n:paragraph
    separators = ["\n# ", "\n## ", "\n### ", "\n\n", "\n"]

    def _split_into_three(text_to_split: str) -> list[str]:
        '''
        Forcefully splits text exceeding the chunking_size into 3 parts with overlap.
        '''
        length = len(text_to_split)
        # total_length = 3 * chunk_len - 2 * chunk_overlap -> chunk_len = (length + 2 * chunk_overlap) // 3
        chunk_len = (length + 2 * chunk_overlap) // 3

        p1_end = chunk_len
        p2_start = max(0, p1_end - chunk_overlap) # Avoid negative value
        p2_end = min(length, p2_start + chunk_len)
        p3_start = max(0, p2_end - chunk_overlap)

        return [
            text_to_split[0:p1_end].strip(),
            text_to_split[p2_start:p2_end].strip(),
            text_to_split[p3_start:].strip()
        ]

    def _get_splits(text_to_split: str, current_seps: list[str]) -> list[str]:
        '''
        Recursively split the text until each chunk is smaller than `chunk_size` or trigger _split_into_three.
        '''
        if len(text_to_split) <= chunk_size:
            return [text_to_split]

        sep = ""
        next_seps = []
        for i, s in enumerate(current_seps):
            if s in text_to_split:
                sep = s
                next_seps = current_seps[i+1:] 
                break

        if not sep:
            return _split_into_three(text_to_split)

        raw_parts = text_to_split.split(sep)

        parts = [raw_parts[0]] if raw_parts[0] else []
        for p in raw_parts[1:]:
            parts.append(sep + p)

        final_parts = []
        for part in parts:
            if len(part) > chunk_size:
                final_parts.extend(_get_splits(part, next_seps))
            else:
                final_parts.append(part)

        return final_parts

    splits = _get_splits(normalized, separators)

    chunks: list[str] = []
    current_chunk = ""

    for split in splits:
        if not current_chunk:
            current_chunk = split
        elif len(current_chunk) + len(split) <= chunk_size:
            current_chunk += split
        else:
            chunks.append(current_chunk.strip())
            
            if chunk_overlap > 0:
                overlap_text = current_chunk[-chunk_overlap:]
                if len(overlap_text) + len(split) > chunk_size:
                    safe_overlap_len = max(0, chunk_size - len(split))
                    overlap_text = overlap_text[-safe_overlap_len:] if safe_overlap_len > 0 else ""
                current_chunk = overlap_text + split
            else:
                current_chunk = split

    if current_chunk:
        chunks.append(current_chunk.strip())

    return [c for c in chunks if c]