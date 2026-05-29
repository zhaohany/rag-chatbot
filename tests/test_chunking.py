from __future__ import annotations

import pytest

from app.shared.chunking import split_into_chunks


def test_split_into_chunks_basic_split() -> None:
    text = """# Title

This is the first paragraph.

This is the second paragraph with more content.
"""

    chunks = split_into_chunks(text=text, chunk_size=45, chunk_overlap=0)

    # Example test (completed): reference style for other TODO tests.
    assert chunks, "expected non-empty chunks for normal markdown input"
    assert all(len(chunk) <= 45 for chunk in chunks), "chunk exceeded chunk_size"
    assert chunks[0].startswith("# Title"), "expected heading to stay in first chunk"


def test_split_into_chunks_empty_text_returns_empty_list() -> None:
    text = "   \n\n  "

    chunks = split_into_chunks(text=text, chunk_size=50, chunk_overlap=0)

    # TODO(要测什么):
    # - 当输入只有空格和换行时，函数应返回空列表 []。
    # - 请补一个“精确相等”断言，直接比较 `chunks` 与 `[]`。
    raise NotImplementedError("TODO: add assertion for empty input")


def test_split_into_chunks_raises_when_chunk_size_not_positive() -> None:
    text = "hello world"

    # TODO(要测什么):
    # - 当 chunk_size <= 0 时，函数必须抛出 ValueError。
    # - 错误信息应包含 "chunk_size"，表明是该参数不合法。
    # - 用 `with pytest.raises(ValueError, match="chunk_size"):` 包住函数调用。
    raise NotImplementedError("TODO: add raises assertion for chunk_size")


def test_split_into_chunks_raises_when_overlap_invalid() -> None:
    text = "hello world"

    # TODO(要测什么):
    # - 当 chunk_overlap >= chunk_size 时，函数必须抛出 ValueError。
    # - 错误信息应体现 overlap 与 chunk_size 的约束关系。
    # - 只验证这一类参数错误，不要混入其他断言。
    raise NotImplementedError("TODO: add raises assertion for overlap")


def test_split_into_chunks_with_overlap_has_shared_boundary_text() -> None:
    text = "AAAAABBBBBCCCCCDDDDDEEEEE"
    overlap = 4

    chunks = split_into_chunks(text=text, chunk_size=10, chunk_overlap=overlap)

    # TODO(要测什么):
    # - 先验证确实发生了切分（至少 2 个 chunk）。
    # - 再验证 overlap 逻辑生效：
    #   至少存在一对相邻 chunk，它们边界上的 overlap 字符串一致。
    #
    # 可用提示（不给答案）:
    # - 相邻下标：`i` 和 `i + 1`
    # - 尾部切片：`chunks[i][-overlap:]`
    # - 头部切片：`chunks[i + 1][:overlap]`
    # - 可考虑用 `any(...)` 聚合判断
    raise NotImplementedError("TODO: add assertions for overlap behavior")
