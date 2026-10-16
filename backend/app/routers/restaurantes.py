from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.restaurante import (
    RegistrarRestauranteSchema,
    ActualizarRestauranteSchema,
    CambiarEstadoRestauranteSchema,
    RestauranteRespuestaSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.restaurante_service import RestauranteService
from app.repositories.restaurante_repository import RestauranteRepository

router = APIRouter(
    prefix="/restaurantes",
    tags=["Restaurantes"]
)


# =========================================================================
# CASO DE USO: CU05 - REGISTRAR RESTAURANTE
# Endpoint: POST /restaurantes
# Acceso: Rol RESTAURANTE o ADMINISTRADOR
# =========================================================================
@router.post(
    "",
    response_model=RestauranteRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU05: Registrar nuevo restaurante con ubicación",
    description="Crea un nuevo restaurante y su ubicación asignando al usuario autenticado como responsable."
)
def registrar_restaurante(
    datos: RegistrarRestauranteSchema,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para el registro de restaurantes (CU05).
    """
    return RestauranteService.registrar_restaurante(
        db=db,
        datos=datos,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CASO DE USO: CU06 - GESTIONAR RESTAURANTE
# =========================================================================

# --- Listar Todos los Restaurantes (Catálogo general para clientes y reservas) ---
# Endpoint: GET /restaurantes
# Acceso: Cualquier usuario autenticado
@router.get(
    "",
    response_model=List[RestauranteRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los restaurantes",
    description="Devuelve el catálogo de restaurantes para consulta general y reservas."
)
def listar_restaurantes_catalogo(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar restaurantes para catálogo general.
    """
    return RestauranteRepository.listar_todos(db)


# --- CU06: Consultar Mis Restaurantes ---
# Endpoint: GET /restaurantes/mis-restaurantes
# Acceso: Rol RESTAURANTE o ADMINISTRADOR
@router.get(
    "/mis-restaurantes",
    response_model=List[RestauranteRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU06: Consultar restaurantes del usuario autenticado",
    description="Devuelve la lista de establecimientos a cargo del usuario autenticado."
)
def listar_mis_restaurantes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para listar restaurantes propios (CU06).
    """
    return RestauranteService.listar_mis_restaurantes(db=db, usuario_actual=usuario_actual)


# --- CU06: Consultar Detalle de Restaurante ---
# Endpoint: GET /restaurantes/{id_restaurante}
# Acceso: Cualquier usuario autenticado
@router.get(
    "/{id_restaurante}",
    response_model=RestauranteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU06: Consultar detalle de un restaurante",
    description="Devuelve la información comercial y de localización de un restaurante específico."
)
def obtener_restaurante(
    id_restaurante: int = Path(..., ge=1, description="ID del restaurante a consultar"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para obtener detalle de un restaurante (CU06).
    """
    return RestauranteService.obtener_restaurante_por_id(
        db=db,
        id_restaurante=id_restaurante,
        usuario_actual=usuario_actual
    )


# --- CU06: Modificar Información del Restaurante ---
# Endpoint: PUT /restaurantes/{id_restaurante}
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.put(
    "/{id_restaurante}",
    response_model=RestauranteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU06: Modificar datos y ubicación del restaurante",
    description="Actualiza la información comercial y geográfica verificando la titularidad del restaurante."
)
def actualizar_restaurante(
    datos: ActualizarRestauranteSchema,
    id_restaurante: int = Path(..., ge=1, description="ID del restaurante"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para modificar restaurante (CU06).
    """
    return RestauranteService.actualizar_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- CU06: Cambiar Estado Lógico del Restaurante ---
# Endpoint: PATCH /restaurantes/{id_restaurante}/estado
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.patch(
    "/{id_restaurante}/estado",
    response_model=RestauranteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU06: Cambiar estado del restaurante (ACTIVO / INACTIVO)",
    description="Aplica activación o desactivación lógica al establecimiento."
)
def cambiar_estado_restaurante(
    datos: CambiarEstadoRestauranteSchema,
    id_restaurante: int = Path(..., ge=1, description="ID del restaurante"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para activar o desactivar restaurante (CU06).
    """
    return RestauranteService.cambiar_estado(
        db=db,
        id_restaurante=id_restaurante,
        nuevo_estado=datos.estado,
        usuario_actual=usuario_actual
    )
