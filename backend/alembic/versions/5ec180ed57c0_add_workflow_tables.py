"""add_workflow_tables

Revision ID: 5ec180ed57c0
Revises: 20250914_add_task_node_binding_fields
Create Date: 2025-09-15 21:18:48.967886

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ec180ed57c0'
down_revision: Union[str, Sequence[str], None] = '20250914_add_task_node_binding_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create workflows table
    op.create_table('workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('concurrent', sa.Boolean(), nullable=True),
        sa.Column('failure_strategy', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['cp_projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_id'), 'workflows', ['id'], unique=False)
    
    # Create workflow_tasks table
    op.create_table('workflow_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('position_x', sa.Integer(), nullable=True),
        sa.Column('position_y', sa.Integer(), nullable=True),
        sa.Column('config', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['cp_tasks.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_tasks_id'), 'workflow_tasks', ['id'], unique=False)
    
    # Create task_dependencies table
    op.create_table('task_dependencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('source_task_id', sa.Integer(), nullable=False),
        sa.Column('target_task_id', sa.Integer(), nullable=False),
        sa.Column('condition', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['source_task_id'], ['cp_tasks.id'], ),
        sa.ForeignKeyConstraint(['target_task_id'], ['cp_tasks.id'], ),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_dependencies_id'), 'task_dependencies', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop task_dependencies table
    op.drop_index(op.f('ix_task_dependencies_id'), table_name='task_dependencies')
    op.drop_table('task_dependencies')
    
    # Drop workflow_tasks table
    op.drop_index(op.f('ix_workflow_tasks_id'), table_name='workflow_tasks')
    op.drop_table('workflow_tasks')
    
    # Drop workflows table
    op.drop_index(op.f('ix_workflows_id'), table_name='workflows')
    op.drop_table('workflows')
