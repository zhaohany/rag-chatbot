# Ingest API Sync V1 Implementation Plan

## 目标

- 先实现一个可本地验证、可教学演示的同步入库接口：`POST /ingest`。
- 本阶段不做 async、队列、并发 worker，优先把最小 RAG ingest 主链路跑通。
- 保持代码少、结构清晰：route 薄层，流程集中在 service，核心算法函数先定义接口。

## 范围（V1）

- 输入：`raw_docs/*.md`
- 处理：读取 markdown -> chunking -> embedding
- 输出：
  - 向量索引：`data/index/faiss.index`
  - 元数据：`data/meta/metadata.json`
  - 系统状态：`data/system/system_meta.json`
- 执行方式：同步执行（请求期间阻塞）。

不在本阶段做：

- 增量更新索引
- 异步任务与任务状态查询接口
- 文档上传接口
- 重排序、多模型切换、复杂 chunk 策略

## API 契约（建议）

- 路径：`POST /ingest`
- 请求体：无
- 返回体（`IngestResponse`）：
  - `status: str`，如 `success` / `failed`
  - `total_docs: int`
  - `total_chunks: int`
  - `message: str | None`

示例（成功）：

```json
{
  "status": "success",
  "total_docs": 3,
  "total_chunks": 18,
  "message": "Ingestion completed"
}
```

## 代码落点

- `app/api/routes/ingest.py`
  - 路由只负责调用 service 和异常映射，不写业务细节。
- `app/services/ingest_service.py`
  - 同步 orchestration 主流程。
  - 状态切换（running/idle/failed）。
- `app/models/schemas.py`
  - 定义 `IngestResponse`。
- `app/core/config.py`
  - 增加 ingest 相关配置项（路径、chunk 参数、embedding 参数）。
- `app/shared/chunking.py`
  - 放 chunk 函数定义（先接口后实现）。
- `app/shared/ids.py`
  - 放 `doc_id/chunk_id` 生成函数定义。
- `docs/api/local-endpoints.md`
  - 更新 `/ingest` 示例。

## 主流程（同步）

1. route 接收 `POST /ingest`。
2. service 记录 `started_at`，将状态写为 `running`。
3. 扫描 `raw_docs/*.md` 并排序。
4. 逐文件读取文本，生成 `doc_id`。
5. 调 chunk 函数生成 chunk 列表。
6. 为每个 chunk 生成 `chunk_id`，收集 metadata record。
7. 对所有 chunk 文本执行 embedding。
8. 用 embedding 构建并写入 FAISS 索引。
9. 写 `metadata.json`。
10. 更新 `system_meta.json`：`idle + last_success_ingestion_time + total_docs`。
11. 返回 `IngestResponse`。

失败路径：

- 任一步骤异常：状态写为 `failed`，route 返回 `HTTPException(500)`。

## 核心函数定义（先声明，不实现细节）

以下函数先写签名和 docstring，后续再填实现。

```python
from __future__ import annotations

from pathlib import Path
from typing import Any


def discover_markdown_files(raw_docs_dir: Path) -> list[Path]:
    """Return sorted markdown file paths.

    Input:
      raw_docs_dir: Path, e.g. Path("raw_docs")

    Output:
      list[Path], sorted .md paths

    Example:
      discover_markdown_files(Path("raw_docs"))
      -> [Path("raw_docs/password_reset_and_account_unlock.md"), Path("raw_docs/common_troubleshooting_playbook.md")]
    """


def read_markdown(path: Path) -> str:
    """Read one markdown file in UTF-8 and return full text.

    Input:
      path: markdown file path

    Output:
      str text

    Example:
      read_markdown(Path("raw_docs/password_reset_and_account_unlock.md")) -> "# Password Reset and Account Unlock SOP\n..."
    """


def split_into_chunks(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into chunks.

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


def make_doc_id(doc_index: int) -> str:
    """Return doc id in format `doc_{n}`.

    Example:
      make_doc_id(3) -> "doc_3"
    """


def make_chunk_id(doc_id: str, chunk_index: int) -> str:
    """Return chunk id in format `{doc_id}_chunk_{n}`.

    Example:
      make_chunk_id("doc_3", 2) -> "doc_3_chunk_2"
    """


def embed_chunks(texts: list[str], model_name: str, batch_size: int) -> Any:
    """Generate embeddings for chunk texts.

    Input:
      texts: list of chunk text
      model_name: sentence-transformers model name
      batch_size: embedding batch size

    Output:
      2D float32 array-like, shape=(num_chunks, dim)

    Example:
      embed_chunks(["hello", "world"], "sentence-transformers/all-MiniLM-L6-v2", 16)
      -> ndarray with shape (2, 384)
    """


def build_faiss_index(vectors: Any) -> Any:
    """Build and return a FAISS index from vectors.

    Input:
      vectors: 2D float32 vectors

    Output:
      FAISS index object

    Example:
      build_faiss_index(vectors) -> <faiss.IndexFlatL2>
    """


def write_faiss_index(index: Any, index_path: Path) -> None:
    """Persist FAISS index to disk.

    Input:
      index: FAISS index
      index_path: e.g. Path("data/index/faiss.index")
    """


def write_metadata(records: list[dict[str, Any]], metadata_path: Path) -> None:
    """Persist chunk metadata records to JSON.

    Input:
      records: list of chunk metadata dicts
      metadata_path: e.g. Path("data/meta/metadata.json")

    Example record:
      {
        "doc_id": "doc_1",
        "chunk_id": "doc_1_chunk_1",
        "source": "password_reset_and_account_unlock.md",
        "chunk_index": 1,
        "chunk_text": "..."
      }
    """


def run_sync_ingest() -> dict[str, Any]:
    """Run sync ingest orchestration and return summary payload.

    Output example:
      {
        "status": "success",
        "total_docs": 3,
        "total_chunks": 18,
        "message": "Ingestion completed"
      }
    """
```

## 建议配置（`app/core/config.py`）

```python
raw_docs_dir: Path = Path("raw_docs")
index_path: Path = Path("data/index/faiss.index")
metadata_path: Path = Path("data/meta/metadata.json")
embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
embedding_batch_size: int = 16
chunk_size: int = 500
chunk_overlap: int = 80
```

## Sample Raw Docs 规划

在 `raw_docs/` 下新增 3 个 markdown 样例文件，用于本地 ingest 验证：

- `raw_docs/password_reset_and_account_unlock.md`
- `raw_docs/common_troubleshooting_playbook.md`
- `raw_docs/it_support_roles_and_handoffs.md`

每个文件建议包含：

- 一个一级标题（主题明确）
- 2-4 个二级标题
- 每节 2-5 行正文

这样可以稳定观察：

- chunk 数量是否符合预期
- metadata 的 `source/doc_id/chunk_id` 是否正确
- 后续 query 时召回是否可解释

## 验收标准（DoD）

- `POST /ingest` 返回结构化结果，不再是空对象。
- 能生成 `data/index/faiss.index` 与 `data/meta/metadata.json`。
- `GET /health` 能反映 ingest 状态变化和 `total_docs`。
- 空 `raw_docs/` 场景可正常处理（返回 0 docs/0 chunks）。
- `docs/api/local-endpoints.md` 已同步更新 `/ingest` 响应示例。
