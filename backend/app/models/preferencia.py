from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.usuario_preferencia import UsuarioPreferencia
    from app.models.planificacion import Planificacion
    from app.models.planificacion_preferencia import PlanificacionPreferencia
    from app.models.plato import Plato
    from app.models.plato_preferencia import PlatoPreferencia


class Preferencia(Base):
    __tablename__ = "preferencia"

    id_preferencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    tipo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relación N:M con Usuario a través de UsuarioPreferencia
    usuarios: Mapped[List["Usuario"]] = relationship(
        "Usuario",
        secondary="usuario_preferencia",
        back_populates="preferencias",
        viewonly=True
    )

    # Relación 1:N con la entidad intermedia UsuarioPreferencia
    usuario_preferencias: Mapped[List["UsuarioPreferencia"]] = relationship(
        "UsuarioPreferencia",
        back_populates="preferencia",
        cascade="all, delete-orphan"
    )

    # Relación N:M con Planificacion a través de PlanificacionPreferencia
    planificaciones: Mapped[List["Planificacion"]] = relationship(
        "Planificacion",
        secondary="planificacion_preferencia",
        back_populates="preferencias",
        viewonly=True
    )

    # Relación 1:N con la entidad intermedia PlanificacionPreferencia
    planificacion_preferencias: Mapped[List["PlanificacionPreferencia"]] = relationship(
        "PlanificacionPreferencia",
        back_populates="preferencia",
        cascade="all, delete-orphan"
    )

    # Relación N:M con Plato a través de PlatoPreferencia
    platos: Mapped[List["Plato"]] = relationship(
        "Plato",
        secondary="plato_preferencia",
        back_populates="preferencias",
        viewonly=True
    )

    # Relación 1:N con la entidad intermedia PlatoPreferencia
    plato_preferencias: Mapped[List["PlatoPreferencia"]] = relationship(
        "PlatoPreferencia",
        back_populates="preferencia",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Preferencia(id_preferencia={self.id_preferencia}, nombre='{self.nombre}', tipo='{self.tipo}')>"
