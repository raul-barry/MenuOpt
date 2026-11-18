"""Prepara datos locales de demostración para los flujos móviles de cliente.

Uso: python -m app.database.seed_clientes_demo

El seeder es aditivo e idempotente: conserva registros existentes y solo trabaja
contra bases locales de desarrollo MenuOpt.
"""
from __future__ import annotations

import unicodedata
from decimal import Decimal

from sqlalchemy import select

from app.database.conexion import SessionLocal, engine
from app.models import (
    Ingrediente,
    IngredienteLugarCompra,
    LugarCompra,
    Planificacion,
    PlanificacionPreferencia,
    Plato,
    PlatoIngrediente,
    PlatoPreferencia,
    Preferencia,
    RecetaIngrediente,
    Usuario,
)
from app.services.recomendacion_service import RecomendacionService


INGREDIENTES_RECETA = {
    "aceite vegetal": "Aceite Vegetal Fino",
    "arroz grano de oro": "Arroz Grano de Oro Seleccionado",
    "carne de res": "Carne de Res - Pulpa Primera",
    "carne molida": "Carne Molida Especial",
    "cebolla roja": "Cebolla Roja Seleccionada",
    "fideos espagueti": "Fideos Espagueti Trigo de Oro",
    "harina de trigo": "Harina de Trigo Especial 000",
    "huevos": "Huevos de Granja Seleccionados",
    "leche entera": "Leche Entera Natural Pil",
    "papa holandesa": "Papa Holandesa Seleccionada",
    "pechuga de pollo": "Pechuga de Pollo Fresca",
    "pimiento morrón": "Pimiento Morrón Rojo",
    "queso chaqueño": "Queso Chaqueño Criollo",
    "tomate manzano": "Tomate Manzano Criollo",
    "zanahoria": "Zanahoria Criolla Fresca",
}

# Cantidades por persona. Los nombres se resuelven en la BD, nunca por ID fijo.
RECETAS_PLATO = {
    "Majadito de Charque Típico": [
        ("Carne de Res - Pulpa Primera", "0.15", "kg"),
        ("Arroz Grano de Oro Seleccionado", "0.12", "kg"),
        ("Huevos de Granja Seleccionados", "0.20", "docena"),
        ("Tomate Manzano Criollo", "0.06", "kg"),
        ("Cebolla Roja Seleccionada", "0.04", "kg"),
        ("Aceite Vegetal Fino", "0.02", "litro"),
    ],
    "Silpancho Tradicional Vallegrandino": [
        ("Carne de Res - Pulpa Primera", "0.18", "kg"),
        ("Arroz Grano de Oro Seleccionado", "0.12", "kg"),
        ("Papa Holandesa Seleccionada", "0.15", "kg"),
        ("Huevos de Granja Seleccionados", "0.20", "docena"),
        ("Tomate Manzano Criollo", "0.05", "kg"),
        ("Cebolla Roja Seleccionada", "0.04", "kg"),
    ],
    "Lasagna a la Boloñesa Gratinada": [
        ("Carne Molida Especial", "0.12", "kg"),
        ("Fideos Espagueti Trigo de Oro", "0.15", "kg"),
        ("Tomate Manzano Criollo", "0.10", "kg"),
        ("Queso Chaqueño Criollo", "0.06", "kg"),
        ("Cebolla Roja Seleccionada", "0.04", "kg"),
    ],
    "Pizza Michelangelo Familiar": [
        ("Harina de Trigo Especial 000", "0.20", "kg"),
        ("Queso Chaqueño Criollo", "0.10", "kg"),
        ("Tomate Manzano Criollo", "0.10", "kg"),
        ("Aceite Vegetal Fino", "0.02", "litro"),
    ],
    "Hamburguesa Clásica Simple": [
        ("Carne Molida Especial", "0.15", "kg"),
        ("Queso Chaqueño Criollo", "0.04", "kg"),
        ("Tomate Manzano Criollo", "0.04", "kg"),
        ("Cebolla Roja Seleccionada", "0.03", "kg"),
    ],
    "Bowl Fit Proteico de Quinoa y Pollo": [
        ("Quinoa Real", "0.12", "kg"),
        ("Pechuga de Pollo Fresca", "0.12", "kg"),
        ("Tomate Manzano Criollo", "0.05", "kg"),
        ("Zanahoria Criolla Fresca", "0.04", "kg"),
        ("Aceite Vegetal Fino", "0.01", "litro"),
    ],
    "Almuerzo Vegetariano Saludable del Día": [
        ("Quinoa Real", "0.14", "kg"),
        ("Zanahoria Criolla Fresca", "0.06", "kg"),
        ("Pimiento Morrón Rojo", "0.04", "kg"),
        ("Tomate Manzano Criollo", "0.05", "kg"),
        ("Cebolla Roja Seleccionada", "0.03", "kg"),
        ("Aceite Vegetal Fino", "0.01", "litro"),
    ],
}

PLANES_DEMO = [
    {
        "ubicacion": "DEMO APK | Equipetrol, Santa Cruz",
        "tipo_comida": "ALMUERZO",
        "presupuesto": Decimal("180.00"),
        "personas": 2,
        "preferencia": None,
    },
    {
        "ubicacion": "DEMO APK | Centro, Santa Cruz",
        "tipo_comida": "CENA",
        "presupuesto": Decimal("180.00"),
        "personas": 2,
        "preferencia": None,
    },
    {
        "ubicacion": "DEMO APK | Centro vegetariano, Santa Cruz",
        "tipo_comida": "ALMUERZO",
        "presupuesto": Decimal("120.00"),
        "personas": 2,
        "preferencia": "Vegetariano",
    },
]


def _normalizar(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in descompuesto if not unicodedata.combining(c)).strip()


def _validar_base_local() -> None:
    host = (engine.url.host or "").lower()
    database = (engine.url.database or "").lower()
    if host not in {"postgres", "localhost", "127.0.0.1", "::1", "host.docker.internal"}:
        raise RuntimeError("Seeder cancelado: la base no parece local.")
    if database not in {"menuopt", "menuopt_db", "menuopt_dev", "menuopt_development"}:
        raise RuntimeError("Seeder cancelado: solo se permite una base local MenuOpt de desarrollo.")


def _asegurar_quinoa(db) -> Ingrediente:
    quinoa = db.query(Ingrediente).filter(Ingrediente.nombre == "Quinoa Real").one_or_none()
    if quinoa is None:
        quinoa = Ingrediente(
            nombre="Quinoa Real",
            unidad_medida="kg",
            precio_estimado=Decimal("25.00"),
            descripcion="Quinua real boliviana, lavada y lista para cocinar.",
            estado="ACTIVO",
        )
        db.add(quinoa)
        db.flush()

    mercados = {
        "Mercado Abasto Mayorista": Decimal("22.00"),
        "Supermercado Fidalga Equipetrol": Decimal("27.50"),
    }
    for nombre_tienda, precio in mercados.items():
        tienda = db.query(LugarCompra).filter(LugarCompra.nombre == nombre_tienda).one_or_none()
        if tienda is None:
            continue
        relacion = db.query(IngredienteLugarCompra).filter_by(
            id_ingrediente=quinoa.id_ingrediente,
            id_lugar_compra=tienda.id_lugar_compra,
        ).one_or_none()
        if relacion is None:
            db.add(IngredienteLugarCompra(
                id_ingrediente=quinoa.id_ingrediente,
                id_lugar_compra=tienda.id_lugar_compra,
                precio=precio,
                cantidad_referencia=Decimal("1.00"),
                unidad_medida="kg",
                disponible=True,
            ))
    return quinoa


def _vincular_ingredientes_biblioteca(db) -> int:
    ingredientes = {i.nombre: i for i in db.query(Ingrediente).all()}
    mapa_alias = {
        _normalizar(alias): ingredientes[nombre]
        for alias, nombre in INGREDIENTES_RECETA.items()
        if nombre in ingredientes
    }
    total = 0
    for item in db.query(RecetaIngrediente).filter(RecetaIngrediente.id_ingrediente.is_(None)).all():
        ingrediente = mapa_alias.get(_normalizar(item.nombre_ingrediente))
        if ingrediente is not None:
            item.id_ingrediente = ingrediente.id_ingrediente
            total += 1
    return total


def _vincular_recetas_de_platos(db) -> int:
    total = 0
    vegetarianismo = db.query(Preferencia).filter(Preferencia.nombre == "Vegetariano").one_or_none()
    veganismo = db.query(Preferencia).filter(Preferencia.nombre == "Vegano").one_or_none()

    for nombre_plato, receta in RECETAS_PLATO.items():
        plato = db.query(Plato).filter(Plato.nombre == nombre_plato).one_or_none()
        if plato is None:
            continue
        for nombre_ingrediente, cantidad, unidad in receta:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.nombre == nombre_ingrediente).one_or_none()
            if ingrediente is None:
                continue
            existente = db.query(PlatoIngrediente).filter_by(
                id_plato=plato.id_plato,
                id_ingrediente=ingrediente.id_ingrediente,
            ).one_or_none()
            if existente is None:
                db.add(PlatoIngrediente(
                    id_plato=plato.id_plato,
                    id_ingrediente=ingrediente.id_ingrediente,
                    cantidad=Decimal(cantidad),
                    unidad_medida=unidad,
                ))
                total += 1

        if nombre_plato in {
            "Almuerzo Vegetariano Saludable del Día",
            "Lasaña Vegana de Berenjenas y Champiñones",
        } and vegetarianismo is not None:
            vinculo = db.query(PlatoPreferencia).filter_by(
                id_plato=plato.id_plato,
                id_preferencia=vegetarianismo.id_preferencia,
            ).one_or_none()
            if vinculo is None:
                db.add(PlatoPreferencia(id_plato=plato.id_plato, id_preferencia=vegetarianismo.id_preferencia))

        if nombre_plato == "Lasaña Vegana de Berenjenas y Champiñones" and veganismo is not None:
            vinculo = db.query(PlatoPreferencia).filter_by(
                id_plato=plato.id_plato,
                id_preferencia=veganismo.id_preferencia,
            ).one_or_none()
            if vinculo is None:
                db.add(PlatoPreferencia(id_plato=plato.id_plato, id_preferencia=veganismo.id_preferencia))
    return total


def _asegurar_planes(db, cliente: Usuario) -> list[Planificacion]:
    vegetarianismo = db.query(Preferencia).filter(Preferencia.nombre == "Vegetariano").one_or_none()
    if vegetarianismo is None:
        vegetarianismo = Preferencia(
            nombre="Vegetariano",
            tipo="DIETARIA",
            descripcion="Excluye carne animal.",
            activo=True,
        )
        db.add(vegetarianismo)
        db.flush()

    resultado = []
    for datos in PLANES_DEMO:
        plan = db.query(Planificacion).filter_by(
            id_usuario=cliente.id_usuario,
            ubicacion_referencia=datos["ubicacion"],
            tipo_comida=datos["tipo_comida"],
        ).one_or_none()
        if plan is None:
            plan = Planificacion(
                presupuesto=datos["presupuesto"],
                cantidad_personas=datos["personas"],
                tipo_comida=datos["tipo_comida"],
                ubicacion_referencia=datos["ubicacion"],
                estado="ACTIVA",
                id_usuario=cliente.id_usuario,
            )
            db.add(plan)
            db.flush()

        nombre_preferencia = datos["preferencia"]
        if nombre_preferencia:
            preferencia = db.query(Preferencia).filter(Preferencia.nombre == nombre_preferencia).one_or_none()
            if preferencia is not None:
                vinculo = db.query(PlanificacionPreferencia).filter_by(
                    id_planificacion=plan.id_planificacion,
                    id_preferencia=preferencia.id_preferencia,
                ).one_or_none()
                if vinculo is None:
                    db.add(PlanificacionPreferencia(
                        id_planificacion=plan.id_planificacion,
                        id_preferencia=preferencia.id_preferencia,
                    ))
        resultado.append(plan)
    db.commit()
    return resultado


def ejecutar_seeder() -> dict[str, int]:
    _validar_base_local()

    # Reutiliza los catálogos ya existentes; ambos seeders agregan por nombre y
    # no limpian registros del usuario.
    from app.database.seed_tiendas_productos import ejecutar_seeder as sembrar_tiendas
    from app.database.seed_restaurantes_categorias_platos import ejecutar_seeder as sembrar_restaurantes

    sembrar_tiendas()
    sembrar_restaurantes()

    db = SessionLocal()
    try:
        cliente = db.query(Usuario).filter(Usuario.correo == "cliente1@menuopt.com").one_or_none()
        if cliente is None:
            raise RuntimeError(
                "No existe cliente1@menuopt.com. Ejecuta primero `python -m app.database.crear_admin`."
            )

        _asegurar_quinoa(db)
        recetas_biblioteca = _vincular_ingredientes_biblioteca(db)
        recetas_platos = _vincular_recetas_de_platos(db)
        planes = _asegurar_planes(db, cliente)

        # Los resultados los calcula el mismo motor que usa la API. Si ya hay
        # recomendaciones, se conservan para no pisar pruebas del usuario.
        db.expire_all()
        recomendaciones_nuevas = 0
        for plan in planes:
            db.refresh(plan)
            if not plan.recomendaciones:
                nuevas = RecomendacionService.generar_recomendaciones(
                    db=db,
                    id_planificacion=plan.id_planificacion,
                    usuario_actual=cliente,
                )
                recomendaciones_nuevas += len(nuevas)

        db.commit()
        return {
            "planes_demo": len(planes),
            "ingredientes_biblioteca_vinculados": recetas_biblioteca,
            "recetas_de_platos_vinculadas": recetas_platos,
            "recomendaciones_generadas": recomendaciones_nuevas,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Preparando datos de prueba para cliente1@menuopt.com...")
    print(ejecutar_seeder())
