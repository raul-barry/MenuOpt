# CASO DE USO: CU23 - Enviar pedido & CU24 - Gestionar pedidos
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class DetallePedidoItemCrear(BaseModel):
    id_plato: int = Field(..., gt=0, description="Identificador del plato")
    cantidad: int = Field(..., gt=0, description="Cantidad entera mayor a cero")
    id_invitado: Optional[int] = Field(None, gt=0, description="Invitado de la reserva al que se asigna el plato")

    model_config = ConfigDict(from_attributes=True)


class PedidoCrear(BaseModel):
    id_restaurante: int = Field(..., gt=0, description="Identificador del restaurante")
    detalles: List[DetallePedidoItemCrear] = Field(..., min_length=1, description="Lista de platos y cantidades")
    id_reserva: Optional[int] = Field(None, gt=0, description="ID opcional de reserva asociada")
    observaciones: Optional[str] = Field(None, max_length=500, description="Instrucciones u observaciones opcionales")

    # La identidad siempre se deriva del token autenticado; rechazar campos
    # adicionales evita aceptar silenciosamente intentos de suplantación.
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class DetallePedidoRespuesta(BaseModel):
    id_detalle_pedido: int
    id_plato: int
    nombre_plato: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal
    id_invitado: Optional[int] = None
    nombre_invitado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PedidoRespuesta(BaseModel):
    id_pedido: int
    id_restaurante: int
    nombre_restaurante: str
    id_usuario: int
    nombre_cliente: Optional[str] = None
    correo_cliente: Optional[str] = None
    telefono_cliente: Optional[str] = None
    id_reserva: Optional[int] = None
    estado: str
    total: Decimal
    observaciones: Optional[str] = None
    fecha_pedido: datetime
    detalles: List[DetallePedidoRespuesta] = []

    model_config = ConfigDict(from_attributes=True)


class PedidoResumen(BaseModel):
    id_pedido: int
    id_restaurante: int
    nombre_restaurante: str
    id_usuario: int
    nombre_cliente: Optional[str] = None
    id_reserva: Optional[int] = None
    estado: str
    total: Decimal
    fecha_pedido: datetime
    cantidad_items: int

    model_config = ConfigDict(from_attributes=True)


class PedidoEstadoActualizar(BaseModel):
    estado: str = Field(..., description="Nuevo estado: ACEPTADO, EN_PREPARACION, LISTO, ENTREGADO, CANCELADO")

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: str):
        permitidos = {"ACEPTADO", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO"}
        v_upper = v.upper().strip()
        if v_upper not in permitidos:
            raise ValueError(f"Estado '{v}' no permitido. Transiciones válidas hacia: {', '.join(permitidos)}")
        return v_upper

    model_config = ConfigDict(from_attributes=True)
