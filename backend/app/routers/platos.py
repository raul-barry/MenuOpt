from typing import Optional, List
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.plato import (
    CrearPlatoSchema,
    ActualizarPlatoSchema,
    CambiarEstadoPlatoSchema,
    CambiarDisponibilidadPlatoSchema,
    PlatoRespuestaSchema
)
from app.schemas.plato_ingrediente import (
    AsociarIngredientePlatoSchema,
    ActualizarIngredientePlatoSchema,
    PlatoIngredienteDetalleSchema
)
from app.schemas.plato_preferencia import (
    ActualizarPreferenciasPlatoSchema,
    PlatoPreferenciasRespuestaSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.plato_service import PlatoService

router = APIRouter(
    tags=["Platos"]
)


# =========================================================================
# CASO DE USO: CU08 - GESTIONAR PLATOS
# =========================================================================

# --- CU08: Listar Platos de un Restaurante ---
# Endpoint: GET /restaurantes/{id_restaurante}/platos
# Acceso: Usuarios autenticados
@router.get(
    "/restaurantes/{id_restaurante}/platos",
    response_model=List[PlatoRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU08: Consultar platos de un restaurante",
    description="Devuelve la carta gastronómica de un restaurante con filtros por categoría, tipo de comida o disponibilidad."
)
def listar_platos_restaurante(
    id_restaurante: int = Path(..., ge=1, description="ID del restaurante"),
    categoria: Optional[int] = Query(None, description="Filtrar por ID de categoría"),
    tipo_comida: Optional[str] = Query(None, description="Filtrar por tipo de comida"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (ACTIVO / INACTIVO)"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para listar platos de un restaurante (CU08).
    """
    return PlatoService.listar_platos_por_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        id_categoria=categoria,
        tipo_comida=tipo_comida,
        disponible=disponible,
        estado=estado
    )


# --- CU08: Registrar Nuevo Plato en Restaurante ---
# Endpoint: POST /restaurantes/{id_restaurante}/platos
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.post(
    "/restaurantes/{id_restaurante}/platos",
    response_model=PlatoRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU08: Crear un plato en el restaurante",
    description="Registra un nuevo plato en el restaurante especificado previa validación de titularidad."
)
def crear_plato(
    datos: CrearPlatoSchema,
    id_restaurante: int = Path(..., ge=1, description="ID del restaurante"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para crear plato en un restaurante (CU08).
    """
    return PlatoService.crear_plato(
        db=db,
        id_restaurante=id_restaurante,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- CU08: Consultar Detalle de un Plato ---
# Endpoint: GET /platos/{id_plato}
# Acceso: Usuarios autenticados
@router.get(
    "/platos/{id_plato}",
    response_model=PlatoRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU08: Consultar detalle de un plato",
    description="Muestra los detalles de un plato específico."
)
def obtener_plato(
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para obtener detalle de un plato (CU08).
    """
    return PlatoService.obtener_plato_por_id(db=db, id_plato=id_plato)


# --- CU08: Modificar Plato ---
# Endpoint: PUT /platos/{id_plato}
# Acceso: Solo responsable del restaurante del plato o ADMINISTRADOR
@router.put(
    "/platos/{id_plato}",
    response_model=PlatoRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU08: Modificar datos de un plato",
    description="Actualiza la receta, precio, categoría o porciones del plato verificando titularidad."
)
def actualizar_plato(
    datos: ActualizarPlatoSchema,
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para modificar plato (CU08).
    """
    return PlatoService.actualizar_plato(
        db=db,
        id_plato=id_plato,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- CU08: Cambiar Estado del Plato (Activación / Desactivación Lógica) ---
# Endpoint: PATCH /platos/{id_plato}/estado
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.patch(
    "/platos/{id_plato}/estado",
    response_model=PlatoRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU08: Desactivar o activar un plato",
    description="Cambia el estado lógico del plato (ACTIVO / INACTIVO)."
)
def cambiar_estado_plato(
    datos: CambiarEstadoPlatoSchema,
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para activar o desactivar plato lógicamente (CU08).
    """
    return PlatoService.cambiar_estado(
        db=db,
        id_plato=id_plato,
        nuevo_estado=datos.estado,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CASO DE USO: CU09 - COMPOSICIÓN DE PLATOS E INGREDIENTES
# =========================================================================

# --- CU09: Relacionar Ingrediente con Plato ---
# Endpoint: POST /platos/{id_plato}/ingredientes
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.post(
    "/platos/{id_plato}/ingredientes",
    response_model=PlatoIngredienteDetalleSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU09: Asignar ingrediente a un plato",
    description="Vincula un ingrediente del catálogo al plato con su cantidad y unidad de medida."
)
def asociar_ingrediente(
    datos: AsociarIngredientePlatoSchema,
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para asignar ingrediente a plato (CU09).
    """
    return PlatoService.asociar_ingrediente(
        db=db,
        id_plato=id_plato,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- CU09: Consultar Ingredientes de un Plato ---
# Endpoint: GET /platos/{id_plato}/ingredientes
# Acceso: Usuarios autenticados
@router.get(
    "/platos/{id_plato}/ingredientes",
    response_model=List[PlatoIngredienteDetalleSchema],
    status_code=status.HTTP_200_OK,
    summary="CU09: Consultar ingredientes de un plato",
    description="Retorna la lista de ingredientes que componen la receta del plato."
)
def listar_ingredientes_plato(
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar ingredientes del plato (CU09).
    """
    return PlatoService.listar_ingredientes_de_plato(db=db, id_plato=id_plato)


# --- CU09: Modificar Ingrediente de un Plato ---
# Endpoint: PUT /platos/{id_plato}/ingredientes/{id_ingrediente}
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.put(
    "/platos/{id_plato}/ingredientes/{id_ingrediente}",
    response_model=PlatoIngredienteDetalleSchema,
    status_code=status.HTTP_200_OK,
    summary="CU09: Modificar cantidad de ingrediente en un plato",
    description="Actualiza la cantidad y unidad de medida requerida de un ingrediente asignado."
)
def actualizar_ingrediente_plato(
    datos: ActualizarIngredientePlatoSchema,
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    id_ingrediente: int = Path(..., ge=1, description="ID del ingrediente"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para modificar cantidad de ingrediente en la receta (CU09).
    """
    return PlatoService.actualizar_ingrediente_de_plato(
        db=db,
        id_plato=id_plato,
        id_ingrediente=id_ingrediente,
        datos=datos,
        usuario_actual=usuario_actual
    )


# --- CU09: Quitar Ingrediente de un Plato ---
# Endpoint: DELETE /platos/{id_plato}/ingredientes/{id_ingrediente}
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.delete(
    "/platos/{id_plato}/ingredientes/{id_ingrediente}",
    status_code=status.HTTP_200_OK,
    summary="CU09: Quitar ingrediente de un plato",
    description="Elimina la relación entre el plato y el ingrediente sin afectar el catálogo general."
)
def eliminar_ingrediente_plato(
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    id_ingrediente: int = Path(..., ge=1, description="ID del ingrediente"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para desvincular ingrediente del plato (CU09).
    """
    return PlatoService.eliminar_ingrediente_de_plato(
        db=db,
        id_plato=id_plato,
        id_ingrediente=id_ingrediente,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CASO DE USO: CU10 - GESTIONAR DISPONIBILIDAD
# Endpoint: PATCH /platos/{id_plato}/disponibilidad
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
# =========================================================================
@router.patch(
    "/platos/{id_plato}/disponibilidad",
    response_model=PlatoRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU10: Cambiar disponibilidad de un plato",
    description="Habilita o deshabilita la disponibilidad inmediata del plato para ofertas al cliente."
)
def cambiar_disponibilidad_plato(
    datos: CambiarDisponibilidadPlatoSchema,
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para cambiar disponibilidad de plato (CU10).
    """
    return PlatoService.cambiar_disponibilidad(
        db=db,
        id_plato=id_plato,
        disponible=datos.disponible,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CASO DE USO: CU08 - GESTIONAR PREFERENCIAS EN PLATOS
# =========================================================================

# --- CU08: Consultar Preferencias de un Plato ---
# Endpoint: GET /platos/{id_plato}/preferencias
# Acceso: Usuarios autenticados
@router.get(
    "/platos/{id_plato}/preferencias",
    response_model=PlatoPreferenciasRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU08: Consultar preferencias asociadas a un plato",
    description="Retorna el catálogo de preferencias gastronómicas asignadas a este plato."
)
def listar_preferencias_plato(
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar preferencias de un plato (CU08).
    """
    return PlatoService.listar_preferencias_de_plato(db=db, id_plato=id_plato)


# --- CU08: Asignar/Actualizar Preferencias a un Plato ---
# Endpoint: PUT /platos/{id_plato}/preferencias
# Acceso: Solo responsable del restaurante o ADMINISTRADOR
@router.put(
    "/platos/{id_plato}/preferencias",
    response_model=PlatoPreferenciasRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU08: Asignar o actualizar preferencias a un plato",
    description="Sincroniza la lista de IDs de preferencias dietarias, alergias o estilos que cumple el plato."
)
def actualizar_preferencias_plato(
    datos: ActualizarPreferenciasPlatoSchema,
    id_plato: int = Path(..., ge=1, description="ID del plato"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    """
    Controlador para actualizar preferencias de un plato (CU08).
    """
    return PlatoService.actualizar_preferencias_de_plato(
        db=db,
        id_plato=id_plato,
        ids_preferencias=datos.obtener_ids(),
        usuario_actual=usuario_actual
    )

