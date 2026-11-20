"""Agregar URL de imagen a restaurantes y platos."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a91d2f6c4b30"
down_revision: Union[str, None] = "9c4e7b2a1d60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("restaurante", sa.Column("imagen_url", sa.String(length=500), nullable=True))
    op.add_column("plato", sa.Column("imagen_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("plato", "imagen_url")
    op.drop_column("restaurante", "imagen_url")
