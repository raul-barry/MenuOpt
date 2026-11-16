# CASO DE USO: CU13 - Generar recomendación
# CASO DE USO: CU14 - Comparar alternativas (RESTAURANTE vs PREPARACION_PROPIA)
from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.models.plato import Plato
from app.models.plato_ingrediente import PlatoIngrediente
from app.models.restaurante import Restaurante
from app.models.recomendacion import Recomendacion
from app.models.recomendacion_plato import RecomendacionPlato
from app.models.preparacion_propia import PreparacionPropia
from app.models.preparacion_ingrediente import PreparacionIngrediente
from app.models.lugar_compra import LugarCompra


class RecomendacionRepository:
    """
    Repositorio para persistencia y consultas de recomendaciones gastronómicas
    (tanto RESTAURANTE como PREPARACION_PROPIA).
    """

    @staticmethod
    def buscar_platos_candidatos(db: Session, tipo_comida: str) -> List[Plato]:
        """
        Obtiene platos activos y disponibles cuyo tipo_comida coincida con la planificación,
        pertenecientes a restaurantes activos.
        """
        return (
            db.query(Plato)
            .join(Restaurante, Plato.id_restaurante == Restaurante.id_restaurante)
            .options(
                joinedload(Plato.restaurante).joinedload(Restaurante.ubicacion),
                joinedload(Plato.preferencias)
            )
            .filter(
                Plato.estado == "ACTIVO",
                Plato.disponible.is_(True),
                func.upper(Plato.tipo_comida) == tipo_comida.upper(),
                Restaurante.estado == "ACTIVO"
            )
            .all()
        )

    @staticmethod
    def buscar_platos_para_preparacion(db: Session, tipo_comida: str) -> List[Plato]:
        """
        Obtiene platos activos cuyo tipo_comida coincida con la planificación,
        que cuenten con receta estructurada de ingredientes (plato_ingrediente).
        """
        return (
            db.query(Plato)
            .options(
                joinedload(Plato.preferencias),
                joinedload(Plato.plato_ingredientes).joinedload(PlatoIngrediente.ingrediente)
            )
            .filter(
                Plato.estado == "ACTIVO",
                func.upper(Plato.tipo_comida) == tipo_comida.upper(),
                Plato.plato_ingredientes.any()
            )
            .all()
        )

    @staticmethod
    def eliminar_recomendaciones_anteriores(
        db: Session,
        id_planificacion: int,
        tipo_recomendacion: Optional[str] = None
    ) -> None:
        """
        Elimina transaccionalmente las recomendaciones previas de la planificación.
        Si se especifica tipo_recomendacion, filtra por dicho tipo; de lo contrario,
        elimina todas para garantizar una regeneración limpia.
        """
        query = db.query(Recomendacion).filter(
            Recomendacion.id_planificacion == id_planificacion
        )
        if tipo_recomendacion:
            query = query.filter(Recomendacion.tipo_recomendacion == tipo_recomendacion.upper())

        anteriores = query.all()
        for rec in anteriores:
            db.delete(rec)
        db.flush()

    @staticmethod
    def guardar_recomendaciones(
        db: Session,
        recomendaciones: List[Recomendacion]
    ) -> List[Recomendacion]:
        """
        Persiste la lista de nuevas recomendaciones calculadas con sus platos y preparaciones asociadas.
        """
        for rec in recomendaciones:
            db.add(rec)
        db.commit()
        for rec in recomendaciones:
            db.refresh(rec)
        return recomendaciones

    @staticmethod
    def listar_por_planificacion(
        db: Session,
        id_planificacion: int,
        tipo_recomendacion: Optional[str] = None
    ) -> List[Recomendacion]:
        """
        Recupera las recomendaciones generadas para una planificación,
        ordenadas por puntuación descendente y costo total ascendente.
        """
        query = (
            db.query(Recomendacion)
            .options(
                joinedload(Recomendacion.restaurante).joinedload(Restaurante.ubicacion),
                joinedload(Recomendacion.recomendacion_platos).joinedload(RecomendacionPlato.plato),
                joinedload(Recomendacion.preparacion_propia)
                .joinedload(PreparacionPropia.ingredientes)
                .joinedload(PreparacionIngrediente.ingrediente),
                joinedload(Recomendacion.preparacion_propia)
                .joinedload(PreparacionPropia.ingredientes)
                .joinedload(PreparacionIngrediente.lugar_compra)
                .joinedload(LugarCompra.ubicacion)
            )
            .filter(Recomendacion.id_planificacion == id_planificacion)
        )

        if tipo_recomendacion:
            query = query.filter(Recomendacion.tipo_recomendacion == tipo_recomendacion.upper())

        return (
            query.order_by(
                Recomendacion.puntuacion.desc(),
                Recomendacion.costo_estimado.asc()
            )
            .all()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_recomendacion: int) -> Optional[Recomendacion]:
        """
        Recupera el detalle de una recomendación específica por su ID.
        """
        return (
            db.query(Recomendacion)
            .options(
                joinedload(Recomendacion.restaurante).joinedload(Restaurante.ubicacion),
                joinedload(Recomendacion.recomendacion_platos).joinedload(RecomendacionPlato.plato),
                joinedload(Recomendacion.planificacion),
                joinedload(Recomendacion.preparacion_propia)
                .joinedload(PreparacionPropia.ingredientes)
                .joinedload(PreparacionIngrediente.ingrediente),
                joinedload(Recomendacion.preparacion_propia)
                .joinedload(PreparacionPropia.ingredientes)
                .joinedload(PreparacionIngrediente.lugar_compra)
                .joinedload(LugarCompra.ubicacion)
            )
            .filter(Recomendacion.id_recomendacion == id_recomendacion)
            .first()
        )
