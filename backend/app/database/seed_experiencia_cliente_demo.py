"""Reservas, invitados de prueba y pedidos para las cuentas cliente existentes."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.seed_demo_util import ejecutar_comando
from app.models.area_restaurante import AreaRestaurante
from app.models.detalle_pedido import DetallePedido
from app.models.mesa import Mesa
from app.models.mesa_reserva import MesaReserva
from app.models.pedido import Pedido
from app.models.plato import Plato
from app.models.reserva import Reserva
from app.models.reserva_invitado import ReservaInvitado
from app.models.restaurante import Restaurante
from app.models.rol import Rol
from app.models.usuario import Usuario


CLIENTES = ("cliente1@menuopt.com", "cliente2@menuopt.com")
ESTADOS_RESERVA = ("CONFIRMADA", "PENDIENTE", "FINALIZADA", "CANCELADA", "CONFIRMADA")
DIAS_RESERVA = (3, 7, -4, 10, 14)
PERSONAS = (2, 4, 2, 2, 4)
ESTADOS_PEDIDO = {
    0: "ACEPTADO",
    1: "PENDIENTE",
    2: "ENTREGADO",
    3: "CANCELADO",
    4: "EN_PREPARACION",
    5: "LISTO",
    6: "ACEPTADO",
    7: "ENTREGADO",
    9: "PENDIENTE",
}


def sembrar(db: Session) -> dict[str, int]:
    clientes = {
        usuario.correo: usuario
        for usuario in db.scalars(select(Usuario).join(Usuario.rol).where(
            Usuario.correo.in_(CLIENTES),
            Usuario.estado == "ACTIVO",
            Rol.nombre == "CLIENTE",
        )).all()
    }
    faltan = set(CLIENTES) - clientes.keys()
    if faltan:
        raise RuntimeError("Faltan cuentas CLIENTE existentes: " + ", ".join(sorted(faltan)))

    restaurantes = db.scalars(
        select(Restaurante).where(Restaurante.nombre.like("DEMO | %")).order_by(Restaurante.id_restaurante)
    ).all()
    if len(restaurantes) < 10:
        raise RuntimeError("Ejecuta primero el seeder de restaurantes: se requieren al menos 10 locales DEMO.")

    creadas_reservas = invitados_nuevos = pedidos_nuevos = detalles_nuevos = 0
    todas_las_reservas: list[tuple[int, Usuario, Reserva, int]] = []
    hoy = date.today()

    for indice_cliente, correo in enumerate(CLIENTES):
        cliente = clientes[correo]
        for secuencia in range(5):
            global_idx = indice_cliente * 5 + secuencia
            restaurante = restaurantes[global_idx]
            estado = ESTADOS_RESERVA[secuencia]
            fecha = hoy + timedelta(days=DIAS_RESERVA[secuencia])
            cantidad = PERSONAS[secuencia]
            marca = f"DEMO-EXP-{indice_cliente + 1}-{secuencia + 1}"
            obs = f"DEMO | Reserva de ejemplo {marca}; datos demostrativos, no es una reserva real."

            areas = db.scalars(select(AreaRestaurante).where(
                AreaRestaurante.id_restaurante == restaurante.id_restaurante,
                AreaRestaurante.nombre == "DEMO | Salón principal",
            )).all()
            if not areas:
                raise RuntimeError(f"Falta el área demostrativa de {restaurante.nombre}.")
            mesas = db.scalars(select(Mesa).where(
                Mesa.id_area == areas[0].id_area,
                Mesa.activo.is_(True),
                Mesa.capacidad >= cantidad,
            ).order_by(Mesa.capacidad, Mesa.numero)).all()
            if not mesas:
                raise RuntimeError(f"No hay mesa con capacidad {cantidad} en {restaurante.nombre}.")
            mesa = mesas[0]

            reserva = db.scalar(select(Reserva).where(
                Reserva.id_usuario == cliente.id_usuario,
                Reserva.id_restaurante == restaurante.id_restaurante,
                Reserva.observaciones == obs,
            ))
            if reserva is None:
                reserva = Reserva(
                    fecha_reserva=fecha,
                    hora_inicio=time(19, 0),
                    hora_fin=time(20, 30),
                    cantidad_personas=cantidad,
                    estado=estado,
                    observaciones=obs,
                    id_usuario=cliente.id_usuario,
                    id_restaurante=restaurante.id_restaurante,
                )
                db.add(reserva)
                db.flush()
                db.add(MesaReserva(id_mesa=mesa.id_mesa, id_reserva=reserva.id_reserva))
                creadas_reservas += 1

            actuales = db.scalars(select(ReservaInvitado).where(
                ReservaInvitado.id_reserva == reserva.id_reserva
            )).all()
            invitados_necesarios = max(0, cantidad - 1)
            for n in range(len(actuales), invitados_necesarios):
                db.add(ReservaInvitado(
                    id_reserva=reserva.id_reserva,
                    id_usuario=None,
                    nombre=f"Invitado DEMO {global_idx + 1:02d}-{n + 1:02d}",
                    correo=None,
                ))
                invitados_nuevos += 1
            db.flush()
            todas_las_reservas.append((global_idx, cliente, reserva, global_idx))

    db.flush()
    invitados_por_reserva = {
        r.id_reserva: db.scalars(select(ReservaInvitado).where(ReservaInvitado.id_reserva == r.id_reserva)
            .order_by(ReservaInvitado.id_invitado)).first()
        for _, _, r, _ in todas_las_reservas
    }

    for global_idx, cliente, reserva, _ in todas_las_reservas:
        if global_idx not in ESTADOS_PEDIDO:
            continue
        marca = f"DEMO | Pedido DEMO-EXP-{global_idx + 1:02d}"
        existe = db.scalar(select(Pedido).where(
            Pedido.id_usuario == cliente.id_usuario,
            Pedido.id_restaurante == reserva.id_restaurante,
            Pedido.observaciones.like(marca + "%"),
        ))
        if existe is not None:
            continue
        platos = db.scalars(select(Plato).where(
            Plato.id_restaurante == reserva.id_restaurante,
            Plato.estado == "ACTIVO",
            Plato.disponible.is_(True),
        ).order_by(Plato.id_plato).limit(2)).all()
        if not platos:
            raise RuntimeError(f"No hay platos activos en {reserva.restaurante.nombre}.")

        pedido = Pedido(
            estado=ESTADOS_PEDIDO[global_idx],
            total=Decimal("0.00"),
            observaciones=marca + "; pedido de ejemplo, no es una compra real.",
            id_usuario=cliente.id_usuario,
            id_restaurante=reserva.id_restaurante,
            id_reserva=reserva.id_reserva,
        )
        db.add(pedido)
        db.flush()
        total = Decimal("0.00")
        for indice_plato, plato in enumerate(platos):
            cantidad_item = 1 if indice_plato == 0 else 2
            precio = Decimal(plato.precio)
            subtotal = (precio * cantidad_item).quantize(Decimal("0.01"))
            total += subtotal
            db.add(DetallePedido(
                cantidad=cantidad_item,
                precio_unitario=precio,
                subtotal=subtotal,
                id_pedido=pedido.id_pedido,
                id_plato=plato.id_plato,
                id_invitado=(invitados_por_reserva[reserva.id_reserva].id_invitado
                             if indice_plato > 0 and invitados_por_reserva[reserva.id_reserva] else None),
            ))
            detalles_nuevos += 1
        pedido.total = total
        pedidos_nuevos += 1

    return {
        "reservas_nuevas": creadas_reservas,
        "invitados_demo_nuevos": invitados_nuevos,
        "pedidos_nuevos": pedidos_nuevos,
        "lineas_de_pedido_nuevas": detalles_nuevos,
    }


if __name__ == "__main__":
    ejecutar_comando("experiencia de cliente: reservas, invitados y pedidos", sembrar)
