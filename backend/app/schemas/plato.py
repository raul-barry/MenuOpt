from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categoria import CategoriaRespuestaSchema


class CrearPlatoSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=150, description="Nombre del plato")
    imagen_url: Optional[str] = Field(None, max_length=500)
    descripcion: Optional[str] = Field(None, description="Descripción gastronómica del plato")
    precio: Decimal = Field(..., ge=0, description="Precio del plato (no negativo)")
    tipo_comida: Optional[str] = Field(None, max_length=50, description="Tipo de comida (ej. Desayuno, Almuerzo, Cena)")
    personas_cubiertas: int = Field(1, gt=0, description="Número de personas cubiertas (mayor a cero)")
    disponible: bool = Field(True, description="Disponibilidad inmediata para ofertar")
    id_categoria: int = Field(..., ge=1, description="ID de la categoría a la que pertenece")


class ActualizarPlatoSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    imagen_url: Optional[str] = Field(None, max_length=500)
    descripcion: Optional[str] = None
    precio: Optional[Decimal] = Field(None, ge=0)
    tipo_comida: Optional[str] = Field(None, max_length=50)
    personas_cubiertas: Optional[int] = Field(None, gt=0)
    disponible: Optional[bool] = None
    id_categoria: Optional[int] = Field(None, ge=1)


class CambiarEstadoPlatoSchema(BaseModel):
    estado: Literal["ACTIVO", "INACTIVO"] = Field(..., description="Nuevo estado del plato en el sistema")


class CambiarDisponibilidadPlatoSchema(BaseModel):
    disponible: bool = Field(..., description="Estado de disponibilidad para servir (True/False)")


class PlatoRespuestaSchema(BaseModel):
    id_plato: int
    nombre: str
    imagen_url: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Decimal
    tipo_comida: Optional[str] = None
    personas_cubiertas: int
    disponible: bool
    estado: str
    fecha_registro: datetime
    fecha_actualizacion: datetime
    id_restaurante: int
    id_categoria: int
    categoria: Optional[CategoriaRespuestaSchema] = None

    model_config = ConfigDict(from_attributes=True)
