# macOS Setup

## 1) Prerequisites

- Python 3.10+
- pip
- 网络可访问 Hugging Face（首次会下载 embedding 模型）

## 2) Create and Activate Virtual Env

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
```

## 3) Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

可选：复制环境变量模板

```bash
cp .env.example .env
```

默认配置已可直接运行，不复制 `.env` 也可以。

## 4) Prepare Local Docs

将你的 markdown 文档放到 `raw_docs/`，例如：

```text
raw_docs/
  lesson1.md
  lesson2.md
```

## 5) Run API

```bash
uvicorn app.main:app --reload
```

访问：

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 6) Quick Verify

```bash
curl -X POST http://127.0.0.1:8000/ingest
curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{"question":"Summarize the docs"}'
```

## Troubleshooting

- `ModuleNotFoundError`: 确认已激活 `.venv` 且依赖安装成功
- 模型下载慢：先确认网络，再重试
- 查询报索引不存在：先执行一次 `/ingest`
