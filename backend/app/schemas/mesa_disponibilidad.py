# CASO DE USO: CU20 - Consultar disponibilidad de mesas
from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MesaDisponibilidadRespuesta(BaseModel):
    id_mesa: int
    numero: str
    nombre: Optional[str] = None
    capacidad: int
    forma: str
    posicion_x: float
    posicion_y: float
    rotacion: int
    ancho: float
    alto: float
    es_fija: bool
    combinable: bool
    estado_disponibilidad: str = Field(
        ...,
        description="Estado horario: DISPONIBLE, NO_DISPONIBLE, NO_COMPATIBLE"
    )
    compatible_capacidad: bool
    seleccionable: bool

    model_config = ConfigDict(from_attributes=True)


class CombinacionDisponibleRespuesta(BaseModel):
    id_combinacion: int
    mesas: List[int]
    numeros_mesas: List[str]
    capacidad_total: int
    disponible: bool
    seleccionable: bool
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DisponibilidadRespuesta(BaseModel):
    id_area: int
    nombre_area: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    cantidad_personas: int
    mesas: List[MesaDisponibilidadRespuesta]
    mesas_disponibles: Optional[List[MesaDisponibilidadRespuesta]] = None
    combinaciones: List[CombinacionDisponibleRespuesta]

    model_config = ConfigDict(from_attributes=True)
