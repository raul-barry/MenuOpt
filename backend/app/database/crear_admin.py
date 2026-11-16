"""Siembra las cuentas de prueba del README y el catálogo base de preferencias."""
from app.database.conexion import SessionLocal
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.preferencia import Preferencia
from app.security.contrasenas import generar_hash_contrasena, verificar_contrasena

ROLES_BASE = [
    ("ADMINISTRADOR", "Acceso total a la administración y bitácora del sistema"),
    ("RESTAURANTE", "Gestión de establecimientos gastronómicos, cartas, planos y reservas"),
    ("CLIENTE", "Planificación gastronómica, reservas, pedidos y asistente virtual"),
    ("ADMINISTRADOR_TIENDA", "Gestión de proveedores, tiendas e insumos con precios actualizados"),
]

USUARIOS_DE_PRUEBA = [
    ("Administrador", "Principal", "admin@menuopt.com", "Admin1234*", "ADMINISTRADOR", "70000000"),
    ("Carlos", "Chef", "restaurante@menuopt.com", "Resto1234*", "RESTAURANTE", "71112233"),
    ("Laura", "Gerente", "restaurante2@menuopt.com", "Resto1234*", "RESTAURANTE", "72223344"),
    ("Cliente", "Uno", "cliente1@menuopt.com", "Cliente1234*", "CLIENTE", "73334455"),
    ("Cliente", "Dos", "cliente2@menuopt.com", "Cliente1234*", "CLIENTE", "74445566"),
    ("Admin", "Eventos", "admineventos@gmail.com", "Admin1234*", "ADMINISTRADOR", "79998877"),
    ("Tienda", "Central", "tienda@menuopt.com", "Tienda1234*", "ADMINISTRADOR_TIENDA", "78889900"),
]


def sembrar_roles(db):
    """Garantiza la presencia de todos los roles del sistema."""
    for nombre_rol, desc in ROLES_BASE:
        rol = db.query(Rol).filter(Rol.nombre == nombre_rol).first()
        if not rol:
            db.add(Rol(nombre=nombre_rol, descripcion=desc, activo=True))
            print(f"[OK] Rol creado: {nombre_rol}")
    db.commit()


def sembrar_usuarios_de_prueba(db):
    """Crea las cuentas documentadas y repara sus credenciales al repetir el seed."""
    for nombres, apellidos, correo, contrasena, nombre_rol, telefono in USUARIOS_DE_PRUEBA:
        rol = db.query(Rol).filter(Rol.nombre == nombre_rol).first()
        if not rol:
            print(f"[ERROR] No existe el rol {nombre_rol}; no se pudo sembrar {correo}.")
            continue

        usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
        if not usuario:
            usuario = Usuario(
                nombres=nombres,
                apellidos=apellidos,
                correo=correo,
                contrasena_hash=generar_hash_contrasena(contrasena),
                telefono=telefono,
                estado="ACTIVO",
                id_rol=rol.id_rol,
            )
            db.add(usuario)
        else:
            # El seed restaura expresamente las cuentas de demostración al estado documentado.
            usuario.nombres = nombres
            usuario.apellidos = apellidos
            usuario.telefono = telefono
            usuario.estado = "ACTIVO"
            usuario.id_rol = rol.id_rol
            if not verificar_contrasena(contrasena, usuario.contrasena_hash):
                usuario.contrasena_hash = generar_hash_contrasena(contrasena)
        print(f"[OK] Cuenta de prueba lista: {correo}")
    db.commit()


def sembrar_preferencias_iniciales(db):
    preferencias_base = [
        {"nombre": "Vegetariano", "tipo": "DIETARIA", "descripcion": "Excluye carne animal."},
        {"nombre": "Vegano", "tipo": "DIETARIA", "descripcion": "Excluye todo producto de origen animal."},
        {"nombre": "Sin gluten", "tipo": "ALERGIA", "descripcion": "Apto para personas con celiaquía o intolerancia al gluten."},
        {"nombre": "Sin lactosa", "tipo": "INTOLERANCIA", "descripcion": "Apto para personas intolerantes a la lactosa."},
        {"nombre": "Picante", "tipo": "SABOR", "descripcion": "Platos con condimento y picante pronunciado."},
        {"nombre": "Sin azúcar", "tipo": "SALUD", "descripcion": "Preparaciones bajas o sin azúcares añadidos."},
    ]
    for pref_data in preferencias_base:
        existente = db.query(Preferencia).filter(Preferencia.nombre == pref_data["nombre"]).first()
        if not existente:
            db.add(Preferencia(
                nombre=pref_data["nombre"],
                tipo=pref_data["tipo"],
                descripcion=pref_data["descripcion"],
                activo=True,
            ))
            print(f"[OK] Preferencia creada: {pref_data['nombre']}")
        else:
            print(f"[INFO] Preferencia '{pref_data['nombre']}' ya existe.")
    db.commit()


def sembrar_areas_por_defecto(db):
    """Garantiza que todo restaurante registrado cuente al menos con el área 'Salón Principal' (CU17)."""
    from app.models.restaurante import Restaurante
    from app.models.area_restaurante import AreaRestaurante

    restaurantes = db.query(Restaurante).all()
    for r in restaurantes:
        tiene_area = db.query(AreaRestaurante).filter(AreaRestaurante.id_restaurante == r.id_restaurante).first()
        if not tiene_area:
            area_default = AreaRestaurante(
                id_restaurante=r.id_restaurante,
                nombre="Salón Principal",
                descripcion="Área física principal del establecimiento",
                ancho_mapa=1200,
                alto_mapa=700,
                orden=1,
                activo=True
            )
            db.add(area_default)
            print(f"[OK] Área 'Salón Principal' autogenerada para el restaurante: {r.nombre}")
    db.commit()


def sembrar_tiendas_por_defecto(db):
    """Siembra proveedores y tiendas por defecto para el rol ADMINISTRADOR_TIENDA (CU09)."""
    from app.models.lugar_compra import LugarCompra
    from app.models.ingrediente import Ingrediente
    from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
    from app.models.ubicacion import Ubicacion
    from decimal import Decimal

    usuario_tienda = db.query(Usuario).filter(Usuario.correo == "tienda@menuopt.com").first()
    if not usuario_tienda:
        return

    tiendas_data = [
        {
            "nombre": "Supermercado Hipermaxi Central",
            "tipo": "SUPERMERCADO",
            "telefono": "33445566",
            "ciudad": "Santa Cruz",
            "direccion": "Av. San Martín esq. 4to Anillo"
        },
        {
            "nombre": "Mercado La Cancha - Sección Abarrotes",
            "tipo": "MERCADO",
            "telefono": "71234567",
            "ciudad": "Cochabamba",
            "direccion": "Calle Punata y San Martín"
        }
    ]

    for td in tiendas_data:
        lugar = db.query(LugarCompra).filter(LugarCompra.nombre == td["nombre"]).first()
        if not lugar:
            ub = Ubicacion(direccion=td["direccion"], ciudad=td["ciudad"])
            db.add(ub)
            db.flush()
            lugar = LugarCompra(
                nombre=td["nombre"],
                tipo=td["tipo"],
                telefono=td["telefono"],
                estado="ACTIVO",
                id_ubicacion=ub.id_ubicacion,
                id_usuario_responsable=usuario_tienda.id_usuario
            )
            db.add(lugar)
            db.flush()
            print(f"[OK] Proveedor / Tienda creada: {lugar.nombre}")
        else:
            if not lugar.id_usuario_responsable:
                lugar.id_usuario_responsable = usuario_tienda.id_usuario

    db.commit()


def sembrar_recetas_biblioteca(db):
    """Siembra el catálogo inicial de la Biblioteca de Recetas (CU15)."""
    from decimal import Decimal
    from app.models.receta import Receta, RecetaIngrediente
    from app.models.ingrediente import Ingrediente

    if db.query(Receta).count() > 0:
        return

    admin_user = db.query(Usuario).filter(Usuario.correo == "admin@menuopt.com").first()
    id_admin = admin_user.id_usuario if admin_user else None

    # Catálogo de ingredientes mapeado por nombre minúsculo
    ings_map = {ing.nombre.lower(): ing for ing in db.query(Ingrediente).all()}

    def buscar_ing_id(nombre_clave):
        for k, v in ings_map.items():
            if nombre_clave.lower() in k:
                return v.id_ingrediente, v.nombre, v.unidad_medida
        return None, nombre_clave, "kg"

    recetas_semilla = [
        {
            "nombre": "Majadito de Charque Tradicional",
            "descripcion": "Plato insignia cruceño con arroz tostado, charque desmenuzado, plátano frito y huevo montado.",
            "instrucciones": "1. Hervir el charque y desmenuzar en tacú.\n2. Tostar el arroz con cebolla, tomate y un toque de urucú.\n3. Incorporar el caldo del charque y cocinar hasta secar.\n4. Servir con huevo frito y plátano maduro.",
            "tipo_comida": "ALMUERZO",
            "porciones": 4,
            "tiempo_minutos": 45,
            "dificultad": "MEDIA",
            "origen": "Tradicional Cruceña",
            "ingredientes": [
                ("carne de res", Decimal("0.50"), "kg"),
                ("arroz grano de oro", Decimal("0.50"), "kg"),
                ("huevos", Decimal("0.50"), "docena"),
                ("cebolla roja", Decimal("0.30"), "kg"),
                ("tomate manzano", Decimal("0.30"), "kg"),
                ("aceite vegetal", Decimal("0.20"), "litro"),
            ]
        },
        {
            "nombre": "Silpancho Cochabambino Casero",
            "descripcion": "Milanesa de carne apanada delgada sobre cama de arroz blanco y papas doradas, coronada con huevo y salsa criolla.",
            "instrucciones": "1. Aplanar los filetes de pulpa con pan molido hasta dejarlos delgados.\n2. Freír en aceite caliente 2 minutos por lado.\n3. Cocinar arroz blanco y dorar rodajas de papa cocida.\n4. Montar con huevo frito y ensalada picada de tomate y cebolla.",
            "tipo_comida": "ALMUERZO",
            "porciones": 2,
            "tiempo_minutos": 35,
            "dificultad": "MEDIA",
            "origen": "Tradicional Boliviana",
            "ingredientes": [
                ("carne de res", Decimal("0.40"), "kg"),
                ("arroz grano de oro", Decimal("0.30"), "kg"),
                ("papa holandesa", Decimal("0.40"), "kg"),
                ("huevos", Decimal("0.25"), "docena"),
                ("tomate manzano", Decimal("0.20"), "kg"),
                ("cebolla roja", Decimal("0.20"), "kg"),
            ]
        },
        {
            "nombre": "Pizza Casera a la Piedra",
            "descripcion": "Masa crocante casera con salsa de tomates frescos, queso chaqueño fundido y orégano.",
            "instrucciones": "1. Amasar la harina con agua tibia, levadura, sal y aceite.\n2. Dejar levar 30 minutos.\n3. Estirar fino, agregar salsa de tomate y abundante queso.\n4. Hornear a 220°C durante 12-15 minutos.",
            "tipo_comida": "CENA",
            "porciones": 4,
            "tiempo_minutos": 40,
            "dificultad": "FACIL",
            "origen": "Internacional",
            "ingredientes": [
                ("harina de trigo", Decimal("0.80"), "kg"),
                ("queso chaqueño", Decimal("0.45"), "kg"),
                ("tomate manzano", Decimal("0.40"), "kg"),
                ("aceite vegetal", Decimal("0.15"), "litro"),
            ]
        },
        {
            "nombre": "Spaghetti a la Boloñesa Gratinado",
            "descripcion": "Pasta al dente bañada en salsa espesa de carne molida, tomate concentrado y queso rallado.",
            "instrucciones": "1. Sofreír cebolla picada y carne molida con sal y pimienta.\n2. Añadir tomate triturado y cocinar a fuego lento 20 minutos.\n3. Hervir los espaguetis en abundante agua con sal.\n4. Mezclar con la salsa, espolvorear queso y gratinar 5 minutos.",
            "tipo_comida": "CENA",
            "porciones": 3,
            "tiempo_minutos": 30,
            "dificultad": "FACIL",
            "origen": "Internacional",
            "ingredientes": [
                ("fideos espagueti", Decimal("0.40"), "kg"),
                ("carne molida", Decimal("0.40"), "kg"),
                ("tomate manzano", Decimal("0.35"), "kg"),
                ("queso chaqueño", Decimal("0.20"), "kg"),
                ("cebolla roja", Decimal("0.20"), "kg"),
            ]
        },
        {
            "nombre": "Hamburguesas Caseras con Queso",
            "descripcion": "Medallones jugosos de carne sazonada a la plancha con queso derretido y rodajas de tomate.",
            "instrucciones": "1. Formar medallones de carne molida sazonados solo con sal y pimienta.\n2. Sellar a fuego fuerte 3 minutos por lado en plancha caliente.\n3. Colocar queso encima para fundir.\n4. Acompañar con rodajas de tomate fresco y cebolla salteada.",
            "tipo_comida": "CENA",
            "porciones": 2,
            "tiempo_minutos": 25,
            "dificultad": "FACIL",
            "origen": "Comida Rápida Casera",
            "ingredientes": [
                ("carne molida", Decimal("0.35"), "kg"),
                ("queso chaqueño", Decimal("0.20"), "kg"),
                ("tomate manzano", Decimal("0.20"), "kg"),
                ("cebolla roja", Decimal("0.15"), "kg"),
            ]
        },
        {
            "nombre": "Sopa de Maní Tradicional Festiva",
            "descripcion": "Reconfortante sopa espesa de maní licuado con carne tierna, papas, arvejas y papas al hilo crocantes.",
            "instrucciones": "1. Cocinar la carne con cebolla y zanahoria hasta obtener un caldo sabroso.\n2. Licuar el maní crudo con agua y verterlo a la olla hirviendo lentamente durante 45 min.\n3. Añadir papas y fideos tostados.\n4. Servir bien caliente con perejil fresco picado y papas hilo.",
            "tipo_comida": "ALMUERZO",
            "porciones": 4,
            "tiempo_minutos": 60,
            "dificultad": "MEDIA",
            "origen": "Tradicional Cruceña",
            "ingredientes": [
                ("carne de res", Decimal("0.50"), "kg"),
                ("papa holandesa", Decimal("0.40"), "kg"),
                ("fideos espagueti", Decimal("0.20"), "kg"),
                ("zanahoria", Decimal("0.20"), "kg"),
                ("cebolla roja", Decimal("0.20"), "kg"),
            ]
        }
    ]

    for r_data in recetas_semilla:
        rec = Receta(
            nombre=r_data["nombre"],
            descripcion=r_data["descripcion"],
            instrucciones=r_data["instrucciones"],
            tipo_comida=r_data["tipo_comida"],
            porciones=r_data["porciones"],
            tiempo_minutos=r_data["tiempo_minutos"],
            dificultad=r_data["dificultad"],
            origen=r_data["origen"],
            id_usuario_creador=id_admin
        )
        for nom_clave, cant, un in r_data["ingredientes"]:
            id_ing, nombre_oficial, unidad_oficial = buscar_ing_id(nom_clave)
            ri = RecetaIngrediente(
                id_ingrediente=id_ing,
                nombre_ingrediente=nombre_oficial,
                cantidad=cant,
                unidad_medida=unidad_oficial if id_ing else un
            )
            rec.ingredientes.append(ri)
        db.add(rec)

    db.commit()
    print(f"[OK] Biblioteca de Recetas sembrada con {len(recetas_semilla)} recetas.")


def sembrar_usuarios_iniciales():
    from app.database.conexion import engine
    from app.database.base import Base
    import app.models
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        sembrar_roles(db)
        sembrar_usuarios_de_prueba(db)
        sembrar_preferencias_iniciales(db)
        sembrar_areas_por_defecto(db)
        sembrar_tiendas_por_defecto(db)
        sembrar_recetas_biblioteca(db)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error al sembrar datos iniciales: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    sembrar_usuarios_iniciales()
