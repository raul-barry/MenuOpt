from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from app.config.settings import settings


def crear_token_acceso(datos: Dict[str, Any], tiempo_expiracion_minutos: Optional[int] = None) -> str:
    """
    Crea un token JWT firmado con el algoritmo y clave secreta configurados.
    Incluye fecha de expiración ('exp') y datos de identificación.
    """
    datos_a_codificar = datos.copy()
    minutos = tiempo_expiracion_minutos if tiempo_expiracion_minutos is not None else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=minutos)
    datos_a_codificar.update({"exp": expiracion})

    token_codificado = jwt.encode(
        datos_a_codificar,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return token_codificado


def decodificar_token(token: str) -> Dict[str, Any]:
    """
    Decodifica y valida la firma y expiración de un token JWT.
    Lanza ExpiredSignatureError si ha expirado, o InvalidTokenError si la firma/formato es inválido.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    return payload
