# Chunking Tests

## Goal

Complete the remaining test logic in `tests/test_chunking.py`.

## Setup

From project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

## Run Tests

Run all tests:

```bash
make test
```

Run only chunking tests:

```bash
python3 -m pytest tests/test_chunking.py -q
```

Run one test function:

```bash
python3 -m pytest tests/test_chunking.py::test_split_into_chunks_basic_split -q
```

## Remaining Work in `tests/test_chunking.py`

Replace each `NotImplementedError` with real assertions.

## 这组测试到底要测什么（中文说明）

目标是验证 `split_into_chunks` 的 5 类核心行为：

1. **正常输入能正确切分**
   - 有输出（不是空列表）
   - 每个 chunk 都不超过 `chunk_size`
   - 标题内容没有丢失（例如首块仍包含 `# Title`）

2. **空白输入的边界行为**
   - 输入只有空格/换行时，返回 `[]`

3. **非法参数：`chunk_size`**
   - 当 `chunk_size <= 0` 时抛出 `ValueError`
   - 错误信息应能看出是 `chunk_size` 问题

4. **非法参数：`chunk_overlap`**
   - 当 `chunk_overlap >= chunk_size` 时抛出 `ValueError`
   - 错误信息应能看出是 overlap 约束问题

5. **重叠逻辑是否生效**
   - 至少产生多个 chunk
   - 至少一对相邻 chunk 在边界上存在预期重叠（尾部/头部片段一致）

### 1) `test_split_into_chunks_basic_split`
- Assert output is not empty.
- Assert every chunk length is `<= chunk_size`.
- Assert heading content is preserved.

### 2) `test_split_into_chunks_empty_text_returns_empty_list`
- Assert blank input returns an empty list.

### 3) `test_split_into_chunks_raises_when_chunk_size_not_positive`
- Use `pytest.raises(ValueError)` for `chunk_size <= 0`.
- Check message includes `chunk_size`.

### 4) `test_split_into_chunks_raises_when_overlap_invalid`
- Use `pytest.raises(ValueError)` for `chunk_overlap >= chunk_size`.

### 5) `test_split_into_chunks_with_overlap_has_shared_boundary_text`
- Assert multiple chunks exist.
- Assert at least one adjacent pair shares expected overlap text.

## Done Criteria

- All five tests in `tests/test_chunking.py` pass.
- Assertions are specific and readable.
- Exception tests verify both exception type and key message text.
