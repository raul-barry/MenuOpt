from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.plato import Plato


class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relación 1:N con Plato
    platos: Mapped[List["Plato"]] = relationship(
        "Plato",
        back_populates="categoria"
    )

    def __repr__(self) -> str:
        return f"<Categoria(id_categoria={self.id_categoria}, nombre='{self.nombre}', activo={self.activo})>"
