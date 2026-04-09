# Health API Implementation Plan

## 目标

- 先完成一个可教学、可演示的 `GET /health`。
- 响应只关注 ingestion 状态，不引入额外复杂字段。

## API 契约（当前阶段）

- 路径：`GET /health`
- 响应字段：
  - `status`: API 本身健康状态，固定 `ok`
  - `version`: 当前服务版本（来自配置）
  - `ingestion_status`: 入库状态（如 `idle` / `running` / `success` / `failed`）
  - `last_success_ingestion_time`: 最近一次成功入库时间（UTC ISO-8601），无则 `null`

示例：

```json
{
  "status": "ok",
  "version": "0.1.0",
  "ingestion_status": "idle",
  "last_success_ingestion_time": null
}
```

## 数据来源

- 文件：`data/system/system_meta.json`
- 当前最小结构：

```json
{
  "ingestion_status": "idle",
  "last_success_ingestion_time": null
}
```

## 代码落点

- `app/models/schemas.py`
  - 定义 `HealthResponse` 字段。
- `app/services/health_service.py`
  - 读取 `system_meta.json`。
  - 提供 ingestion 状态与时间。
- `app/api/routes/health.py`
  - 组合 `status` + `version` + ingestion 元数据并返回。
- `docs/api/local-endpoints.md`
  - 更新 health 响应示例。

## 课堂分步建议

1. 先讲清 API 契约（字段语义）。
2. 再讲 schema（为什么要先定义输出结构）。
3. 实现 service 读取本地状态文件。
4. 最后在 route 里做组装与返回。
5. 用 curl 验证并观察 JSON 响应。

## 验收标准

- `GET /health` 返回 200。
- 返回 JSON 包含 4 个字段：
  - `status`
  - `version`
  - `ingestion_status`
  - `last_success_ingestion_time`
- 当 `system_meta.json` 不同值时，health 响应能反映变化。

## 后续扩展（后续课再做）

- 将 ingestion 状态写入逻辑接入 `POST /ingest`。
- 为状态字段补充更严格的枚举校验。
- 增加最小 API 测试。
