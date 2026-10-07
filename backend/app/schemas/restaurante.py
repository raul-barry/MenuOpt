from datetime import datetime, time
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.ubicacion import (
    CrearUbicacionSchema,
    ActualizarUbicacionSchema,
    UbicacionRespuestaSchema
)


class RegistrarRestauranteSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150, description="Nombre comercial del restaurante")
    descripcion: Optional[str] = Field(None, description="Descripción del concepto gastronómico")
    nit: Optional[str] = Field(None, max_length=30, description="Número de identificación tributaria (único)")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto del restaurante")
    correo: Optional[EmailStr] = Field(None, description="Correo electrónico institucional")
    horario_apertura: Optional[time] = Field(None, description="Horario de apertura (ej. 08:00:00)")
    horario_cierre: Optional[time] = Field(None, description="Horario de cierre (ej. 22:00:00)")
    ubicacion: CrearUbicacionSchema = Field(..., description="Datos de localización del restaurante")


class ActualizarRestauranteSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    descripcion: Optional[str] = None
    nit: Optional[str] = Field(None, max_length=30)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[EmailStr] = None
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    ubicacion: Optional[ActualizarUbicacionSchema] = None


class CambiarEstadoRestauranteSchema(BaseModel):
    estado: Literal["ACTIVO", "INACTIVO"] = Field(..., description="Nuevo estado del restaurante")


class RestauranteRespuestaSchema(BaseModel):
    id_restaurante: int
    nombre: str
    descripcion: Optional[str] = None
    nit: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    estado: str
    fecha_registro: datetime
    fecha_actualizacion: datetime
    id_usuario_responsable: int
    id_ubicacion: int
    ubicacion: Optional[UbicacionRespuestaSchema] = None

    model_config = ConfigDict(from_attributes=True)
