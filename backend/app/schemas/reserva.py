# CASO DE USO: CU21 - Realizar reserva & CU22 - Gestionar reservas
from datetime import datetime, date, time
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MesaResumenReserva(BaseModel):
    id_mesa: int
    numero: str
    nombre: Optional[str] = None
    capacidad: int

    model_config = ConfigDict(from_attributes=True)


class ReservaCrear(BaseModel):
    id_restaurante: int
    id_area: int
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time
    cantidad_personas: int = Field(..., gt=0, description="Cantidad de comensales mayor a cero")
    mesas: List[int] = Field(..., min_length=1, description="Lista de IDs de mesas a reservar (1 individual o par combinado)")
    id_planificacion: Optional[int] = None
    observaciones: Optional[str] = Field(None, max_length=255)

    @field_validator("hora_fin")
    @classmethod
    def validar_horas(cls, v: time, info):
        hora_inicio = info.data.get("hora_inicio")
        if hora_inicio and v <= hora_inicio:
            raise ValueError("La hora_fin debe ser estrictamente posterior a la hora_inicio.")
        return v

    model_config = ConfigDict(from_attributes=True)


class ReservaEstadoActualizar(BaseModel):
    estado: str = Field(..., description="Nuevo estado: CONFIRMADA, CANCELADA, FINALIZADA")

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, v: str):
        permitidos = {"CONFIRMADA", "CANCELADA", "FINALIZADA", "PENDIENTE"}
        v_upper = v.upper().strip()
        if v_upper not in permitidos:
            raise ValueError(f"Estado '{v}' no permitido. Opciones: {', '.join(permitidos)}")
        return v_upper

    model_config = ConfigDict(from_attributes=True)


class ReservaRespuesta(BaseModel):
    id_reserva: int
    id_restaurante: int
    nombre_restaurante: str
    id_area: Optional[int] = None
    nombre_area: Optional[str] = None
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time
    cantidad_personas: int
    estado: str
    observaciones: Optional[str] = None
    id_usuario: int
    nombre_cliente: Optional[str] = None
    correo_cliente: Optional[str] = None
    telefono_cliente: Optional[str] = None
    id_planificacion: Optional[int] = None
    mesas: List[MesaResumenReserva] = []
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
