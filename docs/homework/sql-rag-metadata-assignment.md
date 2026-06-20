# SQL 作业：用 SQLite 替换本地 Metadata 存储

## 目标

这个 RAG chatbot 项目原来主要把 metadata（元数据）存在本地 JSON 文件里。

现在项目里已经加了一层 SQLite database service（本地数据库服务）封装：

- `app/services/database_service.py`

应用代码已经接好了这个 database service。

你不需要从零搭架构。

你只需要完成一个 SQL 练习点。

你要改的位置是：

```text
app/services/database_service.py
```

搜索：

```text
TODO(homework)
```

然后补完整 `load_chunk_metadata(...)` 里面的 SQL query。

---

## 为什么要做这个作业

RAG 系统里通常不会把所有东西都放在一个地方。

| 数据 | 放在哪里 | 原因 |
|---|---|---|
| 原始文档，比如 Markdown / PDF | `raw_docs/` 或 object storage | 文件本体比较大，不适合直接塞进 SQL row |
| embedding vector | FAISS / vector database | 用来做 Top-K similarity search |
| document metadata | SQLite / PostgreSQL | 结构化字段，适合 SQL 查询 |
| chunk text 和 source 信息 | SQLite / PostgreSQL | 最终回答需要引用来源 |
| ingestion status | SQLite / PostgreSQL | `/health` 需要知道当前状态 |

本作业的重点是：

> FAISS 负责向量检索，SQLite 负责根据 `vector_id` 找回 chunk metadata。

---

## 已经帮你写好的部分

以下部分已经写好，不需要你改：

1. SQLite 连接。
2. 建表 SQL。
3. `/ingest` 调用 database 写入 metadata。
4. `/query` 调用 database 读取 metadata。
5. `/health` 调用 database 读取 ingestion status。
6. system state 的 insert / update / select。
7. documents 和 chunks 的 insert。

你只需要补一个 SQL query。

本作业不提供假数据 seed file。

你需要先跑 `/ingest`，让项目从 `raw_docs/*.md` 生成真实的 SQLite metadata。

---

## 你要完成的任务

打开：

```text
app/services/database_service.py
```

找到函数：

```python
load_chunk_metadata(...)
```

这个函数的作用是：

> 从 SQLite 里读取 chunk metadata，让 `/query` 能把 FAISS 返回的 `vector_id` 映射回具体的 chunk text 和 source。

你要写的 SQL 需要做到 4 件事：

1. 从 `chunks` 表读取 chunk metadata。
2. 用 `chunks.doc_id = documents.doc_id` 连接 `documents` 表。
3. 排除 soft-deleted documents：`documents.is_deleted = 0`。
4. 按 `chunks.vector_id ASC` 排序。

必须返回这些字段：

```text
chunks.vector_id
chunks.chunk_id
chunks.doc_id
chunks.chunk_text
chunks.source_path
documents.title AS document_title
documents.status AS document_status
documents.is_deleted
```

---

## 你不要改的东西

不要改这些文件：

1. `app/api/routes/*`
2. `app/models/schemas.py`
3. `app/services/query_service.py`
4. `app/services/ingest_service.py`

不要改 response schema。

不要把 embedding vector 存进 SQLite。

不要把 raw markdown 文件内容整体存进 `documents` 表。

---

## SQL 提示

你需要用到这些 SQL 语法。

### `SELECT`

```sql
SELECT column_1, column_2
FROM table_name;
```

### `JOIN`

```sql
SELECT ...
FROM table_a
JOIN table_b ON table_a.id = table_b.id;
```

### `WHERE`

```sql
WHERE documents.is_deleted = 0
```

### `ORDER BY`

```sql
ORDER BY chunks.vector_id ASC
```

---

## 本地验证

先检查 Python 是否能编译：

```bash
python3 -m compileall app
```

如果你本地装了 `pytest`，可以跑：

```bash
pytest -q
```

启动 API：

```bash
python3 -m uvicorn app.main:app --reload
```

另开一个 terminal，先跑 ingest：

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

这一步会读取 `raw_docs/*.md`，生成：

1. FAISS index：`data/index/faiss.index`
2. SQLite metadata database：`data/meta/rag_metadata.db`

本作业不要求你手写假数据。

再跑 query：

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I reset my password?"}'
```

---

## 通过标准

完成后应该满足：

1. `python3 -m compileall app` 通过。
2. `POST /ingest` 能成功。
3. `POST /query` 能成功。
4. `/query` 返回的 `retrieved_chunks` 里有：
   - `chunk_id`
   - `doc_id`
   - `text`
   - `source_path`
5. SQLite database 会出现在：

```text
data/meta/rag_metadata.db
```

---

## 常见错误

1. 忘记 `JOIN documents ON chunks.doc_id = documents.doc_id`。
2. 忘记过滤 `documents.is_deleted = 0`。
3. 忘记 `ORDER BY chunks.vector_id ASC`。
4. 字段 alias 写错，比如没有写 `documents.title AS document_title`。
5. 改了 Python 其他逻辑，导致 API response schema 变了。

---

## 面试表达

你可以这样复述这个设计：

> In this RAG system, FAISS stores embeddings and handles vector search. SQLite stores structured metadata such as document ids, chunk ids, chunk text, source paths, and ingestion status. The query flow first gets vector ids from FAISS, then uses SQLite to load the matching chunk metadata for prompt construction and citations.

中文解释：

> 在这个 RAG 系统里，FAISS 存 embedding 并负责向量检索。SQLite 存结构化 metadata，比如 document id、chunk id、chunk text、source path 和 ingestion status。查询时先从 FAISS 拿到 vector id，再用 SQLite 查回对应的 chunk metadata，用于 prompt 和引用来源。
