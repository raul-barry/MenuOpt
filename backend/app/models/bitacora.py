from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Bitacora(Base):
    __tablename__ = "bitacora"

    id_bitacora: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    direccion_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    detalles: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Relación opcional con el usuario causante
    usuario: Mapped["Usuario | None"] = relationship("Usuario")
