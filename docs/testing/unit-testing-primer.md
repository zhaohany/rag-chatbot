# Unit Testing 入门说明

## 什么是 Unit Test

Unit Test（单元测试）用于验证一个最小功能单元是否符合预期，通常是一个函数。

在这个项目里，`app/shared/chunking.py` 的 `split_into_chunks` 很适合作为入门测试对象，因为：
- 输入和输出很清晰。
- 行为可重复、结果稳定（确定性）。
- 不依赖外部服务，定位问题更容易。

## 为什么要写 Unit Test

- 代码改动后，能尽早发现回归问题。
- 把“预期行为”写成可执行文档。
- 重构时更有信心，不容易改坏已有功能。
- 失败时能快速定位到具体逻辑。

## 本项目使用的工具

- `pytest`：Python 测试框架。
- `make test`：运行全量测试（底层命令是 `python3 -m pytest -q`）。

`pytest` 已经包含在 `requirements.txt` 中。

常用命令：

```bash
make test
python3 -m pytest tests/test_chunking.py -q
python3 -m pytest tests/test_chunking.py::test_split_into_chunks_basic_split -q
```

## Pytest 基础语法

### 1) 测试命名规范

- 文件名以 `test_` 开头。
- 测试函数名以 `test_` 开头。

示例：

```python
def test_split_into_chunks_basic_split() -> None:
    ...
```

### 2) 普通断言（值断言）

使用 `assert` 验证结果：

```python
assert chunks
assert len(chunks) == 3
assert all(len(chunk) <= 45 for chunk in chunks)
```

解释：
- `assert chunks`：断言列表非空。空列表会被判定为 `False`。
- `assert len(chunks) == 3`：断言数量精确等于 3（精确匹配）。
- `assert all(...)`：断言“每一个”元素都满足条件；只要有一个不满足就失败。

建议：
- 先写“结构断言”（是否为空、数量）再写“内容断言”（具体值、格式）。
- 失败信息要能帮助定位问题，必要时可加提示字符串：

```python
assert len(chunks) == 3, "expected exactly 3 chunks"
```

### 3) 异常断言

使用 `pytest.raises` 验证异常分支：

```python
with pytest.raises(ValueError, match="chunk_size"):
    split_into_chunks(text="hello", chunk_size=0, chunk_overlap=0)
```

解释：
- `ValueError`：期望抛出的异常类型。
- `match="chunk_size"`：期望异常信息中包含 `chunk_size`（正则匹配）。
- `with ...:` 代码块里的调用必须抛出这个异常，否则测试失败。

常见错误：
- 只写 `pytest.raises(Exception)`：过于宽泛，不利于定位。
- 不写 `match`：可能抛了错的错误原因但测试仍通过。

### 4) 常用变量含义（以 chunking 测试为例）

```python
text = "# Title\n\nBody"
chunk_size = 20
chunk_overlap = 4
chunks = split_into_chunks(text=text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
```

- `text`：输入原文（被切分对象）。
- `chunk_size`：单个 chunk 的最大长度上限（字符数）。
- `chunk_overlap`：相邻两个 chunk 的重叠字符数。
- `chunks`：函数返回值，类型是 `list[str]`。

可以优先检查的性质：
- `len(chunks)`：切分后有多少块。
- `len(chunks[i]) <= chunk_size`：每块长度是否合规。
- 相邻块是否存在重叠：`chunks[i][-chunk_overlap:] == chunks[i+1][:chunk_overlap]`（在适用场景下）。

### 5) 变量命名建议

- 用语义化命名，避免 `a`, `b`, `x`。
- 测试里变量名直接表达业务含义，例如：
  - `input_text`
  - `expected_chunks`
  - `actual_chunks`
  - `invalid_chunk_size`

示例：

```python
input_text = "hello"
invalid_chunk_size = 0

with pytest.raises(ValueError, match="chunk_size"):
    split_into_chunks(text=input_text, chunk_size=invalid_chunk_size, chunk_overlap=0)
```

## 推荐写法：AAA 模式

- Arrange：准备输入数据。
- Act：调用被测函数。
- Assert：断言结果或异常。

示例结构：

```python
def test_example() -> None:
    # Arrange
    text = "# Title\n\nBody"

    # Act
    chunks = split_into_chunks(text=text, chunk_size=20, chunk_overlap=0)

    # Assert
    assert chunks
```

## 仓库里的完整示例

`tests/test_chunking.py` 里已经有一个完整测试示例：
- `test_split_into_chunks_basic_split`

建议先参考这个风格，再补同文件中其余 `TODO` 测试。

## 如何教第一次写测试的人

建议按下面流程：

1. 先执行一次 `make test`。
2. 完整阅读一条失败信息。
3. 打开对应的测试函数。
4. 先补一个断言，不要一次写太多。
5. 只重跑这个测试函数。
6. 通过后再处理下一个测试。

核心原则：一次只关注一个行为、一次只解决一个失败。
