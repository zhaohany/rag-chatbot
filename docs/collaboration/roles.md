# Team Roles (Local)

## Recommended Split

- 同学 A：`/ingest` 流程（chunking、embedding、FAISS 写入、metadata）
- 同学 B：`/query` 流程（检索、prompt 组装、生成器适配）
- 共同负责：`README.md`、`docs/setup/*`、接口联调

## Ownership by Folder

- `app/api/routes/`: 接口定义与返回格式
- `app/services/`: 业务流程实现
- `app/shared/`: 可复用工具函数
- `docs/`: 架构、接口、安装文档维护

## Collaboration Rules

- 改接口字段时，必须同步更新 `docs/api/local-endpoints.md`
- 改默认参数时，必须同步更新 `app/core/config.py` 与文档
- 合并前至少完成一次本地接口自测（`/health`、`/ingest`、`/query`）
