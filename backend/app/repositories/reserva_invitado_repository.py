from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.reserva_invitado import ReservaInvitado


class ReservaInvitadoRepository:
    @staticmethod
    def usuario_vinculado(db: Session, id_reserva: int, id_usuario: int) -> bool:
        return (
            db.query(ReservaInvitado.id_invitado)
            .filter(
                ReservaInvitado.id_reserva == id_reserva,
                ReservaInvitado.id_usuario == id_usuario,
            )
            .first()
            is not None
        )

    @staticmethod
    def listar(db: Session, id_reserva: int) -> List[ReservaInvitado]:
        return (
            db.query(ReservaInvitado)
            .filter(ReservaInvitado.id_reserva == id_reserva)
            .order_by(ReservaInvitado.id_invitado)
            .all()
        )

    @staticmethod
    def obtener(db: Session, id_reserva: int, id_invitado: int) -> Optional[ReservaInvitado]:
        return (
            db.query(ReservaInvitado)
            .filter(
                ReservaInvitado.id_reserva == id_reserva,
                ReservaInvitado.id_invitado == id_invitado,
            )
            .first()
        )

    @staticmethod
    def tiene_pedidos_vinculados(db: Session, invitado: ReservaInvitado) -> bool:
        if (
            db.query(DetallePedido.id_detalle_pedido)
            .filter(DetallePedido.id_invitado == invitado.id_invitado)
            .first()
            is not None
        ):
            return True
        if invitado.id_usuario is None:
            return False
        return (
            db.query(Pedido.id_pedido)
            .filter(
                Pedido.id_reserva == invitado.id_reserva,
                Pedido.id_usuario == invitado.id_usuario,
            )
            .first()
            is not None
        )
