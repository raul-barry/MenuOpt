import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.database.conexion import SessionLocal
from app.models.dispositivo_push import DispositivoPush, NotificacionOutbox

logger = logging.getLogger(__name__)


def crear_evento(
    db: Session,
    *,
    clave: str,
    destinatario: int,
    tipo: str,
    recurso_id: int,
    titulo: str,
    cuerpo: str,
) -> NotificacionOutbox:
    """Agrega un evento idempotente a la misma transacción que el cambio de negocio."""
    existente = db.query(NotificacionOutbox).filter_by(clave_evento=clave).first()
    if existente:
        return existente
    evento = NotificacionOutbox(
        clave_evento=clave,
        id_usuario_destino=destinatario,
        tipo_recurso=tipo,
        id_recurso=recurso_id,
        titulo=titulo,
        cuerpo=cuerpo,
        estado="PENDIENTE",
    )
    db.add(evento)
    db.flush()
    return evento


def _firebase_app():
    from firebase_admin import credentials, get_app, initialize_app

    try:
        return get_app()
    except ValueError:
        raw_credentials = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw_credentials:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON no está configurada")
        certificate = credentials.Certificate(json.loads(raw_credentials))
        project_id = os.getenv("FIREBASE_PROJECT_ID", "").strip() or None
        return initialize_app(certificate, options={"projectId": project_id} if project_id else None)


def enviar_evento_notificacion(id_notificacion: int) -> None:
    """Envía un evento confirmado por FCM usando una sesión nueva en background."""
    with SessionLocal() as db:
        evento = db.query(NotificacionOutbox).filter_by(id_notificacion=id_notificacion).with_for_update().first()
        if not evento or evento.estado != "PENDIENTE":
            return

        dispositivos = db.query(DispositivoPush).filter_by(id_usuario=evento.id_usuario_destino).all()
        if not dispositivos:
            evento.estado = "SIN_DESTINATARIOS"
            db.commit()
            return

        entregados = set(evento.dispositivos_enviados or [])
        pendientes = [item for item in dispositivos if item.id_dispositivo not in entregados]
        if not pendientes:
            evento.estado = "ENVIADA"
            evento.error_envio = None
            evento.fecha_envio = datetime.now(timezone.utc)
            db.commit()
            return
        tokens = [item.token_fcm for item in pendientes]

        evento.estado = "ENVIANDO"
        evento.intentos += 1
        db.commit()

        try:
            from firebase_admin import messaging

            app = _firebase_app()
            response = messaging.send_each_for_multicast(
                messaging.MulticastMessage(
                    tokens=tokens,
                    notification=messaging.Notification(title=evento.titulo, body=evento.cuerpo),
                    data={
                        "type": evento.tipo_recurso,
                        "route": evento.tipo_recurso,
                        "resource_id": str(evento.id_recurso),
                        "event_id": evento.clave_evento,
                    },
                    android=messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            channel_id="menuopt_transacciones_v1",
                            tag=evento.clave_evento,
                        ),
                    ),
                ),
                app=app,
            )
            invalid_tokens = []
            exitosos = []
            for device, token, result in zip(pendientes, tokens, response.responses):
                if result.success:
                    exitosos.append(device.id_dispositivo)
                code = str(getattr(getattr(result, "exception", None), "code", "")).lower()
                if not result.success and code == "registration-token-not-registered":
                    invalid_tokens.append(token)
            if invalid_tokens:
                db.query(DispositivoPush).filter(DispositivoPush.token_fcm.in_(invalid_tokens)).delete(synchronize_session=False)
            evento = db.query(NotificacionOutbox).filter_by(id_notificacion=id_notificacion).first()
            evento.dispositivos_enviados = list(set(evento.dispositivos_enviados or []) | set(exitosos))
            evento.estado = "ENVIADA" if response.failure_count == 0 else "FALLIDA"
            evento.error_envio = None if evento.estado == "ENVIADA" else "Firebase rechazó uno o más dispositivos; el reintento omitirá los ya aceptados."
            evento.fecha_envio = datetime.now(timezone.utc) if evento.estado == "ENVIADA" else None
            db.commit()
            if response.failure_count:
                logger.warning(
                    "FCM parcial/fallido para evento %s: ok=%d, fallidos=%d",
                    evento.clave_evento, response.success_count, response.failure_count,
                )
        except Exception as exc:
            db.rollback()
            evento = db.query(NotificacionOutbox).filter_by(id_notificacion=id_notificacion).first()
            if evento:
                evento.estado = "FALLIDA"
                evento.error_envio = f"{type(exc).__name__}: fallo de proveedor FCM"[:240]
                db.commit()
            logger.error(
                "Falló el envío FCM del evento %s (%s)",
                id_notificacion,
                type(exc).__name__,
            )
