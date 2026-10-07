from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ingrediente import Ingrediente


class IngredienteRepository:
    """
    Repositorio para persistencia y consultas del catálogo de Ingredientes.
    """

    @staticmethod
    def buscar_por_id(db: Session, id_ingrediente: int) -> Optional[Ingrediente]:
        return db.query(Ingrediente).filter(Ingrediente.id_ingrediente == id_ingrediente).first()

    @staticmethod
    def buscar_por_nombre(db: Session, nombre: str) -> Optional[Ingrediente]:
        return (
            db.query(Ingrediente)
            .filter(func.lower(Ingrediente.nombre) == func.lower(nombre.strip()))
            .first()
        )

    @staticmethod
    def listar(db: Session, estado: Optional[str] = None) -> List[Ingrediente]:
        query = db.query(Ingrediente)
        if estado:
            query = query.filter(Ingrediente.estado == estado.upper())
        return query.order_by(Ingrediente.nombre.asc()).all()

    @staticmethod
    def crear(db: Session, ingrediente: Ingrediente) -> Ingrediente:
        db.add(ingrediente)
        db.commit()
        db.refresh(ingrediente)
        return ingrediente

    @staticmethod
    def actualizar(db: Session, ingrediente: Ingrediente) -> Ingrediente:
        db.commit()
        db.refresh(ingrediente)
        return ingrediente
