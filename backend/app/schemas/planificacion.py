from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.preferencia import PreferenciaRespuestaSchema

TIPOS_COMIDA_VALIDOS = {"DESAYUNO", "ALMUERZO", "CENA", "MERIENDA", "OTRO"}
ESTADOS_PLANIFICACION_VALIDOS = {"ACTIVA", "CANCELADA", "BORRADOR"}


class CrearPlanificacionSchema(BaseModel):
    presupuesto: Decimal = Field(
        ...,
        gt=0,
        description="Presupuesto total disponible para la planificación (debe ser mayor que 0)"
    )
    cantidad_personas: int = Field(
        ...,
        gt=0,
        description="Cantidad de comensales cubiertos (debe ser mayor que 0)"
    )
    tipo_comida: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Tipo de comida (DESAYUNO, ALMUERZO, CENA, MERIENDA, OTRO)"
    )
    ubicacion_referencia: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Ubicación aproximada o zona de referencia (ej. Equipetrol, Calacoto)"
    )
    preferencias: Optional[List[int]] = Field(
        None,
        description="Lista de IDs de preferencias gastronómicas específicas para esta planificación"
    )

    @field_validator("tipo_comida")
    @classmethod
    def validar_tipo_comida(cls, v: str) -> str:
        v_limpio = v.strip().upper()
        if v_limpio not in TIPOS_COMIDA_VALIDOS:
            permitidos = ", ".join(sorted(TIPOS_COMIDA_VALIDOS))
            raise ValueError(f"Tipo de comida '{v}' inválido. Valores permitidos: {permitidos}")
        return v_limpio

    @field_validator("ubicacion_referencia")
    @classmethod
    def limpiar_ubicacion(cls, v: str) -> str:
        v_limpio = v.strip()
        if len(v_limpio) < 2:
            raise ValueError("La ubicación de referencia debe tener al menos 2 caracteres.")
        return v_limpio


class ActualizarPlanificacionSchema(BaseModel):
    presupuesto: Optional[Decimal] = Field(None, gt=0)
    cantidad_personas: Optional[int] = Field(None, gt=0)
    tipo_comida: Optional[str] = None
    ubicacion_referencia: Optional[str] = Field(None, min_length=2, max_length=255)
    preferencias: Optional[List[int]] = None

    @field_validator("tipo_comida")
    @classmethod
    def validar_tipo_comida_opcional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_limpio = v.strip().upper()
            if v_limpio not in TIPOS_COMIDA_VALIDOS:
                permitidos = ", ".join(sorted(TIPOS_COMIDA_VALIDOS))
                raise ValueError(f"Tipo de comida '{v}' inválido. Valores permitidos: {permitidos}")
            return v_limpio
        return v

    @field_validator("ubicacion_referencia")
    @classmethod
    def limpiar_ubicacion_opcional(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_limpio = v.strip()
            if len(v_limpio) < 2:
                raise ValueError("La ubicación de referencia debe tener al menos 2 caracteres.")
            return v_limpio
        return v


class CambiarEstadoPlanificacionSchema(BaseModel):
    estado: Literal["ACTIVA", "CANCELADA", "BORRADOR"] = Field(
        ...,
        description="Nuevo estado de la planificación"
    )


class PlanificacionRespuestaSchema(BaseModel):
    id_planificacion: int
    presupuesto: Decimal
    cantidad_personas: int
    tipo_comida: str
    ubicacion_referencia: str
    fecha_planificacion: datetime
    estado: str
    id_usuario: int
    preferencias: List[PreferenciaRespuestaSchema] = []

    model_config = ConfigDict(from_attributes=True)


class PlanificacionesPaginadasSchema(BaseModel):
    total: int
    pagina: int
    limite: int
    total_paginas: int
    planificaciones: List[PlanificacionRespuestaSchema]
