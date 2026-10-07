from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.categoria import (
    CrearCategoriaSchema,
    ActualizarCategoriaSchema,
    CategoriaRespuestaSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.categoria_service import CategoriaService

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"]
)


# =========================================================================
# CASO DE USO: CU07 - GESTIONAR CATEGORÍAS
# =========================================================================

# --- CU07: Consultar Categorías ---
# Endpoint: GET /categorias
# Acceso: Usuarios autenticados
@router.get(
    "",
    response_model=List[CategoriaRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU07: Consultar categorías activas",
    description="Devuelve el catálogo de categorías activas para asignación de platos."
)
def listar_categorias(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar categorías (CU07).
    """
    solo_activas = True
    if usuario_actual.rol and usuario_actual.rol.nombre == "ADMINISTRADOR":
        solo_activas = False
    return CategoriaService.listar_categorias(db=db, solo_activas=solo_activas)


# --- CU07: Crear Categoría Global ---
# Endpoint: POST /categorias
# Acceso: Solo ADMINISTRADOR
@router.post(
    "",
    response_model=CategoriaRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU07: Crear nueva categoría (Solo Administrador)",
    description="Agrega una nueva categoría al catálogo global de la plataforma."
)
def crear_categoria(
    datos: CrearCategoriaSchema,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para crear categoría global (CU07).
    """
    return CategoriaService.crear_categoria(db=db, datos=datos)


# --- CU07: Modificar Categoría Global ---
# Endpoint: PUT /categorias/{id_categoria}
# Acceso: Solo ADMINISTRADOR
@router.put(
    "/{id_categoria}",
    response_model=CategoriaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU07: Modificar categoría (Solo Administrador)",
    description="Actualiza el nombre, descripción o estado activo de una categoría del catálogo global."
)
def actualizar_categoria(
    datos: ActualizarCategoriaSchema,
    id_categoria: int = Path(..., ge=1, description="ID de la categoría a modificar"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para actualizar categoría global (CU07).
    """
    return CategoriaService.actualizar_categoria(
        db=db,
        id_categoria=id_categoria,
        datos=datos
    )
