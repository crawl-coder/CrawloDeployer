# /app/models/task.py
from typing import Optional, List
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, func, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
# 使用字符串引用避免循环导入
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task_run import TaskRun, TaskRunStatus
    from app.models.node import Node
else:
    Project = "Project"
    TaskRun = "TaskRun"
    TaskRunStatus = "TaskRunStatus"
    Node = "Node"


class TaskPriority(str, PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TaskDistributionMode(str, PyEnum):
    """任务分发模式"""
    ANY = "ANY"  # 任意节点
    SPECIFIC = "SPECIFIC"  # 指定单个节点
    MULTIPLE = "MULTIPLE"  # 指定多个节点
    TAG_BASED = "TAG_BASED"  # 基于标签分发

class Task(Base):
    __tablename__ = "cp_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("cp_projects.id"), nullable=False)
    spider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    cron_expression: Mapped[Optional[str]] = mapped_column(String(50), comment="CRON表达式")
    args: Mapped[Optional[dict]] = mapped_column(JSON, comment="执行参数")
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # ✅ 新增字段
    entrypoint: Mapped[Optional[str]] = mapped_column(String(100), default="run.py", comment="入口脚本")
    priority: Mapped[TaskPriority] = mapped_column(
        SqlEnum(TaskPriority, name="task_priority_enum"),
        default=TaskPriority.MEDIUM
    )
    timeout_seconds: Mapped[Optional[int]] = mapped_column(Integer, default=3600, comment="任务超时时间")
    max_retries: Mapped[int] = mapped_column(Integer, default=0, comment="失败后最大重试次数")
    notify_on_failure: Mapped[bool] = mapped_column(Boolean, default=True, comment="失败时通知")
    notify_on_success: Mapped[bool] = mapped_column(Boolean, default=False, comment="成功时通知")
    notification_emails: Mapped[Optional[list]] = mapped_column(JSON, comment="通知邮箱列表")
    last_run_status: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="最近一次执行状态"
    )
    last_run_time: Mapped[Optional[DateTime]] = mapped_column(DateTime, comment="最近一次执行时间")
    
    # ✅ 任务依赖关系
    parent_task_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cp_tasks.id"), nullable=True, comment="父任务ID")
    # 依赖任务列表（当前任务依赖的其他任务）
    dependency_task_ids: Mapped[Optional[list]] = mapped_column(JSON, comment="依赖任务ID列表")
    
    # ✅ 节点绑定相关字段
    distribution_mode: Mapped[TaskDistributionMode] = mapped_column(
        SqlEnum(TaskDistributionMode, name="task_distribution_mode_enum"),
        default=TaskDistributionMode.ANY,
        comment="任务分发模式"
    )
    # 指定单个节点时使用
    target_node_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("cp_nodes.id"), nullable=True, comment="目标节点ID")
    # 指定多个节点时使用
    target_node_ids: Mapped[Optional[list]] = mapped_column(JSON, comment="目标节点ID列表")
    # 基于标签分发时使用
    target_node_tags: Mapped[Optional[str]] = mapped_column(String(100), comment="目标节点标签")
    
    # ✅ 节点绑定关系
    target_node: Mapped[Optional["Node"]] = relationship("Node", foreign_keys=[target_node_id])

    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    runs: Mapped[List["TaskRun"]] = relationship("TaskRun", back_populates="task", cascade="all, delete-orphan")
    # 自引用关系
    parent_task: Mapped["Task"] = relationship("Task", remote_side=[id], back_populates="child_tasks")
    child_tasks: Mapped[List["Task"]] = relationship("Task", back_populates="parent_task")
    # 工作流关系
    workflow_tasks: Mapped[List["WorkflowTask"]] = relationship("WorkflowTask", back_populates="task", cascade="all, delete-orphan", primaryjoin="Task.id==WorkflowTask.task_id")