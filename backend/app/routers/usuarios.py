from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioRespuestaSchema,
    ActualizarPerfilSchema,
    CambiarContrasenaSchema,
    CambiarEstadoUsuarioSchema,
    UsuariosPaginadosSchema
)
from app.schemas.preferencia import (
    PreferenciaRespuestaSchema,
    ActualizarPreferenciasUsuarioSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.usuario_service import UsuarioService
from app.services.preferencia_service import PreferenciaService

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


# =========================================================================
# CASO DE USO: CU03 - GESTIONAR PERFIL
# Acceso: Cualquier usuario autenticado con Bearer JWT activo
# =========================================================================

# --- CU03: Consultar Perfil ---
# Endpoint: GET /usuarios/perfil
@router.get(
    "/perfil",
    response_model=UsuarioRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU03: Consultar perfil del usuario autenticado",
    description="Devuelve la información del usuario autenticado a partir de su Bearer Token."
)
def obtener_perfil(
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    """
    Controlador para consultar el perfil personal (CU03).
    """
    return UsuarioService.consultar_perfil(usuario_actual)


# --- CU03: Modificar Perfil ---
# Endpoint: PUT /usuarios/perfil
@router.put(
    "/perfil",
    response_model=UsuarioRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU03: Modificar perfil del usuario autenticado",
    description="Permite modificar nombres, apellidos, teléfono y correo electrónico personal."
)
def actualizar_perfil(
    datos: ActualizarPerfilSchema,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    """
    Controlador para actualizar datos del perfil (CU03).
    """
    return UsuarioService.actualizar_perfil(
        db=db,
        usuario_actual=usuario_actual,
        datos=datos
    )


# --- CU03: Cambiar Contraseña ---
# Endpoint: PUT /usuarios/perfil/contrasena
@router.put(
    "/perfil/contrasena",
    status_code=status.HTTP_200_OK,
    summary="CU03: Cambiar contraseña de forma segura",
    description="Verifica la contraseña actual y actualiza la contraseña aplicando hash con bcrypt."
)
def cambiar_contrasena(
    datos: CambiarContrasenaSchema,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    """
    Controlador para cambio seguro de contraseña (CU03).
    """
    return UsuarioService.cambiar_contrasena(
        db=db,
        usuario_actual=usuario_actual,
        datos=datos
    )


# =========================================================================
# CASO DE USO: CU12 - DEFINIR PREFERENCIAS (Preferencias del Usuario)
# Acceso: Cualquier usuario autenticado con Bearer JWT activo
# =========================================================================

# --- CU12: Consultar Preferencias del Usuario ---
# Endpoint: GET /usuarios/preferencias
@router.get(
    "/preferencias",
    response_model=list[PreferenciaRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU12: Consultar preferencias gastronómicas del usuario autenticado",
    description="Devuelve el conjunto de preferencias gastronómicas guardadas en el perfil del usuario."
)
def obtener_preferencias_usuario(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    """
    Controlador para consultar las preferencias habituales del usuario (CU12).
    """
    return PreferenciaService.obtener_preferencias_usuario(
        db=db,
        usuario_actual=usuario_actual
    )


# --- CU12: Modificar Preferencias del Usuario ---
# Endpoint: PUT /usuarios/preferencias
@router.put(
    "/preferencias",
    response_model=list[PreferenciaRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU12: Modificar preferencias gastronómicas del usuario autenticado",
    description="Actualiza y sincroniza las preferencias gastronómicas habituales asociadas al perfil."
)
def actualizar_preferencias_usuario(
    datos: ActualizarPreferenciasUsuarioSchema,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db)
):
    """
    Controlador para actualizar las preferencias habituales del usuario (CU12).
    """
    return PreferenciaService.actualizar_preferencias_usuario(
        db=db,
        usuario_actual=usuario_actual,
        datos=datos
    )


# =========================================================================
# CASO DE USO: CU04 - GESTIONAR USUARIOS
# Acceso: Exclusivo para usuarios con rol ADMINISTRADOR
# =========================================================================

# --- CU04: Listar Usuarios ---
# Endpoint: GET /usuarios
@router.get(
    "",
    response_model=UsuariosPaginadosSchema,
    status_code=status.HTTP_200_OK,
    summary="CU04: Listar usuarios (Solo Administrador)",
    description="Consulta y lista usuarios de forma paginada con filtros por estado, rol o búsqueda textual."
)
def listar_usuarios(
    pagina: int = Query(1, ge=1, description="Número de página a consultar"),
    limite: int = Query(10, ge=1, le=100, description="Cantidad de registros por página"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (ej. ACTIVO, INACTIVO)"),
    rol: Optional[str] = Query(None, description="Filtrar por nombre de rol (ej. CLIENTE, RESTAURANTE, ADMINISTRADOR)"),
    busqueda: Optional[str] = Query(None, description="Búsqueda por nombres, apellidos o correo"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para listado paginado de usuarios del sistema (CU04).
    Requiere rol ADMINISTRADOR.
    """
    return UsuarioService.listar_usuarios_paginado(
        db=db,
        pagina=pagina,
        limite=limite,
        estado=estado,
        rol=rol,
        busqueda=busqueda
    )


# --- CU04: Obtener Detalle de Usuario ---
# Endpoint: GET /usuarios/{id_usuario}
@router.get(
    "/{id_usuario}",
    response_model=UsuarioRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU04: Obtener detalle de un usuario (Solo Administrador)",
    description="Muestra la información completa de un usuario específico por su ID."
)
def obtener_usuario(
    id_usuario: int = Path(..., ge=1, description="Identificador único del usuario"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para obtener información detallada de un usuario por ID (CU04).
    Requiere rol ADMINISTRADOR.
    """
    return UsuarioService.obtener_usuario_por_id(db=db, id_usuario=id_usuario)


# --- CU04: Cambiar Estado de Usuario (Activación / Desactivación Lógica) ---
# Endpoint: PATCH /usuarios/{id_usuario}/estado
@router.patch(
    "/{id_usuario}/estado",
    response_model=UsuarioRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU04: Cambiar estado de un usuario (Solo Administrador)",
    description="Permite activar o desactivar lógicamente un usuario (ACTIVO / INACTIVO)."
)
def cambiar_estado_usuario(
    datos: CambiarEstadoUsuarioSchema,
    id_usuario: int = Path(..., ge=1, description="Identificador único del usuario"),
    db: Session = Depends(get_db),
    admin_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para modificar el estado lógico del usuario (CU04).
    Requiere rol ADMINISTRADOR.
    """
    return UsuarioService.cambiar_estado(
        db=db,
        id_usuario=id_usuario,
        nuevo_estado=datos.estado,
        admin_actual=admin_actual
    )
