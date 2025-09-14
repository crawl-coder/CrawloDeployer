# /backend/app/api/v1/endpoints/task_runs.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import deps
from app import models, schemas
from app.crud import task_run as crud_task_run
from app.crud import task as crud_task
from app.crud import project as crud_project

router = APIRouter(
    tags=["task-runs"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=List[schemas.TaskRunOut])
def read_task_runs(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取任务执行记录列表（分页）

    - **权限**：登录用户可访问
    - **用途**：监控面板、任务历史
    """
    runs = crud_task_run.get_multi(db, skip=skip, limit=limit)
    return runs


@router.get("/{run_id}", response_model=schemas.TaskRunOut)
def read_task_run(
    *,
    run_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    根据 ID 获取单个任务执行记录

    - **权限**：登录用户可访问
    """
    run = crud_task_run.get(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Task run not found")
    return run


@router.get("/task/{task_id}", response_model=List[schemas.TaskRunOut])
def read_task_runs_by_task(
    *,
    task_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取某个任务的所有执行记录（按时间倒序）

    - **权限**：登录用户可访问
    - **用途**：任务详情页 → 历史执行记录
    """
    # 先检查任务是否存在且用户有权限访问
    task = crud_task.get(db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 检查项目权限
    project = crud_project.get(db, id=task.project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 查询执行记录
    runs = crud_task_run.get_multi_by_task(db, task_id=task_id, skip=skip, limit=limit)
    return runs


@router.get("/celery/{celery_task_id}", response_model=schemas.TaskRunOut)
def read_task_run_by_celery_id(
    *,
    celery_task_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    根据 Celery 任务 ID 查询执行记录

    - **权限**：登录用户可访问
    - **用途**：实时日志页通过 celery_task_id 获取 run 信息
    """
    run = crud_task_run.get_by_celery_id(db, celery_task_id=celery_task_id)
    if not run:
        raise HTTPException(status_code=404, detail="Task run not found")
    return run


@router.delete("/{run_id}", response_model=schemas.TaskRunOut)
def delete_task_run(
    *,
    run_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    【管理员专用】删除某条任务执行记录

    - **权限**：仅 superuser 可访问
    - **用途**：清理数据、调试
    """
    run = crud_task_run.get(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Task run not found")

    db.delete(run)
    db.commit()
    return run


@router.get("/{run_id}/log", response_model=schemas.TaskRunLog)
def get_task_run_log(
    *,
    run_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取任务执行日志
    """
    run = crud_task_run.get(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Task run not found")
    
    # 检查用户权限
    task = crud_task.get(db, id=run.task_id)
    project = crud_project.get(db, id=task.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return schemas.TaskRunLog(
        id=run.id,
        log_content=run.log_output or ""
    )


@router.get("/{run_id}/log/stream", response_model=schemas.TaskRunLog)
def stream_task_run_log(
    *,
    run_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    实时流式获取任务执行日志（模拟实现）
    """
    run = crud_task_run.get(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Task run not found")
    
    # 检查用户权限
    task = crud_task.get(db, id=run.task_id)
    project = crud_project.get(db, id=task.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return schemas.TaskRunLog(
        id=run.id,
        log_content=run.log_output or ""
    )


@router.get("/{run_id}/export", response_model=schemas.TaskRunExport)
def export_task_run_data(
    *,
    run_id: int,
    format: str = "json",
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    导出任务执行结果数据
    """
    run = crud_task_run.get(db, id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Task run not found")
    
    # 检查用户权限
    task = crud_task.get(db, id=run.task_id)
    project = crud_project.get(db, id=task.project_id)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # 构造导出数据
    export_data = {
        "id": run.id,
        "task_id": run.task_id,
        "celery_task_id": run.celery_task_id,
        "status": run.status.value if hasattr(run.status, 'value') else str(run.status),
        "start_time": run.start_time.isoformat() if run.start_time else None,
        "end_time": run.end_time.isoformat() if run.end_time else None,
        "duration_seconds": run.duration_seconds,
        "items_scraped": run.items_scraped,
        "requests_count": run.requests_count,
        "result_size_mb": run.result_size_mb,
        "cpu_usage": run.cpu_usage,
        "memory_usage_mb": run.memory_usage_mb,
        "exit_code": run.exit_code,
        "manually_stopped": run.manually_stopped,
        "worker_node": run.worker_node,
        "log_output": run.log_output
    }
    
    return schemas.TaskRunExport(
        run_id=run_id,
        format=format,
        data=export_data
    )
