from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.schemas.autenticacion import RegistroUsuarioSchema, LoginSchema
from app.schemas.usuario import UsuarioRespuestaSchema
from app.schemas.token import TokenSchema
from app.services.autenticacion_service import AutenticacionService

router = APIRouter(
    prefix="/autenticacion",
    tags=["Autenticación"]
)


# =========================================================================
# CASO DE USO: CU01 - REGISTRARSE
# Endpoint: POST /autenticacion/registro
# Acceso: Público (Crea exclusivamente usuarios con rol CLIENTE)
# =========================================================================
@router.post(
    "/registro",
    response_model=UsuarioRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU01: Registrarse como nuevo cliente",
    description="Permite registrar un nuevo usuario con rol CLIENTE. La contraseña se cifra mediante bcrypt."
)
def registrar(
    datos: RegistroUsuarioSchema,
    db: Session = Depends(get_db)
):
    """
    Controlador para el registro de clientes (CU01).
    Delega la validación de unicidad y hashing a AutenticacionService.
    """
    return AutenticacionService.registrar_cliente(db=db, datos=datos)


# =========================================================================
# CASO DE USO: CU02 - INICIAR SESIÓN
# Endpoint: POST /autenticacion/login
# Acceso: Público (Autentica credenciales y emite token Bearer JWT)
# =========================================================================
@router.post(
    "/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
    summary="CU02: Iniciar sesión",
    description="Valida las credenciales (correo y contraseña) y retorna un token de acceso JWT."
)
def login(
    credenciales: LoginSchema,
    db: Session = Depends(get_db)
):
    """
    Controlador para autenticar usuarios y expedir JWT (CU02).
    Delega la comprobación de credenciales y generación de JWT a AutenticacionService.
    """
    return AutenticacionService.iniciar_sesion(db=db, credenciales=credenciales)
