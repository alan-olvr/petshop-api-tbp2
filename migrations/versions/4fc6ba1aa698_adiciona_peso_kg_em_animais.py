"""adiciona peso_kg em animais

Revision ID: 4fc6ba1aa698
Revises: f7f48720bb6e
Create Date: 2026-11-23 10:50:43.015624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fc6ba1aa698'
down_revision: Union[str, Sequence[str], None] = 'f7f48720bb6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("animais") as batch_op:
        batch_op.add_column(sa.Column("peso_kg", sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("animais") as batch_op:
        batch_op.drop_column("peso_kg")
