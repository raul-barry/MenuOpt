"""Crea o restaura solo las dos cuentas demo necesarias para el primer acceso."""
from app.database.conexion import SessionLocal
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.security.contrasenas import generar_hash_contrasena


CUENTAS = (
    ("ADMINISTRADOR", "Administrador", "Principal", "admin@menuopt.com", "Admin1234*", "70000000"),
    ("RESTAURANTE", "Carlos", "Chef", "restaurante@menuopt.com", "Resto1234*", "71112233"),
)


def bootstrap_demo_accounts() -> None:
    """Garantiza roles y credenciales demo; solo se invoca con el flag explícito."""
    db = SessionLocal()
    try:
        roles = {}
        for nombre, *_ in CUENTAS:
            rol = db.query(Rol).filter(Rol.nombre == nombre).first()
            if rol is None:
                rol = Rol(nombre=nombre, descripcion="Rol de demostración", activo=True)
                db.add(rol)
                db.flush()
            roles[nombre] = rol

        for nombre_rol, nombres, apellidos, correo, contrasena, telefono in CUENTAS:
            usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
            if usuario is None:
                usuario = Usuario(correo=correo)
                db.add(usuario)
            usuario.nombres = nombres
            usuario.apellidos = apellidos
            usuario.telefono = telefono
            usuario.estado = "ACTIVO"
            usuario.id_rol = roles[nombre_rol].id_rol
            usuario.contrasena_hash = generar_hash_contrasena(contrasena)

        db.commit()
        print("[OK] Cuentas demo de administrador y restaurante listas.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
