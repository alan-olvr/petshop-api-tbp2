"""adiciona dose em aplicacoes_vacinas

Revision ID: 42c06d3c2c21
Revises: fa3221c90c2d
Create Date: 2026-11-24 17:25:28.518599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42c06d3c2c21'
down_revision: Union[str, Sequence[str], None] = 'fa3221c90c2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('aplicacoes_vacinas', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('dose', sa.Integer(), server_default=sa.text('1'), nullable=False)
        )
        batch_op.create_unique_constraint(
            op.f('uq_aplicacoes_vacinas_animal_vacina_dose'),
            ['animal_id', 'vacina_id', 'dose'],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('aplicacoes_vacinas', schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f('uq_aplicacoes_vacinas_animal_vacina_dose'), type_='unique'
        )
        batch_op.drop_column('dose')