from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.plato import Plato
    from app.models.plato_ingrediente import PlatoIngrediente
    from app.models.ingrediente_lugar_compra import IngredienteLugarCompra


class Ingrediente(Base):
    __tablename__ = "ingrediente"
    __table_args__ = (
        CheckConstraint(
            "precio_estimado IS NULL OR precio_estimado >= 0",
            name="chk_ingrediente_precio_estimado_no_negativo"
        ),
    )

    id_ingrediente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    unidad_medida: Mapped[str] = mapped_column(String(50), nullable=False)
    precio_estimado: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO", nullable=False)

    # Relación N:M con Plato a través de PlatoIngrediente
    platos: Mapped[List["Plato"]] = relationship(
        "Plato",
        secondary="plato_ingrediente",
        back_populates="ingredientes",
        viewonly=True
    )

    # Relación 1:N con la entidad asociativa PlatoIngrediente
    plato_ingredientes: Mapped[List["PlatoIngrediente"]] = relationship(
        "PlatoIngrediente",
        back_populates="ingrediente",
        cascade="all, delete-orphan"
    )

    # Relación 1:N con IngredienteLugarCompra
    lugares_compra_rel: Mapped[List["IngredienteLugarCompra"]] = relationship(
        "IngredienteLugarCompra",
        back_populates="ingrediente",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ingrediente(id_ingrediente={self.id_ingrediente}, nombre='{self.nombre}', unidad='{self.unidad_medida}')>"

