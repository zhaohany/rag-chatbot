from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.shared.chunking import split_into_chunks, split_markdown_into_chunks


def test_split_markdown_by_h2() -> None:
    text = "# Intro\n\n## Section A\nAlpha\n\n## Section B\nBeta"

    chunks = split_markdown_into_chunks(text, chunk_size=100, chunk_overlap=10)

    assert chunks == ["# Intro", "## Section A\nAlpha", "## Section B\nBeta"]


def test_split_markdown_h2_then_h3() -> None:
    text = (
        "## Big Section\n"
        "Some intro text here.\n\n"
        "### Part 1\n"
        "A short part.\n\n"
        "### Part 2\n"
        "Another short part."
    )

    chunks = split_markdown_into_chunks(text, chunk_size=40, chunk_overlap=5)

    assert chunks == [
        "## Big Section\nSome intro text here.",
        "### Part 1\nA short part.",
        "### Part 2\nAnother short part.",
    ]


def test_split_markdown_h3_then_length() -> None:
    text = (
        "## Big Section\n"
        "### Very Long Part\n"
        + "x" * 120
    )

    chunks = split_markdown_into_chunks(text, chunk_size=50, chunk_overlap=10)

    assert len(chunks) > 1
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert chunks[0] == "## Big Section"
    assert any(chunk.startswith("### Very Long Part") for chunk in chunks)


def test_split_markdown_without_h2_falls_back_to_length() -> None:
    text = "plain text " * 30

    chunks_markdown = split_markdown_into_chunks(text, chunk_size=60, chunk_overlap=10)
    chunks_plain = split_into_chunks(text, chunk_size=60, chunk_overlap=10)

    assert chunks_markdown == chunks_plain


def test_split_markdown_input_validation() -> None:
    text = "## A\ncontent"

    try:
        split_markdown_into_chunks(text, chunk_size=0, chunk_overlap=0)
        assert False, "expected ValueError for chunk_size"
    except ValueError as exc:
        assert "chunk_size" in str(exc)

    try:
        split_markdown_into_chunks(text, chunk_size=10, chunk_overlap=10)
        assert False, "expected ValueError for chunk_overlap"
    except ValueError as exc:
        assert "chunk_overlap" in str(exc)
