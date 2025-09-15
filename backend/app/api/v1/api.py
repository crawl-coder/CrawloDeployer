# /backend/app/api/v1/api.py

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, projects, tasks, nodes, git_credentials, task_runs, workflows

api_router = APIRouter()

# 为不同的功能模块分配路由和前缀
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])

# 之后添加 tasks 和 nodes 的路由
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
api_router.include_router(task_runs.router, prefix="/task-runs", tags=["task-runs"])

api_router.include_router(git_credentials.router, prefix="/git-credentials", tags=["git-credentials"]) # 新增
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])