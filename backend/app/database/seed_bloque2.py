"""Datos de demostración aislados para los casos de uso CU05-CU24 (Bloque 2).

Uso únicamente en desarrollo/pruebas. La contraseña de las cuentas la aporta
quien ejecuta el comando mediante B2_SEED_PASSWORD; nunca se guarda en el código.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.security.contrasenas import generar_hash_contrasena

from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.ubicacion import Ubicacion
from app.models.restaurante import Restaurante
from app.models.categoria import Categoria
from app.models.plato import Plato
from app.models.ingrediente import Ingrediente
from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
from app.models.plato_ingrediente import PlatoIngrediente
from app.models.area_restaurante import AreaRestaurante
from app.models.mesa import Mesa
from app.models.mesa_combinacion import MesaCombinacion
from app.models.reserva import Reserva
from app.models.mesa_reserva import MesaReserva
from app.models.reserva_invitado import ReservaInvitado
from app.models.pedido import Pedido
from app.models.detalle_pedido import DetallePedido


MARCA = "B2-DEMO"
EMAILS = {
    "resto_a": "b2.restaurante.a@example.com",
    "resto_b": "b2.restaurante.b@example.com",
    "cliente_a": "b2.cliente.a@example.com",
    "cliente_b": "b2.cliente.b@example.com",
    "cliente_c": "b2.cliente.c@example.com",
}
CATEGORIAS = ["B2 | Tradicional", "B2 | Parrilla", "B2 | Vegetariano", "B2 | Bebidas"]
INGREDIENTES = [
    ("B2 | Carne de res", "g", Decimal("0.08")),
    ("B2 | Queso", "g", Decimal("0.04")),
    ("B2 | Tomate", "g", Decimal("0.02")),
    ("B2 | Papa", "g", Decimal("0.01")),
    ("B2 | Quinoa", "g", Decimal("0.03")),
    ("B2 | Limonada", "ml", Decimal("0.01")),
]
RESTAURANTES = [
    {"nombre": "B2-DEMO | Sabor Cruceño", "correo": "b2.sabor@example.com", "nit": "B2-DEMO-001", "ciudad": "Santa Cruz", "direccion": "Av. Test 101", "owner": "resto_a"},
    {"nombre": "B2-DEMO | Patio Andino", "correo": "b2.andino@example.com", "nit": "B2-DEMO-002", "ciudad": "Cochabamba", "direccion": "Calle Test 202", "owner": "resto_b"},
]


def _entorno_permitido() -> str:
    entorno = (os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "").strip().lower()
    if entorno not in {"dev", "development", "test", "testing"}:
        raise RuntimeError("Seeder bloqueado: define APP_ENV=development o APP_ENV=test.")
    return entorno


def _preflight(database_engine) -> None:
    # Comprueba conectividad antes de abrir una transacción o insertar datos.
    with database_engine.connect() as conn:
        conn.execute(select(func.now()))


def _validar_destino(database_engine, entorno: str) -> None:
    nombre_db = (database_engine.url.database or "").lower()
    host = (database_engine.url.host or "").lower()
    if entorno == "test":
        if "test" not in nombre_db:
            raise RuntimeError("APP_ENV=test requiere una base cuyo nombre incluya 'test'.")
        return
    hosts_locales = {"postgres", "localhost", "127.0.0.1", "::1", "host.docker.internal"}
    bases_desarrollo = {"menuopt", "menuopt_db", "menuopt_dev", "menuopt_development"}
    if host not in hosts_locales or nombre_db not in bases_desarrollo:
        raise RuntimeError(
            "En desarrollo solo se permite una base local menuopt/menuopt_db/menuopt_dev/menuopt_development. "
            "Usa APP_ENV=test con una base cuyo nombre incluya 'test' para validaciones aisladas."
        )


def _cuentas(db: Session, password_hash: str) -> dict[str, Usuario]:
    roles = {r.nombre: r for r in db.query(Rol).filter(Rol.nombre.in_(["RESTAURANTE", "CLIENTE"])).all()}
    faltantes = {"RESTAURANTE", "CLIENTE"} - roles.keys()
    if faltantes:
        raise RuntimeError(f"Faltan roles base: {', '.join(sorted(faltantes))}. Ejecuta primero crear_admin.")
    cuentas: dict[str, Usuario] = {}
    datos = [
        ("resto_a", "Restaurante", "Prueba A", "70100001", "RESTAURANTE"),
        ("resto_b", "Restaurante", "Prueba B", "70100002", "RESTAURANTE"),
        ("cliente_a", "Cliente", "Prueba A", "70200001", "CLIENTE"),
        ("cliente_b", "Cliente", "Prueba B", "70200002", "CLIENTE"),
        ("cliente_c", "Cliente", "Prueba C", "70200003", "CLIENTE"),
    ]
    for clave, nombres, apellidos, telefono, nombre_rol in datos:
        correo = EMAILS[clave]
        if db.query(Usuario).filter(Usuario.correo == correo).first():
            raise RuntimeError(f"Ya existe {correo}; limpia el conjunto {MARCA} antes de recrearlo.")
        usuario = Usuario(
            nombres=nombres, apellidos=apellidos, correo=correo,
            contrasena_hash=password_hash, telefono=telefono, estado="ACTIVO",
            id_rol=roles[nombre_rol].id_rol,
        )
        db.add(usuario)
        cuentas[clave] = usuario
    db.flush()
    return cuentas


def sembrar(db: Session, password: str) -> dict[str, int]:
    """Inserta el set completo en una transacción; un reintento no duplica datos."""
    if len(password) < 12:
        raise ValueError("B2_SEED_PASSWORD debe contener al menos 12 caracteres.")
    if any(db.query(Usuario).filter(Usuario.correo == e).first() for e in EMAILS.values()):
        raise RuntimeError(f"Ya hay cuentas {MARCA}; usa --clean antes de regenerar el set.")

    password_hash = generar_hash_contrasena(password)
    cuentas = _cuentas(db, password_hash)
    categorias: dict[str, Categoria] = {}
    for nombre in CATEGORIAS:
        cat = db.query(Categoria).filter(Categoria.nombre == nombre).one_or_none()
        if cat is None:
            cat = Categoria(nombre=nombre, descripcion="Categoría ficticia para pruebas Bloque 2", activo=True)
            db.add(cat)
        categorias[nombre] = cat
    ingredientes: dict[str, Ingrediente] = {}
    for nombre, unidad, precio in INGREDIENTES:
        ing = Ingrediente(nombre=nombre, unidad_medida=unidad, precio_estimado=precio,
                          descripcion="Ingrediente ficticio de demostración", estado="ACTIVO")
        db.add(ing)
        ingredientes[nombre] = ing
    db.flush()

    restaurantes: list[Restaurante] = []
    areas_por_restaurante: list[list[AreaRestaurante]] = []
    mesas_por_restaurante: list[list[list[Mesa]]] = []
    platos_por_restaurante: list[list[Plato]] = []
    elementos = json.dumps([
        {"id": "b2-cocina", "tipo": "COCINA", "nombre": "Cocina", "posicion_x": 0.08, "posicion_y": 0.08, "ancho": 0.18, "alto": 0.14, "rotacion": 0, "icono": "restaurant"},
        {"id": "b2-acceso", "tipo": "ACCESO", "nombre": "Acceso", "posicion_x": 0.5, "posicion_y": 0.92, "ancho": 0.14, "alto": 0.07, "rotacion": 0, "icono": "door"},
    ], ensure_ascii=False)

    nombres_platos = [
        ("B2 | Majadito de prueba", Decimal("32.50"), "Tradicional", 1),
        ("B2 | Parrillada para dos", Decimal("89.90"), "Parrilla", 2),
        ("B2 | Bowl de quinoa", Decimal("28.75"), "Vegetariano", 1),
        ("B2 | Limonada", Decimal("8.40"), "Bebidas", 1),
    ]
    for idx, dato in enumerate(RESTAURANTES):
        ubicacion = Ubicacion(direccion=dato["direccion"], ciudad=dato["ciudad"], zona="Zona de pruebas",
                              referencia=f"{MARCA}; ubicación ficticia")
        db.add(ubicacion)
        db.flush()
        resto = Restaurante(
            nombre=dato["nombre"], descripcion="Restaurante ficticio para pruebas manuales del Bloque 2.",
            nit=dato["nit"], telefono=f"7001000{idx}", correo=dato["correo"],
            horario_apertura=time(8, 0), horario_cierre=time(23, 0), estado="ACTIVO",
            id_usuario_responsable=cuentas[dato["owner"]].id_usuario,
            id_ubicacion=ubicacion.id_ubicacion,
        )
        db.add(resto)
        db.flush()
        restaurantes.append(resto)

        areas = []
        mesas_areas = []
        for area_idx, area_nombre in enumerate(["B2 Salón Principal", "B2 Terraza"]):
            area = AreaRestaurante(
                nombre=area_nombre, descripcion=f"Área ficticia {area_idx + 1} para CU17-CU22 ({MARCA})",
                ancho_mapa=1200, alto_mapa=700, activo=True, orden=area_idx + 1,
                elementos=elementos, id_restaurante=resto.id_restaurante,
            )
            db.add(area)
            db.flush()
            areas.append(area)
            mesas = []
            configuracion = [
                ("01", 2, "REDONDA", .18, .25, False, True),
                ("02", 4, "CUADRADA", .40, .25, False, True),
                ("03", 4, "RECTANGULAR", .62, .25, False, True),
                ("04", 6, "REDONDA", .82, .55, False, True),
                ("05", 8, "RECTANGULAR", .42, .70, True, False),
            ]
            for numero, capacidad, forma, x, y, fija, combinable in configuracion:
                mesa = Mesa(
                    id_area=area.id_area, numero=f"B2-{numero}", nombre=f"{area_nombre} · Mesa {numero}",
                    capacidad=capacidad, forma=forma, posicion_x=Decimal(str(x)), posicion_y=Decimal(str(y)),
                    rotacion=0, ancho=Decimal("0.09"), alto=Decimal("0.09"), es_fija=fija,
                    combinable=combinable, activo=True,
                )
                db.add(mesa)
                mesas.append(mesa)
            db.flush()
            # Parejas existentes válidas y una mesa fija/no combinable para intentar casos negativos vía API.
            for origen, destino in [(0, 1), (1, 2)]:
                db.add(MesaCombinacion(
                    id_mesa_origen=mesas[origen].id_mesa, id_mesa_destino=mesas[destino].id_mesa,
                    permitida=True, activo=True, descripcion=f"Combinación de demostración {MARCA}",
                ))
            mesas_areas.append(mesas)
        areas_por_restaurante.append(areas)
        mesas_por_restaurante.append(mesas_areas)

        platos = []
        for pidx, (nombre_base, precio, categoria_base, personas) in enumerate(nombres_platos):
            cat = categorias[f"B2 | {categoria_base}"]
            plato = Plato(
                nombre=f"{nombre_base} · {idx + 1}",
                descripcion=f"Plato ficticio para validar recetas, precios e interfaz ({MARCA}).",
                precio=precio, tipo_comida="ALMUERZO" if pidx < 3 else "BEBIDA",
                personas_cubiertas=personas, disponible=pidx != 3, estado="ACTIVO",
                id_restaurante=resto.id_restaurante, id_categoria=cat.id_categoria,
            )
            db.add(plato)
            db.flush()
            platos.append(plato)
            insumos = list(ingredientes.values())
            receta = [insumos[pidx % len(insumos)], insumos[(pidx + 1) % len(insumos)]]
            for ing in receta:
                db.add(PlatoIngrediente(
                    id_plato=plato.id_plato, id_ingrediente=ing.id_ingrediente,
                    cantidad=Decimal("150.00"), unidad_medida=ing.unidad_medida,
                ))
        platos_por_restaurante.append(platos)

    db.flush()
    hoy = date.today()
    reservas: list[list[Reserva]] = []
    invitados_por_reserva: dict[int, list[ReservaInvitado]] = {}
    for ridx, resto in enumerate(restaurantes):
        cliente = cuentas["cliente_a" if ridx == 0 else "cliente_b"]
        otras_mesas = mesas_por_restaurante[ridx][0]
        casos = [
            (hoy + timedelta(days=3), time(19), time(21), 4, "CONFIRMADA", 1, "Reserva confirmada para probar ocupación y conflicto 409."),
            (hoy + timedelta(days=3), time(19, 30), time(20, 30), 2, "PENDIENTE", 0, "Reserva pendiente para probar confirmación."),
            (hoy + timedelta(days=4), time(13), time(14, 30), 6, "CONFIRMADA", 3, "Reserva grupal con invitado que tiene pedido."),
            (hoy - timedelta(days=2), time(20), time(22), 2, "FINALIZADA", 2, "Reserva histórica finalizada."),
            (hoy + timedelta(days=5), time(18), time(19), 2, "CANCELADA", 0, "Reserva cancelada de referencia."),
        ]
        reservas_resto = []
        for n, (fecha, inicio, fin, personas, estado, mesa_idx, obs) in enumerate(casos):
            reserva = Reserva(
                fecha_reserva=fecha, hora_inicio=inicio, hora_fin=fin, cantidad_personas=personas,
                estado=estado, observaciones=f"{MARCA}: {obs}", id_usuario=cliente.id_usuario,
                id_restaurante=resto.id_restaurante,
            )
            db.add(reserva)
            db.flush()
            db.add(MesaReserva(id_mesa=otras_mesas[mesa_idx].id_mesa, id_reserva=reserva.id_reserva))
            reservas_resto.append(reserva)
            invitados: list[ReservaInvitado] = []
            if n == 0:
                invitados.extend([
                    ReservaInvitado(id_reserva=reserva.id_reserva, id_usuario=cuentas["cliente_c"].id_usuario,
                                    nombre="Cliente Prueba C", correo=EMAILS["cliente_c"]),
                    ReservaInvitado(id_reserva=reserva.id_reserva, nombre=f"Invitado libre {ridx + 1}",
                                    correo=f"b2.invitado.libre.{ridx + 1}@example.com"),
                ])
            elif n == 2:
                invitados.extend([
                    ReservaInvitado(id_reserva=reserva.id_reserva, nombre=f"Invitado con pedido {ridx + 1}",
                                    correo=f"b2.invitado.pedido.{ridx + 1}@example.com"),
                    ReservaInvitado(id_reserva=reserva.id_reserva, nombre=f"Invitado sin pedido {ridx + 1}",
                                    correo=f"b2.invitado.suelto.{ridx + 1}@example.com"),
                ])
            if n == 1:
                invitados.append(ReservaInvitado(
                    id_reserva=reserva.id_reserva, nombre=f"Titular invitado {ridx + 1}",
                    correo=f"b2.titular.invitado.{ridx + 1}@example.com",
                ))
            db.add_all(invitados)
            db.flush()
            invitados_por_reserva[reserva.id_reserva] = invitados
        reservas.append(reservas_resto)

    db.flush()
    estados_pedido = ["PENDIENTE", "ACEPTADO", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO"]
    total_pedidos = 0
    for ridx, resto in enumerate(restaurantes):
        cliente = cuentas["cliente_a" if ridx == 0 else "cliente_b"]
        platos = platos_por_restaurante[ridx]
        lista_reservas = reservas[ridx]
        for pidx, estado in enumerate(estados_pedido):
            reserva = lista_reservas[2] if pidx in (1, 2, 3) else lista_reservas[0]
            invitados = invitados_por_reserva[reserva.id_reserva]
            invitado_id = invitados[0].id_invitado if invitados else None
            platos_comprables = platos[:3]  # El cuarto permanece no disponible para probar CU08.
            indice_plato = pidx % len(platos_comprables)
            cantidades = [(platos_comprables[indice_plato], pidx % 3 + 1, invitado_id)]
            # Una segunda línea hace visible la suma exacta Decimal en varios pedidos.
            if pidx % 2 == 0:
                cantidades.append((platos_comprables[(indice_plato + 1) % len(platos_comprables)], 2, None))
            detalles = []
            total = Decimal("0.00")
            for plato, cantidad, id_invitado in cantidades:
                precio_snapshot = Decimal(plato.precio).quantize(Decimal("0.01"))
                subtotal = (precio_snapshot * cantidad).quantize(Decimal("0.01"))
                total += subtotal
                detalles.append(DetallePedido(
                    cantidad=cantidad, precio_unitario=precio_snapshot, subtotal=subtotal,
                    id_plato=plato.id_plato, id_invitado=id_invitado,
                ))
            pedido = Pedido(
                estado=estado, total=total, observaciones=f"{MARCA}: pedido de demostración estado {estado}",
                id_usuario=cliente.id_usuario, id_restaurante=resto.id_restaurante,
                id_reserva=reserva.id_reserva, detalles=detalles,
            )
            db.add(pedido)
            total_pedidos += 1
    db.flush()
    return {
        "usuarios": len(cuentas), "restaurantes": len(restaurantes),
        "areas": sum(map(len, areas_por_restaurante)),
        "mesas": sum(len(area) for grupo in mesas_por_restaurante for area in grupo),
        "categorias": len(CATEGORIAS), "platos": sum(map(len, platos_por_restaurante)),
        "ingredientes": len(INGREDIENTES), "reservas": sum(map(len, reservas)),
        "invitados": sum(len(v) for v in invitados_por_reserva.values()), "pedidos": total_pedidos,
    }


def limpiar(db: Session) -> dict[str, int]:
    """Borra únicamente filas identificadas por las cuentas y etiquetas B2-DEMO."""
    correos = list(EMAILS.values())
    usuarios = db.query(Usuario).filter(Usuario.correo.in_(correos)).all()
    ids_usuarios = [u.id_usuario for u in usuarios]
    restaurantes = db.query(Restaurante).filter(Restaurante.nombre.like(f"{MARCA} |%")).all()
    ids_restos = [r.id_restaurante for r in restaurantes]
    if not ids_usuarios and not ids_restos:
        return {"eliminados": 0}

    reservas = db.query(Reserva).filter(Reserva.id_restaurante.in_(ids_restos)).all() if ids_restos else []
    ids_reservas = [r.id_reserva for r in reservas]
    pedidos_q = db.query(Pedido)
    filtros = []
    if ids_restos:
        filtros.append(Pedido.id_restaurante.in_(ids_restos))
    filtros.append(Pedido.observaciones.like(f"{MARCA}:%"))
    pedidos = pedidos_q.filter(or_(*filtros)).all() if filtros else []
    ids_pedidos = [p.id_pedido for p in pedidos]
    ids_invitados = [g.id_invitado for g in db.query(ReservaInvitado).filter(
        ReservaInvitado.id_reserva.in_(ids_reservas)
    ).all()] if ids_reservas else []
    counts = {"pedidos": len(pedidos), "reservas": len(reservas), "restaurantes": len(restaurantes)}

    if ids_pedidos:
        db.query(DetallePedido).filter(DetallePedido.id_pedido.in_(ids_pedidos)).delete(synchronize_session=False)
        db.query(Pedido).filter(Pedido.id_pedido.in_(ids_pedidos)).delete(synchronize_session=False)
    if ids_invitados:
        db.query(ReservaInvitado).filter(ReservaInvitado.id_invitado.in_(ids_invitados)).delete(synchronize_session=False)
    if ids_reservas:
        db.query(MesaReserva).filter(MesaReserva.id_reserva.in_(ids_reservas)).delete(synchronize_session=False)
        db.query(Reserva).filter(Reserva.id_reserva.in_(ids_reservas)).delete(synchronize_session=False)

    ids_areas = [a.id_area for a in db.query(AreaRestaurante).filter(AreaRestaurante.id_restaurante.in_(ids_restos)).all()] if ids_restos else []
    ids_mesas = [m.id_mesa for m in db.query(Mesa).filter(Mesa.id_area.in_(ids_areas)).all()] if ids_areas else []
    if ids_mesas:
        db.query(MesaCombinacion).filter(or_(MesaCombinacion.id_mesa_origen.in_(ids_mesas), MesaCombinacion.id_mesa_destino.in_(ids_mesas))).delete(synchronize_session=False)
        db.query(Mesa).filter(Mesa.id_mesa.in_(ids_mesas)).delete(synchronize_session=False)
    if ids_areas:
        db.query(AreaRestaurante).filter(AreaRestaurante.id_area.in_(ids_areas)).delete(synchronize_session=False)

    platos = db.query(Plato).filter(Plato.id_restaurante.in_(ids_restos)).all() if ids_restos else []
    ids_platos = [p.id_plato for p in platos]
    if ids_platos:
        db.query(PlatoIngrediente).filter(PlatoIngrediente.id_plato.in_(ids_platos)).delete(synchronize_session=False)
        db.query(Plato).filter(Plato.id_plato.in_(ids_platos)).delete(synchronize_session=False)

    ubicacion_ids = [r.id_ubicacion for r in restaurantes]
    if ids_restos:
        db.query(Restaurante).filter(Restaurante.id_restaurante.in_(ids_restos)).delete(synchronize_session=False)
    if ubicacion_ids:
        db.query(Ubicacion).filter(Ubicacion.id_ubicacion.in_(ubicacion_ids)).delete(synchronize_session=False)

    # Categorías e ingredientes B2 se retiran solo si ya no tienen referencias ajenas.
    for cat in db.query(Categoria).filter(Categoria.nombre.in_(CATEGORIAS)).all():
        if db.query(Plato).filter(Plato.id_categoria == cat.id_categoria).count() == 0:
            db.delete(cat)
    for ing in db.query(Ingrediente).filter(Ingrediente.nombre.like("B2 |%")).all():
        tiene_receta = db.query(PlatoIngrediente).filter(PlatoIngrediente.id_ingrediente == ing.id_ingrediente).count()
        tiene_catalogo = db.query(IngredienteLugarCompra).filter(
            IngredienteLugarCompra.id_ingrediente == ing.id_ingrediente
        ).count()
        # Si se reutilizó fuera del fixture, se conserva para no romper relaciones ajenas.
        if not tiene_receta and not tiene_catalogo:
            db.delete(ing)

    # No borrar cuentas de prueba que alguien haya reutilizado en registros ajenos.
    from app.models.planificacion import Planificacion
    from app.models.usuario_preferencia import UsuarioPreferencia
    for usuario in usuarios:
        if not db.query(Restaurante).filter(Restaurante.id_usuario_responsable == usuario.id_usuario).count() \
                and not db.query(Reserva).filter(Reserva.id_usuario == usuario.id_usuario).count() \
                and not db.query(Pedido).filter(Pedido.id_usuario == usuario.id_usuario).count() \
                and not db.query(Planificacion).filter(Planificacion.id_usuario == usuario.id_usuario).count() \
                and not db.query(UsuarioPreferencia).filter(UsuarioPreferencia.id_usuario == usuario.id_usuario).count():
            db.delete(usuario)
    counts["usuarios"] = len(usuarios)
    return counts


def _run(clean: bool) -> None:
    entorno = _entorno_permitido()
    from app.database.conexion import SessionLocal, engine

    _validar_destino(engine, entorno)
    _preflight(engine)
    db = SessionLocal()
    try:
        if clean:
            resultado = limpiar(db)
            db.commit()
            print(f"Limpieza {MARCA} completada en entorno {entorno}: {resultado}")
            return
        password = os.getenv("B2_SEED_PASSWORD")
        password_file = os.getenv("B2_SEED_PASSWORD_FILE")
        if password and password_file:
            raise RuntimeError("Configura B2_SEED_PASSWORD o B2_SEED_PASSWORD_FILE, no ambos.")
        if password_file:
            try:
                contenido = Path(password_file).read_text(encoding="utf-8")
            except OSError:
                raise RuntimeError("No se pudo leer el archivo indicado por B2_SEED_PASSWORD_FILE.") from None
            valores_etiquetados = [
                linea.partition("Password:")[2].strip()
                for linea in contenido.splitlines()
                if linea.startswith("Password:")
            ]
            if len(valores_etiquetados) == 1:
                password = valores_etiquetados[0]
            elif len(contenido.splitlines()) == 1:
                password = contenido.strip()
            else:
                raise RuntimeError("El archivo indicado no contiene una única línea Password válida.")
        if not password:
            password = getpass.getpass(
                "Contraseña temporal para las cuentas B2 (mínimo 12 caracteres): "
            )
        resultado = sembrar(db, password)
        db.commit()
        print(f"Seeder {MARCA} completado en entorno {entorno}: {resultado}")
        print("Cuentas: " + ", ".join(EMAILS.values()))
        print("Las cinco cuentas comparten la contraseña indicada en B2_SEED_PASSWORD.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="elimina solamente el conjunto B2-DEMO")
    args = parser.parse_args()
    try:
        _run(args.clean)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
