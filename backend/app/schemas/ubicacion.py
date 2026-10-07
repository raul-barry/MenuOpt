from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UbicacionBaseSchema(BaseModel):
    direccion: str = Field(..., min_length=3, max_length=255, description="Dirección física del restaurante")
    zona: Optional[str] = Field(None, max_length=100, description="Zona o barrio")
    ciudad: str = Field(..., min_length=2, max_length=100, description="Ciudad donde se ubica el establecimiento")
    latitud: Optional[Decimal] = Field(None, description="Coordenada geográfica de latitud (-90 a 90)")
    longitud: Optional[Decimal] = Field(None, description="Coordenada geográfica de longitud (-180 a 180)")
    referencia: Optional[str] = Field(None, max_length=255, description="Referencia de llegada o punto cercano")

    @field_validator("latitud")
    @classmethod
    def validar_latitud(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("La latitud debe estar comprendida entre -90 y 90 grados.")
        return v

    @field_validator("longitud")
    @classmethod
    def validar_longitud(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("La longitud debe estar comprendida entre -180 y 180 grados.")
        return v


class CrearUbicacionSchema(UbicacionBaseSchema):
    pass


class ActualizarUbicacionSchema(BaseModel):
    direccion: Optional[str] = Field(None, min_length=3, max_length=255)
    zona: Optional[str] = Field(None, max_length=100)
    ciudad: Optional[str] = Field(None, min_length=2, max_length=100)
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    referencia: Optional[str] = Field(None, max_length=255)

    @field_validator("latitud")
    @classmethod
    def validar_latitud(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("La latitud debe estar comprendida entre -90 y 90 grados.")
        return v

    @field_validator("longitud")
    @classmethod
    def validar_longitud(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("La longitud debe estar comprendida entre -180 y 180 grados.")
        return v


class UbicacionRespuestaSchema(BaseModel):
    id_ubicacion: int
    direccion: str
    zona: Optional[str] = None
    ciudad: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    referencia: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
