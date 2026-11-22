from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.dispositivo_push import DispositivoPush
from app.models.dispositivo_push import NotificacionOutbox
from app.models.usuario import Usuario
from app.schemas.notificaciones import DispositivoPushRegistro, DispositivoPushRevocar, DispositivoPushRespuesta
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.notificaciones_eventos_service import enviar_evento_notificacion

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.put("/dispositivos", response_model=DispositivoPushRespuesta, status_code=status.HTTP_200_OK)
def registrar_dispositivo(
    datos: DispositivoPushRegistro,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    dispositivo = db.query(DispositivoPush).filter_by(
        id_instalacion=datos.id_instalacion,
        id_usuario=usuario.id_usuario,
    ).first()
    token_existente = db.query(DispositivoPush).filter_by(token_fcm=datos.token).first()
    if dispositivo and token_existente and token_existente.id_dispositivo != dispositivo.id_dispositivo:
        db.delete(token_existente)
        db.flush()
    elif dispositivo is None and token_existente:
        # Poseer el token FCM permite transferir esa instalación al usuario autenticado.
        dispositivo = token_existente
    if dispositivo:
        # Un token rotado/reutilizado en un inicio de sesión nuevo queda solo con el usuario actual.
        dispositivo.id_usuario = usuario.id_usuario
        dispositivo.token_fcm = datos.token
        dispositivo.plataforma = datos.plataforma
    else:
        db.add(DispositivoPush(
            id_usuario=usuario.id_usuario,
            id_instalacion=datos.id_instalacion,
            token_fcm=datos.token,
            plataforma=datos.plataforma,
        ))
    db.commit()
    return {"registrado": True}


@router.post("/dispositivos/revocar", response_model=DispositivoPushRespuesta)
def revocar_dispositivo(
    datos: DispositivoPushRevocar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    # No revela si un token existe ni a qué usuario pertenece.
    db.query(DispositivoPush).filter_by(
        id_instalacion=datos.id_instalacion,
        id_usuario=usuario.id_usuario,
    ).delete(synchronize_session=False)
    db.commit()
    return {"registrado": True}


@router.post("/outbox/{id_notificacion}/reintentar", status_code=status.HTTP_202_ACCEPTED)
def reintentar_notificacion(
    id_notificacion: int,
    tareas: BackgroundTasks,
    db: Session = Depends(get_db),
    _: Usuario = Depends(requiere_roles("ADMINISTRADOR")),
):
    """Reencola un fallo sin crear otro evento ni permitir reenvíos concurrentes."""
    evento = (
        db.query(NotificacionOutbox)
        .filter_by(id_notificacion=id_notificacion)
        .with_for_update()
        .first()
    )
    if not evento:
        raise HTTPException(status_code=404, detail="Notificación no encontrada.")
    if evento.estado not in {"FALLIDA", "SIN_DESTINATARIOS", "PENDIENTE"}:
        return {"programada": False}
    evento.estado = "PENDIENTE"
    evento.error_envio = None
    db.commit()
    tareas.add_task(enviar_evento_notificacion, evento.id_notificacion)
    return {"programada": True}
