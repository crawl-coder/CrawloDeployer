"""make encrypted_token nullable

Revision ID: 41b339fc8672
Revises: ec234bb119cc
Create Date: 2025-09-14 21:28:32.639156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41b339fc8672'
down_revision: Union[str, Sequence[str], None] = 'ec234bb119cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 修改 encrypted_token 列，使其允许为空
    with op.batch_alter_table('git_credentials', schema=None) as batch_op:
        batch_op.alter_column('encrypted_token',
                              existing_type=sa.Text(),
                              nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # 恢复 encrypted_token 列为不允许为空
    with op.batch_alter_table('git_credentials', schema=None) as batch_op:
        batch_op.alter_column('encrypted_token',
                              existing_type=sa.Text(),
                              nullable=False)