# CASO DE USO: CU23 - Enviar pedido & CU24 - Gestionar pedidos
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.models.plato import Plato
from app.models.usuario import Usuario
from app.models.restaurante import Restaurante


class PedidoRepository:

    @staticmethod
    def crear_pedido(
        db: Session,
        pedido: Pedido,
        detalles: List[DetallePedido]
    ) -> Pedido:
        """
        Persiste el pedido y sus líneas de detalle dentro de la transacción activa.
        """
        db.add(pedido)
        db.flush()  # Obtiene id_pedido

        for det in detalles:
            det.id_pedido = pedido.id_pedido
            db.add(det)

        db.flush()
        return pedido

    @staticmethod
    def obtener_por_id(db: Session, id_pedido: int) -> Optional[Pedido]:
        return (
            db.query(Pedido)
            .options(
                joinedload(Pedido.usuario),
                joinedload(Pedido.restaurante),
                joinedload(Pedido.detalles).joinedload(DetallePedido.plato),
                joinedload(Pedido.reserva)
            )
            .filter(Pedido.id_pedido == id_pedido)
            .first()
        )

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario: int) -> List[Pedido]:
        return (
            db.query(Pedido)
            .options(
                joinedload(Pedido.restaurante),
                joinedload(Pedido.detalles).joinedload(DetallePedido.plato)
            )
            .filter(Pedido.id_usuario == id_usuario)
            .order_by(Pedido.fecha_pedido.desc())
            .all()
        )

    @staticmethod
    def listar_por_restaurante(
        db: Session,
        id_restaurante: int,
        estado: Optional[str] = None,
        fecha: Optional[date] = None,
        id_reserva: Optional[int] = None
    ) -> List[Pedido]:
        query = (
            db.query(Pedido)
            .options(
                joinedload(Pedido.usuario),
                joinedload(Pedido.detalles).joinedload(DetallePedido.plato),
                joinedload(Pedido.reserva)
            )
            .filter(Pedido.id_restaurante == id_restaurante)
        )

        if estado:
            query = query.filter(Pedido.estado == estado.upper().strip())
        if fecha:
            # Filtrar por fecha exacta (CAST a date o func.date)
            from sqlalchemy import cast, Date
            query = query.filter(cast(Pedido.fecha_pedido, Date) == fecha)
        if id_reserva:
            query = query.filter(Pedido.id_reserva == id_reserva)

        return query.order_by(Pedido.fecha_pedido.desc()).all()

    @staticmethod
    def actualizar_estado(db: Session, pedido: Pedido, nuevo_estado: str) -> Pedido:
        pedido.estado = nuevo_estado
        db.commit()
        db.refresh(pedido)
        return pedido
