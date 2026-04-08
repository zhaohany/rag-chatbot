"""业务服务层（services）。

这个目录目前与路由一一对应，保持最小骨架：
- health_service.py：健康检查相关服务逻辑
- ingest_service.py：入库触发相关服务逻辑
- query_service.py：查询相关服务逻辑

可以把这里理解为“搭建流程层”：把 shared 的积木按业务目标组装成完整流程。
原则：路由层只做转发与参数校验，核心业务逻辑集中在 services。
"""
