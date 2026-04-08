# Windows Setup

## 1) Prerequisites

- Python 3.10+
- PowerShell 或 CMD

## 2) Create and Activate Virtual Env

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python --version
```

## 3) Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

可选：复制环境变量模板

```powershell
Copy-Item .env.example .env
```

默认配置已可直接运行，不复制 `.env` 也可以。

## 4) Prepare Local Docs

当前 skeleton 阶段这一步可选。后续实现 ingest 时再放入 markdown 文档。

## 5) Run API

```powershell
uvicorn app.main:app --reload
```

访问：

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 6) Quick Verify

```powershell
curl http://127.0.0.1:8000/health
curl -Method Post http://127.0.0.1:8000/ingest
curl -Method Post http://127.0.0.1:8000/query -ContentType "application/json" -Body '{}'
```

可选：启动 lightweight UI（React + Vite + TypeScript）

```powershell
cd ui
Copy-Item .env.example .env  # 可选
npm install
npm run dev
```

访问 UI：`http://127.0.0.1:5173`

## Troubleshooting

- 激活脚本受限：`Set-ExecutionPolicy -Scope Process Bypass`
- 请求体校验报错：当前 `POST /query` 需要 JSON body，可先传 `{}`
