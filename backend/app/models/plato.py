from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.restaurante import Restaurante
    from app.models.categoria import Categoria
    from app.models.ingrediente import Ingrediente
    from app.models.plato_ingrediente import PlatoIngrediente
    from app.models.preferencia import Preferencia
    from app.models.plato_preferencia import PlatoPreferencia
    from app.models.recomendacion_plato import RecomendacionPlato
    from app.models.detalle_pedido import DetallePedido


class Plato(Base):
    __tablename__ = "plato"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="chk_plato_precio_no_negativo"),
        CheckConstraint("personas_cubiertas > 0", name="chk_plato_personas_cubiertas_mayor_cero"),
    )

    id_plato: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tipo_comida: Mapped[str | None] = mapped_column(String(50), nullable=True)
    personas_cubiertas: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO", nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(
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
    id_restaurante: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("restaurante.id_restaurante", ondelete="CASCADE"),
        nullable=False
    )
    id_categoria: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categoria.id_categoria", ondelete="RESTRICT"),
        nullable=False
    )

    # Relaciones
    restaurante: Mapped["Restaurante"] = relationship("Restaurante", back_populates="platos")
    categoria: Mapped["Categoria"] = relationship("Categoria", back_populates="platos")
    ingredientes: Mapped[List["Ingrediente"]] = relationship(
        "Ingrediente",
        secondary="plato_ingrediente",
        back_populates="platos",
        viewonly=True
    )
    plato_ingredientes: Mapped[List["PlatoIngrediente"]] = relationship(
        "PlatoIngrediente",
        back_populates="plato",
        cascade="all, delete-orphan"
    )
    preferencias: Mapped[List["Preferencia"]] = relationship(
        "Preferencia",
        secondary="plato_preferencia",
        back_populates="platos",
        viewonly=True
    )
    plato_preferencias: Mapped[List["PlatoPreferencia"]] = relationship(
        "PlatoPreferencia",
        back_populates="plato",
        cascade="all, delete-orphan"
    )
    recomendacion_platos: Mapped[List["RecomendacionPlato"]] = relationship(
        "RecomendacionPlato",
        back_populates="plato"
    )
    detalles_pedido: Mapped[List["DetallePedido"]] = relationship(
        "DetallePedido",
        back_populates="plato"
    )

    def __repr__(self) -> str:
        return f"<Plato(id_plato={self.id_plato}, nombre='{self.nombre}', precio={self.precio})>"
