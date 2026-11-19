"""Crear las tablas de la biblioteca de recetas.

Revision ID: f7a2c91d6e40
Revises: e5a9c812d47b
Create Date: 2026-11-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7a2c91d6e40"
down_revision: Union[str, None] = "e5a9c812d47b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "receta",
        sa.Column("id_receta", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("instrucciones", sa.Text(), nullable=True),
        sa.Column("tipo_comida", sa.String(length=50), nullable=False),
        sa.Column("porciones", sa.Integer(), nullable=False),
        sa.Column("tiempo_minutos", sa.Integer(), nullable=False),
        sa.Column("dificultad", sa.String(length=50), nullable=False),
        sa.Column("origen", sa.String(length=100), nullable=True),
        sa.Column("imagen_url", sa.String(length=255), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id_usuario_creador", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_usuario_creador"], ["usuario.id_usuario"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id_receta"),
    )
    op.create_index("ix_receta_nombre", "receta", ["nombre"], unique=False)

    op.create_table(
        "receta_ingrediente",
        sa.Column("id_receta_ingrediente", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_receta", sa.Integer(), nullable=False),
        sa.Column("id_ingrediente", sa.Integer(), nullable=True),
        sa.Column("nombre_ingrediente", sa.String(length=100), nullable=False),
        sa.Column("cantidad", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unidad_medida", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["id_receta"], ["receta.id_receta"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id_ingrediente"], ["ingrediente.id_ingrediente"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id_receta_ingrediente"),
    )
    op.create_index("ix_receta_ingrediente_id_receta", "receta_ingrediente", ["id_receta"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_receta_ingrediente_id_receta", table_name="receta_ingrediente")
    op.drop_table("receta_ingrediente")
    op.drop_index("ix_receta_nombre", table_name="receta")
    op.drop_table("receta")
