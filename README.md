# CrawloDeployer

一个用于部署和管理爬虫项目的平台。

## 技术栈

### 后端
- **框架**: FastAPI
- **异步任务**: Celery
- **数据库 ORM**: SQLAlchemy
- **定时调度**: APScheduler
- **数据库**: MySQL 8.0+
- **消息代理**: Redis 6.0+
- **认证**: JWT

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **UI 库**: Element Plus
- **状态管理**: Pinia
- **HTTP 请求**: Axios

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Docker 和 Docker Compose
- MySQL 8.0+
- Redis 6.x

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/your-username/CrawloDeployer.git
cd CrawloDeployer
```

2. 启动依赖服务
```bash
docker-compose up -d
```

3. 配置后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. 初始化数据库
```bash
alembic upgrade head
```

5. 启动后端服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. 配置前端
```bash
cd frontend
pnpm install
```

7. 启动前端开发服务器
```bash
pnpm dev
```

8. 启动工作节点
```bash
cd backend
source venv/bin/activate
pip install -r ../worker/requirements.txt
celery -A app.core.celery_app.celery worker --loglevel=info -n worker1@%h
```

### 使用说明

#### 项目管理
1. **创建项目**:
   - 通过文件上传：支持ZIP包、Python脚本、文件夹或多个文件
   - 通过Git仓库：支持HTTP/HTTPS和SSH方式克隆

2. **文件夹上传**:
   - 在创建项目时选择"上传文件"方式
   - 点击"选择文件/文件夹"按钮
   - 选择文件夹时会保持原有目录结构
   - 支持拖拽上传文件/文件夹

3. **Git集成**:
   - 在Git凭证管理中添加Git仓库的认证信息
   - 支持Token/密码和SSH密钥两种认证方式
   - 创建项目时选择"Git仓库"方式并填写仓库地址
   - SSH方式需要提供SSH私钥内容和可选的公钥指纹

4. **项目同步**:
   - 对于需要在多个节点部署的项目，可以使用项目同步功能
   - 在项目详情页面点击"同步到节点"按钮
   - 选择目标节点，系统会自动将项目文件分发到选中的节点
   - 避免了在每台服务器上手动拉取代码的繁琐操作

#### Git凭证管理
1. **Token/密码认证**:
   - 适用于HTTP/HTTPS协议的Git仓库
   - 需要提供用户名和访问令牌（Token）

2. **SSH密钥认证**:
   - 适用于SSH协议的Git仓库
   - 需要提供SSH私钥内容（PEM格式）
   - 可选提供SSH公钥指纹用于验证

#### 任务管理
1. **创建任务**:
   - 选择所属项目和爬虫名称
   - 配置调度表达式（CRON格式）或选择立即执行
   - 设置优先级、超时时间、重试次数等参数

2. **任务执行器**:
   - 支持通用脚本执行（Python, Shell, Node.js等）
   - 支持Crawlo爬虫框架
   - 支持Scrapy爬虫框架

3. **节点绑定**:
   - **任意节点**: 任务可在任意可用节点执行（默认）
   - **指定单个节点**: 任务只能在指定节点执行
   - **指定多个节点**: 任务可在指定的多个节点中执行
   - **基于标签分发**: 任务可在具有指定标签的节点中执行

4. **任务依赖**:
   - 可以设置任务间的依赖关系
   - 依赖任务完成后才会执行当前任务

#### 项目部署
1. 项目创建后会自动部署到指定目录
2. 可以通过项目详情页面管理环境变量
3. 支持在线编辑项目配置和状态

#### 节点管理
1. **自动注册**:
   - 工作节点启动时自动向主节点注册
   - 通过心跳机制维持节点在线状态

2. **资源监控**:
   - 实时监控节点的CPU、内存、磁盘使用情况
   - 显示节点的操作系统和软件版本信息

3. **标签和能力**:
   - 可以为节点添加标签（如gpu,proxy,chrome等）
   - 可以定义节点的能力（如GPU支持、浏览器支持等）

#### 分布式部署
1. **架构设计**:
   - 主从架构：主节点负责任务调度和管理，工作节点负责执行任务
   - 通过Redis实现主节点与工作节点的异步通信

2. **多节点部署**:
   - 可以部署多个工作节点以提高并发处理能力
   - 节点可以部署在不同的服务器上
   - 支持跨地域部署

3. **负载均衡**:
   - 任务会自动分发到可用的工作节点
   - 可以通过节点绑定功能指定任务执行节点
   - 支持基于节点标签的任务分发

4. **项目文件分发**:
   - 项目文件只需在主节点维护一份
   - 通过项目同步功能可以将文件分发到指定的工作节点
   - 避免了在每台服务器上重复拉取代码的操作