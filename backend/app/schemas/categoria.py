from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CrearCategoriaSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre único de la categoría")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción de la categoría")
    activo: bool = Field(True, description="Indica si la categoría está activa")


class ActualizarCategoriaSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class CategoriaRespuestaSchema(BaseModel):
    id_categoria: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)
