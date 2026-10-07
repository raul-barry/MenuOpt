# CASO DE USO: CU19 - Definir combinación de mesas
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CrearMesaCombinacionSchema(BaseModel):
    id_mesa_origen: int = Field(..., gt=0, description="ID de la primera mesa a combinar")
    id_mesa_destino: int = Field(..., gt=0, description="ID de la segunda mesa a combinar")
    descripcion: Optional[str] = Field(None, max_length=255, description="Nota o motivo de combinación (ej. Mesas contiguas terraza)")


class ActualizarMesaCombinacionSchema(BaseModel):
    permitida: Optional[bool] = None
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class MesaCombinacionRespuestaSchema(BaseModel):
    id_mesa_combinacion: int
    id_mesa_origen: int
    numero_mesa_origen: Optional[str] = None
    capacidad_mesa_origen: Optional[int] = None
    id_mesa_destino: int
    numero_mesa_destino: Optional[str] = None
    capacidad_mesa_destino: Optional[int] = None
    capacidad_combinada: int
    permitida: bool
    descripcion: Optional[str] = None
    activo: bool
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
