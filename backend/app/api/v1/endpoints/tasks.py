# /backend/app/api/v1/endpoints/tasks.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import deps
from app import models, schemas
from app.services.scheduler import scheduler_service
from app.crud import project as crud_project
from app.crud import task as crud_task
from app.crud import task_run as crud_task_run
from app.tasks.crawler_tasks import run_generic_script

router = APIRouter()


def _check_task_project_permission(
    db: Session,
    task_id: int,
    user: models.User
) -> None:
    """
    内部工具函数：检查用户是否有权操作该任务（通过 project.owner_id）
    如果无权，抛出 403
    """
    db_task = crud_task.get(db, id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_project = crud_project.get(db, id=db_task.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if db_project.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task"
        )


@router.post("/", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    创建任务：用户必须是目标项目的拥有者
    """
    # 检查项目是否存在
    project = crud_project.get(db, id=task_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 权限：必须是项目所有者
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create task for this project"
        )

    try:
        db_task = crud_task.create(db=db, obj_in=task_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 调度器：如果启用且有 cron 表达式
    if db_task.is_enabled and db_task.cron_expression:
        try:
            scheduler_service.add_task(db_task)
        except Exception as e:
            print(f"[WARNING] Failed to schedule task {db_task.id}: {str(e)}")

    return db_task


@router.get("/", response_model=List[schemas.TaskOut])
def read_tasks(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取当前用户有权限的任务列表（仅限自己项目下的任务）
    """
    # 获取当前用户的所有项目 ID
    user_projects = crud_project.get_multi_by_owner(db, owner_id=current_user.id)
    project_ids = [p.id for p in user_projects]

    if not project_ids:
        return []

    # 查询这些项目下的所有任务
    tasks = crud_task.get_multi_by_project_ids(db, project_ids=project_ids, skip=skip, limit=limit)
    return tasks


@router.get("/{task_id}", response_model=schemas.TaskOut)
def read_task(
    *,
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取单个任务：必须属于当前用户拥有的项目
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    return crud_task.get(db, id=task_id)


@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(
    *,
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    更新任务：先权限校验，再操作调度器和数据库
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    db_task = crud_task.get(db, id=task_id)  # 已确保存在

    # 1. 从调度器移除旧任务
    if scheduler_service.has_task(task_id):
        try:
            scheduler_service.remove_task(task_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove old task from scheduler: {str(e)}"
            )

    # 2. 更新数据库
    try:
        db_task = crud_task.update(db=db, db_obj=db_task, obj_in=task_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. 如果启用且有 cron，重新添加
    if db_task.is_enabled and db_task.cron_expression:
        try:
            scheduler_service.add_task(db_task)
        except Exception as e:
            print(f"[WARNING] Could not reschedule task {task_id}: {str(e)}")

    return db_task


@router.delete("/{task_id}", response_model=schemas.TaskOut)
def delete_task(
    *,
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    删除任务：需权限校验
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    db_task = crud_task.get(db, id=task_id)

    # 1. 从调度器移除
    if scheduler_service.has_task(task_id):
        try:
            scheduler_service.remove_task(task_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove task from scheduler: {str(e)}"
            )

    # 2. 删除数据库
    db_task = crud_task.remove(db=db, id=task_id)
    return db_task


@router.post("/{task_id}/toggle", response_model=schemas.TaskOut)
def toggle_task(
    *,
    task_id: int,
    enable: bool,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    启用/禁用任务：需权限校验
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    db_task = crud_task.get(db, id=task_id)

    was_enabled = db_task.is_enabled
    now_enabled = enable

    if was_enabled == now_enabled:
        return db_task

    try:
        # 操作调度器
        if now_enabled and db_task.cron_expression:
            scheduler_service.add_task(db_task)
        elif was_enabled:
            scheduler_service.remove_task(task_id)

        # 更新数据库
        db_task = crud_task.toggle_enable(db, id=task_id, enable=enable)
        return db_task

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Toggle failed: {str(e)}")


@router.post("/{task_id}/run", response_model=schemas.TaskRunOut)
def run_task_now(
    *,
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    立即执行任务：需权限校验
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    db_task = crud_task.get(db, id=task_id)
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 提交任务到 Celery 立即执行
    try:
        project_name = db_task.project.name
        entrypoint = db_task.entrypoint or "run.py"
        args = db_task.args or {}
        env = {"RUN_MODE": "manual"}
        
        celery_task = run_generic_script.delay(
            original_task_id=db_task.id,
            project_name=project_name,
            entrypoint=entrypoint,
            args=args,
            env=env
        )
        
        # 创建任务执行记录
        task_run_in = schemas.TaskRunCreate(
            task_id=task_id,
            celery_task_id=celery_task.id,
            worker_node="manual_trigger",
            status="PENDING"  # 添加必需的 status 字段
        )
        task_run = crud_task_run.create(db, obj_in=task_run_in)
        
        db.commit()
        return task_run
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run task: {str(e)}")


@router.get("/{task_id}/stats", response_model=dict)
def get_task_statistics(
    *,
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取任务统计信息：需权限校验
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    
    # 获取任务执行统计
    stmt = crud_task_run.select().where(crud_task_run.model.task_id == task_id)
    result = db.execute(stmt)
    runs = list(result.scalars().all())
    
    total_runs = len(runs)
    success_runs = len([r for r in runs if r.status == "SUCCESS"])
    failed_runs = len([r for r in runs if r.status == "FAILURE"])
    
    # 计算成功率
    success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0
    
    # 获取最近一次执行时间
    last_run_time = max([r.start_time for r in runs if r.start_time], default=None) if runs else None
    
    return {
        "task_id": task_id,
        "total_runs": total_runs,
        "success_runs": success_runs,
        "failed_runs": failed_runs,
        "success_rate": round(success_rate, 2),
        "last_run_time": last_run_time
    }


@router.get("/stats/overview", response_model=dict)
def get_tasks_overview_statistics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取任务概览统计信息：需权限校验
    """
    # 获取当前用户的所有项目
    stmt = crud_project.select().where(crud_project.model.owner_id == current_user.id)
    result = db.execute(stmt)
    user_projects = list(result.scalars().all())
    project_ids = [p.id for p in user_projects]
    
    if not project_ids:
        return {
            "total_projects": 0,
            "total_tasks": 0,
            "total_runs": 0,
            "success_rate": 0
        }
    
    # 获取任务统计
    stmt = crud_task.select().where(crud_task.model.project_id.in_(project_ids))
    result = db.execute(stmt)
    tasks = list(result.scalars().all())
    
    # 获取任务执行统计
    stmt = crud_task_run.select().where(crud_task_run.model.task_id.in_([t.id for t in tasks]))
    result = db.execute(stmt)
    runs = list(result.scalars().all())
    
    total_runs = len(runs)
    success_runs = len([r for r in runs if r.status == "SUCCESS"])
    success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0
    
    return {
        "total_projects": len(user_projects),
        "total_tasks": len(tasks),
        "total_runs": total_runs,
        "success_rate": round(success_rate, 2)
    }


@router.post("/{task_id}/dependencies", response_model=schemas.TaskOut)
def add_task_dependencies(
    *,
    task_id: int,
    dependency_ids: List[int],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    为任务添加依赖任务
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    
    # 检查依赖任务是否存在且属于同一用户
    for dep_id in dependency_ids:
        dep_task = crud_task.get(db, id=dep_id)
        if not dep_task:
            raise HTTPException(status_code=404, detail=f"Dependency task {dep_id} not found")
        # 检查依赖任务是否属于同一用户
        dep_project = crud_project.get(db, id=dep_task.project_id)
        if dep_project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail=f"Dependency task {dep_id} owned by user")
    
    # 更新任务依赖
    db_task = crud_task.get(db, id=task_id)
    task_update = schemas.TaskUpdate(dependency_task_ids=dependency_ids)
    updated_task = crud_task.update(db, db_obj=db_task, obj_in=task_update)
    
    return updated_task


@router.get("/{task_id}/dependencies", response_model=List[schemas.TaskOut])
def get_task_dependencies(
    *,
    task_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取任务的依赖任务列表
    """
    _check_task_project_permission(db, task_id=task_id, user=current_user)
    
    db_task = crud_task.get(db, id=task_id)
    if not db_task or not db_task.dependency_task_ids:
        return []
    
    # 获取依赖任务
    dependencies = []
    for dep_id in db_task.dependency_task_ids:
        dep_task = crud_task.get(db, id=dep_id)
        if dep_task:
            dependencies.append(dep_task)
            
    return dependencies