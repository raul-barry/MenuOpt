from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Rol(Base):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relación 1:N con Usuario
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        back_populates="rol"
    )

    def __repr__(self) -> str:
        return f"<Rol(id_rol={self.id_rol}, nombre='{self.nombre}', activo={self.activo})>"
