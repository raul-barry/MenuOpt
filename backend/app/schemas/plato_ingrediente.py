from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AsociarIngredientePlatoSchema(BaseModel):
    id_ingrediente: int = Field(..., ge=1, description="ID del ingrediente del catálogo")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad requerida para el plato (mayor que cero)")
    unidad_medida: str = Field(..., min_length=1, max_length=50, description="Unidad de medida empleada en la receta")


class ActualizarIngredientePlatoSchema(BaseModel):
    cantidad: Decimal = Field(..., gt=0, description="Nueva cantidad (mayor que cero)")
    unidad_medida: str = Field(..., min_length=1, max_length=50, description="Nueva unidad de medida")


class PlatoIngredienteDetalleSchema(BaseModel):
    id_plato_ingrediente: int
    id_ingrediente: int
    nombre_ingrediente: str
    cantidad: Decimal
    unidad_medida: str
    precio_estimado: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)
