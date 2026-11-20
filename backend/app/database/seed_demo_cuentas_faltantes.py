"""Crea solo las cuentas de demostración que faltan, sin restablecer existentes."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.seed_demo_util import ejecutar_comando
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.security.contrasenas import generar_hash_contrasena


# Cuentas requeridas por los paquetes de restaurantes y experiencia de cliente.
# Se crean con las credenciales ya publicadas en el README, solo si faltan.
CUENTAS = (
    ("RESTAURANTE", "Laura", "Gerente", "restaurante2@menuopt.com", "Resto1234*"),
    ("CLIENTE", "Cliente", "Dos", "cliente2@menuopt.com", "Cliente1234*"),
)


def sembrar(db: Session) -> dict[str, int]:
    roles: dict[str, Rol] = {}
    for nombre_rol in sorted({cuenta[0] for cuenta in CUENTAS}):
        rol = db.scalar(select(Rol).where(Rol.nombre == nombre_rol))
        if rol is None:
            rol = Rol(nombre=nombre_rol, descripcion="Rol de demostración", activo=True)
            db.add(rol)
            db.flush()
        if not rol.activo:
            raise RuntimeError(f"El rol {nombre_rol} existe, pero está inactivo; no se modificó.")
        roles[nombre_rol] = rol

    nuevas = 0
    existentes = 0
    for nombre_rol, nombres, apellidos, correo, contrasena in CUENTAS:
        usuario = db.scalar(select(Usuario).where(Usuario.correo == correo))
        if usuario is not None:
            if usuario.id_rol != roles[nombre_rol].id_rol or usuario.estado != "ACTIVO":
                raise RuntimeError(
                    f"La cuenta {correo} ya existe con otro rol o estado; no se modificó."
                )
            existentes += 1
            continue

        db.add(Usuario(
            nombres=nombres,
            apellidos=apellidos,
            correo=correo,
            contrasena_hash=generar_hash_contrasena(contrasena),
            telefono=None,
            estado="ACTIVO",
            id_rol=roles[nombre_rol].id_rol,
        ))
        nuevas += 1

    db.flush()
    return {"cuentas_nuevas": nuevas, "cuentas_ya_existentes": existentes}


if __name__ == "__main__":
    ejecutar_comando("cuentas demo faltantes", sembrar)
