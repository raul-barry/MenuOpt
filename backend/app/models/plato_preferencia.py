from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.plato import Plato
    from app.models.preferencia import Preferencia


class PlatoPreferencia(Base):
    __tablename__ = "plato_preferencia"
    __table_args__ = (
        UniqueConstraint("id_plato", "id_preferencia", name="uq_plato_preferencia"),
    )

    id_plato_preferencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_plato: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plato.id_plato", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    id_preferencia: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("preferencia.id_preferencia", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Relaciones hacia Plato y Preferencia
    plato: Mapped["Plato"] = relationship("Plato", back_populates="plato_preferencias")
    preferencia: Mapped["Preferencia"] = relationship("Preferencia", back_populates="plato_preferencias")

    def __repr__(self) -> str:
        return f"<PlatoPreferencia(id_plato_preferencia={self.id_plato_preferencia}, id_plato={self.id_plato}, id_preferencia={self.id_preferencia})>"
