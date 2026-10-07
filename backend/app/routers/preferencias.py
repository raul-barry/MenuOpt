from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.preferencia import (
    PreferenciaRespuestaSchema,
    CrearPreferenciaSchema,
    ActualizarPreferenciaSchema,
    CambiarEstadoPreferenciaSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.preferencia_service import PreferenciaService

router = APIRouter(
    prefix="/preferencias",
    tags=["Preferencias"]
)


# =========================================================================
# CASO DE USO: CU12 - DEFINIR PREFERENCIAS
# =========================================================================

# --- CU12: Consultar Catálogo de Preferencias ---
# Endpoint: GET /preferencias
# Acceso: Usuarios autenticados
@router.get(
    "",
    response_model=List[PreferenciaRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU12: Consultar catálogo de preferencias activas",
    description="Devuelve el catálogo de preferencias gastronómicas activas para selección."
)
def listar_preferencias(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar el catálogo de preferencias (CU12).
    Si el usuario es ADMINISTRADOR, lista todas las preferencias (activas e inactivas).
    """
    solo_activas = True
    if usuario_actual.rol and usuario_actual.rol.nombre == "ADMINISTRADOR":
        solo_activas = False
    return PreferenciaService.listar_catalogo(db=db, solo_activas=solo_activas)


# --- CU12: Crear Preferencia en Catálogo ---
# Endpoint: POST /preferencias
# Acceso: Exclusivo para ADMINISTRADOR
@router.post(
    "",
    response_model=PreferenciaRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU12: Crear nueva preferencia en el catálogo (Solo Administrador)",
    description="Agrega una nueva opción al catálogo general de preferencias gastronómicas."
)
def crear_preferencia(
    datos: CrearPreferenciaSchema,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para crear preferencia en el catálogo (CU12).
    """
    return PreferenciaService.crear_preferencia(db=db, datos=datos)


# --- CU12: Modificar Preferencia del Catálogo ---
# Endpoint: PUT /preferencias/{id_preferencia}
# Acceso: Exclusivo para ADMINISTRADOR
@router.put(
    "/{id_preferencia}",
    response_model=PreferenciaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU12: Modificar preferencia del catálogo (Solo Administrador)",
    description="Actualiza nombre, tipo o descripción de una preferencia en el catálogo."
)
def actualizar_preferencia(
    datos: ActualizarPreferenciaSchema,
    id_preferencia: int = Path(..., ge=1, description="ID de la preferencia"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para modificar preferencia del catálogo (CU12).
    """
    return PreferenciaService.actualizar_preferencia(
        db=db,
        id_preferencia=id_preferencia,
        datos=datos
    )


# --- CU12: Cambiar Estado Activo de Preferencia ---
# Endpoint: PATCH /preferencias/{id_preferencia}/estado
# Acceso: Exclusivo para ADMINISTRADOR
@router.patch(
    "/{id_preferencia}/estado",
    response_model=PreferenciaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU12: Activar o desactivar preferencia (Solo Administrador)",
    description="Habilita o deshabilita la disponibilidad de una preferencia en el catálogo."
)
def cambiar_estado_preferencia(
    datos: CambiarEstadoPreferenciaSchema,
    id_preferencia: int = Path(..., ge=1, description="ID de la preferencia"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para activar o desactivar preferencia del catálogo (CU12).
    """
    return PreferenciaService.cambiar_estado(
        db=db,
        id_preferencia=id_preferencia,
        activo=datos.activo
    )
