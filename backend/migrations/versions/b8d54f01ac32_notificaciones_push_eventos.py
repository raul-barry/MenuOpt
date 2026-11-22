"""Registro de dispositivos FCM y outbox idempotente para eventos privados."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b8d54f01ac32"
down_revision: Union[str, Sequence[str], None] = "a91d2f6c4b30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dispositivo_push",
        sa.Column("id_dispositivo", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("id_instalacion", sa.String(80), nullable=False),
        sa.Column("token_fcm", sa.Text(), nullable=False),
        sa.Column("plataforma", sa.String(20), nullable=False, server_default="ANDROID"),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuario.id_usuario"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_dispositivo"),
        sa.UniqueConstraint("token_fcm", name="uq_dispositivo_push_token_fcm"),
        sa.UniqueConstraint("id_usuario", "id_instalacion", name="uq_dispositivo_push_usuario_instalacion"),
    )
    op.create_index("ix_dispositivo_push_id_usuario", "dispositivo_push", ["id_usuario"])
    op.create_table(
        "notificacion_outbox",
        sa.Column("id_notificacion", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("clave_evento", sa.String(120), nullable=False),
        sa.Column("id_usuario_destino", sa.Integer(), nullable=False),
        sa.Column("tipo_recurso", sa.String(20), nullable=False),
        sa.Column("id_recurso", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(120), nullable=False),
        sa.Column("cuerpo", sa.String(240), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="PENDIENTE"),
        sa.Column("intentos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_envio", sa.String(240), nullable=True),
        sa.Column("dispositivos_enviados", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("fecha_envio", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario_destino"], ["usuario.id_usuario"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_notificacion"),
        sa.UniqueConstraint("clave_evento", name="uq_notificacion_outbox_clave_evento"),
    )
    op.create_index("ix_notificacion_outbox_id_usuario_destino", "notificacion_outbox", ["id_usuario_destino"])
    op.create_index("ix_notificacion_outbox_estado", "notificacion_outbox", ["estado"])


def downgrade() -> None:
    op.drop_index("ix_notificacion_outbox_estado", table_name="notificacion_outbox")
    op.drop_index("ix_notificacion_outbox_id_usuario_destino", table_name="notificacion_outbox")
    op.drop_table("notificacion_outbox")
    op.drop_index("ix_dispositivo_push_id_usuario", table_name="dispositivo_push")
    op.drop_table("dispositivo_push")
