# /backend/app/models/workflow.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    project_id = Column(Integer, ForeignKey("cp_projects.id"), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="enabled")  # enabled, disabled
    concurrent = Column(Boolean, default=False)
    failure_strategy = Column(String(20), default="stop")  # stop, continue
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="workflows")
    tasks = relationship("WorkflowTask", back_populates="workflow")


class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("cp_tasks.id"), nullable=False)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    config = Column(Text)  # JSON configuration for the task in this workflow

    # Relationships
    workflow = relationship("Workflow", back_populates="tasks")
    task = relationship("Task", back_populates="workflow_tasks", foreign_keys=[task_id])


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    source_task_id = Column(Integer, ForeignKey("cp_tasks.id"), nullable=False)
    target_task_id = Column(Integer, ForeignKey("cp_tasks.id"), nullable=False)
    condition = Column(String(100))  # Optional condition for the dependency

    # Relationships
    workflow = relationship("Workflow")
    source_task = relationship("Task", foreign_keys=[source_task_id])
    target_task = relationship("Task", foreign_keys=[target_task_id])