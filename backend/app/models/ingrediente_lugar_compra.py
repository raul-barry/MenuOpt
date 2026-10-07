# CASO DE USO: CU16 - Consultar lugares de compra
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.ingrediente import Ingrediente
    from app.models.lugar_compra import LugarCompra


class IngredienteLugarCompra(Base):
    """
    Entidad asociativa N:M entre Ingrediente y LugarCompra.
    Registra el precio comercial, disponibilidad, cantidad y unidad de referencia.
    """
    __tablename__ = "ingrediente_lugar_compra"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="chk_ingrediente_lugar_precio_positivo"),
        CheckConstraint("cantidad_referencia > 0", name="chk_ingrediente_lugar_cant_ref_positiva"),
        UniqueConstraint("id_ingrediente", "id_lugar_compra", name="uq_ingrediente_lugar_compra"),
    )

    id_ingrediente_lugar_compra: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cantidad_referencia: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"), nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String(50), nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    id_ingrediente: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ingrediente.id_ingrediente", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_lugar_compra: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lugar_compra.id_lugar_compra", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relaciones
    ingrediente: Mapped["Ingrediente"] = relationship("Ingrediente", back_populates="lugares_compra_rel")
    lugar_compra: Mapped["LugarCompra"] = relationship("LugarCompra", back_populates="ingrediente_lugares")

    def __repr__(self) -> str:
        return f"<IngredienteLugarCompra(id={self.id_ingrediente_lugar_compra}, ing={self.id_ingrediente}, lugar={self.id_lugar_compra}, precio={self.precio} Bs/{self.cantidad_referencia} {self.unidad_medida})>"
