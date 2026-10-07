# CASO DE USO: CU13 - Generar recomendación
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class RecomendacionPlatoItemSchema(BaseModel):
    id_recomendacion_plato: int
    id_plato: int
    nombre_plato: Optional[str] = None
    personas_cubiertas: Optional[int] = None
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class RecomendacionRespuestaSchema(BaseModel):
    id_recomendacion: int
    id_planificacion: int
    tipo_recomendacion: str
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    costo_total: Decimal
    costo_por_persona: Decimal
    puntuacion: Decimal
    distancia_estimada: Optional[Decimal] = None
    id_restaurante: Optional[int] = None
    nombre_restaurante: Optional[str] = None
    id_preparacion_propia: Optional[int] = None
    nombre_preparacion: Optional[str] = None
    fecha_generacion: datetime
    platos: List[RecomendacionPlatoItemSchema] = []

    model_config = ConfigDict(from_attributes=True)


class GenerarRecomendacionesRespuestaSchema(BaseModel):
    mensaje: str
    total_recomendaciones: int
    recomendaciones: List[RecomendacionRespuestaSchema]
