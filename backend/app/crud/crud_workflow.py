# /backend/app/crud/crud_workflow.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.workflow import Workflow, WorkflowTask, TaskDependency
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowTaskCreate, WorkflowTaskUpdate, TaskDependencyCreate, TaskDependencyUpdate


class CRUDWorkflow(CRUDBase[Workflow, WorkflowCreate, WorkflowUpdate]):
    def get_multi_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Workflow]:
        return db.query(self.model).filter(self.model.project_id == project_id).offset(skip).limit(limit).all()

    def get_by_name_and_project(
        self, db: Session, *, name: str, project_id: int
    ) -> Optional[Workflow]:
        return db.query(self.model).filter(self.model.name == name, self.model.project_id == project_id).first()


class CRUDWorkflowTask(CRUDBase[WorkflowTask, WorkflowTaskCreate, WorkflowTaskUpdate]):
    pass


class CRUDTaskDependency(CRUDBase[TaskDependency, TaskDependencyCreate, TaskDependencyUpdate]):
    def get_by_workflow(self, db: Session, *, workflow_id: int) -> List[TaskDependency]:
        return db.query(self.model).filter(self.model.workflow_id == workflow_id).all()


workflow = CRUDWorkflow(Workflow)
workflow_task = CRUDWorkflowTask(WorkflowTask)
task_dependency = CRUDTaskDependency(TaskDependency)