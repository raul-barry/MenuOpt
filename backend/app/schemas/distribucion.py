# CASO DE USO: CU17 - Crear plano 2D del restaurante & Distribución de mesas
from decimal import Decimal
import json
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
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


class ElementoAreaItemSchema(BaseModel):
    id: str = Field(..., description="Identificador único del elemento/espacio (ej. esp_1)")
    tipo: str = Field(..., description="Tipo de espacio: CAJA, ACCESO, JUEGOS, BANOS, ESCALERA, RETIRO, BARRA, COCINA, ESPERA, TERRAZA, ESCENARIO")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre descriptivo del espacio")
    posicion_x: Decimal = Field(..., ge=0.0, le=1.0, description="Posición X normalizada (0.0 a 1.0)")
    posicion_y: Decimal = Field(..., ge=0.0, le=1.0, description="Posición Y normalizada (0.0 a 1.0)")
    ancho: Optional[Decimal] = Field(Decimal("0.12"), ge=0.01, le=1.0, description="Ancho relativo del elemento")
    alto: Optional[Decimal] = Field(Decimal("0.08"), ge=0.01, le=1.0, description="Alto relativo del elemento")
    rotacion: Optional[int] = Field(0, description="Rotación en grados (0, 90, 180, 270)")
    icono: Optional[str] = Field(None, description="Ícono o símbolo representativo")


class GuardarDistribucionRequestSchema(BaseModel):
    mesas: Optional[List[ActualizarPosicionMesaItemSchema]] = Field(default=None, description="Lista de mesas con nuevas coordenadas")
    posiciones: Optional[List[ActualizarPosicionMesaItemSchema]] = Field(default=None, description="Alias compatible de lista de mesas")
    elementos: Optional[List[ElementoAreaItemSchema]] = Field(default=None, description="Lista de espacios y puntos de interés del plano")

    @model_validator(mode="after")
    def normalizar_mesas_o_posiciones(self):
        if not self.mesas and self.posiciones is not None:
            self.mesas = self.posiciones
        elif self.mesas is None:
            self.mesas = []
        return self


class DistribucionAreaRespuestaSchema(BaseModel):
    id_area: int
    nombre_area: str
    ancho_mapa: int
    alto_mapa: int
    total_mesas: int
    mesas: List[MesaRespuestaSchema]
    elementos: Optional[List[ElementoAreaItemSchema]] = Field(default_factory=list, description="Espacios físicos y puntos de interés del área")

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
