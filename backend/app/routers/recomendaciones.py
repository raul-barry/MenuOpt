# CASO DE USO: CU13 - Generar recomendación
# CASO DE USO: CU14 - Comparar restaurantes
# CASO DE USO: CU15 - Consultar ingredientes para preparación propia
# CASO DE USO: CU16 - Consultar lugares de compra
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.recomendacion import RecomendacionRespuestaSchema
from app.schemas.comparacion import ComparacionPlanificacionRespuestaSchema
from app.schemas.preparacion_propia import (
    PreparacionPropiaRespuestaSchema,
    LugaresCompraRecomendacionRespuestaSchema,
)
from app.security.dependencias import obtener_usuario_actual
from app.services.recomendacion_service import RecomendacionService
from app.services.preparacion_service import PreparacionService

router = APIRouter(
    tags=["Recomendaciones"]
)


# =========================================================================
# CASO DE USO: CU13 - GENERAR RECOMENDACIÓN
# =========================================================================

# --- CU13: Generar recomendaciones para una planificación ---
# Endpoint: POST /planificaciones/{id_planificacion}/recomendaciones/generar
# Acceso: Titular de la planificación o ADMINISTRADOR
@router.post(
    "/planificaciones/{id_planificacion}/recomendaciones/generar",
    response_model=List[RecomendacionRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU13: Generar recomendaciones de restaurantes",
    description="Sugiere restaurantes y platos que satisfacen el presupuesto, la cantidad de comensales, la zona y las preferencias de la planificación."
)
def generar_recomendaciones(
    id_planificacion: int = Path(..., ge=1, description="ID de la planificación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para disparar la generación transaccional de recomendaciones (CU13).
    """
    return RecomendacionService.generar_recomendaciones(
        db=db,
        id_planificacion=id_planificacion,
        usuario_actual=usuario_actual
    )


# --- CU13: Listar recomendaciones persistidas para una planificación ---
# Endpoint: GET /planificaciones/{id_planificacion}/recomendaciones
# Acceso: Titular de la planificación o ADMINISTRADOR
@router.get(
    "/planificaciones/{id_planificacion}/recomendaciones",
    response_model=List[RecomendacionRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU13: Consultar recomendaciones guardadas",
    description="Retorna las recomendaciones de restaurantes generadas para la planificación."
)
def listar_recomendaciones_planificacion(
    id_planificacion: int = Path(..., ge=1, description="ID de la planificación"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (ej. RESTAURANTE, PREPARACION_PROPIA)"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar recomendaciones de una planificación (CU13).
    """
    return RecomendacionService.listar_recomendaciones(
        db=db,
        id_planificacion=id_planificacion,
        usuario_actual=usuario_actual,
        tipo_recomendacion=tipo
    )


# --- CU13: Detalle de una recomendación específica ---
# Endpoint: GET /recomendaciones/{id_recomendacion}
# Acceso: Titular de la planificación o ADMINISTRADOR
@router.get(
    "/recomendaciones/{id_recomendacion}",
    response_model=RecomendacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU13: Consultar detalle de una recomendación",
    description="Retorna el desglose general de una recomendación (Restaurante o Preparación Propia)."
)
def obtener_detalle_recomendacion(
    id_recomendacion: int = Path(..., ge=1, description="ID de la recomendación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para obtener detalle de una recomendación (CU13).
    """
    return RecomendacionService.obtener_recomendacion(
        db=db,
        id_recomendacion=id_recomendacion,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CASO DE USO: CU15 - CONSULTAR INGREDIENTES PARA PREPARACIÓN PROPIA
# =========================================================================

# --- CU15: Consultar detalle de ingredientes de una preparación propia ---
# Endpoint: GET /recomendaciones/{id_recomendacion}/preparacion
# Acceso: Titular de la planificación o ADMINISTRADOR
@router.get(
    "/recomendaciones/{id_recomendacion}/preparacion",
    response_model=PreparacionPropiaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU15: Consultar ingredientes para preparación propia",
    description="Retorna el desglose detallado de ingredientes, cantidades escaladas, costos y lugares sugeridos para una recomendación de tipo PREPARACION_PROPIA."
)
def obtener_detalle_preparacion_propia(
    id_recomendacion: int = Path(..., ge=1, description="ID de la recomendación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar ingredientes de la preparación propia (CU15).
    """
    return PreparacionService.obtener_preparacion_por_recomendacion(
        db=db,
        id_recomendacion=id_recomendacion,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CASO DE USO: CU16 - CONSULTAR LUGARES DE COMPRA
# =========================================================================

# --- CU16: Consultar lugares de compra agrupados para una recomendación ---
# Endpoint: GET /recomendaciones/{id_recomendacion}/lugares-compra
# Acceso: Titular de la planificación o ADMINISTRADOR
@router.get(
    "/recomendaciones/{id_recomendacion}/lugares-compra",
    response_model=LugaresCompraRecomendacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU16: Consultar lugares de compra de una preparación propia",
    description="Retorna la lista de compras agrupada por establecimiento comercial para optimizar la adquisición física de los insumos."
)
def obtener_lugares_compra_recomendacion(
    id_recomendacion: int = Path(..., ge=1, description="ID de la recomendación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar lugares de compra agrupados (CU16).
    """
    return PreparacionService.obtener_lugares_compra_recomendacion(
        db=db,
        id_recomendacion=id_recomendacion,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CASO DE USO: CU14 - COMPARAR RESTAURANTES
# =========================================================================

# --- CU14: Comparar alternativas de una planificación ---
# Endpoint: GET /planificaciones/{id_planificacion}/comparacion
# Acceso: Titular de la planificación o ADMINISTRADOR
@router.get(
    "/planificaciones/{id_planificacion}/comparacion",
    response_model=ComparacionPlanificacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU14: Comparar restaurantes",
    description="Compara los restaurantes recomendados para la planificación según costo, ahorro, puntuación y distancia."
)
def comparar_alternativas_planificacion(
    id_planificacion: int = Path(..., ge=1, description="ID de la planificación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para la comparación de restaurantes recomendados (CU14).
    """
    return RecomendacionService.comparar_alternativas(
        db=db,
        id_planificacion=id_planificacion,
        usuario_actual=usuario_actual
    )
