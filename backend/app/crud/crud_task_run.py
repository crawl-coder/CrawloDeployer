# /app/crud/crud_task_run.py

from typing import Optional, List, cast

from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select
from app.crud.base import CRUDBase
from app.models.task_run import TaskRun, TaskRunStatus
from app.schemas.task_run import TaskRunCreate, TaskRunUpdate


class CRUDTaskRun(CRUDBase[TaskRun, TaskRunCreate, TaskRunUpdate]):
    def get_by_celery_id(self, db: Session, *, celery_task_id: str) -> Optional[TaskRun]:
        stmt = select(self.model).where(self.model.celery_task_id == celery_task_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def get_multi_by_task(self, db: Session, *, task_id: int, skip: int = 0, limit: int = 100) -> List[TaskRun]:
        """获取某个任务的所有执行记录（按时间倒序）"""
        stmt: Select[tuple[TaskRun]] = (
            select(self.model)
            .where(self.model.task_id == task_id)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.start_time.desc())
        )
        result = db.execute(stmt)
        return cast(List[TaskRun], result.scalars().all())

    def start_run(self, db: Session, *, task_id: int, celery_task_id: str, worker_node: str) -> TaskRun:
        db_obj = self.model(
            task_id=task_id,
            celery_task_id=celery_task_id,
            status=TaskRunStatus.RUNNING,
            start_time=func.now(),
            worker_node=worker_node
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def finish_run(self, db: Session, *, celery_task_id: str, status: TaskRunStatus, log_output: str = None) -> None:
        db_obj = self.get_by_celery_id(db, celery_task_id=celery_task_id)
        if not db_obj:
            return
        db_obj.status = status
        db_obj.end_time = func.now()
        db_obj.log_output = log_output
        db.commit()


task_run = CRUDTaskRun(TaskRun)