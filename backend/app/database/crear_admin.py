"""Siembra las cuentas de prueba del README y el catálogo base de preferencias."""
from app.database.conexion import SessionLocal
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.preferencia import Preferencia
from app.security.contrasenas import generar_hash_contrasena, verificar_contrasena

USUARIOS_DE_PRUEBA = [
    ("Administrador", "Principal", "admin@menuopt.com", "Admin1234*", "ADMINISTRADOR", "70000000"),
    ("Carlos", "Chef", "restaurante@menuopt.com", "Resto1234*", "RESTAURANTE", "71112233"),
    ("Laura", "Gerente", "restaurante2@menuopt.com", "Resto1234*", "RESTAURANTE", "72223344"),
    ("Cliente", "Uno", "cliente1@menuopt.com", "Cliente1234*", "CLIENTE", "73334455"),
    ("Cliente", "Dos", "cliente2@menuopt.com", "Cliente1234*", "CLIENTE", "74445566"),
]


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


def sembrar_usuarios_iniciales():
    db = SessionLocal()
    try:
        sembrar_usuarios_de_prueba(db)
        sembrar_preferencias_iniciales(db)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error al sembrar datos iniciales: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    sembrar_usuarios_iniciales()
