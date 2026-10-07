# CASO DE USO: CU23 - Enviar pedido & CU24 - Gestionar pedidos
from decimal import Decimal
from datetime import date
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.restaurante import Restaurante
from app.models.plato import Plato
from app.models.reserva import Reserva
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido
from app.repositories.restaurante_repository import RestauranteRepository
from app.repositories.plato_repository import PlatoRepository
from app.repositories.reserva_repository import ReservaRepository
from app.repositories.pedido_repository import PedidoRepository
from app.schemas.pedido import (
    PedidoCrear,
    PedidoRespuesta,
    PedidoResumen,
    DetallePedidoRespuesta
)


class PedidoService:
    # Máquina de estados de Pedido
    TRANSICIONES_PERMITIDAS = {
        "PENDIENTE": {"ACEPTADO", "CANCELADO"},
        "ACEPTADO": {"EN_PREPARACION", "CANCELADO"},
        "EN_PREPARACION": {"LISTO"},
        "LISTO": {"ENTREGADO"},
        "ENTREGADO": set(),
        "CANCELADO": set(),
    }

    @classmethod
    def _mapear_respuesta(cls, pedido: Pedido) -> PedidoRespuesta:
        detalles_resp = [
            DetallePedidoRespuesta(
                id_detalle_pedido=det.id_detalle_pedido,
                id_plato=det.id_plato,
                nombre_plato=det.plato.nombre if det.plato else f"Plato #{det.id_plato}",
                cantidad=det.cantidad,
                precio_unitario=det.precio_unitario,
                subtotal=det.subtotal
            )
            for det in pedido.detalles
        ]

        cliente = pedido.usuario
        return PedidoRespuesta(
            id_pedido=pedido.id_pedido,
            id_restaurante=pedido.id_restaurante,
            nombre_restaurante=pedido.restaurante.nombre if pedido.restaurante else f"Restaurante #{pedido.id_restaurante}",
            id_usuario=pedido.id_usuario,
            nombre_cliente=f"{cliente.nombres} {cliente.apellidos}" if cliente else None,
            correo_cliente=cliente.correo if cliente else None,
            telefono_cliente=cliente.telefono if cliente else None,
            id_reserva=pedido.id_reserva,
            estado=pedido.estado,
            total=pedido.total,
            observaciones=pedido.observaciones,
            fecha_pedido=pedido.fecha_pedido,
            detalles=detalles_resp
        )

    @classmethod
    def _mapear_resumen(cls, pedido: Pedido) -> PedidoResumen:
        cliente = pedido.usuario
        return PedidoResumen(
            id_pedido=pedido.id_pedido,
            id_restaurante=pedido.id_restaurante,
            nombre_restaurante=pedido.restaurante.nombre if pedido.restaurante else f"Restaurante #{pedido.id_restaurante}",
            id_usuario=pedido.id_usuario,
            nombre_cliente=f"{cliente.nombres} {cliente.apellidos}" if cliente else None,
            id_reserva=pedido.id_reserva,
            estado=pedido.estado,
            total=pedido.total,
            fecha_pedido=pedido.fecha_pedido,
            cantidad_items=sum(det.cantidad for det in pedido.detalles)
        )

    @classmethod
    def crear_pedido(
        cls,
        db: Session,
        datos: PedidoCrear,
        usuario_actual: Usuario
    ) -> PedidoRespuesta:
        """
        CU23: Enviar pedido.
        - Valida restaurante activo.
        - Consolida platos repetidos sumando cantidades.
        - Valida que todos los platos pertenezcan al restaurante, estén activos y disponibles.
        - Copia precio histórico de cada plato en backend y calcula subtotales con Decimal.
        - Valida reserva si fue provista (titularidad, coincidencia de restaurante y estado no CANCELADA).
        - Persiste atómicamente con estado PENDIENTE.
        """
        # 1. Validar restaurante
        resto = RestauranteRepository.buscar_por_id(db, datos.id_restaurante)
        if not resto or resto.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurante #{datos.id_restaurante} no encontrado o inactivo."
            )

        # 2. Consolidar items si el cliente incluyó el mismo plato varias veces
        cantidades_por_plato: Dict[int, int] = {}
        for item in datos.detalles:
            if item.cantidad <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La cantidad del plato #{item.id_plato} debe ser mayor a 0."
                )
            cantidades_por_plato[item.id_plato] = cantidades_por_plato.get(item.id_plato, 0) + item.cantidad

        if not cantidades_por_plato:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El pedido debe contener al menos un plato."
            )

        # 3. Validar reserva opcional asociada
        if datos.id_reserva is not None:
            reserva = ReservaRepository.obtener_por_id(db, datos.id_reserva)
            if not reserva:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Reserva #{datos.id_reserva} no encontrada."
                )
            # Titularidad
            es_admin = bool(usuario_actual.rol and usuario_actual.rol.nombre == "ADMINISTRADOR")
            if reserva.id_usuario != usuario_actual.id_usuario and not es_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="La reserva asociada no pertenece al usuario autenticado."
                )
            # Restaurante coincide
            if reserva.id_restaurante != datos.id_restaurante:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La reserva #{datos.id_reserva} corresponde a otro restaurante (#{reserva.id_restaurante})."
                )
            # No estar cancelada
            if reserva.estado == "CANCELADA":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede asociar un pedido a una reserva cancelada."
                )

        # 4. Validar platos y calcular precios históricos
        detalles_modelo: List[DetallePedido] = []
        total_acumulado = Decimal("0.00")

        for id_plato, cant in cantidades_por_plato.items():
            plato = PlatoRepository.buscar_por_id(db, id_plato)
            if not plato:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plato #{id_plato} no encontrado."
                )
            if plato.id_restaurante != datos.id_restaurante:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El plato '{plato.nombre}' no pertenece al restaurante #{datos.id_restaurante}."
                )
            if plato.estado != "ACTIVO":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El plato '{plato.nombre}' está inactivo y no se puede ordenar."
                )
            if not plato.disponible:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El plato '{plato.nombre}' no está disponible actualmente."
                )

            # Precio histórico backend
            precio_unitario = Decimal(str(plato.precio))
            subtotal = (precio_unitario * Decimal(cant)).quantize(Decimal("0.01"))
            total_acumulado += subtotal

            det = DetallePedido(
                id_plato=id_plato,
                cantidad=cant,
                precio_unitario=precio_unitario,
                subtotal=subtotal
            )
            detalles_modelo.append(det)

        # 5. Instanciar pedido con estado PENDIENTE
        nuevo_pedido = Pedido(
            id_usuario=usuario_actual.id_usuario,
            id_restaurante=datos.id_restaurante,
            id_reserva=datos.id_reserva,
            estado="PENDIENTE",
            total=total_acumulado,
            observaciones=datos.observaciones.strip() if datos.observaciones else None
        )

        pedido_creado = PedidoRepository.crear_pedido(db, nuevo_pedido, detalles_modelo)
        db.commit()

        # Recargar con relaciones completas
        pedido_cargado = PedidoRepository.obtener_por_id(db, pedido_creado.id_pedido)
        return cls._mapear_respuesta(pedido_cargado)

    @classmethod
    def listar_mis_pedidos(cls, db: Session, usuario_actual: Usuario) -> List[PedidoRespuesta]:
        """
        CU24: Lista el historial de pedidos del cliente autenticado.
        """
        pedidos = PedidoRepository.listar_por_usuario(db, usuario_actual.id_usuario)
        return [cls._mapear_respuesta(p) for p in pedidos]

    @classmethod
    def obtener_por_id(cls, db: Session, id_pedido: int, usuario_actual: Usuario) -> PedidoRespuesta:
        """
        CU24: Obtiene el detalle de un pedido con validación de titularidad.
        """
        pedido = PedidoRepository.obtener_por_id(db, id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido #{id_pedido} no encontrado."
            )

        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol == "ADMINISTRADOR":
            pass
        elif rol == "CLIENTE":
            if pedido.id_usuario != usuario_actual.id_usuario:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permiso para consultar un pedido ajeno."
                )
        elif rol == "RESTAURANTE":
            if pedido.restaurante.id_usuario_responsable != usuario_actual.id_usuario:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permiso para consultar pedidos de otro restaurante."
                )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")

        return cls._mapear_respuesta(pedido)

    @classmethod
    def cancelar_pedido_cliente(cls, db: Session, id_pedido: int, usuario_actual: Usuario) -> PedidoRespuesta:
        """
        CU24: El cliente cancela su propio pedido, permitido ÚNICAMENTE si está en estado PENDIENTE.
        """
        pedido = PedidoRepository.obtener_por_id(db, id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido #{id_pedido} no encontrado."
            )

        es_admin = bool(usuario_actual.rol and usuario_actual.rol.nombre == "ADMINISTRADOR")
        if pedido.id_usuario != usuario_actual.id_usuario and not es_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el cliente titular puede cancelar este pedido."
            )

        if pedido.estado != "PENDIENTE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El cliente solo puede cancelar pedidos en estado 'PENDIENTE'. El estado actual es '{pedido.estado}'."
            )

        pedido_actualizado = PedidoRepository.actualizar_estado(db, pedido, "CANCELADO")
        return cls._mapear_respuesta(pedido_actualizado)

    @classmethod
    def listar_pedidos_restaurante(
        cls,
        db: Session,
        id_restaurante: int,
        usuario_actual: Usuario,
        estado: Optional[str] = None,
        fecha: Optional[date] = None,
        id_reserva: Optional[int] = None
    ) -> List[PedidoRespuesta]:
        """
        CU24: Consulta y filtrado de pedidos para el restaurante responsable.
        """
        resto = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not resto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurante #{id_restaurante} no encontrado."
            )

        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol != "ADMINISTRADOR" and resto.id_usuario_responsable != usuario_actual.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para gestionar pedidos de este restaurante."
            )

        pedidos = PedidoRepository.listar_por_restaurante(
            db=db,
            id_restaurante=id_restaurante,
            estado=estado,
            fecha=fecha,
            id_reserva=id_reserva
        )
        return [cls._mapear_respuesta(p) for p in pedidos]

    @classmethod
    def actualizar_estado_restaurante(
        cls,
        db: Session,
        id_pedido: int,
        nuevo_estado: str,
        usuario_actual: Usuario
    ) -> PedidoRespuesta:
        """
        CU24: El restaurante avanza o cancela el estado del pedido según transiciones autorizadas.
        """
        pedido = PedidoRepository.obtener_por_id(db, id_pedido)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pedido #{id_pedido} no encontrado."
            )

        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol != "ADMINISTRADOR" and pedido.restaurante.id_usuario_responsable != usuario_actual.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para modificar pedidos de otro restaurante."
            )

        estado_actual = pedido.estado
        nuevo_upper = nuevo_estado.upper().strip()

        permitidas = cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set())
        if nuevo_upper not in permitidas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transición de estado no permitida de '{estado_actual}' a '{nuevo_upper}'. Permitidas: {list(permitidas) or 'Ninguna'}"
            )

        pedido_actualizado = PedidoRepository.actualizar_estado(db, pedido, nuevo_upper)
        return cls._mapear_respuesta(pedido_actualizado)
