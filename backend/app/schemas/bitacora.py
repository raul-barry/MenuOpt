from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class BitacoraCrearSchema(BaseModel):
    id_usuario: Optional[int] = None
    accion: str = Field(..., max_length=100)
    modulo: str = Field(..., max_length=50)
    descripcion: str
    direccion_ip: Optional[str] = Field(None, max_length=45)
    detalles: Optional[Dict[str, Any]] = None


class BitacoraRespuestaSchema(BaseModel):
    id_bitacora: int
    id_usuario: Optional[int] = None
    correo_usuario: Optional[str] = None
    nombre_usuario: Optional[str] = None
    accion: str
    modulo: str
    descripcion: str
    direccion_ip: Optional[str] = None
    detalles: Optional[Dict[str, Any]] = None
    fecha_hora: datetime

    model_config = ConfigDict(from_attributes=True)


class BitacoraListadoPaginadoSchema(BaseModel):
    total: int
    pagina: int
    limite: int
    total_paginas: int
    items: List[BitacoraRespuestaSchema]
