# CASO DE USO: CU21 - Realizar reserva & CU22 - Gestionar reservas
from datetime import datetime, date, time
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, String, Text, Date, Time, DateTime,
    ForeignKey, func, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.restaurante import Restaurante
    from app.models.planificacion import Planificacion
    from app.models.mesa import Mesa
    from app.models.mesa_reserva import MesaReserva
    from app.models.pedido import Pedido
    from app.models.reserva_invitado import ReservaInvitado


class Reserva(Base):
    __tablename__ = "reserva"

    id_reserva: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_reserva: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    cantidad_personas: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="CONFIRMADA", nullable=False, index=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_restaurante: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("restaurante.id_restaurante", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_planificacion: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("planificacion.id_planificacion", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("hora_fin > hora_inicio", name="ck_reserva_horas"),
        CheckConstraint("cantidad_personas > 0", name="ck_reserva_personas_positivas"),
        Index("ix_reserva_consulta", "id_restaurante", "fecha_reserva", "estado"),
    )

    # Relaciones
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="reservas")
    restaurante: Mapped["Restaurante"] = relationship("Restaurante", back_populates="reservas")
    planificacion: Mapped[Optional["Planificacion"]] = relationship("Planificacion", back_populates="reservas")
    
    mesas: Mapped[List["Mesa"]] = relationship(
        "Mesa",
        secondary="mesa_reserva",
        back_populates="reservas",
        overlaps="mesas_reservadas"
    )
    mesas_reservadas: Mapped[List["MesaReserva"]] = relationship(
        "MesaReserva",
        back_populates="reserva",
        cascade="all, delete-orphan",
        overlaps="mesas,reservas"
    )
    pedidos: Mapped[List["Pedido"]] = relationship(
        "Pedido",
        back_populates="reserva"
    )
    invitados: Mapped[List["ReservaInvitado"]] = relationship(
        "ReservaInvitado",
        back_populates="reserva",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Reserva(id={self.id_reserva}, resto={self.id_restaurante}, fecha={self.fecha_reserva}, {self.hora_inicio}-{self.hora_fin}, estado='{self.estado}')>"
