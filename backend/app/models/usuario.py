from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.rol import Rol
    from app.models.restaurante import Restaurante
    from app.models.preferencia import Preferencia
    from app.models.usuario_preferencia import UsuarioPreferencia
    from app.models.planificacion import Planificacion
    from app.models.reserva import Reserva
    from app.models.pedido import Pedido


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    contrasena_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
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
    id_rol: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rol.id_rol", ondelete="RESTRICT"),
        nullable=False
    )

    # Relaciones
    rol: Mapped["Rol"] = relationship("Rol", back_populates="usuarios")
    restaurantes: Mapped[List["Restaurante"]] = relationship(
        "Restaurante",
        back_populates="usuario_responsable"
    )
    preferencias: Mapped[List["Preferencia"]] = relationship(
        "Preferencia",
        secondary="usuario_preferencia",
        back_populates="usuarios",
        viewonly=True
    )
    usuario_preferencias: Mapped[List["UsuarioPreferencia"]] = relationship(
        "UsuarioPreferencia",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    planificaciones: Mapped[List["Planificacion"]] = relationship(
        "Planificacion",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    reservas: Mapped[List["Reserva"]] = relationship(
        "Reserva",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    pedidos: Mapped[List["Pedido"]] = relationship(
        "Pedido",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario(id_usuario={self.id_usuario}, correo='{self.correo}', estado='{self.estado}')>"
