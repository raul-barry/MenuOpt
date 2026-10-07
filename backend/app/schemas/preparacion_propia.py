# CASO DE USO: CU15 - Consultar ingredientes para preparación propia
# CASO DE USO: CU16 - Consultar lugares de compra
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.preparacion_ingrediente import PreparacionIngredienteItemSchema


class PreparacionPropiaRespuestaSchema(BaseModel):
    id_preparacion_propia: int
    id_recomendacion: int
    nombre: str
    descripcion: Optional[str] = None
    cantidad_personas: int
    costo_estimado: Decimal
    costo_por_persona: Decimal
    ingredientes: List[PreparacionIngredienteItemSchema] = []

    model_config = ConfigDict(from_attributes=True)


class ItemCompraLugarSchema(BaseModel):
    id_ingrediente: int
    nombre_ingrediente: str
    cantidad_requerida: Decimal
    unidad_medida: str
    precio_referencia: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class AgrupacionCompraLugarItemSchema(BaseModel):
    id_lugar_compra: Optional[int] = None
    nombre_lugar: str
    tipo_lugar: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    zona: Optional[str] = None
    ciudad: Optional[str] = None
    items: List[ItemCompraLugarSchema] = []
    subtotal_estimado: Decimal

    model_config = ConfigDict(from_attributes=True)


class LugaresCompraRecomendacionRespuestaSchema(BaseModel):
    id_recomendacion: int
    id_planificacion: int
    nombre_preparacion: str
    costo_total_estimado: Decimal
    cantidad_personas: int
    total_lugares: int
    lugares: List[AgrupacionCompraLugarItemSchema] = []

    model_config = ConfigDict(from_attributes=True)
