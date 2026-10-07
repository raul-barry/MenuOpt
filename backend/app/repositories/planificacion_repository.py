from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.planificacion import Planificacion
from app.models.planificacion_preferencia import PlanificacionPreferencia


class PlanificacionRepository:
    """
    Repositorio para persistencia y consultas de Planificacion y PlanificacionPreferencia.
    """

    # =========================================================================
    # CASO DE USO: CU11 - REGISTRAR PLANIFICACIÓN GASTRONÓMICA
    # =========================================================================

    @staticmethod
    def crear_planificacion(
        db: Session,
        planificacion: Planificacion,
        ids_preferencias: List[int]
    ) -> Planificacion:
        """
        Crea una planificación y sus preferencias asociadas de forma transaccional.
        """
        db.add(planificacion)
        db.flush()  # Obtiene el id_planificacion generado

        for id_pref in ids_preferencias:
            db.add(PlanificacionPreferencia(
                id_planificacion=planificacion.id_planificacion,
                id_preferencia=id_pref
            ))

        db.commit()
        db.refresh(planificacion)
        return planificacion

    @staticmethod
    def buscar_por_id(db: Session, id_planificacion: int) -> Optional[Planificacion]:
        return (
            db.query(Planificacion)
            .options(joinedload(Planificacion.preferencias))
            .filter(Planificacion.id_planificacion == id_planificacion)
            .first()
        )

    @staticmethod
    def listar_por_usuario_paginado(
        db: Session,
        id_usuario: int,
        pagina: int = 1,
        limite: int = 10,
        estado: Optional[str] = None
    ) -> Tuple[List[Planificacion], int]:
        query = (
            db.query(Planificacion)
            .options(joinedload(Planificacion.preferencias))
            .filter(Planificacion.id_usuario == id_usuario)
        )

        if estado:
            query = query.filter(Planificacion.estado == estado.strip().upper())

        total = query.count()
        offset = (pagina - 1) * limite
        registros = (
            query.order_by(Planificacion.fecha_planificacion.desc(), Planificacion.id_planificacion.desc())
            .offset(offset)
            .limit(limite)
            .all()
        )
        return registros, total

    @staticmethod
    def actualizar_planificacion(
        db: Session,
        planificacion: Planificacion,
        ids_preferencias: Optional[List[int]] = None
    ) -> Planificacion:
        if ids_preferencias is not None:
            existentes = (
                db.query(PlanificacionPreferencia)
                .filter(PlanificacionPreferencia.id_planificacion == planificacion.id_planificacion)
                .all()
            )
            mapa_existentes = {pp.id_preferencia: pp for pp in existentes}
            ids_set = set(ids_preferencias)

            # Eliminar las deseleccionadas
            for id_pref, obj_pp in mapa_existentes.items():
                if id_pref not in ids_set:
                    db.delete(obj_pp)

            # Insertar las nuevas
            for id_pref in ids_set:
                if id_pref not in mapa_existentes:
                    db.add(PlanificacionPreferencia(
                        id_planificacion=planificacion.id_planificacion,
                        id_preferencia=id_pref
                    ))

        db.commit()
        db.refresh(planificacion)
        return planificacion

    @staticmethod
    def cambiar_estado(
        db: Session,
        planificacion: Planificacion,
        nuevo_estado: str
    ) -> Planificacion:
        planificacion.estado = nuevo_estado
        db.commit()
        db.refresh(planificacion)
        return planificacion
