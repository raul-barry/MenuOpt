# CASO DE USO: CU16 - Consultar lugares de compra
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.lugar_compra import LugarCompra


class LugarCompraRepository:
    """
    Repositorio para persistencia y consultas de establecimientos comerciales de compra (LugarCompra).
    """

    @staticmethod
    def buscar_por_id(db: Session, id_lugar_compra: int) -> Optional[LugarCompra]:
        return (
            db.query(LugarCompra)
            .options(joinedload(LugarCompra.ubicacion))
            .filter(LugarCompra.id_lugar_compra == id_lugar_compra)
            .first()
        )

    @staticmethod
    def buscar_por_nombre(db: Session, nombre: str) -> Optional[LugarCompra]:
        return (
            db.query(LugarCompra)
            .filter(func.lower(LugarCompra.nombre) == func.lower(nombre.strip()))
            .first()
        )

    @staticmethod
    def listar(
        db: Session,
        estado: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> List[LugarCompra]:
        query = db.query(LugarCompra).options(joinedload(LugarCompra.ubicacion))

        if estado:
            query = query.filter(LugarCompra.estado == estado.strip().upper())
        if tipo:
            query = query.filter(func.lower(LugarCompra.tipo) == func.lower(tipo.strip()))

        return query.order_by(LugarCompra.nombre.asc()).all()

    @staticmethod
    def crear(db: Session, lugar: LugarCompra) -> LugarCompra:
        db.add(lugar)
        db.commit()
        db.refresh(lugar)
        return lugar

    @staticmethod
    def actualizar(db: Session, lugar: LugarCompra) -> LugarCompra:
        db.commit()
        db.refresh(lugar)
        return lugar
