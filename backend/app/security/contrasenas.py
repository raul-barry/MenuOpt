import bcrypt


def generar_hash_contrasena(contrasena: str) -> str:
    """
    Genera un hash seguro para la contraseña en texto plano utilizando bcrypt con salt automático.
    """
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(contrasena.encode("utf-8"), salt)
    return hash_bytes.decode("utf-8")


def verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash almacenado.
    """
    try:
        return bcrypt.checkpw(
            contrasena_plana.encode("utf-8"),
            contrasena_hash.encode("utf-8")
        )
    except Exception:
        return False
