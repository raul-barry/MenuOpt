from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.planificacion import Planificacion
    from app.models.preferencia import Preferencia


class PlanificacionPreferencia(Base):
    __tablename__ = "planificacion_preferencia"
    __table_args__ = (
        UniqueConstraint("id_planificacion", "id_preferencia", name="uq_planificacion_preferencia"),
    )

    id_planificacion_preferencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_planificacion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("planificacion.id_planificacion", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_preferencia: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("preferencia.id_preferencia", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Relaciones hacia Planificacion y Preferencia
    planificacion: Mapped["Planificacion"] = relationship("Planificacion", back_populates="planificacion_preferencias")
    preferencia: Mapped["Preferencia"] = relationship("Preferencia", back_populates="planificacion_preferencias")

    def __repr__(self) -> str:
        return f"<PlanificacionPreferencia(id_planificacion_preferencia={self.id_planificacion_preferencia}, id_planificacion={self.id_planificacion}, id_preferencia={self.id_preferencia})>"
