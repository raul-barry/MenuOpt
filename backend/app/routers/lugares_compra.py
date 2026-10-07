# CASO DE USO: CU16 - Consultar lugares de compra
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.lugar_compra import (
    CrearLugarCompraSchema,
    ActualizarLugarCompraSchema,
    CambiarEstadoLugarCompraSchema,
    LugarCompraRespuestaSchema,
)
from app.schemas.ingrediente_lugar_compra import (
    AsociarIngredienteLugarCompraSchema,
    ActualizarIngredienteLugarCompraSchema,
    IngredienteLugarCompraRespuestaSchema,
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.lugar_compra_service import LugarCompraService

router = APIRouter(
    prefix="/lugares-compra",
    tags=["Lugares de Compra"]
)


# =========================================================================
# ADMINISTRACIÓN DE LUGARES DE COMPRA (SOLO ADMINISTRADOR / CONSULTA PÚBLICA)
# =========================================================================

# --- Registrar nuevo lugar de compra ---
# Endpoint: POST /lugares-compra
# Acceso: Rol ADMINISTRADOR
@router.post(
    "",
    response_model=LugarCompraRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU16: Registrar nuevo lugar de compra",
    description="Crea un establecimiento comercial donde pueden adquirirse ingredientes."
)
def crear_lugar_compra(
    datos: CrearLugarCompraSchema,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para registrar un lugar de compra (CU16).
    """
    return LugarCompraService.crear_lugar(db=db, datos=datos, usuario_actual=usuario_actual)


# --- Consultar listado de lugares de compra ---
# Endpoint: GET /lugares-compra
# Acceso: Usuarios autenticados
@router.get(
    "",
    response_model=List[LugarCompraRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU16: Listar lugares de compra",
    description="Devuelve el catálogo de establecimientos registrados con filtros opcionales."
)
def listar_lugares_compra(
    estado: Optional[str] = Query(None, description="Filtrar por estado (ACTIVO / INACTIVO)"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (MERCADO, SUPERMERCADO, etc.)"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar lugares de compra (CU16).
    """
    return LugarCompraService.listar_lugares(db=db, estado=estado, tipo=tipo)


# --- Consultar detalle de un lugar de compra ---
# Endpoint: GET /lugares-compra/{id_lugar_compra}
# Acceso: Usuarios autenticados
@router.get(
    "/{id_lugar_compra}",
    response_model=LugarCompraRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU16: Consultar detalle de un lugar de compra",
    description="Muestra la información de contacto y localización de un establecimiento específico."
)
def obtener_lugar_compra(
    id_lugar_compra: int = Path(..., ge=1, description="ID del lugar de compra"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para ver detalle de un lugar de compra (CU16).
    """
    return LugarCompraService.obtener_lugar(db=db, id_lugar_compra=id_lugar_compra)


# --- Modificar información del lugar de compra ---
# Endpoint: PUT /lugares-compra/{id_lugar_compra}
# Acceso: Rol ADMINISTRADOR
@router.put(
    "/{id_lugar_compra}",
    response_model=LugarCompraRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU16: Modificar datos de un lugar de compra",
    description="Actualiza nombre, tipo, teléfono o ubicación del establecimiento."
)
def actualizar_lugar_compra(
    datos: ActualizarLugarCompraSchema,
    id_lugar_compra: int = Path(..., ge=1, description="ID del lugar de compra"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para modificar datos de un lugar de compra (CU16).
    """
    return LugarCompraService.actualizar_lugar(
        db=db,
        id_lugar_compra=id_lugar_compra,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- Cambiar estado lógico del lugar de compra ---
# Endpoint: PATCH /lugares-compra/{id_lugar_compra}/estado
# Acceso: Rol ADMINISTRADOR
@router.patch(
    "/{id_lugar_compra}/estado",
    response_model=LugarCompraRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU16: Cambiar estado del lugar de compra (ACTIVO / INACTIVO)",
    description="Activa o desactiva lógicamente el establecimiento comercial."
)
def cambiar_estado_lugar_compra(
    datos: CambiarEstadoLugarCompraSchema,
    id_lugar_compra: int = Path(..., ge=1, description="ID del lugar de compra"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para activar o desactivar lugar de compra (CU16).
    """
    return LugarCompraService.cambiar_estado(
        db=db,
        id_lugar_compra=id_lugar_compra,
        nuevo_estado=datos.estado,
        usuario_actual=usuario_actual
    )


# =========================================================================
# ASOCIACIÓN Y GESTIÓN DE PRECIOS POR INGREDIENTE EN ESTABLECIMIENTOS
# =========================================================================

# --- Asociar ingrediente y precio a un lugar de compra ---
# Endpoint: POST /lugares-compra/{id_lugar_compra}/ingredientes
# Acceso: Rol ADMINISTRADOR
@router.post(
    "/{id_lugar_compra}/ingredientes",
    response_model=IngredienteLugarCompraRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU16: Asociar ingrediente y precio a lugar de compra",
    description="Registra la disponibilidad y precio comercial de un ingrediente en el establecimiento."
)
def asociar_ingrediente_a_lugar(
    datos: AsociarIngredienteLugarCompraSchema,
    id_lugar_compra: int = Path(..., ge=1, description="ID del lugar de compra"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para asociar ingrediente y precio al establecimiento (CU16).
    """
    return LugarCompraService.asociar_ingrediente(
        db=db,
        id_lugar_compra=id_lugar_compra,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- Listar ingredientes comercializados en un lugar de compra ---
# Endpoint: GET /lugares-compra/{id_lugar_compra}/ingredientes
# Acceso: Usuarios autenticados
@router.get(
    "/{id_lugar_compra}/ingredientes",
    response_model=List[IngredienteLugarCompraRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU16: Consultar ingredientes registrados en un lugar de compra",
    description="Devuelve el catálogo de insumos comercializados por este establecimiento."
)
def listar_ingredientes_de_lugar(
    id_lugar_compra: int = Path(..., ge=1, description="ID del lugar de compra"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar insumos de un lugar de compra (CU16).
    """
    return LugarCompraService.listar_ingredientes_de_lugar(db=db, id_lugar_compra=id_lugar_compra)


# --- Actualizar precio o disponibilidad de un ingrediente en un lugar ---
# Endpoint: PUT /lugares-compra/{id_lugar_compra}/ingredientes/{id_ingrediente}
# Acceso: Rol ADMINISTRADOR
@router.put(
    "/{id_lugar_compra}/ingredientes/{id_ingrediente}",
    response_model=IngredienteLugarCompraRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU16: Modificar precio o disponibilidad de un ingrediente en un lugar",
    description="Actualiza el precio, cantidad de referencia o estado de stock del insumo."
)
def actualizar_ingrediente_en_lugar(
    datos: ActualizarIngredienteLugarCompraSchema,
    id_lugar_compra: int = Path(..., ge=1, description="ID del lugar de compra"),
    id_ingrediente: int = Path(..., ge=1, description="ID del ingrediente"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para modificar precio o stock de ingrediente en un lugar (CU16).
    """
    return LugarCompraService.actualizar_ingrediente_en_lugar(
        db=db,
        id_lugar_compra=id_lugar_compra,
        id_ingrediente=id_ingrediente,
        datos=datos,
        usuario_actual=usuario_actual
    )
