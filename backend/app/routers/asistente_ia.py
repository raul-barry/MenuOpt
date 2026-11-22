# CASO DE USO: CU26 - Usar asistencia con IA
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.security.dependencias import requiere_roles
from app.ai.schemas import (
    SolicitudInterpretar,
    SolicitudInterpretada,
    SolicitudExplicarRecomendacion,
    SolicitudExplicarComparacion,
    ExplicacionRespuesta
)
from app.services.asistente_ia_service import AsistenteIAService
from app.services.agente_guia_service import AgenteGuiaService
from app.schemas.agente_guia import MensajeGuia, RespuestaGuia

router = APIRouter(
    prefix="/asistente",
    tags=["Asistente IA"]
)


@router.post(
    "/guia",
    response_model=RespuestaGuia,
    status_code=status.HTTP_200_OK,
    summary="Orientar al usuario sobre las funciones de MenuOpt según su rol",
)
def guiar_usuario(
    solicitud: MensajeGuia,
    usuario_actual: Usuario = Depends(requiere_roles(
        "CLIENTE", "RESTAURANTE", "ADMINISTRADOR", "ADMINISTRADOR_TIENDA"
    )),
):
    rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
    return AgenteGuiaService.responder(solicitud, rol)


# =========================================================================
# CU26 - INTERPRETAR SOLICITUD EN LENGUAJE NATURAL
# =========================================================================
@router.post(
    "/interpretar",
    response_model=SolicitudInterpretada,
    status_code=status.HTTP_200_OK,
    summary="CU26: Interpretar solicitud gastronómica en lenguaje natural"
)
def interpretar_solicitud(
    solicitud: SolicitudInterpretar,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return AsistenteIAService.interpretar_solicitud(
        db=db,
        solicitud=solicitud,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CU26 - EXPLICAR RECOMENDACIÓN EXISTENTE (CU13)
# =========================================================================
@router.post(
    "/explicar-recomendacion",
    response_model=ExplicacionRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU26: Explicar por qué una recomendación se adapta a los criterios reales"
)
def explicar_recomendacion(
    datos: SolicitudExplicarRecomendacion,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return AsistenteIAService.explicar_recomendacion(
        db=db,
        id_recomendacion=datos.id_recomendacion,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CU26 - EXPLICAR COMPARACIÓN EXISTENTE (CU14)
# =========================================================================
@router.post(
    "/explicar-comparacion",
    response_model=ExplicacionRespuesta,
    status_code=status.HTTP_200_OK,
    summary="CU26: Explicar la comparativa entre Restaurante y Preparación Propia"
)
def explicar_comparacion(
    datos: SolicitudExplicarComparacion,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("CLIENTE", "ADMINISTRADOR"))
):
    return AsistenteIAService.explicar_comparacion(
        db=db,
        id_planificacion=datos.id_planificacion,
        usuario_actual=usuario_actual
    )
