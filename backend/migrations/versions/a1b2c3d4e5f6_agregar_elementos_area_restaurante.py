"""Agregar columna elementos a area_restaurante para espacios y puntos de interes del plano.

Revision ID: a1b2c3d4e5f6
Revises: f2c8d1e4a3b7
Create Date: 2026-11-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f2c8d1e4a3b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "area_restaurante",
        sa.Column("elementos", sa.Text(), nullable=True, server_default="[]")
    )


def downgrade() -> None:
    op.drop_column("area_restaurante", "elementos")
