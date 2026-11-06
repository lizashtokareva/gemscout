"""create gems table

Revision ID: 61c83eee2120
Revises:
Create Date: 2026-11-04 01:50:01.619067

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "61c83eee2120"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gems",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        # Остальные столбцы
    )


def downgrade() -> None:
    op.drop_table("gems")
