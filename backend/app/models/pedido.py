# CASO DE USO: CU23 - Enviar pedido & CU24 - Gestionar pedidos
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import (
    Integer, String, Text, Numeric, DateTime,
    ForeignKey, func, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.restaurante import Restaurante
    from app.models.reserva import Reserva
    from app.models.detalle_pedido import DetallePedido


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_pedido: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        default="PENDIENTE",
        nullable=False,
        index=True
    )
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_restaurante: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("restaurante.id_restaurante", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_reserva: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("reserva.id_reserva", ondelete="SET NULL"),
        nullable=True,
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
        CheckConstraint("total >= 0", name="chk_pedido_total_no_negativo"),
        Index("ix_pedido_restaurante_estado", "id_restaurante", "estado"),
        Index("ix_pedido_usuario_estado", "id_usuario", "estado"),
    )

    # Relaciones
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="pedidos")
    restaurante: Mapped["Restaurante"] = relationship("Restaurante", back_populates="pedidos")
    reserva: Mapped[Optional["Reserva"]] = relationship("Reserva", back_populates="pedidos")
    detalles: Mapped[List["DetallePedido"]] = relationship(
        "DetallePedido",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Pedido(id_pedido={self.id_pedido}, id_usuario={self.id_usuario}, id_restaurante={self.id_restaurante}, estado='{self.estado}', total={self.total})>"
