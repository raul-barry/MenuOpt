# CASO DE USO: CU17 - Crear plano 2D del restaurante & Distribución de mesas
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.mesa import MesaRespuestaSchema


class ItemConfiguracionCapacidad(BaseModel):
    capacidad: int = Field(..., gt=0, le=50, description="Capacidad de personas de la mesa")
    cantidad: int = Field(..., gt=0, le=100, description="Cantidad de mesas de esta capacidad a crear")


class GenerarDistribucionRequestSchema(BaseModel):
    mesas: List[ItemConfiguracionCapacidad] = Field(..., min_length=1, description="Lista de requerimientos de mesas por capacidad")


class ActualizarPosicionMesaItemSchema(BaseModel):
    id_mesa: int = Field(..., gt=0, description="ID de la mesa")
    posicion_x: Decimal = Field(..., ge=0.0, le=1.0, description="Posición X normalizada (0.0 a 1.0)")
    posicion_y: Decimal = Field(..., ge=0.0, le=1.0, description="Posición Y normalizada (0.0 a 1.0)")
    rotacion: Optional[int] = Field(None, description="Rotación opcional en grados (0, 90, 180, 270)")


class GuardarDistribucionRequestSchema(BaseModel):
    mesas: List[ActualizarPosicionMesaItemSchema] = Field(..., description="Lista de mesas con nuevas coordenadas normalizadas")


class DistribucionAreaRespuestaSchema(BaseModel):
    id_area: int
    nombre_area: str
    ancho_mapa: int
    alto_mapa: int
    total_mesas: int
    mesas: List[MesaRespuestaSchema]

    model_config = ConfigDict(from_attributes=True)
