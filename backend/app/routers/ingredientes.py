from typing import Optional, List
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.ingrediente import (
    CrearIngredienteSchema,
    ActualizarIngredienteSchema,
    IngredienteRespuestaSchema
)
from app.schemas.ingrediente_lugar_compra import LugarCompraParaIngredienteRespuestaSchema
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.ingrediente_service import IngredienteService
from app.services.lugar_compra_service import LugarCompraService

router = APIRouter(
    prefix="/ingredientes",
    tags=["Ingredientes"]
)


# =========================================================================
# CASO DE USO: CU09 - GESTIONAR INGREDIENTES (Catálogo General)
# =========================================================================

# --- CU09: Consultar Catálogo de Ingredientes ---
# Endpoint: GET /ingredientes
# Acceso: Usuarios autenticados
@router.get(
    "",
    response_model=List[IngredienteRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU09: Consultar catálogo de ingredientes",
    description="Devuelve el catálogo de ingredientes disponibles para la elaboración de platos."
)
def listar_ingredientes(
    estado: Optional[str] = Query(None, description="Filtrar por estado (ej. ACTIVO, INACTIVO)"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar ingredientes del catálogo (CU09).
    """
    return IngredienteService.listar_ingredientes(db=db, estado=estado)


# --- CU09: Registrar Nuevo Ingrediente ---
# Endpoint: POST /ingredientes
# Acceso: Rol RESTAURANTE o ADMINISTRADOR
@router.post(
    "",
    response_model=IngredienteRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU09: Registrar nuevo ingrediente",
    description="Permite a un restaurante o administrador proponer un nuevo ingrediente al catálogo global."
)
def crear_ingrediente(
    datos: CrearIngredienteSchema,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para crear ingrediente en el catálogo (CU09).
    """
    return IngredienteService.crear_ingrediente(db=db, datos=datos)


# --- CU09: Obtener Detalle de Ingrediente ---
# Endpoint: GET /ingredientes/{id_ingrediente}
# Acceso: Usuarios autenticados
@router.get(
    "/{id_ingrediente}",
    response_model=IngredienteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU09: Consultar detalle de un ingrediente",
    description="Muestra los detalles de un ingrediente específico por su ID."
)
def obtener_ingrediente(
    id_ingrediente: int = Path(..., ge=1, description="ID del ingrediente"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para obtener detalle de un ingrediente (CU09).
    """
    return IngredienteService.obtener_por_id(db=db, id_ingrediente=id_ingrediente)


# --- CU09: Modificar Ingrediente Global ---
# Endpoint: PUT /ingredientes/{id_ingrediente}
# Acceso: Solo ADMINISTRADOR
@router.put(
    "/{id_ingrediente}",
    response_model=IngredienteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU09: Modificar ingrediente del catálogo (Solo Administrador)",
    description="Actualiza la unidad de medida, precio estimado o nombre de un ingrediente en el catálogo global."
)
def actualizar_ingrediente(
    datos: ActualizarIngredienteSchema,
    id_ingrediente: int = Path(..., ge=1, description="ID del ingrediente"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para modificar ingrediente del catálogo (CU09).
    """
    return IngredienteService.actualizar_ingrediente(
        db=db,
        id_ingrediente=id_ingrediente,
        datos=datos
    )


# =========================================================================
# CASO DE USO: CU16 - CONSULTAR LUGARES DE COMPRA PARA UN INGREDIENTE
# =========================================================================

# --- CU16: Consultar Lugares de Compra para un Ingrediente ---
# Endpoint: GET /ingredientes/{id_ingrediente}/lugares-compra
# Acceso: Usuarios autenticados
@router.get(
    "/{id_ingrediente}/lugares-compra",
    response_model=List[LugarCompraParaIngredienteRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU16: Consultar lugares de compra para un ingrediente",
    description="Retorna la lista de establecimientos comerciales activos donde se comercializa el ingrediente, ordenados por menor precio."
)
def listar_lugares_de_ingrediente(
    id_ingrediente: int = Path(..., ge=1, description="ID del ingrediente"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar qué establecimientos venden este ingrediente (CU16).
    """
    return LugarCompraService.listar_lugares_de_ingrediente(db=db, id_ingrediente=id_ingrediente)

