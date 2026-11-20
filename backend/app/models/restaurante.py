from datetime import datetime, time
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Time, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.ubicacion import Ubicacion
    from app.models.plato import Plato
    from app.models.recomendacion import Recomendacion
    from app.models.area_restaurante import AreaRestaurante
    from app.models.reserva import Reserva
    from app.models.pedido import Pedido


class Restaurante(Base):
    __tablename__ = "restaurante"

    id_restaurante: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nit: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(150), nullable=True)
    horario_apertura: Mapped[time | None] = mapped_column(Time, nullable=True)
    horario_cierre: Mapped[time | None] = mapped_column(Time, nullable=True)
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
    id_usuario_responsable: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="RESTRICT"),
        nullable=False
    )
    id_ubicacion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ubicacion.id_ubicacion", ondelete="RESTRICT"),
        nullable=False
    )

    # Relaciones
    usuario_responsable: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="restaurantes"
    )
    ubicacion: Mapped["Ubicacion"] = relationship(
        "Ubicacion",
        back_populates="restaurantes"
    )
    platos: Mapped[List["Plato"]] = relationship(
        "Plato",
        back_populates="restaurante",
        cascade="all, delete-orphan"
    )
    recomendaciones: Mapped[List["Recomendacion"]] = relationship(
        "Recomendacion",
        back_populates="restaurante"
    )
    areas: Mapped[List["AreaRestaurante"]] = relationship(
        "AreaRestaurante",
        back_populates="restaurante",
        cascade="all, delete-orphan"
    )
    reservas: Mapped[List["Reserva"]] = relationship(
        "Reserva",
        back_populates="restaurante",
        cascade="all, delete-orphan"
    )
    pedidos: Mapped[List["Pedido"]] = relationship(
        "Pedido",
        back_populates="restaurante",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Restaurante(id_restaurante={self.id_restaurante}, nombre='{self.nombre}', estado='{self.estado}')>"
