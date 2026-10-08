from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.reserva import Reserva
from app.models.reserva_invitado import ReservaInvitado
from app.models.usuario import Usuario
from app.repositories.reserva_invitado_repository import ReservaInvitadoRepository
from app.schemas.reserva import ReservaInvitadoCrear, ReservaInvitadoRespuesta


class ReservaInvitadoService:
    @staticmethod
    def _obtener_reserva(db: Session, id_reserva: int, *, bloquear: bool = False) -> Reserva:
        query = db.query(Reserva).filter(Reserva.id_reserva == id_reserva)
        if bloquear:
            query = query.with_for_update()
        reserva = query.first()
        if reserva is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada.")
        return reserva

    @staticmethod
    def _verificar_permiso(reserva: Reserva, usuario_actual: Usuario) -> None:
        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol == "ADMINISTRADOR":
            return
        if rol == "CLIENTE" and reserva.id_usuario == usuario_actual.id_usuario:
            return
        if rol == "RESTAURANTE" and reserva.restaurante.id_usuario_responsable == usuario_actual.id_usuario:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para gestionar invitados de esta reserva.",
        )

    @classmethod
    def listar(
        cls, db: Session, id_reserva: int, usuario_actual: Usuario
    ) -> List[ReservaInvitadoRespuesta]:
        reserva = cls._obtener_reserva(db, id_reserva)
        cls._verificar_permiso(reserva, usuario_actual)
        return ReservaInvitadoRepository.listar(db, id_reserva)

    @classmethod
    def crear(
        cls,
        db: Session,
        id_reserva: int,
        datos: ReservaInvitadoCrear,
        usuario_actual: Usuario,
    ) -> ReservaInvitadoRespuesta:
        reserva = cls._obtener_reserva(db, id_reserva, bloquear=True)
        cls._verificar_permiso(reserva, usuario_actual)

        invitados = ReservaInvitadoRepository.listar(db, id_reserva)
        if len(invitados) >= reserva.cantidad_personas:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva ya alcanzó la cantidad máxima de invitados.",
            )

        usuario_invitado: Optional[Usuario] = None
        nombre = datos.nombre
        correo = str(datos.correo).strip().lower() if datos.correo else None
        if datos.id_usuario is not None:
            usuario_invitado = (
                db.query(Usuario)
                .options(joinedload(Usuario.rol))
                .filter(Usuario.id_usuario == datos.id_usuario)
                .first()
            )
            if usuario_invitado is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario invitado no encontrado.")
            if usuario_invitado.estado != "ACTIVO" or not usuario_invitado.rol or usuario_invitado.rol.nombre != "CLIENTE":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario vinculado debe ser un cliente activo.",
                )
            if usuario_invitado.id_usuario == reserva.id_usuario:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El titular ya forma parte de la reserva.")
            nombre = f"{usuario_invitado.nombres} {usuario_invitado.apellidos}".strip()
            correo = usuario_invitado.correo.strip().lower()

        nombre_normalizado = (nombre or "").strip().casefold()
        correo_normalizado = correo.casefold() if correo else None
        for existente in invitados:
            if datos.id_usuario is not None and existente.id_usuario == datos.id_usuario:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya está invitado a esta reserva.")
            if correo_normalizado and existente.correo and existente.correo.casefold() == correo_normalizado:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un invitado con ese correo en esta reserva.")
            correo_existente = existente.correo.casefold() if existente.correo else None
            mismo_nombre = existente.nombre.strip().casefold() == nombre_normalizado
            if mismo_nombre and (
                correo_normalizado is None
                or correo_existente is None
                or correo_normalizado == correo_existente
            ):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un invitado con ese nombre en esta reserva.")

        invitado = ReservaInvitado(
            id_reserva=id_reserva,
            id_usuario=usuario_invitado.id_usuario if usuario_invitado else None,
            nombre=nombre or "",
            correo=correo,
        )
        db.add(invitado)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El usuario o correo ya está asociado a esta reserva.",
            ) from exc
        db.refresh(invitado)
        return invitado

    @classmethod
    def eliminar(
        cls,
        db: Session,
        id_reserva: int,
        id_invitado: int,
        usuario_actual: Usuario,
    ) -> None:
        reserva = cls._obtener_reserva(db, id_reserva, bloquear=True)
        cls._verificar_permiso(reserva, usuario_actual)
        invitado = ReservaInvitadoRepository.obtener(db, id_reserva, id_invitado)
        if invitado is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitado no encontrado en esta reserva.")
        if ReservaInvitadoRepository.tiene_pedidos_vinculados(db, invitado):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar un invitado con pedidos asociados a esta reserva.",
            )
        db.delete(invitado)
        db.commit()
