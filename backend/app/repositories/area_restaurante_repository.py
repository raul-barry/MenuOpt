# CASO DE USO: CU17 - Crear plano 2D del restaurante
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.area_restaurante import AreaRestaurante
from app.models.mesa import Mesa


class AreaRestauranteRepository:

    @staticmethod
    def crear(db: Session, area: AreaRestaurante) -> AreaRestaurante:
        db.add(area)
        db.commit()
        db.refresh(area)
        return area

    @staticmethod
    def obtener_por_id(db: Session, id_area: int) -> Optional[AreaRestaurante]:
        stmt = select(AreaRestaurante).where(AreaRestaurante.id_area == id_area)
        return db.scalar(stmt)

    @staticmethod
    def obtener_por_restaurante_y_nombre(db: Session, id_restaurante: int, nombre: str) -> Optional[AreaRestaurante]:
        stmt = select(AreaRestaurante).where(
            AreaRestaurante.id_restaurante == id_restaurante,
            func.lower(AreaRestaurante.nombre) == func.lower(nombre.strip())
        )
        return db.scalar(stmt)

    @staticmethod
    def listar_por_restaurante(db: Session, id_restaurante: int, solo_activas: bool = False) -> List[AreaRestaurante]:
        stmt = select(AreaRestaurante).where(AreaRestaurante.id_restaurante == id_restaurante)
        if solo_activas:
            stmt = stmt.where(AreaRestaurante.activo.is_(True))
        stmt = stmt.order_by(AreaRestaurante.orden.asc(), AreaRestaurante.id_area.asc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def contar_mesas_por_area(db: Session, id_area: int) -> int:
        stmt = select(func.count(Mesa.id_mesa)).where(
            Mesa.id_area == id_area,
            Mesa.activo.is_(True)
        )
        return db.scalar(stmt) or 0

    @staticmethod
    def actualizar(db: Session, area: AreaRestaurante) -> AreaRestaurante:
        db.commit()
        db.refresh(area)
        return area
