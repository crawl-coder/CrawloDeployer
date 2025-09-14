"""merge heads

Revision ID: ec234bb119cc
Revises: 20250914_add_ssh_key_support_to_git_credentials, dfccaf7f6751
Create Date: 2025-09-14 21:05:06.143816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec234bb119cc'
down_revision: Union[str, Sequence[str], None] = ('20250914_add_ssh_key_support_to_git_credentials', 'dfccaf7f6751')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
