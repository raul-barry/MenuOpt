# Módulo de Asistencia con Inteligencia Artificial (CU26)
from app.ai.proveedor import ProveedorIA, obtener_proveedor_ia
from app.ai.schemas import (
    SolicitudInterpretar,
    SolicitudInterpretada,
    PreferenciaCoincidencia,
    SolicitudExplicarRecomendacion,
    SolicitudExplicarComparacion,
    ExplicacionRespuesta
)
from app.ai.prompts import (
    SYSTEM_PROMPT_INTERPRETAR,
    SYSTEM_PROMPT_EXPLICAR_RECOMENDACION,
    SYSTEM_PROMPT_EXPLICAR_COMPARACION
)
from app.ai.parser import ParserIA

__all__ = [
    "ProveedorIA",
    "obtener_proveedor_ia",
    "SolicitudInterpretar",
    "SolicitudInterpretada",
    "PreferenciaCoincidencia",
    "SolicitudExplicarRecomendacion",
    "SolicitudExplicarComparacion",
    "ExplicacionRespuesta",
    "SYSTEM_PROMPT_INTERPRETAR",
    "SYSTEM_PROMPT_EXPLICAR_RECOMENDACION",
    "SYSTEM_PROMPT_EXPLICAR_COMPARACION",
    "ParserIA"
]
