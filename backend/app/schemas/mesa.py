# CASO DE USO: CU18 - Gestionar mesas
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CrearMesaSchema(BaseModel):
    numero: str = Field(..., min_length=1, max_length=30, description="Identificador visual de la mesa (ej. M1, T2, VIP1)")
    nombre: Optional[str] = Field(None, max_length=100, description="Nombre o etiqueta adicional opcional")
    capacidad: int = Field(..., gt=0, le=50, description="Capacidad máxima de comensales sentados")
    forma: Literal["REDONDA", "CUADRADA", "RECTANGULAR"] = Field("CUADRADA", description="Forma geométrica de la mesa")
    posicion_x: Decimal = Field(Decimal("0.5000"), ge=0.0, le=1.0, description="Posición X normalizada (0.0 a 1.0)")
    posicion_y: Decimal = Field(Decimal("0.5000"), ge=0.0, le=1.0, description="Posición Y normalizada (0.0 a 1.0)")
    rotacion: int = Field(0, description="Rotación en grados (0, 90, 180, 270)")
    ancho: Decimal = Field(Decimal("0.0800"), gt=0, le=1.0, description="Ancho relativo respecto al lienzo")
    alto: Decimal = Field(Decimal("0.0800"), gt=0, le=1.0, description="Alto relativo respecto al lienzo")
    es_fija: bool = Field(False, description="Indica si la mesa no puede moverse ni combinarse")
    combinable: bool = Field(True, description="Indica si la mesa admite combinaciones con otras")

    @field_validator("rotacion")
    @classmethod
    def validar_rotacion(cls, v: int) -> int:
        grados_normalizados = v % 360
        if grados_normalizados not in {0, 90, 180, 270}:
            raise ValueError("La rotación debe ser un múltiplo de 90 grados (0, 90, 180, 270)")
        return grados_normalizados


class ActualizarMesaSchema(BaseModel):
    numero: Optional[str] = Field(None, min_length=1, max_length=30)
    nombre: Optional[str] = Field(None, max_length=100)
    capacidad: Optional[int] = Field(None, gt=0, le=50)
    forma: Optional[Literal["REDONDA", "CUADRADA", "RECTANGULAR"]] = None
    posicion_x: Optional[Decimal] = Field(None, ge=0.0, le=1.0)
    posicion_y: Optional[Decimal] = Field(None, ge=0.0, le=1.0)
    rotacion: Optional[int] = None
    ancho: Optional[Decimal] = Field(None, gt=0, le=1.0)
    alto: Optional[Decimal] = Field(None, gt=0, le=1.0)
    es_fija: Optional[bool] = None
    combinable: Optional[bool] = None
    activo: Optional[bool] = None

    @field_validator("rotacion")
    @classmethod
    def validar_rotacion(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            grados_normalizados = v % 360
            if grados_normalizados not in {0, 90, 180, 270}:
                raise ValueError("La rotación debe ser un múltiplo de 90 grados (0, 90, 180, 270)")
            return grados_normalizados
        return v


class CambiarEstadoMesaSchema(BaseModel):
    activo: bool = Field(..., description="Nuevo estado lógico de la mesa")


class MesaRespuestaSchema(BaseModel):
    id_mesa: int
    id_area: int
    numero: str
    nombre: Optional[str] = None
    capacidad: int
    forma: str
    posicion_x: Decimal
    posicion_y: Decimal
    rotacion: int
    ancho: Decimal
    alto: Decimal
    es_fija: bool
    combinable: bool
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)
