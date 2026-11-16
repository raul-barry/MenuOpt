# CASO DE USO: CU16 - Consultar lugares de compra
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.ubicacion import UbicacionRespuestaSchema


class AsociarIngredienteLugarCompraSchema(BaseModel):
    id_ingrediente: Optional[int] = Field(None, ge=1, description="ID del ingrediente")
    nombre_ingrediente: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre manual del ingrediente")
    precio: Decimal = Field(..., ge=0, description="Precio unitario o por lote de referencia")
    cantidad_referencia: Decimal = Field(Decimal("1.00"), gt=0, description="Cantidad a la que corresponde el precio")
    unidad_medida: str = Field(..., min_length=1, max_length=50, description="Unidad de medida del precio (ej. kg, litro, unidad)")
    disponible: bool = Field(True, description="Indica si actualmente está en stock")


class ActualizarIngredienteLugarCompraSchema(BaseModel):
    precio: Optional[Decimal] = Field(None, ge=0)
    cantidad_referencia: Optional[Decimal] = Field(None, gt=0)
    unidad_medida: Optional[str] = Field(None, min_length=1, max_length=50)
    disponible: Optional[bool] = None


class IngredienteLugarCompraRespuestaSchema(BaseModel):
    id_ingrediente_lugar_compra: int
    id_ingrediente: int
    nombre_ingrediente: Optional[str] = None
    id_lugar_compra: int
    nombre_lugar_compra: Optional[str] = None
    precio: Decimal
    cantidad_referencia: Decimal
    unidad_medida: str
    disponible: bool
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)


class LugarCompraParaIngredienteRespuestaSchema(BaseModel):
    id_lugar_compra: int
    nombre_lugar: str
    tipo_lugar: Optional[str] = None
    telefono: Optional[str] = None
    estado_lugar: str
    precio: Decimal
    cantidad_referencia: Decimal
    unidad_medida: str
    disponible: bool
    fecha_actualizacion: datetime
    ubicacion: Optional[UbicacionRespuestaSchema] = None

    model_config = ConfigDict(from_attributes=True)
