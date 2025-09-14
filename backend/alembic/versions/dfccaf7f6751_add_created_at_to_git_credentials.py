"""add_created_at_to_git_credentials

Revision ID: dfccaf7f6751
Revises: 7b01d2f1cd2d
Create Date: 2025-09-14 09:24:56.233717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfccaf7f6751'
down_revision: Union[str, Sequence[str], None] = '7b01d2f1cd2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('git_credentials', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('git_credentials', 'created_at')
