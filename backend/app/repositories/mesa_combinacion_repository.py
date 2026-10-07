# CASO DE USO: CU19 - Definir combinación de mesas
from typing import List, Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session, joinedload
from app.models.mesa_combinacion import MesaCombinacion
from app.models.mesa import Mesa


class MesaCombinacionRepository:

    @staticmethod
    def crear(db: Session, combinacion: MesaCombinacion) -> MesaCombinacion:
        db.add(combinacion)
        db.commit()
        db.refresh(combinacion)
        return combinacion

    @staticmethod
    def obtener_por_id(db: Session, id_combinacion: int) -> Optional[MesaCombinacion]:
        stmt = (
            select(MesaCombinacion)
            .options(
                joinedload(MesaCombinacion.mesa_origen),
                joinedload(MesaCombinacion.mesa_destino)
            )
            .where(MesaCombinacion.id_mesa_combinacion == id_combinacion)
        )
        return db.scalar(stmt)

    @staticmethod
    def obtener_por_par_ordenado(db: Session, id_origen: int, id_destino: int) -> Optional[MesaCombinacion]:
        stmt = select(MesaCombinacion).where(
            MesaCombinacion.id_mesa_origen == id_origen,
            MesaCombinacion.id_mesa_destino == id_destino
        )
        return db.scalar(stmt)

    @staticmethod
    def listar_por_area(db: Session, id_area: int, solo_activas: bool = False) -> List[MesaCombinacion]:
        # Busca combinaciones donde al menos una de las mesas pertenece al área dada
        stmt = (
            select(MesaCombinacion)
            .join(MesaCombinacion.mesa_origen)
            .options(
                joinedload(MesaCombinacion.mesa_origen),
                joinedload(MesaCombinacion.mesa_destino)
            )
            .where(Mesa.id_area == id_area)
        )
        if solo_activas:
            stmt = stmt.where(MesaCombinacion.activo.is_(True))
        stmt = stmt.order_by(MesaCombinacion.id_mesa_combinacion.asc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def actualizar(db: Session, combinacion: MesaCombinacion) -> MesaCombinacion:
        db.commit()
        db.refresh(combinacion)
        return combinacion
