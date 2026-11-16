# CASO DE USO: CU17 - Crear plano 2D del restaurante
from datetime import datetime
import json
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CrearAreaRestauranteSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre descriptivo del área (ej. Salón Principal, Terraza)")
    descripcion: Optional[str] = Field(None, max_length=500, description="Detalles o descripción del área")
    ancho_mapa: int = Field(1200, gt=0, le=5000, description="Ancho lógico del lienzo 2D")
    alto_mapa: int = Field(700, gt=0, le=5000, description="Alto lógico del lienzo 2D")
    orden: int = Field(0, ge=0, description="Orden de despliegue")


class ActualizarAreaRestauranteSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    ancho_mapa: Optional[int] = Field(None, gt=0, le=5000)
    alto_mapa: Optional[int] = Field(None, gt=0, le=5000)
    activo: Optional[bool] = None
    orden: Optional[int] = Field(None, ge=0)


class CambiarEstadoAreaSchema(BaseModel):
    activo: bool = Field(..., description="Nuevo estado lógico del área")


class AreaRestauranteRespuestaSchema(BaseModel):
    id_area: int
    id_restaurante: int
    nombre: str
    descripcion: Optional[str] = None
    ancho_mapa: int
    alto_mapa: int
    activo: bool
    orden: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    total_mesas: Optional[int] = 0
    elementos: Optional[List[Any]] = Field(default_factory=list)

    @field_validator("elementos", mode="before")
    @classmethod
    def normalizar_elementos(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        if isinstance(v, list):
            return v
        return []

    model_config = ConfigDict(from_attributes=True)
