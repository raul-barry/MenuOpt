from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.autenticacion import RegistroUsuarioSchema, LoginSchema
from app.schemas.token import TokenSchema
from app.security.contrasenas import generar_hash_contrasena, verificar_contrasena
from app.security.jwt import crear_token_acceso


class AutenticacionService:
    """
    Servicio encargado de la lógica de negocio de autenticación (CU01 y CU02).
    """

    # =========================================================================
    # CASO DE USO: CU01 - REGISTRARSE
    # Descripción: Permite a un nuevo usuario registrarse como CLIENTE en la
    #              plataforma. Valida datos, normaliza correo, comprueba unicidad,
    #              cifra la contraseña con bcrypt y asigna rol CLIENTE de forma segura.
    # =========================================================================
    @staticmethod
    def registrar_cliente(db: Session, datos: RegistroUsuarioSchema) -> Usuario:
        """
        LÓGICA CU01 - REGISTRARSE:
        Registra un nuevo usuario con rol CLIENTE.
        Valida que el correo no esté duplicado y cifra la contraseña.
        """
        correo_normalizado = datos.correo.strip().lower()

        # Verificar si el correo ya está registrado
        usuario_existente = UsuarioRepository.buscar_por_correo(db, correo_normalizado)
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya se encuentra registrado en el sistema."
            )

        # Obtener rol CLIENTE garantizando que el usuario público solo sea CLIENTE
        rol_cliente = UsuarioRepository.buscar_rol_por_nombre(db, "CLIENTE")
        if not rol_cliente:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="El rol base CLIENTE no está configurado en el sistema."
            )

        # Generar hash seguro de la contraseña
        hash_contrasena = generar_hash_contrasena(datos.contrasena)

        # Instanciar el nuevo usuario
        nuevo_usuario = Usuario(
            nombres=datos.nombres.strip(),
            apellidos=datos.apellidos.strip(),
            correo=correo_normalizado,
            contrasena_hash=hash_contrasena,
            telefono=datos.telefono.strip() if datos.telefono else None,
            estado="ACTIVO",
            id_rol=rol_cliente.id_rol
        )

        usuario_creado = UsuarioRepository.crear_usuario(db, nuevo_usuario)
        # Recargar para asegurar que la relación 'rol' esté accesible
        return UsuarioRepository.buscar_por_id(db, usuario_creado.id_usuario)

    # =========================================================================
    # CASO DE USO: CU02 - INICIAR SESIÓN
    # Descripción: Valida las credenciales del usuario (correo y contraseña),
    #              comprueba que la cuenta esté activa y emite un token de acceso JWT.
    # =========================================================================
    @staticmethod
    def iniciar_sesion(db: Session, credenciales: LoginSchema) -> TokenSchema:
        """
        LÓGICA CU02 - INICIAR SESIÓN:
        Valida credenciales, comprueba estado del usuario y genera token JWT.
        """
        correo_normalizado = credenciales.correo.strip().lower()
        usuario = UsuarioRepository.buscar_por_correo(db, correo_normalizado)

        # Mensaje de error genérico para evitar divulgación de información
        error_credenciales = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"}
        )

        if not usuario:
            raise error_credenciales

        # Verificar contraseña
        if not verificar_contrasena(credenciales.contrasena, usuario.contrasena_hash):
            raise error_credenciales

        # Comprobar estado del usuario
        if usuario.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su cuenta se encuentra inactiva o suspendida. Contacte al administrador."
            )

        # Generar JWT con datos mínimos de identificación
        payload = {
            "sub": str(usuario.id_usuario),
            "id_usuario": usuario.id_usuario,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre if usuario.rol else "CLIENTE"
        }
        token_acceso = crear_token_acceso(datos=payload)

        return TokenSchema(
            access_token=token_acceso,
            token_type="bearer",
            usuario=usuario
        )
