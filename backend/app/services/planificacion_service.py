from typing import Optional, List, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.planificacion import Planificacion
from app.models.usuario import Usuario
from app.repositories.planificacion_repository import PlanificacionRepository
from app.repositories.preferencia_repository import PreferenciaRepository
from app.schemas.planificacion import (
    CrearPlanificacionSchema,
    ActualizarPlanificacionSchema
)
from app.security.propiedad import verificar_propiedad_planificacion


class PlanificacionService:
    """
    Servicio de lógica de negocio para la gestión de planificaciones gastronómicas (CU11).
    """

    # =========================================================================
    # CASO DE USO: CU11 - REGISTRAR PLANIFICACIÓN GASTRONÓMICA
    # =========================================================================

    @staticmethod
    def crear_planificacion(
        db: Session,
        datos: CrearPlanificacionSchema,
        usuario_actual: Usuario
    ) -> Planificacion:
        """
        Crea una nueva planificación gastronómica para el usuario autenticado.
        Valida presupuesto (> 0), comensales (> 0), tipo de comida, preferencias válidas,
        y sincroniza preferencias de forma transaccional e independiente de usuario_preferencia.
        """
        if usuario_actual.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su cuenta no se encuentra activa para registrar planificaciones."
            )

        if datos.presupuesto <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El presupuesto disponible debe ser mayor que cero."
            )

        if datos.cantidad_personas <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad de personas debe ser mayor que cero."
            )

        # Determinar preferencias a asociar
        if datos.preferencias is None:
            # Si no se enviaron preferencias específicas, usar las preferencias guardadas del usuario como valores iniciales
            prefs_usuario = PreferenciaRepository.obtener_preferencias_usuario(db, usuario_actual.id_usuario)
            ids_a_guardar = [p.id_preferencia for p in prefs_usuario if p.activo]
        else:
            # Si se envió lista de preferencias (incluso vacía []), deduplicar y validar existencia
            ids_unicos = list(dict.fromkeys(datos.preferencias))
            if ids_unicos:
                activas = PreferenciaRepository.buscar_activas_por_ids(db, ids_unicos)
                ids_encontrados = {p.id_preferencia for p in activas}
                no_encontrados = [i for i in ids_unicos if i not in ids_encontrados]
                if no_encontrados:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Las siguientes preferencias no existen o no están activas en el catálogo: {no_encontrados}"
                    )
            ids_a_guardar = ids_unicos

        nueva_planificacion = Planificacion(
            presupuesto=datos.presupuesto,
            cantidad_personas=datos.cantidad_personas,
            tipo_comida=datos.tipo_comida.strip().upper(),
            ubicacion_referencia=datos.ubicacion_referencia.strip(),
            estado="ACTIVA",
            id_usuario=usuario_actual.id_usuario
        )

        return PlanificacionRepository.crear_planificacion(
            db=db,
            planificacion=nueva_planificacion,
            ids_preferencias=ids_a_guardar
        )

    @staticmethod
    def listar_mis_planificaciones(
        db: Session,
        usuario_actual: Usuario,
        pagina: int = 1,
        limite: int = 10,
        estado: Optional[str] = None
    ) -> Dict:
        """
        Consulta paginada de las planificaciones pertenecientes al usuario autenticado.
        """
        registros, total = PlanificacionRepository.listar_por_usuario_paginado(
            db=db,
            id_usuario=usuario_actual.id_usuario,
            pagina=pagina,
            limite=limite,
            estado=estado
        )
        total_paginas = (total + limite - 1) // limite if total > 0 else 0

        return {
            "total": total,
            "pagina": pagina,
            "limite": limite,
            "total_paginas": total_paginas,
            "planificaciones": registros
        }

    @staticmethod
    def obtener_por_id(
        db: Session,
        id_planificacion: int,
        usuario_actual: Usuario
    ) -> Planificacion:
        """
        Consulta el detalle de una planificación verificando estricta propiedad de los datos.
        """
        planificacion = PlanificacionRepository.buscar_por_id(db, id_planificacion)
        if not planificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planificación con ID {id_planificacion} no encontrada."
            )

        verificar_propiedad_planificacion(planificacion, usuario_actual)
        return planificacion

    @staticmethod
    def actualizar_planificacion(
        db: Session,
        id_planificacion: int,
        datos: ActualizarPlanificacionSchema,
        usuario_actual: Usuario
    ) -> Planificacion:
        """
        Modifica una planificación gastronómica existente siempre que no esté cancelada.
        Sincroniza el conjunto de preferencias específicas de la planificación.
        """
        planificacion = PlanificacionRepository.buscar_por_id(db, id_planificacion)
        if not planificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planificación con ID {id_planificacion} no encontrada."
            )

        verificar_propiedad_planificacion(planificacion, usuario_actual)

        if planificacion.estado == "CANCELADA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede modificar una planificación que ha sido cancelada."
            )

        if datos.presupuesto is not None:
            if datos.presupuesto <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El presupuesto disponible debe ser mayor que cero."
                )
            planificacion.presupuesto = datos.presupuesto

        if datos.cantidad_personas is not None:
            if datos.cantidad_personas <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La cantidad de personas debe ser mayor que cero."
                )
            planificacion.cantidad_personas = datos.cantidad_personas

        if datos.tipo_comida is not None:
            planificacion.tipo_comida = datos.tipo_comida.strip().upper()

        if datos.ubicacion_referencia is not None:
            planificacion.ubicacion_referencia = datos.ubicacion_referencia.strip()

        ids_a_sincronizar: Optional[List[int]] = None
        if datos.preferencias is not None:
            ids_unicos = list(dict.fromkeys(datos.preferencias))
            if ids_unicos:
                activas = PreferenciaRepository.buscar_activas_por_ids(db, ids_unicos)
                ids_encontrados = {p.id_preferencia for p in activas}
                no_encontrados = [i for i in ids_unicos if i not in ids_encontrados]
                if no_encontrados:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Las siguientes preferencias no existen o no están activas en el catálogo: {no_encontrados}"
                    )
            ids_a_sincronizar = ids_unicos

        return PlanificacionRepository.actualizar_planificacion(
            db=db,
            planificacion=planificacion,
            ids_preferencias=ids_a_sincronizar
        )

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_planificacion: int,
        nuevo_estado: str,
        usuario_actual: Usuario
    ) -> Planificacion:
        """
        Cambia el estado lógico de una planificación (ej. cancelación lógica).
        """
        planificacion = PlanificacionRepository.buscar_por_id(db, id_planificacion)
        if not planificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planificación con ID {id_planificacion} no encontrada."
            )

        verificar_propiedad_planificacion(planificacion, usuario_actual)
        estado_limpio = nuevo_estado.strip().upper()

        return PlanificacionRepository.cambiar_estado(
            db=db,
            planificacion=planificacion,
            nuevo_estado=estado_limpio
        )
