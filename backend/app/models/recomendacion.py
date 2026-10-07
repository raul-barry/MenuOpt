from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, ForeignKey, Numeric, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.planificacion import Planificacion
    from app.models.restaurante import Restaurante
    from app.models.recomendacion_plato import RecomendacionPlato
    from app.models.preparacion_propia import PreparacionPropia


class Recomendacion(Base):
    __tablename__ = "recomendacion"
    __table_args__ = (
        CheckConstraint("costo_estimado >= 0", name="ck_recomendacion_costo_estimado_positivo"),
        CheckConstraint("costo_por_persona >= 0", name="ck_recomendacion_costo_persona_positivo"),
        CheckConstraint("puntuacion >= 0 AND puntuacion <= 100", name="ck_recomendacion_puntuacion_rango"),
    )

    id_recomendacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_recomendacion: Mapped[str] = mapped_column(String(50), default="RESTAURANTE", nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    costo_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    costo_por_persona: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    puntuacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    distancia_estimada: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    id_planificacion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("planificacion.id_planificacion", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_restaurante: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("restaurante.id_restaurante", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relaciones
    planificacion: Mapped["Planificacion"] = relationship("Planificacion", back_populates="recomendaciones")
    restaurante: Mapped[Optional["Restaurante"]] = relationship("Restaurante", back_populates="recomendaciones")
    recomendacion_platos: Mapped[List["RecomendacionPlato"]] = relationship(
        "RecomendacionPlato",
        back_populates="recomendacion",
        cascade="all, delete-orphan"
    )
    preparacion_propia: Mapped[Optional["PreparacionPropia"]] = relationship(
        "PreparacionPropia",
        back_populates="recomendacion",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Recomendacion(id_recomendacion={self.id_recomendacion}, tipo='{self.tipo_recomendacion}', costo={self.costo_estimado}, puntaje={self.puntuacion})>"
