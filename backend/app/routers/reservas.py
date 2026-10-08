# CASO DE USO: CU20 - Consultar disponibilidad de mesas
# CASO DE USO: CU21 - Realizar reserva
# CASO DE USO: CU22 - Gestionar reservas
from datetime import date, time
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.mesa_disponibilidad import DisponibilidadRespuesta
from app.schemas.reserva import (
    ReservaCrear,
    ReservaRespuesta,
    ReservaEstadoActualizar,
    ReservaInvitadoCrear,
    ReservaInvitadoRespuesta,
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.disponibilidad_mesas_service import DisponibilidadMesasService
from app.services.reserva_service import ReservaService
from app.services.reserva_invitado_service import ReservaInvitadoService

router = APIRouter(
    tags=["Reservas y Disponibilidad"]
)


# =========================================================================
# CU20 - CONSULTAR DISPONIBILIDAD DE MESAS
# =========================================================================
@router.get(
    "/restaurantes/{id_restaurante}/mesas-disponibles",
    response_model=DisponibilidadRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU20: Consultar disponibilidad de mesas por fecha, horario y área"
)
def consultar_mesas_disponibles(
    id_restaurante: int = Path(..., gt=0),
    id_area: int = Query(..., gt=0, description="ID del área física del restaurante"),
    fecha: date = Query(..., description="Fecha de la reserva (YYYY-MM-DD)"),
    hora_inicio: time = Query(..., description="Hora de inicio (HH:MM:SS)"),
    hora_fin: time = Query(..., description="Hora de finalización (HH:MM:SS)"),
    cantidad_personas: int = Query(..., gt=0, description="Cantidad de comensales"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return DisponibilidadMesasService.consultar_disponibilidad(
        db=db,
        id_restaurante=id_restaurante,
        id_area=id_area,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        cantidad_personas=cantidad_personas
    )


# =========================================================================
# CU21 - REALIZAR Y CANCELAR RESERVA (CLIENTE)
# =========================================================================
@router.post(
    "/reservas",
    response_model=ReservaRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="CU21: Confirmar reserva de mesa individual o combinación"
)
def crear_reserva(
    datos: ReservaCrear,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return ReservaService.crear_reserva(
        db=db,
        datos=datos,
        usuario_actual=usuario_actual
    )


@router.get(
    "/reservas/{id_reserva}/invitados",
    response_model=List[ReservaInvitadoRespuesta],
    status_code=status.HTTP_200_OK,
    summary="Consultar invitados de una reserva",
)
def listar_invitados_reserva(
    id_reserva: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return ReservaInvitadoService.listar(db, id_reserva, usuario_actual)


@router.post(
    "/reservas/{id_reserva}/invitados",
    response_model=ReservaInvitadoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un invitado en una reserva",
)
def agregar_invitado_reserva(
    datos: ReservaInvitadoCrear,
    id_reserva: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    return ReservaInvitadoService.crear(db, id_reserva, datos, usuario_actual)


@router.delete(
    "/reservas/{id_reserva}/invitados/{id_invitado}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un invitado de una reserva",
)
def eliminar_invitado_reserva(
    id_reserva: int = Path(..., gt=0),
    id_invitado: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    ReservaInvitadoService.eliminar(db, id_reserva, id_invitado, usuario_actual)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/reservas/mis-reservas",
    response_model=List[ReservaRespuesta],
    status_code=status.HTTP_200_OK,
    summary="CU21: Consultar reservas del cliente autenticado"
)
def listar_mis_reservas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return ReservaService.listar_mis_reservas(
        db=db,
        usuario_actual=usuario_actual
    )


@router.get(
    "/reservas/{id_reserva}",
    response_model=ReservaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU21 & CU22: Obtener detalle de una reserva"
)
def obtener_detalle_reserva(
    id_reserva: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return ReservaService.obtener_detalle(
        db=db,
        id_reserva=id_reserva,
        usuario_actual=usuario_actual
    )


@router.patch(
    "/reservas/{id_reserva}/cancelar",
    response_model=ReservaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU21: Cancelar reserva como cliente titular"
)
def cancelar_reserva(
    id_reserva: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return ReservaService.cancelar_reserva_cliente(
        db=db,
        id_reserva=id_reserva,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CU22 - GESTIONAR RESERVAS (RESTAURANTE)
# =========================================================================
@router.get(
    "/restaurantes/{id_restaurante}/reservas",
    response_model=List[ReservaRespuesta],
    status_code=status.HTTP_200_OK,
    summary="CU22: Consultar reservas recibidas por el restaurante"
)
def listar_reservas_restaurante(
    id_restaurante: int = Path(..., gt=0),
    fecha: Optional[date] = Query(None, description="Filtrar por fecha específica"),
    estado: Optional[str] = Query(None, description="Filtrar por estado (CONFIRMADA, CANCELADA, FINALIZADA)"),
    id_area: Optional[int] = Query(None, description="Filtrar por área específica"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return ReservaService.listar_reservas_restaurante(
        db=db,
        id_restaurante=id_restaurante,
        usuario_actual=usuario_actual,
        fecha=fecha,
        estado=estado,
        id_area=id_area
    )


@router.patch(
    "/reservas/{id_reserva}/estado",
    response_model=ReservaRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU22: Actualizar estado de reserva (Restaurante o Administrador)"
)
def actualizar_estado_reserva(
    id_reserva: int = Path(..., gt=0),
    datos: ReservaEstadoActualizar = ...,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return ReservaService.actualizar_estado_restaurante(
        db=db,
        id_reserva=id_reserva,
        nuevo_estado=datos.estado,
        usuario_actual=usuario_actual
    )
