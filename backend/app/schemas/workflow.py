# /backend/app/schemas/workflow.py
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


# Task Dependency Schemas
class TaskDependencyBase(BaseModel):
    source_task_id: int
    target_task_id: int
    condition: Optional[str] = None


class TaskDependencyCreate(TaskDependencyBase):
    pass


class TaskDependencyUpdate(TaskDependencyBase):
    pass


class TaskDependencyInDBBase(TaskDependencyBase):
    id: int
    workflow_id: int

    class Config:
        from_attributes = True


# Workflow Task Schemas
class WorkflowTaskBase(BaseModel):
    task_id: int
    position_x: Optional[int] = 0
    position_y: Optional[int] = 0
    config: Optional[str] = None


class WorkflowTaskCreate(WorkflowTaskBase):
    pass


class WorkflowTaskUpdate(WorkflowTaskBase):
    pass


class WorkflowTaskInDBBase(WorkflowTaskBase):
    id: int
    workflow_id: int

    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowBase(BaseModel):
    name: str
    project_id: int
    description: Optional[str] = None
    status: Optional[str] = "enabled"
    concurrent: Optional[bool] = False
    failure_strategy: Optional[str] = "stop"


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    name: Optional[str] = None
    project_id: Optional[int] = None


class WorkflowInDBBase(WorkflowBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Workflow(WorkflowInDBBase):
    tasks: List[WorkflowTaskInDBBase] = []
    dependencies: List[TaskDependencyInDBBase] = []


class WorkflowListResponse(BaseModel):
    items: List[Workflow]
    total: int
    page: int
    size: int