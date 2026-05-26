# alembic/versions/xxxx_seed_roles.py
from typing import Sequence, Union

from alembic import op


revision: str = "8efdf7ab94f2"
down_revision: Union[str, Sequence[str], None] = "a3a222683d17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO roles (title, description) VALUES
        ('USER', 'Regular user with basic permissions'),
        ('STAFF', 'Moderator or support staff'),
        ('SUPERUSER', 'Administrator with full access')
        ON CONFLICT DO NOTHING;
        """
    )


def downgrade() -> None:
    """Очищаем таблицу ролей при откате."""
    op.execute("DELETE FROM roles WHERE title IN ('USER', 'STAFF', 'SUPERUSER');")
