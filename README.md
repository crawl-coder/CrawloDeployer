# CrawloDeployer: 分布式爬虫管理平台

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)![Vue.js](https://img.shields.io/badge/vue.js-3.x-brightgreen.svg)![Celery](https://img.shields.io/badge/Celery-5.x-orange.svg)![MySQL](https://img.shields.io/badge/MySQL-8.0-blue.svg)![Redis](https://img.shields.io/badge/redis-6.x-red.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CrawloDeployer** 是一个现代化的、可视化的分布式爬虫管理平台。它基于 `FastAPI` + `Vue3` 构建，允许开发者和团队轻松部署、调度、监控和管理他们的爬虫项目（如 `Scrapy`）。

[English](./README.en.md) | **中文**

## ✨ 主要特性

*   **可视化管理:** 提供现代、友好的 Web UI，所有操作均可在线完成。
*   **爬虫部署:** 支持将 `Scrapy` 项目打包上传，并在所有工作节点上进行分发。
*   **任务调度:**
    *   **即时任务:** 立即运行指定的爬虫。
    *   **定时任务:** 支持 `CRON` 表达式，实现灵活的周期性任务调度。
*   **分布式架构:** 采用主从（Master-Worker）架构，工作节点可水平扩展，轻松应对大规模爬取需求。
*   **节点监控:** 实时查看所有工作节点的状态（在线/离线）、心跳和资源占用情况。
*   **任务监控:** 跟踪每个任务的执行状态（运行中、成功、失败）、查看详细的运行日志和结果。
*   **高可用性:** 基于 `Celery` 和 `Redis` 实现稳定可靠的异步任务队列。

## 🛠️ 技术栈

*   **后端:**
    *   **框架:** FastAPI - 高性能的 Python Web 框架。
    *   **异步任务:** Celery - 分布式任务队列。
    *   **数据库 ORM:** SQLAlchemy - 强大的数据库工具集。
    *   **定时调度:** APScheduler - 轻量级的进程内任务调度库。
*   **前端:**
    *   **框架:** Vue 3 - 渐进式 JavaScript 框架。
    *   **构建工具:** Vite - 极速的开发和构建体验。
    *   **UI 库:** Element Plus - 成熟的 Vue 3 组件库。
    *   **状态管理:** Pinia - Vue 官方推荐的状态管理器。
    *   **HTTP 请求:** Axios。
*   **数据库 & 中间件:**
    *   **数据存储:** MySQL 8.0+
    *   **消息代理 & 缓存:** Redis 6.0+

## 🏗️ 系统架构

CrawloDeployer 采用主从（Master-Worker）架构设计：

*   **主节点 (Master):** 运行 FastAPI Web 应用和任务调度器。负责接收用户指令、管理项目、向任务队列推送任务，并监控所有工作节点。
*   **工作节点 (Worker):** 运行 Celery Worker 进程。负责从任务队列中获取并执行具体的爬虫任务，同时定期向主节点发送心跳。
*   **通信:** 主节点和工作节点通过 Redis 任务队列进行解耦，实现了高效的异步通信。

```
+----------------+      +------------------+      +-------------------+
|   用户 (浏览器)  | ---> |   主节点 (Master)  | ---> |   Redis (任务队列)  |
+----------------+      |  - FastAPI (API) |      +-------------------+
      ^               |  - Vue3 (UI)     |                |
      |               |  - APScheduler   |                |
      |               +------------------+                |
      |                                                 |
      |    +------------------+                         |
      +--- |   MySQL (数据持久化) | <-----------------------+
           +------------------+                         |
                                                        V
           +------------------+      +------------------+
           | 工作节点 1 (Worker)| <--- | 工作节点 N (Worker)| ...
           |  - Celery Worker |      |  - Celery Worker |
           |  - Scrapy Engine |      |  - Scrapy Engine |
           +------------------+      +------------------+
```

## 🚀 快速开始

### 1. 先决条件

*   Git
*   Python 3.8+
*   Node.js 16+ 和 pnpm (或 npm/yarn)
*   Docker 和 Docker Compose (推荐，用于快速启动数据库和Redis)

### 2. 克隆项目

```bash
git clone https://github.com/your-username/CrawloDeployer.git
cd CrawloDeployer
```

### 3. 环境配置

项目中包含 `.env.template` 文件，请复制并重命名为 `.env`，然后根据您的环境修改其中的配置。

```bash
cp backend/.env.template backend/.env
```

`backend/.env` 文件内容示例:
```env
# 数据库配置
DATABASE_URL="mysql+pymysql://user:password@localhost:3306/crawlpro"

# Redis 配置
REDIS_URL="redis://localhost:6379/0"

# Celery 配置
CELERY_BROKER_URL="redis://localhost:6379/1"
CELERY_RESULT_BACKEND="redis://localhost:6379/2"

# 安全配置
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. 启动依赖服务 (推荐使用 Docker)

项目根目录下提供了 `docker-compose.yml` 来快速启动 MySQL 和 Redis。

```bash
docker-compose up -d
```

### 5. 后端设置

```bash
# 进入后端目录
cd backend

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库 (运行 Alembic 迁移)
alembic upgrade head

# 启动主节点 (FastAPI 应用)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install # 或者 npm install

# 启动开发服务器
pnpm dev # 或者 npm run dev```

### 7. 启动工作节点

在新的终端窗口中，为工作节点设置环境。

```bash
# 进入后端目录 (工作节点和主节点共享大部分代码)
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装工作节点特定的依赖 (例如 Scrapy)
pip install -r ../worker/requirements.txt

# 启动 Celery Worker (假设 Celery app 实例在 app.core.celery_app 中)
celery -A app.core.celery_app.celery worker --loglevel=info -n worker1@%h
```

### 8. 访问系统

*   **前端界面:** `http://localhost:5173`
*   **后端 API 文档:** `http://localhost:8000/docs`

## 📖 使用指南

1.  **登录/注册:** 访问系统并创建一个管理员账户。
2.  **上传项目:** 在“项目管理”页面，将您的 Scrapy 项目打包为 `.zip` 文件并上传。
3.  **创建任务:** 在“任务管理”页面，点击“新建任务”，选择您刚上传的项目和其中的爬虫，配置执行参数，并设置执行计划（立即执行或定时执行）。
4.  **监控:** 在“任务日志”和“节点管理”页面，实时查看任务的执行情况和所有工作节点的健康状态。

## 🤝 贡献

欢迎任何形式的贡献！如果您有好的想法或发现了 Bug，请随时提交 Pull Request 或创建 Issue。

1.  Fork 本仓库
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  提交一个 Pull Request

## 📄 许可证

本项目使用 [MIT License](LICENSE) 授权。