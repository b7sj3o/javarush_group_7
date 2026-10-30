"""phone number nullable

Revision ID: 62a6a1076bd8
Revises: 784a0dac6fc4
Create Date: 2026-10-30 18:06:53.746520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62a6a1076bd8'
down_revision: Union[str, Sequence[str], None] = '784a0dac6fc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Після L7 колонка NOT NULL із server_default '', а реєстрація телефон не передає:
    # SQLAlchemy шле NULL, і POST /users падає з NotNullViolationError. Робимо телефон необов'язковим.
    op.alter_column('users', 'phone_number',
               existing_type=sa.VARCHAR(length=15),
               nullable=True,
               server_default=None)
    # Порожній рядок означав «телефону немає»; тепер це NULL (і UNIQUE не сваритиметься на два '')
    op.execute("UPDATE users SET phone_number = NULL WHERE phone_number = ''")


def downgrade() -> None:
    """Downgrade schema."""
    # Падає на UNIQUE, якщо без телефону більше одного користувача: так було влаштовано до цієї міграції
    op.execute("UPDATE users SET phone_number = '' WHERE phone_number IS NULL")
    op.alter_column('users', 'phone_number',
               existing_type=sa.VARCHAR(length=15),
               nullable=False,
               server_default=sa.text("''"))
