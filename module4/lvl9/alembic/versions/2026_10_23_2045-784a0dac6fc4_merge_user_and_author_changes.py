"""merge user and author changes

Revision ID: 784a0dac6fc4
Revises: 9ed060cbe071, f393050b5be8
Create Date: 2026-10-23 20:45:45.313500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '784a0dac6fc4'
down_revision: Union[str, Sequence[str], None] = ('9ed060cbe071', 'f393050b5be8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
