"""Carga demostrativa de tiendas, ingredientes y precios de referencia.

No crea ni modifica usuarios. Las tiendas son establecimientos ficticios en
zonas reales; no incluyen teléfonos ni direcciones de negocios existentes.

Por defecto solo muestra el resumen y revierte la transacción. Para aplicar:
    python -m app.database.seed_datos_base_demo --apply

En producción requiere además --allow-production.
"""
from __future__ import annotations

import argparse
import os
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.database.conexion import SessionLocal
from app.config.settings import settings
from app.models.ingrediente import Ingrediente
from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
from app.models.lugar_compra import LugarCompra
from app.models.ubicacion import Ubicacion
from app.models.usuario import Usuario


TIENDAS = [
    ("DEMO | Mercado La Ramada", "MERCADO", "Santa Cruz de la Sierra", "La Ramada"),
    ("DEMO | Mercado del Abasto", "MERCADO", "Santa Cruz de la Sierra", "El Abasto"),
    ("DEMO | Despensa Equipetrol", "SUPERMERCADO", "Santa Cruz de la Sierra", "Equipetrol"),
    ("DEMO | Abarrotes del Centro", "SUPERMERCADO", "Santa Cruz de la Sierra", "Centro"),
    ("DEMO | Mercado del Plan", "MERCADO", "Santa Cruz de la Sierra", "Plan 3000"),
    ("DEMO | Mercado Rodríguez", "MERCADO", "La Paz", "Max Paredes"),
    ("DEMO | Mercado de Sopocachi", "MERCADO", "La Paz", "Sopocachi"),
    ("DEMO | Despensa Calacoto", "SUPERMERCADO", "La Paz", "Calacoto"),
    ("DEMO | Abarrotes de Miraflores", "SUPERMERCADO", "La Paz", "Miraflores"),
    ("DEMO | Mercado de Villa Fátima", "MERCADO", "La Paz", "Villa Fátima"),
    ("DEMO | Mercado La Cancha", "MERCADO", "Cochabamba", "La Cancha"),
    ("DEMO | Mercado Cala Cala", "MERCADO", "Cochabamba", "Cala Cala"),
    ("DEMO | Despensa de la Recoleta", "SUPERMERCADO", "Cochabamba", "Recoleta"),
    ("DEMO | Abarrotes del Prado", "SUPERMERCADO", "Cochabamba", "El Prado"),
    ("DEMO | Mercado de Quillacollo", "MERCADO", "Cochabamba", "Quillacollo"),
]

# Nombre, unidad, precio de referencia en Bs, descripción. Se resuelven por
# nombre para que otros seeders puedan enlazarlos sin depender de IDs.
PRODUCTOS = [
    ("Arroz grano largo", "kg", "11.00", "Arroz para guarniciones, majadito y platos salteados."),
    ("Carne de res para guiso", "kg", "52.00", "Corte de res para guisos, sopas y preparaciones largas."),
    ("Carne molida de res", "kg", "43.00", "Carne molida para hamburguesas, albóndigas y salsas."),
    ("Carne de cerdo", "kg", "39.00", "Carne de cerdo para chicharrón y preparaciones al horno."),
    ("Pechuga de pollo", "kg", "29.00", "Pechuga fresca para platos a la plancha, guisos y rellenos."),
    ("Charque", "kg", "78.00", "Carne deshidratada y salada para recetas tradicionales."),
    ("Pescado de río", "kg", "48.00", "Pescado de río para preparaciones al horno o fritas."),
    ("Papa", "kg", "7.00", "Papa para hervir, freír, hornear y acompañar platos."),
    ("Chuño", "kg", "24.00", "Papa deshidratada andina para guisos y platos tradicionales."),
    ("Yuca", "kg", "8.00", "Raíz fresca para hervir, freír o acompañar platos orientales."),
    ("Plátano de cocinar", "kg", "9.00", "Plátano para freír y acompañar platos tradicionales."),
    ("Quinua", "kg", "28.00", "Quinua lavada para sopas, guarniciones y platos vegetarianos."),
    ("Fideo", "kg", "12.00", "Pasta seca para sopas y platos de fondo."),
    ("Harina de trigo", "kg", "9.00", "Harina para masas, panes y preparaciones de cocina."),
    ("Huevo", "docena", "16.00", "Huevos frescos para platos, masas y repostería."),
    ("Queso criollo", "kg", "38.00", "Queso de sabor suave para rellenos, horneados y guarniciones."),
    ("Queso mozzarella", "kg", "55.00", "Queso mozzarella para pizza y preparaciones gratinadas."),
    ("Leche", "litro", "7.00", "Leche entera para salsas, masas y bebidas."),
    ("Maní", "kg", "27.00", "Maní para salsas y sopas tradicionales."),
    ("Tomate", "kg", "6.00", "Tomate fresco para ensaladas, salsas y guisos."),
    ("Cebolla", "kg", "7.00", "Cebolla para sofritos, salsas y guarniciones."),
    ("Zanahoria", "kg", "6.00", "Zanahoria fresca para sopas, guisos y ensaladas."),
    ("Locoto", "kg", "22.00", "Locoto para llajua y salsas picantes."),
    ("Ají amarillo", "kg", "34.00", "Ají amarillo para salsas y platos de cocina boliviana."),
    ("Ají colorado", "kg", "30.00", "Ají colorado para guisos y preparaciones tradicionales."),
    ("Ajo", "kg", "28.00", "Ajo fresco para aderezos, salsas y guisos."),
    ("Aceite vegetal", "litro", "16.00", "Aceite vegetal para cocina y frituras."),
    ("Azúcar", "kg", "8.00", "Azúcar para bebidas, masas y postres."),
    ("Limón", "kg", "12.00", "Limón para aderezos, bebidas y marinados."),
    ("Lechuga", "unidad", "6.00", "Lechuga fresca para ensaladas y sándwiches."),
    ("Poroto", "kg", "18.00", "Poroto seco para sopas y guisos."),
    ("Orégano seco", "kg", "65.00", "Hierba aromática para salsas, pizzas y guisos."),
    ("Tallarín para lasaña", "kg", "18.00", "Pasta seca en láminas para lasaña al horno."),
    ("Pan de hamburguesa", "unidad", "2.50", "Pan suave para hamburguesas y sándwiches."),
    ("Pan rallado", "kg", "18.00", "Pan seco molido para apanados y milanesas."),
    ("Chorizo parrillero", "kg", "42.00", "Chorizo fresco para parrilla y platos al sartén."),
    ("Salchicha", "kg", "32.00", "Salchicha cocida para pique macho y platos rápidos."),
    ("Tocino", "kg", "58.00", "Tocino para hamburguesas, desayunos y salsas."),
    ("Mantequilla", "kg", "48.00", "Mantequilla para masas, salsas y preparaciones al horno."),
    ("Crema de leche", "litro", "28.00", "Crema para salsas, pastas y postres."),
    ("Pimiento morrón", "kg", "12.00", "Pimiento fresco para salteados, rellenos y guisos."),
    ("Choclo", "unidad", "4.00", "Choclo fresco para guarniciones y platos tradicionales."),
    ("Arveja", "kg", "14.00", "Arveja fresca para sopas, guisos y rellenos."),
    ("Palta", "kg", "26.00", "Palta madura para ensaladas, salsas y sándwiches."),
    ("Pepino", "kg", "7.00", "Pepino fresco para ensaladas y acompañamientos."),
    ("Cilantro", "atado", "3.50", "Hierba fresca para salsas, sopas y platos regionales."),
    ("Perejil", "atado", "3.00", "Hierba fresca para aderezos y guarniciones."),
    ("Lenteja", "kg", "16.00", "Lenteja seca para sopas y platos vegetarianos."),
    ("Frijol negro", "kg", "19.00", "Frijol seco para guarniciones, tacos y platos de olla."),
    ("Mayonesa", "kg", "26.00", "Mayonesa para sándwiches, hamburguesas y aderezos."),
    ("Mostaza", "kg", "24.00", "Mostaza para aderezos, sándwiches y marinados."),
    ("Salsa de tomate", "kg", "22.00", "Salsa de tomate para pizzas y preparaciones rápidas."),
    ("Vinagre", "litro", "12.00", "Vinagre para encurtidos, marinados y aderezos."),
    ("Sal", "kg", "4.00", "Sal de cocina para sazonar preparaciones."),
    ("Comino", "kg", "52.00", "Comino molido para guisos y adobos."),
    ("Canela", "kg", "68.00", "Canela para bebidas calientes, masas y postres."),
    ("Cacao en polvo", "kg", "75.00", "Cacao para bebidas, tortas y postres."),
    ("Gelatina sin sabor", "kg", "90.00", "Gelatina neutra para postres y preparaciones frías."),
    ("Manzana", "kg", "14.00", "Manzana fresca para postres, jugos y meriendas."),
    ("Banana", "kg", "10.00", "Banana fresca para licuados, postres y desayunos."),
    ("Naranja", "kg", "9.00", "Naranja fresca para jugos, postres y marinados."),
    ("Miel", "kg", "42.00", "Miel para bebidas, desayunos y preparaciones dulces."),
    ("Café molido", "kg", "92.00", "Café tostado y molido para bebidas calientes."),
    ("Avena", "kg", "14.00", "Avena en hojuelas para desayunos, masas y bebidas."),
    ("Maíz mote", "kg", "17.00", "Maíz seco para mote, sopas y guarniciones."),
    ("Tunta", "kg", "26.00", "Papa deshidratada blanca para platos andinos."),
    ("Queso parmesano", "kg", "92.00", "Queso curado rallado para pastas y platos gratinados."),
    ("Albahaca", "atado", "5.00", "Hierba fresca para pesto, salsas y pizzas."),
    ("Champiñón", "kg", "38.00", "Champiñón fresco para pizzas, pastas y salteados."),
    ("Berenjena", "kg", "13.00", "Berenjena fresca para lasañas, guisos y platos vegetarianos."),
    ("Tofu", "kg", "38.00", "Tofu firme para salteados y preparaciones vegetarianas."),
    ("Entraña de res", "kg", "86.00", "Corte de res para asar rápidamente a la parrilla."),
    ("Bife de chorizo", "kg", "78.00", "Corte grueso de res para parrilla y cocción a las brasas."),
    ("Costilla de res", "kg", "49.00", "Costilla de res para cocción lenta, horno y parrilla."),
    ("Pollo entero", "unidad", "48.00", "Pollo entero fresco para brasa, horno o espiedo."),
    ("Alitas de pollo", "kg", "32.00", "Alitas frescas para hornear, asar o freír."),
    ("Lengua de res", "kg", "58.00", "Lengua de res para cocción lenta y platos tradicionales."),
    ("Haba", "kg", "15.00", "Haba fresca para sopas, guisos y platos andinos."),
    ("Pepperoni", "kg", "62.00", "Embutido curado en rodajas para pizzas y sándwiches."),
    ("Tortilla de trigo", "unidad", "3.00", "Tortilla de trigo para tacos, burritos y quesadillas."),
    ("Salsa de soya", "litro", "24.00", "Salsa de soya para salteados, arroz y marinados."),
]

# Diferencias moderadas de referencia para mostrar comparación por ciudad y tipo.
FACTORES = {
    "MERCADO": Decimal("0.92"),
    "SUPERMERCADO": Decimal("1.12"),
}

FACTOR_CIUDAD = {
    "Santa Cruz de la Sierra": Decimal("1.00"),
    "La Paz": Decimal("1.04"),
    "Cochabamba": Decimal("0.98"),
}


def _obtener_o_crear_tienda(db: Session, datos: tuple[str, str, str, str], id_usuario: int) -> LugarCompra:
    nombre, tipo, ciudad, zona = datos
    tienda = db.scalar(select(LugarCompra).where(LugarCompra.nombre == nombre))
    if tienda:
        return tienda

    ubicacion = Ubicacion(
        ciudad=ciudad,
        zona=zona,
        direccion="Ubicación demostrativa aproximada; no corresponde a un local real",
        referencia="Registro de datos de demostración",
    )
    db.add(ubicacion)
    db.flush()
    tienda = LugarCompra(
        nombre=nombre,
        tipo=tipo,
        telefono=None,
        estado="ACTIVO",
        id_ubicacion=ubicacion.id_ubicacion,
        id_usuario_responsable=id_usuario,
    )
    db.add(tienda)
    db.flush()
    return tienda


def ejecutar_seeder(aplicar: bool = False, permitir_produccion: bool = False) -> None:
    ambiente = (os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development").lower()
    host_db = (make_url(settings.sqlalchemy_database_url).host or "").lower()
    entorno_remoto = host_db not in {"", "localhost", "127.0.0.1", "postgres", "db"}
    if aplicar and (ambiente in {"production", "prod"} or entorno_remoto) and not permitir_produccion:
        raise SystemExit("Protección: para escribir en una base de producción/remota agrega --allow-production.")

    db = SessionLocal()
    try:
        responsable = db.scalar(select(Usuario).where(Usuario.correo == "tienda@menuopt.com"))
        if responsable is None:
            raise RuntimeError(
                "No existe tienda@menuopt.com. El seeder no crea usuarios ni usa IDs de respaldo."
            )

        tiendas = {
            datos[0]: _obtener_o_crear_tienda(db, datos, responsable.id_usuario)
            for datos in TIENDAS
        }
        productos: dict[str, Ingrediente] = {}
        for nombre, unidad, precio, descripcion in PRODUCTOS:
            ingrediente = db.scalar(select(Ingrediente).where(Ingrediente.nombre == nombre))
            if ingrediente is None:
                ingrediente = Ingrediente(
                    nombre=nombre,
                    unidad_medida=unidad,
                    precio_estimado=Decimal(precio),
                    descripcion=descripcion,
                    estado="ACTIVO",
                )
                db.add(ingrediente)
                db.flush()
            productos[nombre] = ingrediente

        relaciones_nuevas = 0
        for nombre, unidad, precio_base, _ in PRODUCTOS:
            ingrediente = productos[nombre]
            for tienda_nombre, tienda in tiendas.items():
                factor = FACTORES[tienda.tipo] * FACTOR_CIUDAD[tienda.ubicacion.ciudad]
                # Variación estable por producto/tienda, evitando aleatoriedad
                # para que una reejecución mantenga los mismos precios.
                variacion = Decimal(1) + Decimal((len(nombre) + len(tienda_nombre)) % 5 - 2) / Decimal(100)
                precio = (Decimal(precio_base) * factor * variacion).quantize(Decimal("0.01"))
                relacion = db.scalar(
                    select(IngredienteLugarCompra).where(
                        IngredienteLugarCompra.id_ingrediente == ingrediente.id_ingrediente,
                        IngredienteLugarCompra.id_lugar_compra == tienda.id_lugar_compra,
                    )
                )
                if relacion is None:
                    db.add(
                        IngredienteLugarCompra(
                            id_ingrediente=ingrediente.id_ingrediente,
                            id_lugar_compra=tienda.id_lugar_compra,
                            precio=precio,
                            cantidad_referencia=Decimal("1.00"),
                            unidad_medida=unidad,
                            disponible=True,
                        )
                    )
                    relaciones_nuevas += 1

        db.flush()
        resumen = (
            f"Tiendas previstas: {len(TIENDAS)}; ingredientes de catálogo: {len(PRODUCTOS)}; "
            f"relaciones tienda-producto nuevas: {relaciones_nuevas}."
        )
        if aplicar:
            db.commit()
            print("APLICADO. " + resumen)
        else:
            db.rollback()
            print("VISTA PREVIA (sin cambios). " + resumen)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carga segura de datos base demostrativos MenuOpt")
    parser.add_argument("--apply", action="store_true", help="confirmar los cambios en la base configurada")
    parser.add_argument("--allow-production", action="store_true", help="permitir escritura si la base es remota o el entorno es production")
    args = parser.parse_args()
    ejecutar_seeder(aplicar=args.apply, permitir_produccion=args.allow_production)
