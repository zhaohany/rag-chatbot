# Query Prompt Generation 实施计划（基于最新 main）

## 目标

目标：在 `/query` 完成 retrieval 后，产出一个可直接用于 generation 的 prompt（prompt-ready artifact）。

- 保留现有 retrieval 流程
- 不在接入 LLM 生成
- 将 prompt 模板独立放到 `data/`，方便后续做 prompt engineering
- 不把 prompt 通过 API 返回给前端/用户，先写入本地 `data/` 文件用于测试

## 分支策略

- 基线分支：`main`（已包含 retrieval merge）
- 新分支：`zachar/prompt-generation-feature`
- 记得checkout main， pull再checkout new branch确保main updated并且在feature branch再implement

## 实施范围

### 1) Prompt 模板文件化管理

- 新增模板文件：
  - `data/prompts/query_prompt_v1.txt`
- 模板保留占位符：
  - `{context_blocks}`
  - `{question}`
- 模板文本风格以教学可读、可迭代为主（后续可直接改模板，不改代码）。

### 2) 配置层增加路径

- 更新 `app/core/config.py`：
  - 增加 `prompt_template_path: Path = Path("data/prompts/query_prompt_v1.txt")`
  - 增加 `final_prompt_path: Path = Path("data/prompts/final_prompt.txt")`
- 可选：更新 `.env.example`
  - `RAG_PROMPT_TEMPLATE_PATH=data/prompts/query_prompt_v1.txt`
  - `RAG_FINAL_PROMPT_PATH=data/prompts/final_prompt.txt`

### 3) 增加独立的 Generation Service（为下一步 LLM 做结构准备）

- 新增 `app/services/generation_service.py`：
  - `build_prompt(question, retrieved_chunks)`：组装最终 prompt
  - `save_prompt(prompt)`：写入 `settings.final_prompt_path`
- 设计原则：
  - Query 负责 retrieval orchestration
  - Generation 负责 prompt orchestration
  - 后续接 LLM 时可在 `generation_service` 继续加 `generate_answer()`，不污染 query 逻辑

### 4) Query Service 对接 Generation Service

- 更新 `app/services/query_service.py`：
  - 保留现有检索逻辑（index + metadata + top_k）
  - 调用 `generation_service.build_prompt(...)`
  - 调用 `generation_service.save_prompt(...)`
- 返回结果仅包含 retrieval 信息（不包含 prompt 字段）

### 5) Schema 更新

- 更新 `app/models/schemas.py`：
  - 保持 `QueryResponse` 以 retrieval 输出为主（不新增 `prompt` 返回）
  - 如有必要，仅增加内部调试字段开关（默认关闭）

### 6) Route 保持薄层

- 更新 `app/api/routes/query.py`：
  - 维持 thin route，只做调用与错误映射
  - 模板缺失/写文件失败等错误返回清晰信息（`HTTPException`）

### 7) 文档更新

- 更新 `docs/api/local-endpoints.md`：
  - `/query` request/response 示例保持 retrieval-only
  - 补充说明：最终 prompt 写入 `data/prompts/final_prompt.txt`
- 更新 `README.md` 当前状态说明：
  - `/query` 返回 retrieval；prompt 产物本地落盘，供 generation 使用

## 目标响应结构（建议）

- `answer`: `null`（不生成最终答案）
- `used_top_k`: 整数
- `retrieved_chunks`: 检索结果数组

## 本地落盘产物（新增）

- `data/prompts/query_prompt_v1.txt`：可编辑模板
- `data/prompts/final_prompt.txt`：每次 `/query` 生成后的最终 prompt

## 验证计划

- 语法检查：
  - `python3 -m compileall app`
- 手工联调：
  - 先 `POST /ingest` 建索引
  - 再 `POST /query` 验证：
    - 有检索结果
    - `data/prompts/final_prompt.txt` 已生成
    - 文件内容包含 context 与 question
- 异常路径：
  - 模板文件缺失时，报错信息清晰且可操作

## 非目标（不做）

- 不接入任何 LLM provider 的生成调用
- 不做 retrieval 算法大改
- 不做 UI 大改

## 风险与注意事项

- 如果 metadata 里 chunk 正文不全，prompt context 质量会受限；需保留 fallback 文本提示。
- 代码重构时保留现有教学注释与 docstring。
