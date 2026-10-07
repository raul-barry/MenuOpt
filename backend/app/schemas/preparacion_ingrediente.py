# CASO DE USO: CU15 - Consultar ingredientes para preparación propia
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PreparacionIngredienteItemSchema(BaseModel):
    id_preparacion_ingrediente: int
    id_ingrediente: int
    nombre_ingrediente: Optional[str] = None
    cantidad: Decimal
    unidad_medida: str
    precio_unitario_usado: Optional[Decimal] = None
    costo_estimado: Decimal
    id_lugar_compra: Optional[int] = None
    nombre_lugar_compra: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
