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


def sembrar_usuarios_iniciales():
    db = SessionLocal()
    try:
        sembrar_roles(db)
        sembrar_usuarios_de_prueba(db)
        sembrar_preferencias_iniciales(db)
        sembrar_areas_por_defecto(db)
        sembrar_tiendas_por_defecto(db)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error al sembrar datos iniciales: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    sembrar_usuarios_iniciales()
