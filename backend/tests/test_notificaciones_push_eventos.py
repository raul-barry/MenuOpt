from datetime import date, timedelta
from types import ModuleType, SimpleNamespace

import pytest

from app.database.conexion import SessionLocal
from app.models.dispositivo_push import DispositivoPush, NotificacionOutbox
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.services import notificaciones_eventos_service as push_service


def _fake_firebase(monkeypatch, *, fail=False):
    sent = []
    control = SimpleNamespace(fail=fail, calls=0, failure_tokens=set())
    firebase = ModuleType("firebase_admin")
    messaging = ModuleType("firebase_admin.messaging")
    firebase.credentials = SimpleNamespace(Certificate=lambda value: value)
    firebase.get_app = lambda: (_ for _ in ()).throw(ValueError("not initialized"))
    firebase.initialize_app = lambda *args, **kwargs: object()

    class FakeMessage:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    messaging.MulticastMessage = FakeMessage
    messaging.Notification = FakeMessage
    messaging.AndroidConfig = FakeMessage
    messaging.AndroidNotification = FakeMessage

    def send(message, app=None):
        control.calls += 1
        if control.fail:
            raise RuntimeError("simulated Firebase outage")
        sent.append(message)
        responses = [
            SimpleNamespace(
                success=token not in control.failure_tokens,
                exception=None if token not in control.failure_tokens else SimpleNamespace(code="server-unavailable"),
            )
            for token in message.tokens
        ]
        return SimpleNamespace(
            success_count=sum(result.success for result in responses),
            failure_count=sum(not result.success for result in responses),
            responses=responses,
        )

    messaging.send_each_for_multicast = send
    firebase.messaging = messaging
    monkeypatch.setitem(__import__("sys").modules, "firebase_admin", firebase)
    monkeypatch.setitem(__import__("sys").modules, "firebase_admin.messaging", messaging)
    monkeypatch.setattr(push_service, "_firebase_app", lambda: object())
    return sent, control


def _register(api, auth, token, installation_id=None, platform="ANDROID"):
    response = api.put(
        "/notificaciones/dispositivos",
        headers=auth,
        json={
            "id_instalacion": installation_id or f"installation-{token[-16:]}",
            "token": token,
            "plataforma": platform,
        },
    )
    assert response.status_code == 200, response.text


def _create_booking(world, table_id, suffix):
    fecha = (date.today() + timedelta(days=30)).isoformat()
    return world["api"].post("/reservas", headers=world["tokens"]["client"], json={
        "id_restaurante": world["restaurant_id"],
        "id_area": world["area_id"],
        "fecha_reserva": fecha,
        "hora_inicio": "14:00:00",
        "hora_fin": "16:00:00",
        "cantidad_personas": 2,
        "mesas": [table_id],
        "observaciones": suffix,
    })


def test_device_token_is_transferred_and_revoked_only_by_current_owner(world):
    api, tokens = world["api"], world["tokens"]
    installation_id = "installation-shared-device-0001"
    _register(api, tokens["client"], "fcm_test_device_token_abcdefghijklmnopqrstuvwxyz", installation_id)
    device_token = "fcm_test_device_token_rotated_abcdefghijklmnopqrstuvwxyz"
    _register(api, tokens["client"], device_token, installation_id)
    _register(api, tokens["restaurant"], device_token, installation_id)

    with SessionLocal() as db:
        device = db.query(DispositivoPush).filter_by(token_fcm=device_token).one()
        restaurant_id = db.query(Usuario).filter_by(correo="test-restaurant@example.com").one().id_usuario
        client_id = db.query(Usuario).filter_by(correo="test-client@example.com").one().id_usuario
        assert device.id_usuario == restaurant_id
        assert device.id_usuario != client_id
        assert db.query(DispositivoPush).filter_by(id_instalacion=installation_id).count() == 1

    api.post("/notificaciones/dispositivos/revocar", headers=tokens["client"], json={"id_instalacion": installation_id})
    with SessionLocal() as db:
        assert db.query(DispositivoPush).filter_by(token_fcm=device_token).count() == 1

    response = api.post("/notificaciones/dispositivos/revocar", headers=tokens["restaurant"], json={"id_instalacion": installation_id})
    assert response.status_code == 200
    with SessionLocal() as db:
        assert db.query(DispositivoPush).filter_by(token_fcm=device_token).count() == 0


def test_registering_device_recovers_recent_events_without_recipients(world, monkeypatch):
    sent, _ = _fake_firebase(monkeypatch)
    api, tokens = world["api"], world["tokens"]
    table = api.post(f"/areas/{world['area_id']}/mesas", headers=tokens["restaurant"], json={
        "numero": "PUSH-LATE-DEVICE", "capacidad": 4, "es_fija": False, "combinable": True,
    })
    assert table.status_code == 201, table.text

    booking = _create_booking(world, table.json()["id_mesa"], "push-late-device")
    assert booking.status_code == 201, booking.text
    reservation_id = booking.json()["id_reserva"]
    with SessionLocal() as db:
        confirmed = db.query(NotificacionOutbox).filter_by(
            clave_evento=f"reservation.confirmed:{reservation_id}"
        ).one()
        created = db.query(NotificacionOutbox).filter_by(
            clave_evento=f"reservation.created:{reservation_id}"
        ).one()
        assert confirmed.estado == "SIN_DESTINATARIOS"
        assert created.estado == "SIN_DESTINATARIOS"

    client_device = "fcm_late_client_device_token_000011"
    _register(api, tokens["client"], client_device)
    assert [message.tokens for message in sent] == [[client_device]]
    with SessionLocal() as db:
        confirmed = db.query(NotificacionOutbox).filter_by(
            clave_evento=f"reservation.confirmed:{reservation_id}"
        ).one()
        created = db.query(NotificacionOutbox).filter_by(
            clave_evento=f"reservation.created:{reservation_id}"
        ).one()
        assert confirmed.estado == "ENVIADA"
        assert confirmed.intentos == 1
        assert confirmed.dispositivos_enviados
        assert created.estado == "SIN_DESTINATARIOS"


def test_five_business_events_are_private_and_idempotent(world, monkeypatch):
    sent, _ = _fake_firebase(monkeypatch)
    api, tokens = world["api"], world["tokens"]
    restaurant_device = "fcm_restaurant_owner_device_token_000001"
    other_restaurant_device = "fcm_other_restaurant_device_token_000002"
    client_device = "fcm_client_owner_device_token_000003"
    _register(api, tokens["restaurant"], restaurant_device)
    _register(api, tokens["restaurant_2"], other_restaurant_device)
    _register(api, tokens["client"], client_device)

    # 1) La reserva nueva llega al responsable del restaurante, nunca al otro local.
    table = api.post(f"/areas/{world['area_id']}/mesas", headers=tokens["restaurant"], json={
        "numero": "PUSH-1", "capacidad": 4, "es_fija": False, "combinable": True,
    })
    assert table.status_code == 201, table.text
    booking = _create_booking(world, table.json()["id_mesa"], "push-create")
    assert booking.status_code == 201, booking.text
    assert [message.tokens for message in sent] == [[restaurant_device], [client_device]]
    reservation_id = booking.json()["id_reserva"]

    # El flujo habitual crea CONFIRMADA; colocarla PENDIENTE en fixture permite probar
    # la transición que existe para reservas importadas/pendientes sin cambiar reglas.
    with SessionLocal() as db:
        db.query(Reserva).filter_by(id_reserva=reservation_id).update({"estado": "PENDIENTE"})
        db.commit()
    confirmed = api.patch(f"/reservas/{reservation_id}/estado", headers=tokens["restaurant"], json={"estado": "CONFIRMADA"})
    assert confirmed.status_code == 200, confirmed.text
    assert len(sent) == 2  # La reserva ya se confirmó al crearse; el evento es único.
    assert api.get(f"/reservas/{reservation_id}", headers=tokens["guest"]).status_code == 403

    # Cancelación por cliente notifica al restaurante, sin publicar al tema de promociones.
    table2 = api.post(f"/areas/{world['area_id']}/mesas", headers=tokens["restaurant"], json={
        "numero": "PUSH-2", "capacidad": 4, "es_fija": False, "combinable": True,
    })
    booking2 = _create_booking(world, table2.json()["id_mesa"], "push-cancel")
    assert booking2.status_code == 201, booking2.text
    cancelled = api.patch(f"/reservas/{booking2.json()['id_reserva']}/cancelar", headers=tokens["client"], json={})
    assert cancelled.status_code == 200, cancelled.text
    assert sent[-1].tokens == [restaurant_device]

    dish = api.post(f"/restaurantes/{world['restaurant_id']}/platos", headers=tokens["restaurant"], json={
        "nombre": "Push meal", "precio": "15.00", "disponible": True,
        "personas_cubiertas": 1, "id_categoria": world["category_id"],
    })
    assert dish.status_code == 201, dish.text
    order = api.post("/pedidos", headers=tokens["client"], json={
        "id_restaurante": world["restaurant_id"],
        "detalles": [{"id_plato": dish.json()["id_plato"], "cantidad": 1}],
    })
    assert order.status_code == 201, order.text
    assert sent[-1].tokens == [restaurant_device]
    order_id = order.json()["id_pedido"]
    for state in ("ACEPTADO", "EN_PREPARACION", "LISTO"):
        response = api.patch(f"/pedidos/{order_id}/estado", headers=tokens["restaurant"], json={"estado": state})
        assert response.status_code == 200, response.text
    assert sent[-1].tokens == [client_device]
    assert api.get(f"/pedidos/{order_id}", headers=tokens["guest"]).status_code == 403

    # Un despacho repetido del mismo outbox ya enviado no vuelve a llamar FCM.
    with SessionLocal() as db:
        evento = db.query(NotificacionOutbox).filter_by(clave_evento=f"order.ready:{order_id}").one()
        notification_id = evento.id_notificacion
        assert evento.estado == "ENVIADA"
    send_count = len(sent)
    push_service.enviar_evento_notificacion(notification_id)
    assert len(sent) == send_count
    assert [message.tokens for message in sent] == [
        [restaurant_device], [client_device], [restaurant_device], [client_device],
        [restaurant_device], [restaurant_device], [client_device],
    ]


def test_firebase_failure_does_not_rollback_reservation(world, monkeypatch):
    _, control = _fake_firebase(monkeypatch, fail=True)
    table = world["api"].post(f"/areas/{world['area_id']}/mesas", headers=world["tokens"]["restaurant"], json={
        "numero": "PUSH-FAIL", "capacidad": 4, "es_fija": False, "combinable": True,
    })
    assert table.status_code == 201, table.text
    _register(world["api"], world["tokens"]["restaurant"], "fcm_restaurant_failure_test_token_004")
    booking = _create_booking(world, table.json()["id_mesa"], "push-failure")
    assert booking.status_code == 201, booking.text
    with SessionLocal() as db:
        evento = db.query(NotificacionOutbox).filter_by(
            clave_evento=f"reservation.created:{booking.json()['id_reserva']}"
        ).one()
        assert evento.estado == "FALLIDA"
        assert "RuntimeError" in evento.error_envio
        notification_id = evento.id_notificacion

    # La reserva persiste a pesar del fallo, y un administrador puede reintentar
    # el mismo evento outbox cuando Firebase vuelve a estar disponible.
    control.fail = False
    retried = world["api"].post(
        f"/notificaciones/outbox/{notification_id}/reintentar",
        headers=world["tokens"]["admin"],
    )
    assert retried.status_code == 202, retried.text
    assert retried.json() == {"programada": True}
    with SessionLocal() as db:
        evento = db.query(NotificacionOutbox).filter_by(id_notificacion=notification_id).one()
        assert evento.estado == "ENVIADA"
        assert evento.intentos == 2
    calls = control.calls
    duplicate = world["api"].post(
        f"/notificaciones/outbox/{notification_id}/reintentar",
        headers=world["tokens"]["admin"],
    )
    assert duplicate.status_code == 202
    assert duplicate.json() == {"programada": False}
    assert control.calls == calls


def test_outbox_retry_requires_admin_and_preserves_tenant_isolation(world, monkeypatch):
    sent, _ = _fake_firebase(monkeypatch, fail=True)
    _register(world["api"], world["tokens"]["restaurant"], "fcm_restaurant_isolated_token_0005")
    _register(world["api"], world["tokens"]["restaurant_2"], "fcm_other_restaurant_isolated_token_0006")
    table = world["api"].post(f"/areas/{world['area_id']}/mesas", headers=world["tokens"]["restaurant"], json={
        "numero": "PUSH-TENANT", "capacidad": 4, "es_fija": False, "combinable": True,
    })
    booking = _create_booking(world, table.json()["id_mesa"], "push-tenant")
    with SessionLocal() as db:
        event = db.query(NotificacionOutbox).filter_by(
            clave_evento=f"reservation.created:{booking.json()['id_reserva']}"
        ).one()
        event_id = event.id_notificacion
        assert event.estado == "FALLIDA"

    assert world["api"].post(f"/notificaciones/outbox/{event_id}/reintentar", headers=world["tokens"]["restaurant"]).status_code == 403
    other_event = world["api"].post(f"/notificaciones/outbox/999999/reintentar", headers=world["tokens"]["admin"])
    assert other_event.status_code == 404
    assert sent == []


def test_restaurant_web_tokens_receive_only_their_establishments(world, monkeypatch):
    sent, _ = _fake_firebase(monkeypatch)
    restaurant_web = "fcm_restaurant_web_panel_token_000007"
    other_web = "fcm_other_restaurant_web_panel_token_000008"
    _register(world["api"], world["tokens"]["restaurant"], restaurant_web, platform="WEB")
    _register(world["api"], world["tokens"]["restaurant_2"], other_web, platform="WEB")
    with SessionLocal() as db:
        device = db.query(DispositivoPush).filter_by(token_fcm=restaurant_web).one()
        assert device.plataforma == "WEB"

    table = world["api"].post(f"/areas/{world['area_id']}/mesas", headers=world["tokens"]["restaurant"], json={
        "numero": "PUSH-WEB", "capacidad": 4, "es_fija": False, "combinable": True,
    })
    booking = _create_booking(world, table.json()["id_mesa"], "push-web")
    assert booking.status_code == 201, booking.text
    assert [message.tokens for message in sent] == [[restaurant_web]]


def test_partial_firebase_retry_skips_devices_already_accepted(world, monkeypatch):
    sent, control = _fake_firebase(monkeypatch)
    already_delivered = "fcm_restaurant_delivered_token_000009"
    temporarily_failed = "fcm_restaurant_retry_token_000010"
    _register(world["api"], world["tokens"]["restaurant"], already_delivered)
    _register(world["api"], world["tokens"]["restaurant"], temporarily_failed)
    control.failure_tokens.add(temporarily_failed)

    table = world["api"].post(f"/areas/{world['area_id']}/mesas", headers=world["tokens"]["restaurant"], json={
        "numero": "PUSH-PARTIAL", "capacidad": 4, "es_fija": False, "combinable": True,
    })
    booking = _create_booking(world, table.json()["id_mesa"], "push-partial")
    assert booking.status_code == 201, booking.text
    with SessionLocal() as db:
        event = db.query(NotificacionOutbox).filter_by(
            clave_evento=f"reservation.created:{booking.json()['id_reserva']}"
        ).one()
        event_id = event.id_notificacion
        assert event.estado == "FALLIDA"
        assert len(event.dispositivos_enviados) == 1

    control.failure_tokens.clear()
    retry = world["api"].post(
        f"/notificaciones/outbox/{event_id}/reintentar", headers=world["tokens"]["admin"]
    )
    assert retry.status_code == 202
    assert retry.json() == {"programada": True}
    assert set(sent[0].tokens) == {already_delivered, temporarily_failed}
    assert sent[1].tokens == [temporarily_failed]
    with SessionLocal() as db:
        event = db.query(NotificacionOutbox).filter_by(id_notificacion=event_id).one()
        assert event.estado == "ENVIADA"
        assert len(event.dispositivos_enviados) == 2
