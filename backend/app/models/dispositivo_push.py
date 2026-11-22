from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class DispositivoPush(Base):
    __tablename__ = "dispositivo_push"
    __table_args__ = (UniqueConstraint("id_usuario", "id_instalacion", name="uq_dispositivo_push_usuario_instalacion"),)

    id_dispositivo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False, index=True
    )
    id_instalacion: Mapped[str] = mapped_column(String(80), nullable=False)
    token_fcm: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    plataforma: Mapped[str] = mapped_column(String(20), nullable=False, default="ANDROID")
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class NotificacionOutbox(Base):
    __tablename__ = "notificacion_outbox"

    id_notificacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clave_evento: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    id_usuario_destino: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_recurso: Mapped[str] = mapped_column(String(20), nullable=False)
    id_recurso: Mapped[int] = mapped_column(Integer, nullable=False)
    titulo: Mapped[str] = mapped_column(String(120), nullable=False)
    cuerpo: Mapped[str] = mapped_column(String(240), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE", index=True)
    intentos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_envio: Mapped[str | None] = mapped_column(String(240), nullable=True)
    dispositivos_enviados: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_envio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
