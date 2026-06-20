# Frontend Dockerfile 作业模板。
# 目标：把 Vite + React 前端跑在容器里，用最简单的开发服务器版本。
#
# 学生任务：只需要填写保留了 TODO_STUDENT_* 的几行。
# 完成后在 ui/ 目录下直接构建：
#   docker build -t rag-chatbot-ui:student .
#   docker run --rm -p 5173:5173 rag-chatbot-ui:student

# Step 1: 选择 Node.js 基础镜像。
# 这一步已经给出答案：Vite 前端需要 Node.js 来安装依赖并启动 dev server。
FROM node:20-alpine

# Step 2: 设置容器内工作目录。
# 这一步已经给出答案：后续 COPY / RUN / CMD 默认都会在 /app 下执行。
WORKDIR /app

# Step 3: 先复制 package.json 和 package-lock.json。
# 提示：这样 Docker 可以缓存 npm install 这一层；源码变化时不用每次重新安装依赖。
COPY package*.json ./

# Step 4: 安装前端依赖。
# 提示：和本地开发一样，使用 npm install 安装依赖。
RUN npm ci

# Step 5: 复制剩余前端源码。
# 这一步已经给出答案：把 index.html、vite.config.ts、src/ 等复制进镜像。
COPY . .

# Step 6: 声明 Vite dev server 端口。
# 这一步已经给出答案：ui/vite.config.ts 里配置了 5173。
EXPOSE 5173

# Step 7: 启动前端开发服务器。
# 提示：Docker 容器内必须监听 0.0.0.0，否则宿主机访问不到。
# 可参考命令：npm run dev -- --host 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
