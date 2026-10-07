from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.recomendacion import Recomendacion
    from app.models.plato import Plato


class RecomendacionPlato(Base):
    __tablename__ = "recomendacion_plato"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_recomendacion_plato_cantidad_positiva"),
        CheckConstraint("subtotal >= 0", name="ck_recomendacion_plato_subtotal_no_negativo"),
    )

    id_recomendacion_plato: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    id_recomendacion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recomendacion.id_recomendacion", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_plato: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plato.id_plato", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Relaciones
    recomendacion: Mapped["Recomendacion"] = relationship("Recomendacion", back_populates="recomendacion_platos")
    plato: Mapped["Plato"] = relationship("Plato", back_populates="recomendacion_platos")

    def __repr__(self) -> str:
        return f"<RecomendacionPlato(id_recomendacion_plato={self.id_recomendacion_plato}, id_recomendacion={self.id_recomendacion}, id_plato={self.id_plato}, cantidad={self.cantidad})>"
