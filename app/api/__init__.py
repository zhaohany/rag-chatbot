"""API 接口层（api）。

这个目录用于放置所有对外 HTTP 接口相关代码，例如：
- 路由模块（FastAPI routers/endpoints）
- 请求进入 API 边界后的参数接收与响应返回
- 轻量的 HTTP 错误映射

原则：api 层保持轻薄，不放核心业务逻辑。
"""
