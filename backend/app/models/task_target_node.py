# /app/models/task_target_node.py
"""任务与目标节点关联表"""

from sqlalchemy import Column, Integer, ForeignKey, Table
from app.db.base_class import Base


# 任务与目标节点多对多关联表
task_target_nodes = Table(
    "cp_task_target_nodes",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("cp_tasks.id"), primary_key=True),
    Column("node_id", Integer, ForeignKey("cp_nodes.id"), primary_key=True)
)