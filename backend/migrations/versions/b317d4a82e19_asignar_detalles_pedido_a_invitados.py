"""Asignar detalles de pedido a invitados de reserva.

Revision ID: b317d4a82e19
Revises: 74c12e89a531
Create Date: 2026-10-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b317d4a82e19"
down_revision: Union[str, None] = "74c12e89a531"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("detalle_pedido", sa.Column("id_invitado", sa.Integer(), nullable=True))
    op.create_index("ix_detalle_pedido_id_invitado", "detalle_pedido", ["id_invitado"], unique=False)
    op.create_foreign_key(
        "fk_detalle_pedido_id_invitado_reserva_invitado",
        "detalle_pedido",
        "reserva_invitado",
        ["id_invitado"],
        ["id_invitado"],
        ondelete="RESTRICT",
    )
    op.drop_constraint("uq_detalle_pedido_plato", "detalle_pedido", type_="unique")
    op.create_unique_constraint(
        "uq_detalle_pedido_plato_invitado",
        "detalle_pedido",
        ["id_pedido", "id_plato", "id_invitado"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_detalle_pedido_plato_invitado", "detalle_pedido", type_="unique")
    op.create_unique_constraint(
        "uq_detalle_pedido_plato",
        "detalle_pedido",
        ["id_pedido", "id_plato"],
    )
    op.drop_constraint(
        "fk_detalle_pedido_id_invitado_reserva_invitado",
        "detalle_pedido",
        type_="foreignkey",
    )
    op.drop_index("ix_detalle_pedido_id_invitado", table_name="detalle_pedido")
    op.drop_column("detalle_pedido", "id_invitado")
