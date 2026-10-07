# CASO DE USO: CU21 - Realizar reserva (Tabla intermedia N:M Reserva - Mesa)
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.mesa import Mesa
    from app.models.reserva import Reserva


class MesaReserva(Base):
    __tablename__ = "mesa_reserva"

    id_mesa_reserva: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_mesa: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mesa.id_mesa", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_reserva: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reserva.id_reserva", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        UniqueConstraint("id_mesa", "id_reserva", name="uq_mesa_reserva"),
    )

    # Relaciones
    mesa: Mapped["Mesa"] = relationship(
        "Mesa",
        back_populates="mesas_reservadas",
        overlaps="mesas,reservas"
    )
    reserva: Mapped["Reserva"] = relationship(
        "Reserva",
        back_populates="mesas_reservadas",
        overlaps="mesas,reservas"
    )

    def __repr__(self) -> str:
        return f"<MesaReserva(id={self.id_mesa_reserva}, mesa={self.id_mesa}, reserva={self.id_reserva})>"
