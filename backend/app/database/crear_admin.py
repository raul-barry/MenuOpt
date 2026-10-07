"""
Script auxiliar para sembrar de forma idempotente usuarios de prueba iniciales
(ADMINISTRADOR y usuarios con rol RESTAURANTE) y catálogo base de preferencias.
"""
from app.database.conexion import SessionLocal
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.preferencia import Preferencia
from app.security.contrasenas import generar_hash_contrasena


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
            nueva = Preferencia(
                nombre=pref_data["nombre"],
                tipo=pref_data["tipo"],
                descripcion=pref_data["descripcion"],
                activo=True
            )
            db.add(nueva)
            print(f"[OK] Preferencia creada: {pref_data['nombre']}")
        else:
            print(f"[INFO] Preferencia '{pref_data['nombre']}' ya existe.")
    db.commit()


def sembrar_usuarios_iniciales():
    db = SessionLocal()
    try:
        # 1. Sembrar Administrador
        correo_admin = "admin@menuopt.com"
        admin_existente = db.query(Usuario).filter(Usuario.correo == correo_admin).first()
        if not admin_existente:
            rol_admin = db.query(Rol).filter(Rol.nombre == "ADMINISTRADOR").first()
            if rol_admin:
                nuevo_admin = Usuario(
                    nombres="Administrador",
                    apellidos="Principal",
                    correo=correo_admin,
                    contrasena_hash=generar_hash_contrasena("Admin1234*"),
                    telefono="70000000",
                    estado="ACTIVO",
                    id_rol=rol_admin.id_rol
                )
                db.add(nuevo_admin)
                db.commit()
                print(f"[OK] Usuario administrador creado: {correo_admin} (contraseña: Admin1234*)")
        else:
            print(f"[INFO] Administrador '{correo_admin}' ya existe.")

        # 2. Sembrar Usuario Restaurante 1 (para pruebas CU05-CU10)
        correo_resto = "restaurante@menuopt.com"
        resto_existente = db.query(Usuario).filter(Usuario.correo == correo_resto).first()
        rol_resto = db.query(Rol).filter(Rol.nombre == "RESTAURANTE").first()
        if not resto_existente and rol_resto:
            nuevo_resto = Usuario(
                nombres="Carlos",
                apellidos="Chef",
                correo=correo_resto,
                contrasena_hash=generar_hash_contrasena("Resto1234*"),
                telefono="71112233",
                estado="ACTIVO",
                id_rol=rol_resto.id_rol
            )
            db.add(nuevo_resto)
            db.commit()
            print(f"[OK] Usuario restaurante 1 creado: {correo_resto} (contraseña: Resto1234*)")
        else:
            print(f"[INFO] Usuario restaurante 1 '{correo_resto}' ya existe.")

        # 3. Sembrar Usuario Restaurante 2 (para probar restricción de propiedad ajena 403)
        correo_resto2 = "restaurante2@menuopt.com"
        resto2_existente = db.query(Usuario).filter(Usuario.correo == correo_resto2).first()
        if not resto2_existente and rol_resto:
            nuevo_resto2 = Usuario(
                nombres="Laura",
                apellidos="Gerente",
                correo=correo_resto2,
                contrasena_hash=generar_hash_contrasena("Resto1234*"),
                telefono="72223344",
                estado="ACTIVO",
                id_rol=rol_resto.id_rol
            )
            db.add(nuevo_resto2)
            db.commit()
            print(f"[OK] Usuario restaurante 2 creado: {correo_resto2} (contraseña: Resto1234*)")
        else:
            print(f"[INFO] Usuario restaurante 2 '{correo_resto2}' ya existe.")

        # 4. Sembrar Preferencias Base (CU12)
        sembrar_preferencias_iniciales(db)

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error al sembrar datos iniciales: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    sembrar_usuarios_iniciales()
