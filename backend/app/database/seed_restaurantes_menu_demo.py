"""12 restaurantes ficticios, cartas coherentes y mesas demostrativas."""
from __future__ import annotations

import json
from datetime import time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.seed_demo_util import ejecutar_comando
from app.models.area_restaurante import AreaRestaurante
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.mesa import Mesa
from app.models.plato import Plato
from app.models.plato_ingrediente import PlatoIngrediente
from app.models.plato_preferencia import PlatoPreferencia
from app.models.preferencia import Preferencia
from app.models.restaurante import Restaurante
from app.models.rol import Rol
from app.models.ubicacion import Ubicacion
from app.models.usuario import Usuario


# Ingredientes expresados por porción y unidad del catálogo.
PARRILLA = [
    ("Parrillada de cortes para dos", "Selección de entraña, bife y chorizo a la parrilla con papa y ensalada.", "105.00", [("Entraña de res", "0.30", "kg"), ("Bife de chorizo", "0.30", "kg"), ("Chorizo parrillero", "0.20", "kg"), ("Papa", "0.35", "kg"), ("Tomate", "0.10", "kg"), ("Lechuga", "0.25", "unidad")]),
    ("Entraña a las brasas", "Entraña sellada a fuego fuerte, acompañada de yuca dorada y llajua.", "68.00", [("Entraña de res", "0.28", "kg"), ("Yuca", "0.25", "kg"), ("Tomate", "0.05", "kg"), ("Locoto", "0.01", "kg")]),
    ("Bife de chorizo con guarnición", "Bife a la parrilla con arroz graneado, ensalada fresca y papa.", "72.00", [("Bife de chorizo", "0.30", "kg"), ("Arroz grano largo", "0.12", "kg"), ("Papa", "0.20", "kg"), ("Tomate", "0.08", "kg"), ("Lechuga", "0.20", "unidad")]),
    ("Chorizo parrillero con yuca", "Chorizo a las brasas con yuca cocida y salsa criolla.", "39.00", [("Chorizo parrillero", "0.25", "kg"), ("Yuca", "0.25", "kg"), ("Tomate", "0.06", "kg"), ("Cebolla", "0.04", "kg")]),
    ("Costilla de res a la leña", "Costilla cocida lentamente y terminada a la leña, con papa rústica.", "76.00", [("Costilla de res", "0.38", "kg"), ("Papa", "0.30", "kg"), ("Ajo", "0.01", "kg"), ("Limón", "0.03", "kg")]),
    ("Pacumutu de res", "Brochetas de res a la parrilla con yuca, arroz y ensalada.", "48.00", [("Carne de res para guiso", "0.25", "kg"), ("Yuca", "0.18", "kg"), ("Arroz grano largo", "0.10", "kg"), ("Cebolla", "0.04", "kg"), ("Pimiento morrón", "0.05", "kg")]),
]

POLLO = [
    ("Pollo entero a la brasa", "Pollo marinado y asado a la brasa, con papa, ensalada y llajua.", "78.00", [("Pollo entero", "1.00", "unidad"), ("Papa", "0.45", "kg"), ("Lechuga", "0.50", "unidad"), ("Tomate", "0.15", "kg"), ("Locoto", "0.02", "kg")]),
    ("Pollo al espiedo con yuca", "Presa de pollo dorada lentamente en espiedo, servida con yuca y ensalada.", "38.00", [("Pechuga de pollo", "0.28", "kg"), ("Yuca", "0.25", "kg"), ("Lechuga", "0.20", "unidad"), ("Tomate", "0.08", "kg")]),
    ("Alitas crocantes de la casa", "Alitas marinadas y horneadas, con papas y salsa de mostaza.", "42.00", [("Alitas de pollo", "0.35", "kg"), ("Papa", "0.25", "kg"), ("Mostaza", "0.02", "kg"), ("Aceite vegetal", "0.03", "litro")]),
    ("Pollo broaster con arroz", "Pollo apanado y frito, acompañado de arroz, papa y ensalada.", "36.00", [("Pechuga de pollo", "0.28", "kg"), ("Pan rallado", "0.05", "kg"), ("Huevo", "0.08", "docena"), ("Arroz grano largo", "0.10", "kg"), ("Papa", "0.20", "kg")]),
    ("Milanesa de pollo", "Pechuga apanada y dorada, con puré de papa y ensalada fresca.", "34.00", [("Pechuga de pollo", "0.25", "kg"), ("Pan rallado", "0.05", "kg"), ("Huevo", "0.08", "docena"), ("Papa", "0.25", "kg"), ("Leche", "0.03", "litro")]),
    ("Sándwich de pollo a la plancha", "Pollo a la plancha en pan suave con tomate, lechuga y mayonesa.", "29.00", [("Pechuga de pollo", "0.18", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Tomate", "0.04", "kg"), ("Lechuga", "0.10", "unidad"), ("Mayonesa", "0.02", "kg")]),
]

HAMBURGUESAS = [
    ("Hamburguesa clásica", "Carne a la plancha, queso, tomate, lechuga y salsa de la casa.", "32.00", [("Carne molida de res", "0.16", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Queso mozzarella", "0.03", "kg"), ("Tomate", "0.04", "kg"), ("Lechuga", "0.10", "unidad"), ("Papa", "0.18", "kg")]),
    ("Hamburguesa con tocino", "Doble carne, tocino crocante, queso y cebolla a la plancha.", "43.00", [("Carne molida de res", "0.22", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Tocino", "0.05", "kg"), ("Queso mozzarella", "0.04", "kg"), ("Cebolla", "0.04", "kg"), ("Papa", "0.18", "kg")]),
    ("Hamburguesa de pollo crispy", "Pollo apanado crujiente con lechuga, tomate y mayonesa de limón.", "35.00", [("Pechuga de pollo", "0.18", "kg"), ("Pan rallado", "0.04", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Lechuga", "0.10", "unidad"), ("Tomate", "0.04", "kg"), ("Mayonesa", "0.02", "kg")]),
    ("Hamburguesa de champiñones", "Carne a la plancha con champiñones salteados y queso gratinado.", "39.00", [("Carne molida de res", "0.16", "kg"), ("Champiñón", "0.08", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Queso mozzarella", "0.04", "kg"), ("Papa", "0.18", "kg")]),
    ("Hamburguesa vegetariana de lentejas", "Medallón casero de lentejas con tomate, lechuga y salsa de mostaza.", "31.00", [("Lenteja", "0.12", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Huevo", "0.04", "docena"), ("Tomate", "0.04", "kg"), ("Lechuga", "0.10", "unidad"), ("Mostaza", "0.01", "kg")]),
    ("Papas con queso y tocino", "Papas doradas cubiertas con queso fundido y tocino crocante.", "28.00", [("Papa", "0.30", "kg"), ("Queso mozzarella", "0.06", "kg"), ("Tocino", "0.04", "kg"), ("Aceite vegetal", "0.03", "litro")]),
]

TIPICA = [
    ("Majadito de charque", "Arroz majado con charque, plátano frito y huevo; acompañado de llajua.", "38.00", [("Charque", "0.12", "kg"), ("Arroz grano largo", "0.14", "kg"), ("Plátano de cocinar", "0.15", "kg"), ("Huevo", "0.08", "docena"), ("Tomate", "0.05", "kg"), ("Locoto", "0.01", "kg")]),
    ("Majadito de pollo", "Arroz dorado con pollo desmenuzado, plátano y huevo frito.", "34.00", [("Pechuga de pollo", "0.18", "kg"), ("Arroz grano largo", "0.14", "kg"), ("Plátano de cocinar", "0.15", "kg"), ("Huevo", "0.08", "docena"), ("Cebolla", "0.04", "kg")]),
    ("Picante de pollo", "Pollo guisado en ají amarillo, con papa, chuño y arroz.", "39.00", [("Pechuga de pollo", "0.25", "kg"), ("Ají amarillo", "0.04", "kg"), ("Papa", "0.20", "kg"), ("Chuño", "0.08", "kg"), ("Arroz grano largo", "0.10", "kg"), ("Cebolla", "0.05", "kg")]),
    ("Picante de lengua", "Lengua de res en salsa de ají colorado, con papa y tunta.", "47.00", [("Lengua de res", "0.22", "kg"), ("Ají colorado", "0.04", "kg"), ("Papa", "0.20", "kg"), ("Tunta", "0.08", "kg"), ("Cebolla", "0.04", "kg")]),
    ("Sopa de maní", "Caldo de res con maní, papa, fideo y verduras, servido con perejil.", "29.00", [("Carne de res para guiso", "0.12", "kg"), ("Maní", "0.04", "kg"), ("Papa", "0.12", "kg"), ("Fideo", "0.04", "kg"), ("Zanahoria", "0.04", "kg"), ("Perejil", "0.10", "atado")]),
    ("Plato paceño", "Choclo, papa, haba y queso criollo con llajua de locoto.", "35.00", [("Choclo", "1", "unidad"), ("Papa", "0.25", "kg"), ("Queso criollo", "0.08", "kg"), ("Locoto", "0.01", "kg"), ("Haba", "0.08", "kg")]),
    ("Locro de gallina", "Caldo de gallina con arroz, yuca, plátano y verduras.", "32.00", [("Pollo entero", "0.30", "unidad"), ("Arroz grano largo", "0.08", "kg"), ("Yuca", "0.12", "kg"), ("Plátano de cocinar", "0.08", "kg"), ("Cebolla", "0.04", "kg"), ("Zanahoria", "0.04", "kg"), ("Ajo", "0.01", "kg")]),
]

RESTAURANTES = [
    ("Brasas del Urubó", "PARRILLA", "Santa Cruz de la Sierra", "Equipetrol", "restaurante@menuopt.com", PARRILLA),
    ("Fogón de la Ladera", "PARRILLA", "La Paz", "Sopocachi", "restaurante2@menuopt.com", PARRILLA),
    ("Brasas del Valle", "PARRILLA", "Cochabamba", "Cala Cala", "restaurante@menuopt.com", PARRILLA),
    ("Pollo al Punto", "POLLO", "Santa Cruz de la Sierra", "Plan 3000", "restaurante2@menuopt.com", POLLO),
    ("Brasa Andina", "POLLO", "La Paz", "Calacoto", "restaurante@menuopt.com", POLLO),
    ("Espiedo del Valle", "POLLO", "Cochabamba", "El Prado", "restaurante2@menuopt.com", POLLO),
    ("Burger del Anillo", "HAMBURGUESA", "Santa Cruz de la Sierra", "Centro", "restaurante@menuopt.com", HAMBURGUESAS),
    ("Pan y Plancha", "HAMBURGUESA", "La Paz", "Miraflores", "restaurante2@menuopt.com", HAMBURGUESAS),
    ("Hamburguesas del Prado", "HAMBURGUESA", "Cochabamba", "Recoleta", "restaurante@menuopt.com", HAMBURGUESAS),
    ("Sazón Camba", "TIPICA", "Santa Cruz de la Sierra", "Equipetrol", "restaurante2@menuopt.com", TIPICA),
    ("Mesa Andina", "TIPICA", "La Paz", "Sopocachi", "restaurante@menuopt.com", TIPICA),
    ("Fogón Cochala", "TIPICA", "Cochabamba", "Centro", "restaurante2@menuopt.com", TIPICA),
]

CATEGORIAS = {
    "PARRILLA": ("DEMO | Parrilla", "Cortes y preparaciones a las brasas."),
    "POLLO": ("DEMO | Pollo", "Pollo a la brasa, espiedo y otras preparaciones."),
    "HAMBURGUESA": ("DEMO | Hamburguesas", "Hamburguesas, sándwiches y acompañamientos."),
    "TIPICA": ("DEMO | Cocina boliviana", "Platos demostrativos inspirados en cocinas regionales de Bolivia."),
}

MESAS = [("01", 2, "REDONDA"), ("02", 4, "CUADRADA"), ("03", 4, "RECTANGULAR"), ("04", 6, "REDONDA"), ("05", 8, "RECTANGULAR")]


def _buscar_o_crear_categoria(db: Session, nombre: str, descripcion: str) -> Categoria:
    categoria = db.scalar(select(Categoria).where(Categoria.nombre == nombre))
    if categoria is None:
        categoria = Categoria(nombre=nombre, descripcion=descripcion, activo=True)
        db.add(categoria)
        db.flush()
    return categoria


def _asegurar_area_mesas(db: Session, restaurante: Restaurante) -> int:
    nombre_area = "DEMO | Salón principal"
    area = db.scalar(select(AreaRestaurante).where(
        AreaRestaurante.id_restaurante == restaurante.id_restaurante,
        AreaRestaurante.nombre == nombre_area,
    ))
    if area is None:
        area = AreaRestaurante(
            nombre=nombre_area,
            descripcion="Área demostrativa para pruebas de disponibilidad y reservas.",
            ancho_mapa=1200,
            alto_mapa=700,
            activo=True,
            orden=1,
            elementos=json.dumps([], ensure_ascii=False),
            id_restaurante=restaurante.id_restaurante,
        )
        db.add(area)
        db.flush()

    coords = [Decimal("0.16"), Decimal("0.33"), Decimal("0.50"), Decimal("0.67"), Decimal("0.84")]
    creadas = 0
    for (numero, capacidad, forma), x in zip(MESAS, coords):
        numero_demo = f"D{numero}"
        mesa = db.scalar(select(Mesa).where(Mesa.id_area == area.id_area, Mesa.numero == numero_demo))
        if mesa is None:
            mesa = Mesa(
                id_area=area.id_area,
                numero=numero_demo,
                nombre=f"Mesa demostrativa {numero}",
                capacidad=capacidad,
                forma=forma,
                posicion_x=x,
                posicion_y=Decimal("0.45"),
                rotacion=0,
                ancho=Decimal("0.08"),
                alto=Decimal("0.08"),
                es_fija=(numero == "05"),
                combinable=(numero != "05"),
                activo=True,
            )
            db.add(mesa)
            creadas += 1
    return creadas


def sembrar(db: Session) -> dict[str, int]:
    correos = sorted({r[4] for r in RESTAURANTES})
    usuarios = {
        usuario.correo: usuario
        for usuario in db.scalars(
            select(Usuario).join(Usuario.rol).where(
                Usuario.correo.in_(correos),
                Usuario.estado == "ACTIVO",
                Rol.nombre == "RESTAURANTE",
            )
        ).all()
    }
    faltantes = set(correos) - usuarios.keys()
    if faltantes:
        raise RuntimeError("Faltan cuentas de restaurante existentes: " + ", ".join(sorted(faltantes)))

    categorias = {tipo: _buscar_o_crear_categoria(db, *datos) for tipo, datos in CATEGORIAS.items()}
    ingredientes = {i.nombre: i for i in db.scalars(select(Ingrediente)).all()}
    necesarios = {
        ingrediente
        for _, _, _, _, _, menu in RESTAURANTES
        for plato in menu
        for ingrediente, _, _ in plato[3]
    }
    faltan_ingredientes = necesarios - ingredientes.keys()
    if faltan_ingredientes:
        raise RuntimeError("Ejecuta primero el seeder base; faltan: " + ", ".join(sorted(faltan_ingredientes)))

    restaurantes_creados = platos_creados = relaciones_creadas = mesas_creadas = 0
    preferencia_vegetariana = db.scalar(select(Preferencia).where(Preferencia.nombre == "Vegetariano"))
    if preferencia_vegetariana is None:
        preferencia_vegetariana = Preferencia(
            nombre="Vegetariano",
            tipo="DIETARIA",
            descripcion="No incluye carnes ni pescados; puede incluir lácteos y huevos.",
            activo=True,
        )
        db.add(preferencia_vegetariana)
        db.flush()
    for nombre, tipo, ciudad, zona, correo, menu in RESTAURANTES:
        nombre_demo = f"DEMO | {nombre}"
        restaurante = db.scalar(select(Restaurante).where(Restaurante.nombre == nombre_demo))
        if restaurante is None:
            ubicacion = Ubicacion(
                ciudad=ciudad,
                zona=zona,
                direccion="Ubicación demostrativa aproximada; no corresponde a un local real",
                referencia="Restaurante ficticio para datos de demostración",
            )
            db.add(ubicacion)
            db.flush()
            restaurante = Restaurante(
                nombre=nombre_demo,
                descripcion=f"Establecimiento ficticio de demostración especializado en {tipo.lower()}; carta de ejemplo, sin dirección comercial real.",
                nit=None,
                telefono=None,
                correo=None,
                horario_apertura=time(11, 0),
                horario_cierre=time(23, 0),
                estado="ACTIVO",
                id_usuario_responsable=usuarios[correo].id_usuario,
                id_ubicacion=ubicacion.id_ubicacion,
            )
            db.add(restaurante)
            db.flush()
            restaurantes_creados += 1

        for indice_plato, (nombre_plato, descripcion, precio, receta_ingredientes) in enumerate(menu):
            plato = db.scalar(select(Plato).where(
                Plato.id_restaurante == restaurante.id_restaurante,
                Plato.nombre == nombre_plato,
            ))
            if plato is None:
                plato = Plato(
                    nombre=nombre_plato,
                    descripcion=descripcion,
                    precio=Decimal(precio),
                    tipo_comida="ALMUERZO" if indice_plato < len(menu) // 2 else "CENA",
                    personas_cubiertas=2 if "para dos" in nombre_plato.lower() or "entero" in nombre_plato.lower() else 1,
                    disponible=True,
                    estado="ACTIVO",
                    id_restaurante=restaurante.id_restaurante,
                    id_categoria=categorias[tipo].id_categoria,
                )
                db.add(plato)
                db.flush()
                platos_creados += 1

            for nombre_ingrediente, cantidad, unidad in receta_ingredientes:
                ingrediente = ingredientes[nombre_ingrediente]
                relacion = db.scalar(select(PlatoIngrediente).where(
                    PlatoIngrediente.id_plato == plato.id_plato,
                    PlatoIngrediente.id_ingrediente == ingrediente.id_ingrediente,
                ))
                if relacion is None:
                    db.add(PlatoIngrediente(
                        id_plato=plato.id_plato,
                        id_ingrediente=ingrediente.id_ingrediente,
                        cantidad=Decimal(cantidad),
                        unidad_medida=unidad,
                    ))
                    relaciones_creadas += 1

            if "vegetariana" in nombre_plato.lower() or "plato paceño" in nombre_plato.lower():
                preferencia_plato = db.scalar(select(PlatoPreferencia).where(
                    PlatoPreferencia.id_plato == plato.id_plato,
                    PlatoPreferencia.id_preferencia == preferencia_vegetariana.id_preferencia,
                ))
                if preferencia_plato is None:
                    db.add(PlatoPreferencia(
                        id_plato=plato.id_plato,
                        id_preferencia=preferencia_vegetariana.id_preferencia,
                    ))

        mesas_creadas += _asegurar_area_mesas(db, restaurante)

    return {
        "restaurantes_nuevos": restaurantes_creados,
        "platos_nuevos": platos_creados,
        "recetas_de_plato_nuevas": relaciones_creadas,
        "mesas_nuevas": mesas_creadas,
    }


if __name__ == "__main__":
    ejecutar_comando("restaurantes, cartas y mesas demostrativas", sembrar)
