# CASO DE USO: CU15 - Consultar ingredientes para preparación propia
from decimal import Decimal
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.recomendacion import Recomendacion
    from app.models.preparacion_ingrediente import PreparacionIngrediente


class PreparacionPropia(Base):
    """
    Entidad que almacena los detalles de una alternativa gastronómica de preparación
    por cuenta propia del consumidor vinculada 1:1 a una recomendación de tipo PREPARACION_PROPIA.
    """
    __tablename__ = "preparacion_propia"
    __table_args__ = (
        CheckConstraint("costo_estimado >= 0", name="chk_preparacion_propia_costo_positivo"),
        CheckConstraint("cantidad_personas > 0", name="chk_preparacion_propia_personas_positiva"),
    )

    id_preparacion_propia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    costo_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cantidad_personas: Mapped[int] = mapped_column(Integer, nullable=False)
    id_recomendacion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recomendacion.id_recomendacion", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Relaciones
    recomendacion: Mapped["Recomendacion"] = relationship("Recomendacion", back_populates="preparacion_propia")
    ingredientes: Mapped[List["PreparacionIngrediente"]] = relationship(
        "PreparacionIngrediente",
        back_populates="preparacion_propia",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PreparacionPropia(id={self.id_preparacion_propia}, nombre='{self.nombre}', costo={self.costo_estimado}, personas={self.cantidad_personas})>"
