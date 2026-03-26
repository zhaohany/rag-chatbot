# Windows Setup

## 1) Prerequisites

- Python 3.10+
- PowerShell 或 CMD
- 网络可访问 Hugging Face（首次会下载 embedding 模型）

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

如果 `faiss-cpu` 在 Windows 上安装失败，建议两种方案：

1. 使用 Conda 环境安装 FAISS
2. 使用 WSL 运行本项目

## 4) Prepare Local Docs

将 markdown 文件放入 `raw_docs/`。

## 5) Run API

```powershell
uvicorn app.main:app --reload
```

访问：

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 6) Quick Verify

```powershell
curl -Method Post http://127.0.0.1:8000/ingest
curl -Method Post http://127.0.0.1:8000/query -ContentType "application/json" -Body '{"question":"Summarize the docs"}'
```

## Troubleshooting

- 激活脚本受限：`Set-ExecutionPolicy -Scope Process Bypass`
- 查询报索引不存在：先执行 `/ingest`
