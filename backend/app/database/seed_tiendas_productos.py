# CASO DE USO: CU09, CU15, CU16 - Seeders de Tiendas y Productos
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.models.ubicacion import Ubicacion
from app.models.lugar_compra import LugarCompra
from app.models.ingrediente import Ingrediente
from app.models.ingrediente_lugar_compra import IngredienteLugarCompra


def ejecutar_seeder():
    db: Session = next(get_db())

    # 1. Obtener usuario responsable para tiendas (tienda@menuopt.com o admin)
    usuario_tienda = db.query(Usuario).filter(Usuario.correo == "tienda@menuopt.com").first()
    if not usuario_tienda:
        usuario_tienda = db.query(Usuario).filter(Usuario.correo == "admin@menuopt.com").first()

    id_usuario = usuario_tienda.id_usuario if usuario_tienda else 1

    # 2. Tiendas (Lugares de Compra) con Ubicaciones específicas
    tiendas_data = [
        {
            "nombre": "Supermercado Fidalga Equipetrol",
            "tipo": "SUPERMERCADO",
            "telefono": "33451200",
            "ciudad": "Santa Cruz",
            "zona": "Equipetrol",
            "direccion": "Av. San Martín entre 2do y 3er Anillo",
            "referencia": "Frente al Centro Empresarial"
        },
        {
            "nombre": "Mercado Los Pozos - Sector Abarrotes",
            "tipo": "MERCADO",
            "telefono": "78123456",
            "ciudad": "Santa Cruz",
            "zona": "Centro",
            "direccion": "Calle 6 de Agosto esq. Suárez Arana",
            "referencia": "Sector de canastas y verduras"
        },
        {
            "nombre": "Hipermaxi Norte Banzer",
            "tipo": "SUPERMERCADO",
            "telefono": "33418899",
            "ciudad": "Santa Cruz",
            "zona": "Norte",
            "direccion": "Av. Cristo Redentor entre 3er y 4to Anillo",
            "referencia": "Pasando el 3er anillo externo"
        },
        {
            "nombre": "Mercado Abasto Mayorista",
            "tipo": "MERCADO",
            "telefono": "76543210",
            "ciudad": "Santa Cruz",
            "zona": "Suroeste",
            "direccion": "Av. Piraí y 3er Anillo Interno",
            "referencia": "Pabellón de carnes y tubérculos"
        },
        {
            "nombre": "Tienda y Abarrotes Doña María",
            "tipo": "TIENDA",
            "telefono": "72112233",
            "ciudad": "Santa Cruz",
            "zona": "Urbarí",
            "direccion": "Calle Los Pinos #120",
            "referencia": "A dos cuadras de la plaza principal"
        },
        {
            "nombre": "Distribuidora Avícola Sofía Central",
            "tipo": "DISTRIBUIDORA",
            "telefono": "33465544",
            "ciudad": "Santa Cruz",
            "zona": "Parque Industrial",
            "direccion": "Av. Mutualista y 4to Anillo",
            "referencia": "Planta de distribución comercial"
        },
        {
            "nombre": "Frutería y Verdulería El Edén",
            "tipo": "VERDULERIA",
            "telefono": "73399887",
            "ciudad": "Santa Cruz",
            "zona": "Equipetrol",
            "direccion": "Calle Güemes esq. Enrique Finot",
            "referencia": "Junto al Café de la Esquina"
        },
        {
            "nombre": "Carnicería y Frial San Carlos",
            "tipo": "FRIAL",
            "telefono": "33324567",
            "ciudad": "Santa Cruz",
            "zona": "Centro",
            "direccion": "Calle Arenales #340",
            "referencia": "Cerca del Parque El Arenal"
        }
    ]

    tiendas_creadas = {}
    for td in tiendas_data:
        tienda = db.query(LugarCompra).filter(LugarCompra.nombre == td["nombre"]).first()
        if not tienda:
            # Crear ubicación asociada
            ubicacion = Ubicacion(
                ciudad=td["ciudad"],
                zona=td["zona"],
                direccion=td["direccion"],
                referencia=td["referencia"]
            )
            db.add(ubicacion)
            db.flush()

            tienda = LugarCompra(
                nombre=td["nombre"],
                tipo=td["tipo"],
                telefono=td["telefono"],
                estado="ACTIVO",
                id_ubicacion=ubicacion.id_ubicacion,
                id_usuario_responsable=id_usuario
            )
            db.add(tienda)
            db.flush()
            print(f"[OK] Creada tienda: {tienda.nombre} ({tienda.tipo} en {td['zona']})")
        else:
            print(f"[INFO] Tienda ya existe: {tienda.nombre}")
        tiendas_creadas[td["nombre"]] = tienda

    # 3. Ingredientes / Productos a sembrar
    productos_data = [
        {
            "nombre": "Pechuga de Pollo Fresca",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("28.00"),
            "descripcion": "Pechuga de pollo limpia sin piel, fresca de primera calidad"
        },
        {
            "nombre": "Carne de Res - Pulpa Primera",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("46.00"),
            "descripcion": "Corte magro de primera calidad para bistec, asados y milanesas"
        },
        {
            "nombre": "Carne Molida Especial",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("38.00"),
            "descripcion": "Carne molida magra fresca ideal para hamburguesas y albóndigas"
        },
        {
            "nombre": "Arroz Grano de Oro Seleccionado",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("12.00"),
            "descripcion": "Arroz blanco de grano largo graneado fino"
        },
        {
            "nombre": "Fideos Espagueti Trigo de Oro",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("9.50"),
            "descripcion": "Pasta larga de sémola de trigo duro fortificada"
        },
        {
            "nombre": "Huevos de Granja Seleccionados",
            "unidad_medida": "docena",
            "precio_estimado": Decimal("13.00"),
            "descripcion": "Huevos frescos de granja clase A en envase protector"
        },
        {
            "nombre": "Aceite Vegetal Fino",
            "unidad_medida": "litro",
            "precio_estimado": Decimal("14.50"),
            "descripcion": "Aceite vegetal comestible refinado 100% puro de soya"
        },
        {
            "nombre": "Tomate Manzano Criollo",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("8.00"),
            "descripcion": "Tomate rojo maduro jugoso para ensaladas y salsas"
        },
        {
            "nombre": "Cebolla Roja Seleccionada",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("6.50"),
            "descripcion": "Cebolla morada de cabeza firme y buen tamaño"
        },
        {
            "nombre": "Papa Holandesa Seleccionada",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("7.00"),
            "descripcion": "Papa lavada ideal para freír, hervir o puré"
        },
        {
            "nombre": "Zanahoria Criolla Fresca",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("5.00"),
            "descripcion": "Zanahoria fresca crujiente rica en carotenos"
        },
        {
            "nombre": "Pimiento Morrón Rojo",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("10.00"),
            "descripcion": "Pimiento morrón fresco aromático para guisos y salteados"
        },
        {
            "nombre": "Queso Chaqueño Criollo",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("34.00"),
            "descripcion": "Queso artesanal semi-duro chaqueño con sal moderada"
        },
        {
            "nombre": "Leche Entera Natural Pil",
            "unidad_medida": "litro",
            "precio_estimado": Decimal("6.50"),
            "descripcion": "Leche fluida pasteurizada homogeneizada ultrapurificada"
        },
        {
            "nombre": "Harina de Trigo Especial 000",
            "unidad_medida": "kg",
            "precio_estimado": Decimal("8.50"),
            "descripcion": "Harina de trigo enriquecida para repostería y panes"
        }
    ]

    productos_creados = {}
    for prod in productos_data:
        ing = db.query(Ingrediente).filter(Ingrediente.nombre == prod["nombre"]).first()
        if not ing:
            ing = Ingrediente(
                nombre=prod["nombre"],
                unidad_medida=prod["unidad_medida"],
                precio_estimado=prod["precio_estimado"],
                descripcion=prod["descripcion"],
                estado="ACTIVO"
            )
            db.add(ing)
            db.flush()
            print(f"[OK] Creado ingrediente: {ing.nombre} ({ing.precio_estimado} Bs / {ing.unidad_medida})")
        else:
            print(f"[INFO] Ingrediente ya existe: {ing.nombre}")
        productos_creados[prod["nombre"]] = ing

    # 4. Asignación realista de Precios en Tiendas (IngredienteLugarCompra)
    # Variaciones de precios según tipo de tienda:
    # Mercados: más baratos en verduras y carnes frescas
    # Supermercados: precio estándar / empaquetado
    # Distribuidora: mejor precio en pollo y huevo
    # Tiendas de barrio: conveniencia
    precios_relaciones = [
        # Pechuga de Pollo
        ("Pechuga de Pollo Fresca", "Distribuidora Avícola Sofía Central", Decimal("25.50")),
        ("Pechuga de Pollo Fresca", "Mercado Los Pozos - Sector Abarrotes", Decimal("26.00")),
        ("Pechuga de Pollo Fresca", "Mercado Abasto Mayorista", Decimal("25.00")),
        ("Pechuga de Pollo Fresca", "Supermercado Fidalga Equipetrol", Decimal("29.50")),
        ("Pechuga de Pollo Fresca", "Hipermaxi Norte Banzer", Decimal("28.90")),

        # Carne de Res Pulpa Primera
        ("Carne de Res - Pulpa Primera", "Carnicería y Frial San Carlos", Decimal("44.00")),
        ("Carne de Res - Pulpa Primera", "Mercado Abasto Mayorista", Decimal("42.50")),
        ("Carne de Res - Pulpa Primera", "Supermercado Fidalga Equipetrol", Decimal("48.50")),
        ("Carne de Res - Pulpa Primera", "Hipermaxi Norte Banzer", Decimal("47.90")),

        # Carne Molida Especial
        ("Carne Molida Especial", "Carnicería y Frial San Carlos", Decimal("35.00")),
        ("Carne Molida Especial", "Mercado Abasto Mayorista", Decimal("34.00")),
        ("Carne Molida Especial", "Hipermaxi Norte Banzer", Decimal("39.90")),

        # Arroz Grano de Oro
        ("Arroz Grano de Oro Seleccionado", "Mercado Los Pozos - Sector Abarrotes", Decimal("10.50")),
        ("Arroz Grano de Oro Seleccionado", "Mercado Abasto Mayorista", Decimal("10.00")),
        ("Arroz Grano de Oro Seleccionado", "Tienda y Abarrotes Doña María", Decimal("12.50")),
        ("Arroz Grano de Oro Seleccionado", "Supermercado Fidalga Equipetrol", Decimal("12.90")),

        # Fideos Espagueti
        ("Fideos Espagueti Trigo de Oro", "Mercado Los Pozos - Sector Abarrotes", Decimal("8.50")),
        ("Fideos Espagueti Trigo de Oro", "Tienda y Abarrotes Doña María", Decimal("10.00")),
        ("Fideos Espagueti Trigo de Oro", "Hipermaxi Norte Banzer", Decimal("9.80")),

        # Huevos de Granja
        ("Huevos de Granja Seleccionados", "Distribuidora Avícola Sofía Central", Decimal("11.50")),
        ("Huevos de Granja Seleccionados", "Mercado Los Pozos - Sector Abarrotes", Decimal("12.00")),
        ("Huevos de Granja Seleccionados", "Tienda y Abarrotes Doña María", Decimal("13.50")),
        ("Huevos de Granja Seleccionados", "Supermercado Fidalga Equipetrol", Decimal("14.00")),

        # Aceite Vegetal Fino
        ("Aceite Vegetal Fino", "Mercado Abasto Mayorista", Decimal("13.00")),
        ("Aceite Vegetal Fino", "Mercado Los Pozos - Sector Abarrotes", Decimal("13.50")),
        ("Aceite Vegetal Fino", "Hipermaxi Norte Banzer", Decimal("14.90")),
        ("Aceite Vegetal Fino", "Tienda y Abarrotes Doña María", Decimal("15.50")),

        # Tomate Manzano
        ("Tomate Manzano Criollo", "Mercado Abasto Mayorista", Decimal("6.00")),
        ("Tomate Manzano Criollo", "Frutería y Verdulería El Edén", Decimal("7.50")),
        ("Tomate Manzano Criollo", "Mercado Los Pozos - Sector Abarrotes", Decimal("6.50")),
        ("Tomate Manzano Criollo", "Supermercado Fidalga Equipetrol", Decimal("9.50")),

        # Cebolla Roja
        ("Cebolla Roja Seleccionada", "Mercado Abasto Mayorista", Decimal("5.00")),
        ("Cebolla Roja Seleccionada", "Mercado Los Pozos - Sector Abarrotes", Decimal("5.50")),
        ("Cebolla Roja Seleccionada", "Frutería y Verdulería El Edén", Decimal("6.50")),
        ("Cebolla Roja Seleccionada", "Hipermaxi Norte Banzer", Decimal("7.50")),

        # Papa Holandesa
        ("Papa Holandesa Seleccionada", "Mercado Abasto Mayorista", Decimal("5.50")),
        ("Papa Holandesa Seleccionada", "Mercado Los Pozos - Sector Abarrotes", Decimal("6.00")),
        ("Papa Holandesa Seleccionada", "Frutería y Verdulería El Edén", Decimal("7.00")),
        ("Papa Holandesa Seleccionada", "Supermercado Fidalga Equipetrol", Decimal("8.50")),

        # Zanahoria Criolla
        ("Zanahoria Criolla Fresca", "Mercado Abasto Mayorista", Decimal("4.00")),
        ("Zanahoria Criolla Fresca", "Frutería y Verdulería El Edén", Decimal("5.00")),
        ("Zanahoria Criolla Fresca", "Hipermaxi Norte Banzer", Decimal("6.00")),

        # Pimiento Morrón
        ("Pimiento Morrón Rojo", "Mercado Abasto Mayorista", Decimal("8.00")),
        ("Pimiento Morrón Rojo", "Frutería y Verdulería El Edén", Decimal("9.50")),
        ("Pimiento Morrón Rojo", "Supermercado Fidalga Equipetrol", Decimal("11.90")),

        # Queso Chaqueño
        ("Queso Chaqueño Criollo", "Mercado Los Pozos - Sector Abarrotes", Decimal("30.00")),
        ("Queso Chaqueño Criollo", "Carnicería y Frial San Carlos", Decimal("32.00")),
        ("Queso Chaqueño Criollo", "Supermercado Fidalga Equipetrol", Decimal("36.50")),

        # Leche Entera Pil
        ("Leche Entera Natural Pil", "Tienda y Abarrotes Doña María", Decimal("6.50")),
        ("Leche Entera Natural Pil", "Hipermaxi Norte Banzer", Decimal("6.20")),
        ("Leche Entera Natural Pil", "Supermercado Fidalga Equipetrol", Decimal("6.30")),

        # Harina de Trigo
        ("Harina de Trigo Especial 000", "Mercado Los Pozos - Sector Abarrotes", Decimal("7.50")),
        ("Harina de Trigo Especial 000", "Mercado Abasto Mayorista", Decimal("7.00")),
        ("Harina de Trigo Especial 000", "Tienda y Abarrotes Doña María", Decimal("9.00")),
    ]

    total_precios = 0
    for nom_prod, nom_tienda, precio in precios_relaciones:
        prod_obj = productos_creados.get(nom_prod) or db.query(Ingrediente).filter(Ingrediente.nombre == nom_prod).first()
        tienda_obj = tiendas_creadas.get(nom_tienda) or db.query(LugarCompra).filter(LugarCompra.nombre == nom_tienda).first()

        if prod_obj and tienda_obj:
            rel = db.query(IngredienteLugarCompra).filter(
                IngredienteLugarCompra.id_ingrediente == prod_obj.id_ingrediente,
                IngredienteLugarCompra.id_lugar_compra == tienda_obj.id_lugar_compra
            ).first()

            if not rel:
                rel = IngredienteLugarCompra(
                    id_ingrediente=prod_obj.id_ingrediente,
                    id_lugar_compra=tienda_obj.id_lugar_compra,
                    precio=precio,
                    cantidad_referencia=Decimal("1.00"),
                    unidad_medida=prod_obj.unidad_medida,
                    disponible=True
                )
                db.add(rel)
                total_precios += 1

    db.commit()
    print(f"\n[ÉXITO] Seeder completado. Precios enlazados: {total_precios}")


if __name__ == "__main__":
    ejecutar_seeder()
