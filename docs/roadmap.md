# Roadmap (Local First)

## Milestone 1: Skeleton (Done)

- FastAPI app + 3 endpoints
- Route/service/model/shared/core 分层结构
- Services 与 routes 一一对应（health/ingest/query）
- 系统元数据最小结构：`ingestion_status` + `last_success_ingestion_time`
- Setup docs for macOS and Windows
- Flat local structure (`app/`, `docs/`, `data/`, `raw_docs/`)
- Lightweight UI scaffold (`ui/`, React + Vite + TypeScript)

## Milestone 2: Quality

- add tests for API skeleton routes
- improve error handling and logging
- add ingest status endpoint (optional)

## Milestone 3: Better Answer Quality

- implement ingest pipeline step by step
- implement retrieval pipeline step by step
- implement generation pipeline step by step

后续如需上云，再在此基础上拆分部署方案。
