from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.bitacora import Bitacora


class BitacoraRepository:
    """
    Repositorio para persistencia y consultas de la tabla Bitacora (CU25).
    """

    @staticmethod
    def crear(db: Session, registro: Bitacora) -> Bitacora:
        db.add(registro)
        db.commit()
        db.refresh(registro)
        return registro

    @staticmethod
    def buscar_por_id(db: Session, id_bitacora: int) -> Optional[Bitacora]:
        return (
            db.query(Bitacora)
            .options(joinedload(Bitacora.usuario))
            .filter(Bitacora.id_bitacora == id_bitacora)
            .first()
        )

    @staticmethod
    def listar_con_filtros(
        db: Session,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        modulo: Optional[str] = None,
        accion: Optional[str] = None,
        id_usuario: Optional[int] = None,
        busqueda: Optional[str] = None,
        pagina: int = 1,
        limite: int = 20
    ) -> Tuple[List[Bitacora], int]:
        query = db.query(Bitacora).options(joinedload(Bitacora.usuario))

        if fecha_desde:
            query = query.filter(Bitacora.fecha_hora >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Bitacora.fecha_hora <= fecha_hasta)
        if modulo:
            query = query.filter(func.upper(Bitacora.modulo) == modulo.strip().upper())
        if accion:
            query = query.filter(func.upper(Bitacora.accion) == accion.strip().upper())
        if id_usuario:
            query = query.filter(Bitacora.id_usuario == id_usuario)
        if busqueda:
            termino = f"%{busqueda.strip().lower()}%"
            query = query.filter(
                (func.lower(Bitacora.descripcion).like(termino)) |
                (func.lower(Bitacora.accion).like(termino))
            )

        total = query.count()
        offset = (pagina - 1) * limite
        items = query.order_by(Bitacora.fecha_hora.desc()).offset(offset).limit(limite).all()

        return items, total
