# CASO DE USO: CU16 - Consultar lugares de compra
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.ubicacion import Ubicacion
    from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
    from app.models.preparacion_ingrediente import PreparacionIngrediente
    from app.models.usuario import Usuario


class LugarCompra(Base):
    """
    Entidad que representa un establecimiento comercial donde se comercializan ingredientes
    (mercado, supermercado, tienda, distribuidora).
    """
    __tablename__ = "lugar_compra"

    id_lugar_compra: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    tipo: Mapped[str | None] = mapped_column(String(50), nullable=True)  # MERCADO, SUPERMERCADO, TIENDA, etc.
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVO", nullable=False)
    id_ubicacion: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("ubicacion.id_ubicacion", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    id_usuario_responsable: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Relaciones
    ubicacion: Mapped[Optional["Ubicacion"]] = relationship("Ubicacion", back_populates="lugares_compra")
    usuario_responsable: Mapped[Optional["Usuario"]] = relationship("Usuario")
    ingrediente_lugares: Mapped[List["IngredienteLugarCompra"]] = relationship(
        "IngredienteLugarCompra",
        back_populates="lugar_compra",
        cascade="all, delete-orphan"
    )
    preparacion_ingredientes: Mapped[List["PreparacionIngrediente"]] = relationship(
        "PreparacionIngrediente",
        back_populates="lugar_compra"
    )

    def __repr__(self) -> str:
        return f"<LugarCompra(id_lugar_compra={self.id_lugar_compra}, nombre='{self.nombre}', tipo='{self.tipo}', estado='{self.estado}')>"
