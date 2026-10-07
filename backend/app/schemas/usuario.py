from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RolRespuestaSchema(BaseModel):
    id_rol: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class UsuarioRespuestaSchema(BaseModel):
    id_usuario: int
    nombres: str
    apellidos: str
    correo: EmailStr
    telefono: Optional[str] = None
    estado: str
    fecha_registro: datetime
    fecha_actualizacion: datetime
    id_rol: int
    rol: Optional[RolRespuestaSchema] = None

    model_config = ConfigDict(from_attributes=True)


class ActualizarPerfilSchema(BaseModel):
    nombres: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombres del usuario")
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100, description="Apellidos del usuario")
    correo: Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")


class CambiarContrasenaSchema(BaseModel):
    contrasena_actual: str = Field(..., min_length=1, description="Contraseña actual del usuario")
    contrasena_nueva: str = Field(..., min_length=8, description="Nueva contraseña (mínimo 8 caracteres)")


class CambiarEstadoUsuarioSchema(BaseModel):
    estado: Literal["ACTIVO", "INACTIVO"] = Field(..., description="Nuevo estado del usuario")


class UsuariosPaginadosSchema(BaseModel):
    total: int
    pagina: int
    limite: int
    total_paginas: int
    usuarios: List[UsuarioRespuestaSchema]
