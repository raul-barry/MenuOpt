# CASO DE USO: CU23 - Enviar pedido
# CASO DE USO: CU24 - Gestionar pedidos
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.pedido import (
    PedidoCrear,
    PedidoRespuesta,
    PedidoEstadoActualizar
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.pedido_service import PedidoService

router = APIRouter(
    tags=["Pedidos"]
)


# =========================================================================
# CU23 - ENVIAR PEDIDO (CLIENTE)
# =========================================================================
@router.post(
    "/pedidos",
    response_model=PedidoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="CU23: Enviar pedido gastronómico"
)
def crear_pedido(
    datos: PedidoCrear,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return PedidoService.crear_pedido(
        db=db,
        datos=datos,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CU24 - CONSULTAR Y GESTIONAR PEDIDOS
# =========================================================================
@router.get(
    "/pedidos/mis-pedidos",
    response_model=List[PedidoRespuesta],
    status_code=status.HTTP_200_OK,
    summary="CU24: Consultar historial de pedidos del cliente autenticado"
)
def listar_mis_pedidos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return PedidoService.listar_mis_pedidos(
        db=db,
        usuario_actual=usuario_actual
    )


@router.get(
    "/pedidos/{id_pedido}",
    response_model=PedidoRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU24: Obtener detalle completo de un pedido"
)
def obtener_detalle_pedido(
    id_pedido: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return PedidoService.obtener_por_id(
        db=db,
        id_pedido=id_pedido,
        usuario_actual=usuario_actual
    )


@router.patch(
    "/pedidos/{id_pedido}/cancelar",
    response_model=PedidoRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU24: Cancelar pedido como cliente (sólo permitido si está PENDIENTE)"
)
def cancelar_pedido_cliente(
    id_pedido: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return PedidoService.cancelar_pedido_cliente(
        db=db,
        id_pedido=id_pedido,
        usuario_actual=usuario_actual
    )


@router.get(
    "/restaurantes/{id_restaurante}/pedidos",
    response_model=List[PedidoRespuesta],
    status_code=status.HTTP_200_OK,
    summary="CU24: Consultar pedidos recibidos por el restaurante"
)
def listar_pedidos_restaurante(
    id_restaurante: int = Path(..., gt=0),
    estado: Optional[str] = Query(None, description="Filtrar por estado (PENDIENTE, ACEPTADO, EN_PREPARACION, LISTO, ENTREGADO, CANCELADO)"),
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica (YYYY-MM-DD)"),
    id_reserva: Optional[int] = Query(None, description="Filtrar pedidos vinculados a una reserva"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return PedidoService.listar_pedidos_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        usuario_actual=usuario_actual,
        estado=estado,
        fecha=fecha,
        id_reserva=id_reserva
    )


@router.patch(
    "/pedidos/{id_pedido}/estado",
    response_model=PedidoRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU24: Actualizar estado de pedido por el restaurante"
)
def actualizar_estado_pedido(
    id_pedido: int = Path(..., gt=0),
    datos: PedidoEstadoActualizar = ...,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return PedidoService.actualizar_estado_restaurante(
        db=db,
        id_pedido=id_pedido,
        nuevo_estado=datos.estado,
        usuario_actual=usuario_actual
    )
