from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.plato import Plato
    from app.models.ingrediente import Ingrediente


class PlatoIngrediente(Base):
    __tablename__ = "plato_ingrediente"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_plato_ingrediente_cantidad_mayor_cero"),
        UniqueConstraint("id_plato", "id_ingrediente", name="uq_plato_ingrediente"),
    )

    id_plato_ingrediente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String(50), nullable=False)
    id_plato: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plato.id_plato", ondelete="CASCADE"),
        nullable=False
    )
    id_ingrediente: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ingrediente.id_ingrediente", ondelete="RESTRICT"),
        nullable=False
    )

    # Relaciones
    plato: Mapped["Plato"] = relationship("Plato", back_populates="plato_ingredientes")
    ingrediente: Mapped["Ingrediente"] = relationship("Ingrediente", back_populates="plato_ingredientes")

    def __repr__(self) -> str:
        return f"<PlatoIngrediente(id_plato_ingrediente={self.id_plato_ingrediente}, plato={self.id_plato}, ingrediente={self.id_ingrediente}, cantidad={self.cantidad})>"
