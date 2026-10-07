# CASO DE USO: CU18 - Gestionar mesas
from datetime import datetime
from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, Boolean, DateTime, ForeignKey, func, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.area_restaurante import AreaRestaurante
    from app.models.mesa_combinacion import MesaCombinacion
    from app.models.reserva import Reserva
    from app.models.mesa_reserva import MesaReserva


class Mesa(Base):
    __tablename__ = "mesa"

    id_mesa: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_area: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("area_restaurante.id_area", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    numero: Mapped[str] = mapped_column(String(30), nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False)
    forma: Mapped[str] = mapped_column(String(20), default="CUADRADA", nullable=False)  # REDONDA, CUADRADA, RECTANGULAR
    posicion_x: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0.5000"), nullable=False)
    posicion_y: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0.5000"), nullable=False)
    rotacion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0, 90, 180, 270
    ancho: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0.0800"), nullable=False)
    alto: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0.0800"), nullable=False)
    es_fija: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    combinable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
        CheckConstraint("posicion_x >= 0.0 AND posicion_x <= 1.0", name="chk_mesa_posicion_x"),
        CheckConstraint("posicion_y >= 0.0 AND posicion_y <= 1.0", name="chk_mesa_posicion_y"),
        CheckConstraint("capacidad > 0", name="chk_mesa_capacidad"),
        UniqueConstraint("id_area", "numero", name="uq_mesa_area_numero"),
    )

    area: Mapped["AreaRestaurante"] = relationship(
        "AreaRestaurante",
        back_populates="mesas"
    )
    combinaciones_origen: Mapped[List["MesaCombinacion"]] = relationship(
        "MesaCombinacion",
        foreign_keys="MesaCombinacion.id_mesa_origen",
        back_populates="mesa_origen",
        cascade="all, delete-orphan"
    )
    combinaciones_destino: Mapped[List["MesaCombinacion"]] = relationship(
        "MesaCombinacion",
        foreign_keys="MesaCombinacion.id_mesa_destino",
        back_populates="mesa_destino",
        cascade="all, delete-orphan"
    )
    reservas: Mapped[List["Reserva"]] = relationship(
        "Reserva",
        secondary="mesa_reserva",
        back_populates="mesas",
        overlaps="mesas_reservadas"
    )
    mesas_reservadas: Mapped[List["MesaReserva"]] = relationship(
        "MesaReserva",
        back_populates="mesa",
        cascade="all, delete-orphan",
        overlaps="mesas,reservas"
    )

    def __repr__(self) -> str:
        return f"<Mesa(id_mesa={self.id_mesa}, numero='{self.numero}', capacidad={self.capacidad}, forma='{self.forma}')>"
