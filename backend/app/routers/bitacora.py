from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.bitacora import BitacoraListadoPaginadoSchema
from app.security.dependencias import requiere_roles
from app.services.bitacora_service import BitacoraService

router = APIRouter(
    prefix="/bitacora",
    tags=["Bitácora"]
)


# =========================================================================
# CASO DE USO: CU25 - CONSULTAR BITÁCORA DEL SISTEMA
# Acceso: Exclusivo para usuarios con rol ADMINISTRADOR
# =========================================================================

@router.get(
    "",
    response_model=BitacoraListadoPaginadoSchema,
    status_code=status.HTTP_200_OK,
    summary="CU25: Consultar bitácora del sistema (Solo Administrador)",
    description="Consulta y lista eventos de auditoría de forma paginada con filtros por módulo, acción, usuario y rango de fechas."
)
def listar_bitacora(
    pagina: int = Query(1, ge=1, description="Número de página a consultar"),
    limite: int = Query(20, ge=1, le=100, description="Cantidad de registros por página"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha y hora de inicio (ISO 8601)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha y hora de fin (ISO 8601)"),
    modulo: Optional[str] = Query(None, description="Filtrar por módulo (ej. AUTENTICACION, RESERVAS, PEDIDOS)"),
    accion: Optional[str] = Query(None, description="Filtrar por acción (ej. LOGIN_EXITOSO, CREAR_RESERVA)"),
    id_usuario: Optional[int] = Query(None, description="Filtrar por ID de usuario causante"),
    busqueda: Optional[str] = Query(None, description="Búsqueda por texto en descripción o acción"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    """
    Controlador para consultar la bitácora de auditoría del sistema (CU25).
    Requiere rol ADMINISTRADOR.
    """
    return BitacoraService.listar(
        db=db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        modulo=modulo,
        accion=accion,
        id_usuario=id_usuario,
        busqueda=busqueda,
        pagina=pagina,
        limite=limite
    )
