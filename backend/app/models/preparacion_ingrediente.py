# CASO DE USO: CU15 - Consultar ingredientes para preparación propia
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.preparacion_propia import PreparacionPropia
    from app.models.ingrediente import Ingrediente
    from app.models.lugar_compra import LugarCompra


class PreparacionIngrediente(Base):
    """
    Entidad que detalla los insumos calculados para una preparación propia,
    incluyendo cantidad escalada, unidad, costo estimado y el establecimiento de compra seleccionado.
    """
    __tablename__ = "preparacion_ingrediente"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_preparacion_ingrediente_cant_positiva"),
        CheckConstraint("costo_estimado >= 0", name="chk_preparacion_ingrediente_costo_positivo"),
    )

    id_preparacion_ingrediente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String(50), nullable=False)
    costo_estimado: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    precio_unitario_usado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    id_preparacion_propia: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("preparacion_propia.id_preparacion_propia", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_ingrediente: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ingrediente.id_ingrediente", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    id_lugar_compra: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("lugar_compra.id_lugar_compra", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relaciones
    preparacion_propia: Mapped["PreparacionPropia"] = relationship("PreparacionPropia", back_populates="ingredientes")
    ingrediente: Mapped["Ingrediente"] = relationship("Ingrediente")
    lugar_compra: Mapped[Optional["LugarCompra"]] = relationship("LugarCompra", back_populates="preparacion_ingredientes")

    def __repr__(self) -> str:
        return f"<PreparacionIngrediente(id={self.id_preparacion_ingrediente}, ing={self.id_ingrediente}, cant={self.cantidad} {self.unidad_medida}, costo={self.costo_estimado})>"
