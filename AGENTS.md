# AGENTS.md
Practical instructions for coding agents in this repository.

## Project at a glance
- Stack: Python 3.10+, FastAPI, sentence-transformers, FAISS.
- Entrypoint: `app/main.py`.
- Main endpoints: `/health`, `/ingest`, `/query`.
- Data files:
  - index: `data/index/faiss.index`
  - metadata: `data/meta/metadata.json`
  - source docs: `raw_docs/*.md`

## Setup and run
From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```

Optional env file:

```bash
cp .env.example .env
```

Quick API smoke checks:

```bash
curl -X GET http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/ingest
curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{}'
```

## Build / lint / test commands
Note: repo currently has no committed lint/test config (`pyproject.toml`, `pytest.ini`, `ruff.toml`, etc.).
Use the following baseline commands.

### Build-equivalent validation
No packaging build pipeline exists. Use runtime checks:

```bash
python3 -m compileall app
python3 -m uvicorn app.main:app --reload
```

### Lint, format, typing
Install dev tools if missing:

```bash
pip3 install ruff mypy pytest
```

Run quality checks:

```bash
ruff check app
ruff check app --fix
ruff format app
mypy app
```

### Tests
Current state: no tests are committed yet.

Run all tests:

```bash
pytest -q
```

Run a single test file:

```bash
pytest tests/test_ingest_service.py -q
```

Run a single test function (preferred single-test pattern):

```bash
pytest tests/test_ingest_service.py::test_run_ingest_happy_path -q
```

Useful variants:

```bash
pytest -q -k ingest
pytest -q -x
```

## Repository structure
- `app/api/routes/`: thin HTTP endpoints and `HTTPException` mapping.
- `app/services/`: service skeletons aligned with routes (health / ingest / query).
- `app/models/`: Pydantic request/response models.
- `app/shared/`: reusable helpers (`chunking`, IDs).
- `app/core/config.py`: default settings and env-driven config.
- `docs/`: setup, architecture, API docs, team conventions.

When changing endpoint fields or defaults:
- update `docs/api/local-endpoints.md`
- update relevant setup/architecture docs and `README.md`

## Code style guidelines

### Python, typing, and formatting
- Keep `from __future__ import annotations` in Python modules (existing pattern).
- Type annotate all new/edited functions and methods.
- Prefer modern types: `list[str]`, `dict[str, Any]`, `str | None`.
- Keep functions focused and short; split complex logic into services/helpers.
- Follow PEP 8 and keep line length readable (88-100 target is acceptable).

### Import rules
- Group imports in this order with one blank line between groups:
  1) standard library
  2) third-party
  3) local `app.*`
- Prefer absolute imports from `app...`.
- Remove unused imports.

### Naming conventions
- Files/modules: `snake_case.py`.
- Functions/variables: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Keep naming explicit; avoid vague abbreviations.
- Preserve existing ID formats:
  - `doc_id` = `doc_{n}`
  - `chunk_id` = `{doc_id}_chunk_{n}`

### API and schema conventions
- Route handlers should stay thin; delegate work to `app/services`.
- Define request/response models with Pydantic (`app/models/schemas.py`).
- Use `Field(...)` constraints for validation where appropriate.
- Keep API changes backward compatible unless task explicitly changes contract.

### Error handling rules
- Catch specific exceptions first.
- In routes, convert domain/runtime failures into clear `HTTPException` status codes.
- Avoid broad `except Exception`; only use at boundaries where you must preserve service stability.
- If broad catch is used, keep message actionable and chain exceptions (`raise ... from exc`).
- Never silently swallow errors.

### State and persistence
- Use UTF-8 for text reads/writes.
- Use `pathlib.Path` and create parent dirs before writing.
- Keep JSON readable (`indent=2`) unless performance requires otherwise.
- Keep side effects in service/store layer, not in route handlers.
- Handle mutable run state (`ingest_state`) carefully; always reset flags in `finally`.

## Architecture guardrails for agents
- Prefer minimal, targeted edits over broad refactors.
- Preserve boundaries between `routes`, `services`, `models`, `shared`, `core`.
- Do not introduce cloud infra, DBs, or queues unless explicitly requested.
- Keep local-first assumptions unless task requirements state otherwise.
- Do not commit generated local data files unless explicitly requested.

## Cursor/Copilot rules status
Checked:
- `.cursorrules`
- `.cursor/rules/`
- `.github/copilot-instructions.md`

Result: no Cursor or Copilot instruction files currently exist.
If added later, treat them as higher-priority guidance and merge into this file.
