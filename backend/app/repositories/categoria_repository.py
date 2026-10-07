from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.categoria import Categoria


class CategoriaRepository:
    """
    Repositorio para persistencia y consultas de Categoria.
    """

    @staticmethod
    def buscar_por_id(db: Session, id_categoria: int) -> Optional[Categoria]:
        return db.query(Categoria).filter(Categoria.id_categoria == id_categoria).first()

    @staticmethod
    def buscar_por_nombre(db: Session, nombre: str) -> Optional[Categoria]:
        return (
            db.query(Categoria)
            .filter(func.lower(Categoria.nombre) == func.lower(nombre.strip()))
            .first()
        )

    @staticmethod
    def listar_activas(db: Session) -> List[Categoria]:
        return (
            db.query(Categoria)
            .filter(Categoria.activo.is_(True))
            .order_by(Categoria.nombre.asc())
            .all()
        )

    @staticmethod
    def listar_todas(db: Session) -> List[Categoria]:
        return db.query(Categoria).order_by(Categoria.id_categoria.asc()).all()

    @staticmethod
    def crear(db: Session, categoria: Categoria) -> Categoria:
        db.add(categoria)
        db.commit()
        db.refresh(categoria)
        return categoria

    @staticmethod
    def actualizar(db: Session, categoria: Categoria) -> Categoria:
        db.commit()
        db.refresh(categoria)
        return categoria
