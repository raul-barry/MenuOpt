# CASO DE USO: CU26 - Usar asistencia con IA
# Esquemas Pydantic para el módulo de IA
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ContextoPrevio(BaseModel):
    presupuesto: Optional[Decimal] = None
    cantidad_personas: Optional[int] = None
    tipo_comida: Optional[str] = None
    ubicacion_referencia: Optional[str] = None
    preferencias_detectadas: List[str] = []


class SolicitudInterpretar(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario en lenguaje natural")
    contexto_previo: Optional[ContextoPrevio] = Field(None, description="Contexto acumulado de la sesión")

    @field_validator("mensaje")
    @classmethod
    def validar_longitud_mensaje(cls, v: str) -> str:
        v_limpio = v.strip()
        if not v_limpio:
            raise ValueError("El mensaje no puede estar vacío.")
        if len(v_limpio) > 1000:
            raise ValueError("El mensaje excede el límite máximo de 1000 caracteres.")
        return v_limpio


class PreferenciaCoincidencia(BaseModel):
    nombre_detectado: str
    id_preferencia: Optional[int] = None
    registrada: bool


class SolicitudInterpretada(BaseModel):
    presupuesto: Optional[Decimal] = None
    cantidad_personas: Optional[int] = None
    tipo_comida: Optional[str] = None
    ubicacion_referencia: Optional[str] = None
    preferencias_detectadas: List[str] = []
    preferencias_validadas: List[PreferenciaCoincidencia] = []
    datos_faltantes: List[str] = []
    mensaje_asistente: str
    listo_para_crear: bool = False

    model_config = ConfigDict(from_attributes=True)


class SolicitudExplicarRecomendacion(BaseModel):
    id_recomendacion: int = Field(..., gt=0, description="ID de la recomendación calculada por CU13")


class ExplicacionRespuesta(BaseModel):
    id_referencia: int
    tipo: str  # "RECOMENDACION" o "COMPARACION"
    explicacion: str
    detalles_clave: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class SolicitudExplicarComparacion(BaseModel):
    id_planificacion: int = Field(..., gt=0, description="ID de la planificación evaluada en CU14")
