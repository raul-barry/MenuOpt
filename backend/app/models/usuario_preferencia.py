from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.preferencia import Preferencia


class UsuarioPreferencia(Base):
    __tablename__ = "usuario_preferencia"
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_preferencia", name="uq_usuario_preferencia"),
    )

    id_usuario_preferencia: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False
    )
    id_preferencia: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("preferencia.id_preferencia", ondelete="RESTRICT"),
        nullable=False
    )

    # Relaciones hacia Usuario y Preferencia
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="usuario_preferencias")
    preferencia: Mapped["Preferencia"] = relationship("Preferencia", back_populates="usuario_preferencias")

    def __repr__(self) -> str:
        return f"<UsuarioPreferencia(id_usuario_preferencia={self.id_usuario_preferencia}, id_usuario={self.id_usuario}, id_preferencia={self.id_preferencia})>"
