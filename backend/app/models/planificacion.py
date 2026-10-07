from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, ForeignKey, Numeric, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.preferencia import Preferencia
    from app.models.planificacion_preferencia import PlanificacionPreferencia
    from app.models.recomendacion import Recomendacion
    from app.models.reserva import Reserva


class Planificacion(Base):
    __tablename__ = "planificacion"
    __table_args__ = (
        CheckConstraint("presupuesto > 0", name="ck_planificacion_presupuesto_positivo"),
        CheckConstraint("cantidad_personas > 0", name="ck_planificacion_personas_positivo"),
    )

    id_planificacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    presupuesto: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cantidad_personas: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_comida: Mapped[str] = mapped_column(String(50), nullable=False)
    ubicacion_referencia: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_planificacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVA", nullable=False)
    id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relaciones
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="planificaciones")
    preferencias: Mapped[List["Preferencia"]] = relationship(
        "Preferencia",
        secondary="planificacion_preferencia",
        back_populates="planificaciones",
        viewonly=True
    )
    planificacion_preferencias: Mapped[List["PlanificacionPreferencia"]] = relationship(
        "PlanificacionPreferencia",
        back_populates="planificacion",
        cascade="all, delete-orphan"
    )
    recomendaciones: Mapped[List["Recomendacion"]] = relationship(
        "Recomendacion",
        back_populates="planificacion",
        cascade="all, delete-orphan"
    )
    reservas: Mapped[List["Reserva"]] = relationship(
        "Reserva",
        back_populates="planificacion"
    )

    def __repr__(self) -> str:
        return f"<Planificacion(id_planificacion={self.id_planificacion}, presupuesto={self.presupuesto}, estado='{self.estado}')>"
