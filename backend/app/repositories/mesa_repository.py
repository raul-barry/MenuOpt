# CASO DE USO: CU18 - Gestionar mesas
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, update
from sqlalchemy.orm import Session
from app.models.mesa import Mesa


class MesaRepository:

    @staticmethod
    def crear(db: Session, mesa: Mesa) -> Mesa:
        db.add(mesa)
        db.commit()
        db.refresh(mesa)
        return mesa

    @staticmethod
    def crear_varias(db: Session, mesas: List[Mesa]) -> List[Mesa]:
        db.add_all(mesas)
        db.commit()
        for m in mesas:
            db.refresh(m)
        return mesas

    @staticmethod
    def obtener_por_id(db: Session, id_mesa: int) -> Optional[Mesa]:
        stmt = select(Mesa).where(Mesa.id_mesa == id_mesa)
        return db.scalar(stmt)

    @staticmethod
    def obtener_por_area_y_numero(db: Session, id_area: int, numero: str) -> Optional[Mesa]:
        stmt = select(Mesa).where(
            Mesa.id_area == id_area,
            func.lower(Mesa.numero) == func.lower(numero.strip())
        )
        return db.scalar(stmt)

    @staticmethod
    def listar_por_area(db: Session, id_area: int, solo_activas: bool = False) -> List[Mesa]:
        stmt = select(Mesa).where(Mesa.id_area == id_area)
        if solo_activas:
            stmt = stmt.where(Mesa.activo.is_(True))
        stmt = stmt.order_by(Mesa.numero.asc(), Mesa.id_mesa.asc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def obtener_todas_por_ids(db: Session, ids_mesas: List[int]) -> List[Mesa]:
        stmt = select(Mesa).where(Mesa.id_mesa.in_(ids_mesas))
        return list(db.scalars(stmt).all())

    @staticmethod
    def actualizar(db: Session, mesa: Mesa) -> Mesa:
        db.commit()
        db.refresh(mesa)
        return mesa

    @staticmethod
    def actualizar_posiciones_masivas(db: Session, actualizaciones: List[Dict[str, Any]]) -> None:
        """
        Ejecuta actualización masiva de coordenadas y rotaciones dentro de una transacción.
        actualizaciones: [{'id_mesa': int, 'posicion_x': Decimal, 'posicion_y': Decimal, 'rotacion': Optional[int]}]
        """
        for item in actualizaciones:
            valores: Dict[str, Any] = {
                "posicion_x": item["posicion_x"],
                "posicion_y": item["posicion_y"]
            }
            if item.get("rotacion") is not None:
                valores["rotacion"] = item["rotacion"]

            stmt = (
                update(Mesa)
                .where(Mesa.id_mesa == item["id_mesa"])
                .values(**valores)
            )
            db.execute(stmt)
        db.commit()
