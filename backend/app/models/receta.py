from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.ingrediente import Ingrediente


class Receta(Base):
    __tablename__ = "receta"

    id_receta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instrucciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo_comida: Mapped[str] = mapped_column(String(50), default="ALMUERZO", nullable=False)
    porciones: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    tiempo_minutos: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    dificultad: Mapped[str] = mapped_column(String(50), default="FACIL", nullable=False)
    origen: Mapped[str | None] = mapped_column(String(100), default="Tradicional Cruceña", nullable=True)
    imagen_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    id_usuario_creador: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="SET NULL"),
        nullable=True
    )

    # Relaciones
    usuario_creador: Mapped[Optional["Usuario"]] = relationship("Usuario")
    ingredientes: Mapped[List["RecetaIngrediente"]] = relationship(
        "RecetaIngrediente",
        back_populates="receta",
        cascade="all, delete-orphan",
        order_by="RecetaIngrediente.id_receta_ingrediente"
    )

    def __repr__(self) -> str:
        return f"<Receta(id_receta={self.id_receta}, nombre='{self.nombre}', tipo='{self.tipo_comida}')>"


class RecetaIngrediente(Base):
    __tablename__ = "receta_ingrediente"

    id_receta_ingrediente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_receta: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("receta.id_receta", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_ingrediente: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("ingrediente.id_ingrediente", ondelete="SET NULL"),
        nullable=True
    )
    nombre_ingrediente: Mapped[str] = mapped_column(String(100), nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unidad_medida: Mapped[str] = mapped_column(String(50), nullable=False)

    receta: Mapped["Receta"] = relationship("Receta", back_populates="ingredientes")
    ingrediente: Mapped[Optional["Ingrediente"]] = relationship("Ingrediente")

    def __repr__(self) -> str:
        return f"<RecetaIngrediente(id={self.id_receta_ingrediente}, nombre='{self.nombre_ingrediente}', cant={self.cantidad} {self.unidad_medida})>"
