# 使用官方 Python 3.11 slim 镜像作为基础镜像。
# slim 版本比完整 Debian 镜像更小，但仍然适合安装本项目的 Python 依赖。
FROM python:3.11-slim

# Python / pip / Hugging Face 运行时配置：
# - PYTHONDONTWRITEBYTECODE=1：不生成 __pycache__ / .pyc，减少容器内无用文件。
# - PYTHONUNBUFFERED=1：让日志直接输出到 stdout/stderr，方便 docker logs 实时查看。
# - PIP_NO_CACHE_DIR=1：pip 安装后不保留下载缓存，减少镜像体积。
# - HF_HOME：指定 sentence-transformers / transformers 模型缓存目录。
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface

# 设置容器内工作目录。后续 COPY、RUN、CMD 默认都在 /app 下执行。
WORKDIR /app

# 先只复制 requirements.txt，利用 Docker layer cache。
# 只要依赖文件没变，后续重新 build 时可以复用 pip install 这一层。
COPY requirements.txt .

# 安装 Python 依赖。
# 本项目依赖 torch、sentence-transformers、faiss 等较大的 ML 包，首次构建会比较慢。
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 复制应用源码。
COPY app ./app

# 复制 prompt 模板文件。query 服务默认会从 data/prompts 下读取 prompt template。
COPY data/prompts ./data/prompts

# 复制系统状态元数据。health / ingest 相关逻辑会读取这个目录下的状态文件。
COPY data/system ./data/system

# 创建运行时需要的目录，并创建非 root 用户运行服务：
# - data/index：FAISS index 默认保存目录。
# - data/meta：metadata 默认保存目录。
# - raw_docs：ingest 默认读取 markdown 文档的目录。
# - HF_HOME：模型缓存目录。
# - appuser：避免以 root 身份运行 Web 服务，更安全。
# - chown：确保 appuser 对 /app 下的运行时目录有读写权限。
RUN mkdir -p data/index data/meta raw_docs "$HF_HOME" \
    && useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app

# 切换到非 root 用户。后面的 HEALTHCHECK 和 CMD 都会以 appuser 身份执行。
USER appuser

# 声明容器内服务监听端口。这个指令只做元数据声明，真正映射端口在 compose.yaml 里配置。
EXPOSE 8000

# 容器健康检查。
# Docker 会定期访问容器内部的 /health：
# - interval=30s：每 30 秒检查一次。
# - timeout=5s：单次检查超过 5 秒算失败。
# - start-period=120s：启动后的前 120 秒内给模型加载 / 服务启动留缓冲时间。
# - retries=3：连续失败 3 次后标记为 unhealthy。
# 使用 Python 标准库 urllib，避免为了 healthcheck 额外安装 curl。
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read()"

# 容器启动命令。
# - python -m uvicorn：用当前 Python 环境启动 uvicorn。
# - app.main:app：FastAPI app 对象位置，对应 app/main.py 里的 app。
# - --host 0.0.0.0：监听所有网卡，允许 Docker 端口映射访问。
# - --port 8000：容器内监听 8000 端口。
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
