from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.restaurante import Restaurante
    from app.models.lugar_compra import LugarCompra


class Ubicacion(Base):
    __tablename__ = "ubicacion"

    id_ubicacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    zona: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(11, 8), nullable=True)
    referencia: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relación 1:N con Restaurante
    restaurantes: Mapped[List["Restaurante"]] = relationship(
        "Restaurante",
        back_populates="ubicacion"
    )

    # Relación 1:N con LugarCompra
    lugares_compra: Mapped[List["LugarCompra"]] = relationship(
        "LugarCompra",
        back_populates="ubicacion"
    )

    def __repr__(self) -> str:
        return f"<Ubicacion(id_ubicacion={self.id_ubicacion}, ciudad='{self.ciudad}', direccion='{self.direccion}')>"
