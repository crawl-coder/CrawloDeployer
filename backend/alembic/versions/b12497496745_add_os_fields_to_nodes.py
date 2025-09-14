"""add_os_fields_to_nodes

Revision ID: b12497496745
Revises: 7ef483fed353
Create Date: 2025-09-13 22:41:38.092833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b12497496745'
down_revision: Union[str, Sequence[str], None] = '7ef483fed353'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 添加缺失的字段
    op.add_column('cp_nodes', sa.Column('os', sa.Enum('WINDOWS', 'LINUX', 'MACOS', 'UNKNOWN', name='node_os_enum'), nullable=False, server_default='UNKNOWN'))
    op.add_column('cp_nodes', sa.Column('os_version', sa.String(length=50), nullable=True, comment='操作系统版本，如 Windows 11, Ubuntu 20.04'))
    op.add_column('cp_nodes', sa.Column('cpu_usage', sa.Float(), nullable=True, comment='CPU 使用率 (%)'))
    op.add_column('cp_nodes', sa.Column('memory_usage', sa.Float(), nullable=True, comment='内存使用量（GB）'))
    op.add_column('cp_nodes', sa.Column('disk_usage', sa.Float(), nullable=True, comment='磁盘使用量（GB）'))
    op.add_column('cp_nodes', sa.Column('python_version', sa.String(length=20), nullable=True, comment='Python 版本'))
    op.add_column('cp_nodes', sa.Column('capabilities', sa.String(length=200), nullable=True, comment='节点能力（JSON 格式），如 {\'gpu\': true, \'browser\': \'chrome\'}'))
    op.add_column('cp_nodes', sa.Column('public_ip', sa.String(length=50), nullable=True, comment='公网 IP'))
    op.add_column('cp_nodes', sa.Column('agent_port', sa.Integer(), nullable=True, comment='Worker 通信端口'))


def downgrade() -> None:
    """Downgrade schema."""
    # 删除添加的字段
    op.drop_column('cp_nodes', 'agent_port')
    op.drop_column('cp_nodes', 'public_ip')
    op.drop_column('cp_nodes', 'capabilities')
    op.drop_column('cp_nodes', 'python_version')
    op.drop_column('cp_nodes', 'disk_usage')
    op.drop_column('cp_nodes', 'memory_usage')
    op.drop_column('cp_nodes', 'cpu_usage')
    op.drop_column('cp_nodes', 'os_version')
    op.drop_column('cp_nodes', 'os')