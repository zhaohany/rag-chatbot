# Roadmap (Local First)

## Milestone 1: Skeleton (Done)

- FastAPI app + 3 endpoints
- Ingest from `raw_docs/*.md`
- FAISS + metadata persistence
- Query retrieval + mock generation
- Setup docs for macOS and Windows
- Flat local structure (`app/`, `docs/`, `data/`, `raw_docs/`)

## Milestone 2: Quality

- add tests for chunking and API routes
- improve error handling and logging
- add ingest status endpoint (optional)

## Milestone 3: Better Answer Quality

- tune chunk size / overlap
- better prompt template
- optional switch to real hosted LLM

后续如需上云，再在此基础上拆分部署方案。
