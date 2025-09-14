# /app/schemas/task.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.task import TaskPriority, TaskDistributionMode


class TaskBase(BaseModel):
    name: str
    project_id: int
    spider_name: str
    entrypoint: Optional[str] = "run.py"
    cron_expression: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    is_enabled: bool = True
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout_seconds: Optional[int] = 3600
    max_retries: int = 0
    notify_on_failure: bool = True
    notify_on_success: bool = False
    notification_emails: Optional[List[str]] = None
    
    # 节点绑定相关字段
    distribution_mode: TaskDistributionMode = TaskDistributionMode.ANY
    target_node_id: Optional[int] = None
    target_node_ids: Optional[List[int]] = None
    target_node_tags: Optional[str] = None


class TaskCreate(TaskBase):
    name: str
    project_id: int
    spider_name: str
    entrypoint: Optional[str] = "run.py"


class TaskUpdate(TaskBase):
    name: Optional[str] = None
    project_id: Optional[int] = None
    spider_name: Optional[str] = None
    entrypoint: Optional[str] = None
    cron_expression: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None
    priority: Optional[TaskPriority] = None
    timeout_seconds: Optional[int] = None
    max_retries: Optional[int] = None
    notify_on_failure: Optional[bool] = None
    notify_on_success: Optional[bool] = None
    notification_emails: Optional[List[str]] = None
    
    # 节点绑定相关字段
    distribution_mode: Optional[TaskDistributionMode] = None
    target_node_id: Optional[int] = None
    target_node_ids: Optional[List[int]] = None
    target_node_tags: Optional[str] = None


class TaskOut(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2