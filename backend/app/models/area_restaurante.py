# CASO DE USO: CU17 - Crear plano 2D del restaurante
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.restaurante import Restaurante
    from app.models.mesa import Mesa


class AreaRestaurante(Base):
    __tablename__ = "area_restaurante"

    id_area: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    ancho_mapa: Mapped[int] = mapped_column(Integer, default=1200, nullable=False)
    alto_mapa: Mapped[int] = mapped_column(Integer, default=700, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    elementos: Mapped[str | None] = mapped_column(Text, nullable=True, server_default="[]")
    id_restaurante: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("restaurante.id_restaurante", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("id_restaurante", "nombre", name="uq_area_restaurante_nombre"),
    )

    restaurante: Mapped["Restaurante"] = relationship(
        "Restaurante",
        back_populates="areas"
    )
    mesas: Mapped[List["Mesa"]] = relationship(
        "Mesa",
        back_populates="area",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AreaRestaurante(id_area={self.id_area}, nombre='{self.nombre}', id_restaurante={self.id_restaurante})>"
