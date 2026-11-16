"""Agregar id_usuario_responsable a lugar_compra para CU09 Administrador de Tienda.

Revision ID: f2c8d1e4a3b7
Revises: e5a9c812d47b
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2c8d1e4a3b7"
down_revision: Union[str, None] = "e5a9c812d47b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lugar_compra", sa.Column("id_usuario_responsable", sa.Integer(), nullable=True))
    op.create_index("ix_lugar_compra_id_usuario_responsable", "lugar_compra", ["id_usuario_responsable"], unique=False)
    op.create_foreign_key(
        "fk_lugar_compra_id_usuario_responsable_usuario",
        "lugar_compra",
        "usuario",
        ["id_usuario_responsable"],
        ["id_usuario"],
        ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("fk_lugar_compra_id_usuario_responsable_usuario", "lugar_compra", type_="foreignkey")
    op.drop_index("ix_lugar_compra_id_usuario_responsable", table_name="lugar_compra")
    op.drop_column("lugar_compra", "id_usuario_responsable")
