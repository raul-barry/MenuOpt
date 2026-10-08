"""Crear registro de invitados por reserva.

Revision ID: 74c12e89a531
Revises: 24a8f9850af4
Create Date: 2026-10-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "74c12e89a531"
down_revision: Union[str, None] = "24a8f9850af4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reserva_invitado",
        sa.Column("id_invitado", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_reserva", sa.Integer(), nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=True),
        sa.Column("nombre", sa.String(length=201), nullable=False),
        sa.Column("correo", sa.String(length=150), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["id_reserva"], ["reserva.id_reserva"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id_usuario"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id_invitado"),
    )
    op.create_index("ix_reserva_invitado_id_reserva", "reserva_invitado", ["id_reserva"], unique=False)
    op.create_index("ix_reserva_invitado_id_usuario", "reserva_invitado", ["id_usuario"], unique=False)
    op.create_index(
        "ux_reserva_invitado_usuario",
        "reserva_invitado",
        ["id_reserva", "id_usuario"],
        unique=True,
        postgresql_where=sa.text("id_usuario IS NOT NULL"),
    )
    op.create_index(
        "ux_reserva_invitado_correo_ci",
        "reserva_invitado",
        ["id_reserva", sa.text("lower(correo)")],
        unique=True,
        postgresql_where=sa.text("correo IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ux_reserva_invitado_correo_ci", table_name="reserva_invitado")
    op.drop_index("ux_reserva_invitado_usuario", table_name="reserva_invitado")
    op.drop_index("ix_reserva_invitado_id_usuario", table_name="reserva_invitado")
    op.drop_index("ix_reserva_invitado_id_reserva", table_name="reserva_invitado")
    op.drop_table("reserva_invitado")
