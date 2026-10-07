from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.planificacion import (
    CrearPlanificacionSchema,
    ActualizarPlanificacionSchema,
    CambiarEstadoPlanificacionSchema,
    PlanificacionRespuestaSchema,
    PlanificacionesPaginadasSchema
)
from app.security.dependencias import obtener_usuario_actual
from app.services.planificacion_service import PlanificacionService

router = APIRouter(
    prefix="/planificaciones",
    tags=["Planificaciones"]
)


# =========================================================================
# CASO DE USO: CU11 - REGISTRAR PLANIFICACIÓN GASTRONÓMICA
# =========================================================================

# --- CU11: Registrar Planificación ---
# Endpoint: POST /planificaciones
# Acceso: Usuarios autenticados (Consumidores)
@router.post(
    "",
    response_model=PlanificacionRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU11: Registrar nueva planificación gastronómica",
    description="Permite a un consumidor registrar su solicitud de planificación gastronómica con presupuesto, cantidad de personas, tipo de comida, ubicación de referencia y preferencias."
)
def registrar_planificacion(
    datos: CrearPlanificacionSchema,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para registrar una planificación gastronómica (CU11).
    """
    return PlanificacionService.crear_planificacion(
        db=db,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- CU11: Consultar Mis Planificaciones ---
# Endpoint: GET /planificaciones/mis-planificaciones
# Acceso: Usuarios autenticados
@router.get(
    "/mis-planificaciones",
    response_model=PlanificacionesPaginadasSchema,
    status_code=status.HTTP_200_OK,
    summary="CU11: Consultar mis planificaciones",
    description="Devuelve el historial paginado de planificaciones gastronómicas del usuario autenticado."
)
def listar_mis_planificaciones(
    pagina: int = Query(1, ge=1, description="Número de página"),
    limite: int = Query(10, ge=1, le=100, description="Cantidad de registros por página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (ej. ACTIVA, CANCELADA, BORRADOR)"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar las planificaciones propias (CU11).
    """
    return PlanificacionService.listar_mis_planificaciones(
        db=db,
        usuario_actual=usuario_actual,
        pagina=pagina,
        limite=limite,
        estado=estado
    )


# --- CU11: Consultar Detalle de una Planificación ---
# Endpoint: GET /planificaciones/{id_planificacion}
# Acceso: Dueño de la planificación o ADMINISTRADOR
@router.get(
    "/{id_planificacion}",
    response_model=PlanificacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU11: Consultar detalle de una planificación",
    description="Obtiene los datos de una planificación específica y sus preferencias asociadas, verificando titularidad del usuario."
)
def obtener_planificacion(
    id_planificacion: int = Path(..., ge=1, description="ID de la planificación a consultar"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar una planificación por ID con validación de propiedad (CU11).
    """
    return PlanificacionService.obtener_por_id(
        db=db,
        id_planificacion=id_planificacion,
        usuario_actual=usuario_actual
    )


# --- CU11: Modificar Planificación ---
# Endpoint: PUT /planificaciones/{id_planificacion}
# Acceso: Dueño de la planificación o ADMINISTRADOR
@router.put(
    "/{id_planificacion}",
    response_model=PlanificacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU11: Modificar datos de una planificación",
    description="Actualiza el presupuesto, personas, tipo de comida, ubicación y sincroniza las preferencias de la planificación mientras esté activa."
)
def actualizar_planificacion(
    datos: ActualizarPlanificacionSchema,
    id_planificacion: int = Path(..., ge=1, description="ID de la planificación a modificar"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para modificar una planificación (CU11).
    """
    return PlanificacionService.actualizar_planificacion(
        db=db,
        id_planificacion=id_planificacion,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- CU11: Cambiar Estado / Cancelar Planificación ---
# Endpoint: PATCH /planificaciones/{id_planificacion}/estado
# Acceso: Dueño de la planificación o ADMINISTRADOR
@router.patch(
    "/{id_planificacion}/estado",
    response_model=PlanificacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU11: Cambiar estado o cancelar planificación",
    description="Aplica cambio de estado lógico sobre la planificación (ej. ACTIVA -> CANCELADA)."
)
def cambiar_estado_planificacion(
    datos: CambiarEstadoPlanificacionSchema,
    id_planificacion: int = Path(..., ge=1, description="ID de la planificación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para cambiar estado o cancelar una planificación lógicamente (CU11).
    """
    return PlanificacionService.cambiar_estado(
        db=db,
        id_planificacion=id_planificacion,
        nuevo_estado=datos.estado,
        usuario_actual=usuario_actual
    )
