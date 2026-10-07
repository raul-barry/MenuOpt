# CASO DE USO: CU16 - Consultar lugares de compra
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.ubicacion import (
    CrearUbicacionSchema,
    ActualizarUbicacionSchema,
    UbicacionRespuestaSchema
)


class CrearLugarCompraSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150, description="Nombre del establecimiento o mercado")
    tipo: Optional[str] = Field(None, max_length=50, description="Tipo de establecimiento (MERCADO, SUPERMERCADO, TIENDA, DISTRIBUIDOR)")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    id_ubicacion: Optional[int] = Field(None, ge=1, description="ID de una ubicación existente")
    ubicacion: Optional[CrearUbicacionSchema] = Field(None, description="Datos para crear una nueva ubicación")


class ActualizarLugarCompraSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    tipo: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = Field(None, max_length=20)
    id_ubicacion: Optional[int] = Field(None, ge=1)
    ubicacion: Optional[ActualizarUbicacionSchema] = None


class CambiarEstadoLugarCompraSchema(BaseModel):
    estado: Literal["ACTIVO", "INACTIVO"] = Field(..., description="Nuevo estado del lugar de compra")


class LugarCompraRespuestaSchema(BaseModel):
    id_lugar_compra: int
    nombre: str
    tipo: Optional[str] = None
    telefono: Optional[str] = None
    estado: str
    id_ubicacion: Optional[int] = None
    ubicacion: Optional[UbicacionRespuestaSchema] = None

    model_config = ConfigDict(from_attributes=True)
