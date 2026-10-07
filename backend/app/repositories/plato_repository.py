from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.plato import Plato
from app.models.plato_ingrediente import PlatoIngrediente


class PlatoRepository:
    """
    Repositorio para persistencia y consultas de Plato y sus ingredientes asociados.
    """

    @staticmethod
    def buscar_por_id(db: Session, id_plato: int) -> Optional[Plato]:
        return (
            db.query(Plato)
            .options(joinedload(Plato.categoria), joinedload(Plato.restaurante))
            .filter(Plato.id_plato == id_plato)
            .first()
        )

    @staticmethod
    def listar_por_restaurante(
        db: Session,
        id_restaurante: int,
        id_categoria: Optional[int] = None,
        tipo_comida: Optional[str] = None,
        disponible: Optional[bool] = None,
        estado: Optional[str] = None
    ) -> List[Plato]:
        query = (
            db.query(Plato)
            .options(joinedload(Plato.categoria))
            .filter(Plato.id_restaurante == id_restaurante)
        )

        if id_categoria:
            query = query.filter(Plato.id_categoria == id_categoria)
        if tipo_comida:
            query = query.filter(Plato.tipo_comida == tipo_comida)
        if disponible is not None:
            query = query.filter(Plato.disponible == disponible)
        if estado:
            query = query.filter(Plato.estado == estado.upper())

        return query.order_by(Plato.id_plato.asc()).all()

    @staticmethod
    def crear(db: Session, plato: Plato) -> Plato:
        db.add(plato)
        db.commit()
        db.refresh(plato)
        return plato

    @staticmethod
    def actualizar(db: Session, plato: Plato) -> Plato:
        db.commit()
        db.refresh(plato)
        return plato

    # --- Métodos de relación plato_ingrediente ---

    @staticmethod
    def asociar_ingrediente(db: Session, relacion: PlatoIngrediente) -> PlatoIngrediente:
        db.add(relacion)
        db.commit()
        db.refresh(relacion)
        return relacion

    @staticmethod
    def buscar_relacion_ingrediente(db: Session, id_plato: int, id_ingrediente: int) -> Optional[PlatoIngrediente]:
        return (
            db.query(PlatoIngrediente)
            .options(joinedload(PlatoIngrediente.ingrediente))
            .filter(
                PlatoIngrediente.id_plato == id_plato,
                PlatoIngrediente.id_ingrediente == id_ingrediente
            )
            .first()
        )

    @staticmethod
    def listar_ingredientes_de_plato(db: Session, id_plato: int) -> List[PlatoIngrediente]:
        return (
            db.query(PlatoIngrediente)
            .options(joinedload(PlatoIngrediente.ingrediente))
            .filter(PlatoIngrediente.id_plato == id_plato)
            .all()
        )

    @staticmethod
    def eliminar_relacion_ingrediente(db: Session, relacion: PlatoIngrediente) -> None:
        db.delete(relacion)
        db.commit()
