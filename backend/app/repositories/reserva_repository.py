# CASO DE USO: CU20, CU21, CU22 - Repositorio de Reservas
from datetime import date, time
from typing import List, Optional, Set
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.models.reserva import Reserva
from app.models.mesa_reserva import MesaReserva
from app.models.mesa import Mesa


class ReservaRepository:
    ESTADOS_BLOQUEANTES = ["CONFIRMADA", "PENDIENTE"]

    @staticmethod
    def buscar_conflictos_mesas(
        db: Session,
        mesas_ids: List[int],
        fecha: date,
        hora_inicio: time,
        hora_fin: time
    ) -> List[int]:
        """
        Retorna la lista de IDs de mesas que ya tienen una reserva vigente
        cuyo horario se solapa con el intervalo solicitado.
        Fórmula de solapamiento:
            reserva.hora_inicio < hora_fin AND reserva.hora_fin > hora_inicio
        """
        if not mesas_ids:
            return []

        resultado = (
            db.query(MesaReserva.id_mesa)
            .join(Reserva, MesaReserva.id_reserva == Reserva.id_reserva)
            .filter(
                MesaReserva.id_mesa.in_(mesas_ids),
                Reserva.fecha_reserva == fecha,
                Reserva.estado.in_(ReservaRepository.ESTADOS_BLOQUEANTES),
                Reserva.hora_inicio < hora_fin,
                Reserva.hora_fin > hora_inicio
            )
            .distinct()
            .all()
        )
        return [row[0] for row in resultado]

    @staticmethod
    def obtener_mesas_ocupadas_en_intervalo(
        db: Session,
        id_restaurante: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time
    ) -> Set[int]:
        """
        Retorna un conjunto con todos los IDs de mesas del restaurante que están
        bloqueadas por una reserva vigente en el intervalo solicitado (consulta masiva O(1)).
        """
        resultado = (
            db.query(MesaReserva.id_mesa)
            .join(Reserva, MesaReserva.id_reserva == Reserva.id_reserva)
            .filter(
                Reserva.id_restaurante == id_restaurante,
                Reserva.fecha_reserva == fecha,
                Reserva.estado.in_(ReservaRepository.ESTADOS_BLOQUEANTES),
                Reserva.hora_inicio < hora_fin,
                Reserva.hora_fin > hora_inicio
            )
            .distinct()
            .all()
        )
        return {row[0] for row in resultado}

    @staticmethod
    def crear_reserva(
        db: Session,
        reserva: Reserva,
        mesas_ids: List[int]
    ) -> Reserva:
        """
        Persiste la reserva y sus asociaciones N:M con las mesas dentro de la transacción activa.
        """
        db.add(reserva)
        db.flush()

        for id_m in mesas_ids:
            mr = MesaReserva(
                id_mesa=id_m,
                id_reserva=reserva.id_reserva
            )
            db.add(mr)

        db.flush()
        return reserva

    @staticmethod
    def obtener_por_id(db: Session, id_reserva: int) -> Optional[Reserva]:
        return (
            db.query(Reserva)
            .options(
                joinedload(Reserva.usuario),
                joinedload(Reserva.restaurante),
                joinedload(Reserva.mesas).joinedload(Mesa.area),
                joinedload(Reserva.planificacion)
            )
            .filter(Reserva.id_reserva == id_reserva)
            .first()
        )

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int) -> List[Reserva]:
        return (
            db.query(Reserva)
            .options(
                joinedload(Reserva.restaurante),
                joinedload(Reserva.mesas).joinedload(Mesa.area)
            )
            .filter(Reserva.id_usuario == id_usuario)
            .order_by(Reserva.fecha_reserva.desc(), Reserva.hora_inicio.desc())
            .all()
        )

    @staticmethod
    def listar_por_restaurante(
        db: Session,
        id_restaurante: int,
        fecha: Optional[date] = None,
        estado: Optional[str] = None,
        id_area: Optional[int] = None
    ) -> List[Reserva]:
        query = (
            db.query(Reserva)
            .options(
                joinedload(Reserva.usuario),
                joinedload(Reserva.mesas).joinedload(Mesa.area)
            )
            .filter(Reserva.id_restaurante == id_restaurante)
        )

        if fecha:
            query = query.filter(Reserva.fecha_reserva == fecha)
        if estado:
            query = query.filter(Reserva.estado == estado.upper())
        if id_area:
            query = query.join(MesaReserva, Reserva.id_reserva == MesaReserva.id_reserva).join(Mesa, MesaReserva.id_mesa == Mesa.id_mesa).filter(Mesa.id_area == id_area).distinct()

        return query.order_by(Reserva.fecha_reserva.desc(), Reserva.hora_inicio.desc()).all()

    @staticmethod
    def actualizar_estado(db: Session, id_reserva: int, nuevo_estado: str) -> Optional[Reserva]:
        reserva = db.query(Reserva).filter(Reserva.id_reserva == id_reserva).first()
        if reserva:
            reserva.estado = nuevo_estado
            db.commit()
            db.refresh(reserva)
        return reserva
