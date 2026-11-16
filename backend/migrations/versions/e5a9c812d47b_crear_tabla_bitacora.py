"""Crear tabla bitacora para auditoria del sistema (CU25).

Revision ID: e5a9c812d47b
Revises: b317d4a82e19
Create Date: 2026-11-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5a9c812d47b"
down_revision: Union[str, None] = "b317d4a82e19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bitacora",
        sa.Column("id_bitacora", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=True),
        sa.Column("accion", sa.String(length=100), nullable=False),
        sa.Column("modulo", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("direccion_ip", sa.String(length=45), nullable=True),
        sa.Column("detalles", sa.JSON(), nullable=True),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_usuario"],
            ["usuario.id_usuario"],
            name="fk_bitacora_id_usuario_usuario",
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id_bitacora", name="pk_bitacora")
    )
    op.create_index("ix_bitacora_id_usuario", "bitacora", ["id_usuario"], unique=False)
    op.create_index("ix_bitacora_accion", "bitacora", ["accion"], unique=False)
    op.create_index("ix_bitacora_modulo", "bitacora", ["modulo"], unique=False)
    op.create_index("ix_bitacora_fecha_hora", "bitacora", ["fecha_hora"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bitacora_fecha_hora", table_name="bitacora")
    op.drop_index("ix_bitacora_modulo", table_name="bitacora")
    op.drop_index("ix_bitacora_accion", table_name="bitacora")
    op.drop_index("ix_bitacora_id_usuario", table_name="bitacora")
    op.drop_table("bitacora")
