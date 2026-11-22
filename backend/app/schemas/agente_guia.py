from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MensajeGuia(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000)
    accion_id: Optional[str] = Field(None, max_length=80)
    pagina_actual: Optional[str] = Field(None, max_length=160)
    plataforma: Optional[str] = Field(None, pattern="^(web|mobile)$")
    historial: List[Dict[str, Any]] = Field(default_factory=list, max_length=12)

    @field_validator("mensaje")
    @classmethod
    def validar_mensaje(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El mensaje no puede estar vacío.")
        return valor


class RespuestaGuia(BaseModel):
    respuesta: str
    acciones: List[Dict[str, Any]] = Field(default_factory=list)
    destino: Optional[str] = None
    seccion_movil: Optional[int] = None
