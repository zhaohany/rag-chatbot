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

推荐：复制环境变量模板

```powershell
Copy-Item .env.example .env
```

如需启用 Gemini 生成，请在 `.env` 中替换你的 API Key：

```powershell
RAG_GEMINI_API_KEY=your_gemini_api_key_here
```

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
curl -Method Post http://127.0.0.1:8000/query -ContentType "application/json" -Body '{"question":"How to reset password?"}'
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
- 请求体校验报错：当前 `POST /query` 需要 JSON body，且必须包含 `question`
