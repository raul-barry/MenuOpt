from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.security.jwt import decodificar_token

# Esquema OAuth2 Bearer para Swagger UI y extracción de header Authorization
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/autenticacion/login",
    description="Ingrese el token JWT con formato: Bearer {token}"
)


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que extrae y valida el token Bearer JWT, obteniendo el usuario
    autenticado y verificando que su cuenta se encuentre activa.
    """
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas o expiradas.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decodificar_token(token)
        id_usuario: int = payload.get("id_usuario")
        if id_usuario is None:
            raise credenciales_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado. Por favor inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credenciales_exception

    # Buscar usuario en la base de datos cargando anticipadamente su rol
    usuario = (
        db.query(Usuario)
        .options(joinedload(Usuario.rol))
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )

    if usuario is None:
        raise credenciales_exception

    if usuario.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Su cuenta se encuentra inactiva o suspendida. Contacte al administrador.",
        )

    return usuario


def requiere_roles(*roles_permitidos: str) -> Callable[[Usuario], Usuario]:
    """
    Fábrica de dependencias para autorización por roles.
    Verifica que el rol del usuario autenticado coincida con alguno de los roles permitidos.
    """
    def verificador_rol(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        nombre_rol = usuario_actual.rol.nombre if usuario_actual.rol else None
        if nombre_rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene los permisos necesarios para realizar esta acción.",
            )
        return usuario_actual

    return verificador_rol
