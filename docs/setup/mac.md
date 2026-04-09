# macOS Setup

## 1) Prerequisites

- Python 3.10+
- pip3

## 2) Create and Activate Virtual Env

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
```

## 3) Install Dependencies

```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

可选：复制环境变量模板

```bash
cp .env.example .env
```

默认配置已可直接运行，不复制 `.env` 也可以。

## 4) Prepare Local Docs

当前 skeleton 阶段这一步可选。后续实现 ingest 时再放入 markdown 文档。

示例目录：

```text
raw_docs/
  lesson1.md
  lesson2.md
```

## 5) Run API

```bash
python3 -m uvicorn app.main:app --reload
```

访问：

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 6) Quick Verify

```bash
curl -X GET http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/ingest
curl -X POST http://127.0.0.1:8000/query -H "Content-Type: application/json" -d '{}'
```

可选：启动 lightweight UI（React + Vite + TypeScript）

```bash
cd ui
cp .env.example .env  # 可选
npm install
npm run dev
```

访问 UI：`http://127.0.0.1:5173`

## Troubleshooting

- `ModuleNotFoundError`: 确认已激活 `.venv` 且依赖安装成功
- 请求体校验报错：当前 `POST /query` 需要 JSON body，可先传 `{}`
