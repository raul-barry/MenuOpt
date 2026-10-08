from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.reserva import Reserva
    from app.models.usuario import Usuario


class ReservaInvitado(Base):
    __tablename__ = "reserva_invitado"

    id_invitado: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_reserva: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reserva.id_reserva", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id_usuario: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(201), nullable=False)
    correo: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index(
            "ux_reserva_invitado_usuario",
            "id_reserva",
            "id_usuario",
            unique=True,
            postgresql_where=id_usuario.is_not(None),
        ),
        Index(
            "ux_reserva_invitado_correo_ci",
            "id_reserva",
            func.lower(correo),
            unique=True,
            postgresql_where=correo.is_not(None),
        ),
    )

    reserva: Mapped["Reserva"] = relationship("Reserva", back_populates="invitados")
    usuario: Mapped[Optional["Usuario"]] = relationship("Usuario")
