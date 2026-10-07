# CASO DE USO: CU19 - Definir combinación de mesas
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, func, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.mesa import Mesa


class MesaCombinacion(Base):
    __tablename__ = "mesa_combinacion"

    id_mesa_combinacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_mesa_origen: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mesa.id_mesa", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_mesa_destino: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mesa.id_mesa", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    permitida: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("id_mesa_origen < id_mesa_destino", name="chk_mesa_combinacion_orden_simetrico"),
        UniqueConstraint("id_mesa_origen", "id_mesa_destino", name="uq_mesa_combinacion_par"),
    )

    mesa_origen: Mapped["Mesa"] = relationship(
        "Mesa",
        foreign_keys=[id_mesa_origen],
        back_populates="combinaciones_origen"
    )
    mesa_destino: Mapped["Mesa"] = relationship(
        "Mesa",
        foreign_keys=[id_mesa_destino],
        back_populates="combinaciones_destino"
    )

    def __repr__(self) -> str:
        return f"<MesaCombinacion(id={self.id_mesa_combinacion}, origen={self.id_mesa_origen}, destino={self.id_mesa_destino}, permitida={self.permitida})>"
