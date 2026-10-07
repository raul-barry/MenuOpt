from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class PreferenciaRespuestaSchema(BaseModel):
    id_preferencia: int
    nombre: str
    tipo: Optional[str] = None
    descripcion: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class CrearPreferenciaSchema(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre único de la preferencia")
    tipo: Optional[str] = Field(None, max_length=50, description="Categoría (ej. DIETARIA, ALERGIA, SABOR, SALUD)")
    descripcion: Optional[str] = Field(None, max_length=255, description="Descripción explicativa de la preferencia")
    activo: bool = Field(True, description="Indica si la preferencia está activa para selección")


class ActualizarPreferenciaSchema(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo: Optional[str] = Field(None, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)
    activo: Optional[bool] = None


class CambiarEstadoPreferenciaSchema(BaseModel):
    activo: bool = Field(..., description="Nuevo estado activo de la preferencia")


class ActualizarPreferenciasUsuarioSchema(BaseModel):
    preferencias: List[int] = Field(
        ...,
        description="Lista de IDs de preferencias gastronómicas asociadas al usuario"
    )
