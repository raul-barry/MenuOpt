# CASO DE USO: CU23 - Enviar pedido & CU24 - Gestionar pedidos
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Integer, Numeric, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.pedido import Pedido
    from app.models.plato import Plato


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id_detalle_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    id_pedido: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pedido.id_pedido", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_plato: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plato.id_plato", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_detalle_cantidad_positiva"),
        CheckConstraint("precio_unitario >= 0", name="chk_detalle_precio_unitario_no_negativo"),
        CheckConstraint("subtotal >= 0", name="chk_detalle_subtotal_no_negativo"),
        UniqueConstraint("id_pedido", "id_plato", name="uq_detalle_pedido_plato"),
    )

    # Relaciones
    pedido: Mapped["Pedido"] = relationship("Pedido", back_populates="detalles")
    plato: Mapped["Plato"] = relationship("Plato", back_populates="detalles_pedido")

    def __repr__(self) -> str:
        return f"<DetallePedido(id_detalle_pedido={self.id_detalle_pedido}, id_pedido={self.id_pedido}, id_plato={self.id_plato}, cantidad={self.cantidad}, subtotal={self.subtotal})>"
