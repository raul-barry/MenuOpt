from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CrearIngredienteSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre único del ingrediente")
    unidad_medida: str = Field(..., min_length=1, max_length=50, description="Unidad de medida (ej. gramos, kg, ml, unidad)")
    precio_estimado: Optional[Decimal] = Field(None, ge=0, description="Precio referencial estimado (no negativo)")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción del ingrediente")
    estado: str = Field("ACTIVO", max_length=20, description="Estado del ingrediente")


class ActualizarIngredienteSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    unidad_medida: Optional[str] = Field(None, min_length=1, max_length=50)
    precio_estimado: Optional[Decimal] = Field(None, ge=0)
    descripcion: Optional[str] = Field(None, max_length=255)
    estado: Optional[str] = Field(None, max_length=20)


class IngredienteRespuestaSchema(BaseModel):
    id_ingrediente: int
    nombre: str
    unidad_medida: str
    precio_estimado: Optional[Decimal] = None
    descripcion: Optional[str] = None
    estado: str

    model_config = ConfigDict(from_attributes=True)
