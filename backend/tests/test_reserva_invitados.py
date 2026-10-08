from datetime import date, timedelta
from decimal import Decimal

from app.database.conexion import SessionLocal
from app.models.pedido import Pedido
from app.models.usuario import Usuario


def make_reservation(world, party_size=3):
    table_response = world["api"].post(
        f"/areas/{world['area_id']}/mesas",
        headers=world["tokens"]["restaurant"],
        json={"numero": "GUEST-TABLE", "capacidad": party_size},
    )
    assert table_response.status_code == 201, table_response.text
    response = world["api"].post("/reservas", headers=world["tokens"]["client"], json={
        "id_restaurante": world["restaurant_id"],
        "id_area": world["area_id"],
        "fecha_reserva": (date.today() + timedelta(days=30)).isoformat(),
        "hora_inicio": "17:00:00",
        "hora_fin": "19:00:00",
        "cantidad_personas": party_size,
        "mesas": [table_response.json()["id_mesa"]],
    })
    assert response.status_code == 201, response.text
    return response.json()["id_reserva"]


def guest_user_id(email="test-guest@example.com"):
    with SessionLocal() as db:
        return db.query(Usuario.id_usuario).filter(Usuario.correo == email).scalar()


def test_add_list_and_reject_duplicate_guests(world):
    api = world["api"]
    reservation_id = make_reservation(world)
    path = f"/reservas/{reservation_id}/invitados"

    anonymous = api.post(path, headers=world["tokens"]["client"], json={
        "nombre": "  Alex Invitado  ", "correo": "Alex.Invited@example.com",
    })
    assert anonymous.status_code == 201, anonymous.text
    anonymous_guest = anonymous.json()
    assert anonymous_guest["id_usuario"] is None
    assert anonymous_guest["nombre"] == "Alex Invitado"

    duplicate_email = api.post(path, headers=world["tokens"]["client"], json={
        "nombre": "Different Person", "correo": "alex.invited@EXAMPLE.com",
    })
    assert duplicate_email.status_code == 409

    anonymous_without_email = api.post(path, headers=world["tokens"]["client"], json={"nombre": "Sam Guest"})
    assert anonymous_without_email.status_code == 201, anonymous_without_email.text
    duplicate_name = api.post(path, headers=world["tokens"]["client"], json={"nombre": " sam guest "})
    assert duplicate_name.status_code == 409
    assert api.post(path, headers=world["tokens"]["client"], json={}).status_code == 422

    linked_id = guest_user_id()
    linked = api.post(path, headers=world["tokens"]["client"], json={"id_usuario": linked_id})
    assert linked.status_code == 201, linked.text
    assert linked.json()["id_usuario"] == linked_id
    assert linked.json()["correo"] == "test-guest@example.com"

    duplicate_user = api.post(path, headers=world["tokens"]["client"], json={"id_usuario": linked_id})
    assert duplicate_user.status_code == 409

    listed = api.get(path, headers=world["tokens"]["client"])
    assert listed.status_code == 200
    assert [guest["id_invitado"] for guest in listed.json()] == [
        anonymous_guest["id_invitado"], anonymous_without_email.json()["id_invitado"], linked.json()["id_invitado"]
    ]


def test_invite_limit_and_permission_checks(world):
    api = world["api"]
    reservation_id = make_reservation(world, party_size=1)
    path = f"/reservas/{reservation_id}/invitados"

    first = api.post(path, headers=world["tokens"]["client"], json={"nombre": "First Guest"})
    assert first.status_code == 201, first.text
    over_limit = api.post(path, headers=world["tokens"]["client"], json={"nombre": "Second Guest"})
    assert over_limit.status_code == 409

    assert api.get(path, headers=world["tokens"]["guest"]).status_code == 403
    assert api.post(path, headers=world["tokens"]["guest"], json={"nombre": "Unauthorized Guest"}).status_code == 403
    assert api.get(path, headers=world["tokens"]["restaurant_2"]).status_code == 403
    assert api.get(path, headers=world["tokens"]["restaurant"]).status_code == 200
    assert api.get("/reservas/999999/invitados", headers=world["tokens"]["client"]).status_code == 404
    assert api.post("/reservas/999999/invitados", headers=world["tokens"]["client"], json={"nombre": "Nobody"}).status_code == 404


def test_delete_guest_and_retain_guest_with_reservation_order(world):
    api = world["api"]
    reservation_id = make_reservation(world)
    path = f"/reservas/{reservation_id}/invitados"

    removable = api.post(path, headers=world["tokens"]["client"], json={"nombre": "Removable Guest"})
    assert removable.status_code == 201, removable.text
    deleted = api.delete(f"{path}/{removable.json()['id_invitado']}", headers=world["tokens"]["client"])
    assert deleted.status_code == 204

    linked_id = guest_user_id()
    linked = api.post(path, headers=world["tokens"]["client"], json={"id_usuario": linked_id})
    assert linked.status_code == 201, linked.text
    with SessionLocal() as db:
        db.add(Pedido(
            id_usuario=linked_id,
            id_restaurante=world["restaurant_id"],
            id_reserva=reservation_id,
            estado="PENDIENTE",
            total=Decimal("0.00"),
        ))
        db.commit()

    blocked = api.delete(f"{path}/{linked.json()['id_invitado']}", headers=world["tokens"]["client"])
    assert blocked.status_code == 409
    remaining = api.get(path, headers=world["tokens"]["client"])
    assert [guest["id_invitado"] for guest in remaining.json()] == [linked.json()["id_invitado"]]
