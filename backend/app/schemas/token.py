from typing import Optional
from pydantic import BaseModel
from app.schemas.usuario import UsuarioRespuestaSchema


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRespuestaSchema


class TokenPayloadSchema(BaseModel):
    id_usuario: int
    correo: str
    rol: str
    exp: Optional[int] = None
