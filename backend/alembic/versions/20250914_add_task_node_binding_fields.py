"""add task node binding fields

Revision ID: 20250914_add_task_node_binding_fields
Revises: 9e86d90edd43
Create Date: 2025-09-14 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '20250914_add_task_node_binding_fields'
down_revision: Union[str, Sequence[str], None] = '9e86d90edd43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建任务与目标节点关联表
    op.create_table('cp_task_target_nodes',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['node_id'], ['cp_nodes.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['cp_tasks.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'node_id')
    )
    
    # 为cp_tasks表添加新字段
    with op.batch_alter_table('cp_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('distribution_mode', sa.Enum('ANY', 'SPECIFIC', 'MULTIPLE', 'TAG_BASED', name='task_distribution_mode_enum'), nullable=True, comment='任务分发模式'))
        batch_op.add_column(sa.Column('target_node_id', sa.Integer(), nullable=True, comment='目标节点ID'))
        batch_op.add_column(sa.Column('target_node_ids', sa.JSON(), nullable=True, comment='目标节点ID列表'))
        batch_op.add_column(sa.Column('target_node_tags', sa.String(length=100), nullable=True, comment='目标节点标签'))
        batch_op.create_foreign_key('fk_task_target_node', 'cp_nodes', ['target_node_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # 删除cp_tasks表中的新字段
    with op.batch_alter_table('cp_tasks', schema=None) as batch_op:
        batch_op.drop_constraint('fk_task_target_node', type_='foreignkey')
        batch_op.drop_column('target_node_tags')
        batch_op.drop_column('target_node_ids')
        batch_op.drop_column('target_node_id')
        batch_op.drop_column('distribution_mode')
    
    # 删除任务与目标节点关联表
    op.drop_table('cp_task_target_nodes')
    
    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS task_distribution_mode_enum")