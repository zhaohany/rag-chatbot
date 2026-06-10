# Frontend Docker Assignment

这个作业的目标是让学生用 Docker 跑起 `ui/` 里的 Vite + React 前端。

为了保持作业简单，这里不做生产环境 nginx 部署，也不做 multi-stage build。学生只需要完成一个开发版 Dockerfile：安装依赖，然后运行 Vite dev server。

## Frontend 快速背景

这个仓库的前端在 `ui/` 目录下，是一个很小的 React demo UI，用来调用后端的 `/health`、`/ingest`、`/query` 接口。

前端技术栈：

- `React`：负责写浏览器里的 UI 组件。
- `React DOM`：把 React 组件渲染到浏览器页面上。
- `Vite`：本地开发服务器和前端打包工具。开发时它会启动一个 web server，默认端口是 `5173`。
- `TypeScript`：给 JavaScript 加类型检查，帮助提前发现参数、返回值、字段名错误。

关键文件：

- `ui/package.json`：前端项目的配置文件，里面定义依赖和可运行命令。
- `ui/package-lock.json`：锁定依赖的精确版本，让大家安装出来的依赖一致。
- `ui/src/`：React 和 TypeScript 源码。
- `ui/index.html`：浏览器打开的 HTML 入口。
- `ui/vite.config.ts`：Vite 配置，本项目里设置了 dev server 端口 `5173`。
- `ui/.env.example`：前端环境变量示例，里面有后端 API 地址 `VITE_API_BASE_URL`。

常见命令：

```bash
cd ui
npm install
npm run dev
```

这些命令的含义：

- `cd ui`：进入前端项目目录。
- `npm install`：根据 `package.json` / `package-lock.json` 下载依赖，生成 `node_modules/`。
- `npm run dev`：运行 `package.json` 里的 `dev` 脚本，也就是启动 Vite dev server。

`package.json` 里目前定义了这些 scripts：

```json
{
  "dev": "vite",
  "build": "tsc -b && vite build",
  "preview": "vite preview"
}
```

它们分别表示：

- `npm run dev`：本地开发时使用，启动 Vite server。
- `npm run build`：生产构建时使用，先做 TypeScript 检查，再生成静态文件到 `dist/`。
- `npm run preview`：预览 `npm run build` 生成的生产构建结果。

几个容易混淆的概念：

- `Node.js`：让 JavaScript 可以在本机或容器里运行。前端构建工具 Vite 需要 Node.js。
- `npm`：Node.js 自带的包管理器，用来安装依赖和运行 scripts。
- `node_modules/`：npm 下载下来的依赖目录，通常很大，不应该复制进 Docker build context。
- `5173`：Vite dev server 的端口。浏览器访问 `http://127.0.0.1:5173` 可以打开前端。
- `VITE_API_BASE_URL`：前端调用后端 API 的基础地址。本项目默认是 `http://127.0.0.1:8000`。

Dockerfile 要做的事情，本质上就是把上面的本地步骤放进容器里：

- 选择一个带 Node.js 的基础镜像。
- 把 `package.json` / `package-lock.json` 复制进去。
- 在容器里运行 `npm ci` 安装依赖。
- 把前端源码复制进去。
- 暴露 `5173` 端口。
- 用 `npm run dev -- --host 0.0.0.0` 启动 Vite，让宿主机浏览器可以访问容器里的前端。

## 学生要完成什么

作业文件在：

```text
ui/Dockerfile
```

学生只需要填写 `ui/Dockerfile` 里保留了 `TODO_STUDENT_*` 的几行。

已给出的部分：

- `FROM node:20-alpine`
- `WORKDIR /app`
- `COPY . .`
- `EXPOSE 5173`

需要学生填写的部分：

- `COPY TODO_STUDENT_PACKAGE_FILES ./`
- `RUN TODO_STUDENT_INSTALL_COMMAND`
- `CMD TODO_STUDENT_START_COMMAND`

完成后，在 `ui/` 目录下直接执行：

```bash
docker build -t rag-chatbot-ui:student .
docker run --rm \
  -p 5173:5173 \
  -e VITE_API_BASE_URL="http://127.0.0.1:8000" \
  rag-chatbot-ui:student
```

也可以在仓库根目录用 Compose 启动：

```bash
docker compose up --build frontend
```

因为 `compose.yaml` 里配置了 `frontend` 依赖 `backend`，所以上面这条命令会同时启动后端。

也可以显式写出两个服务：

```bash
docker compose up --build backend frontend
```

浏览器访问：

```text
http://127.0.0.1:5173
```

## 每一步要做什么

### Step 1: 选择基础镜像

前端项目需要 Node.js 来执行 `npm ci` 和 `npm run dev`。这一步已经在作业文件里写好。

推荐使用：

```dockerfile
FROM node:20-alpine
```

`alpine` 版本体积较小，适合这个简单前端作业。

### Step 2: 设置工作目录

容器里需要一个目录放前端代码。这一步已经在作业文件里写好：

```dockerfile
WORKDIR /app
```

设置后，后面的 `COPY`、`RUN`、`CMD` 默认都在 `/app` 下执行。

### Step 3: 先复制依赖描述文件

前端依赖由 `package.json` 和 `package-lock.json` 描述。

推荐写法：

```dockerfile
COPY package*.json ./
```

这样做可以利用 Docker 缓存。只要依赖文件没变，重新构建时就不用重复安装依赖。

### Step 4: 安装依赖

本项目已经有 `package-lock.json`，所以推荐：

```dockerfile
RUN npm ci
```

`npm ci` 会严格按照 lockfile 安装，更适合自动化构建。

### Step 5: 复制源码

安装完依赖后，再复制前端源码。这一步已经在作业文件里写好：

```dockerfile
COPY . .
```

这里会复制 `src/`、`index.html`、`vite.config.ts` 等文件。

`ui/.dockerignore` 会排除 `node_modules/`、`dist/`、`.env` 等不应该进入镜像的文件。

### Step 6: 声明端口

Vite 默认开发端口在本项目中是 `5173`：

```dockerfile
EXPOSE 5173
```

注意：`EXPOSE` 只是声明容器内服务使用的端口。真正把端口映射到宿主机，是 `docker run -p 5173:5173`。

### Step 7: 启动 Vite dev server

容器里启动 Vite 时，需要监听 `0.0.0.0`：

```dockerfile
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

如果只监听默认的 `localhost`，服务可能只在容器内部可见，宿主机浏览器访问不到。

## 参考答案

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

## 和 backend Dockerfile 的区别

- backend 需要 Python、FastAPI、ML 依赖和模型缓存。
- frontend 只需要 Node.js、npm 依赖和 Vite dev server。
- backend 有本地数据目录 `data/`、`raw_docs/` 的挂载需求。
- frontend 这个作业版本不需要 volume，代码已经被复制进镜像。
- frontend 生产部署通常会用 `npm run build` 加 nginx，但这个作业先不引入。
