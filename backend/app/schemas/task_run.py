# /app/schemas/task_run.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class TaskRunBase(BaseModel):
    task_id: int
    celery_task_id: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    log_output: Optional[str] = None
    worker_node: Optional[str] = None
    exit_code: Optional[int] = None
    cpu_usage: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    duration_seconds: Optional[float] = None
    items_scraped: Optional[int] = None
    requests_count: Optional[int] = None
    result_size_mb: Optional[float] = None
    manually_stopped: bool = False
    node_id: Optional[int] = None


class TaskRunCreate(TaskRunBase):
    pass


class TaskRunUpdate(TaskRunBase):
    task_id: Optional[int] = None
    celery_task_id: Optional[str] = None
    status: Optional[str] = None


class TaskRunOut(TaskRunBase):
    id: int
    start_time: Optional[datetime] = None  # 修改为可选

    class Config:
        from_attributes = True


class TaskRunLog(BaseModel):
    id: int
    log_content: str

    class Config:
        from_attributes = True


class TaskRunExport(BaseModel):
    run_id: int
    format: str
    data: Dict[str, Any]

    class Config:
        from_attributes = True