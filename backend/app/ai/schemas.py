# CASO DE USO: CU26 - Usar asistencia con IA
# Esquemas Pydantic para el módulo de IA
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ContextoPrevio(BaseModel):
    presupuesto: Optional[Decimal] = None
    cantidad_personas: Optional[int] = None
    tipo_comida: Optional[str] = None
    ubicacion_referencia: Optional[str] = None
    preferencias_detectadas: List[str] = []


class SolicitudInterpretar(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario en lenguaje natural")
    contexto_previo: Optional[ContextoPrevio] = Field(None, description="Contexto acumulado de la sesión")

    @model_validator(mode="before")
    @classmethod
    def compatibilizar_solicitud(cls, data):
        if isinstance(data, dict):
            if "mensaje" not in data and "solicitud" in data:
                data["mensaje"] = data["solicitud"]
        return data

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
    opcion_recomendada: Optional[Dict[str, Any]] = None

    # Campos de retrocompatibilidad con versiones de cliente móvil
    explicacion: Optional[str] = None
    respuesta: Optional[str] = None
    intencion: Optional[str] = "CONSULTA"
    entidades: Optional[Dict[str, Any]] = None

    @model_validator(mode="before")
    @classmethod
    def enriquecer_compatibilidad(cls, data):
        if isinstance(data, dict):
            msg = data.get("mensaje_asistente")
            if msg:
                if not data.get("explicacion"):
                    data["explicacion"] = msg
                if not data.get("respuesta"):
                    data["respuesta"] = msg
            if not data.get("intencion"):
                data["intencion"] = "PLANIFICACION" if data.get("listo_para_crear") else "CONSULTA"
            if not data.get("entidades"):
                ents = {}
                if data.get("tipo_comida"):
                    ents["tipo_comida"] = data["tipo_comida"]
                if data.get("cantidad_personas"):
                    ents["personas"] = data["cantidad_personas"]
                if data.get("presupuesto"):
                    ents["presupuesto"] = f"{data['presupuesto']} Bs"
                if data.get("ubicacion_referencia"):
                    ents["ubicacion"] = data["ubicacion_referencia"]
                if data.get("preferencias_detectadas"):
                    ents["preferencias"] = ", ".join(data["preferencias_detectadas"])
                data["entidades"] = ents
        return data

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
