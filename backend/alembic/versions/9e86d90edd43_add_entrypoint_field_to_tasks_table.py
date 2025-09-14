"""add entrypoint field to tasks table

Revision ID: 9e86d90edd43
Revises: 41b339fc8672
Create Date: 2025-09-14 21:42:27.586589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e86d90edd43'
down_revision: Union[str, Sequence[str], None] = '41b339fc8672'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 添加 entrypoint 字段到 cp_tasks 表
    with op.batch_alter_table('cp_tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('entrypoint', sa.String(length=100), nullable=True, default='run.py', comment='入口脚本'))


def downgrade() -> None:
    """Downgrade schema."""
    # 删除 entrypoint 字段
    with op.batch_alter_table('cp_tasks', schema=None) as batch_op:
        batch_op.drop_column('entrypoint')