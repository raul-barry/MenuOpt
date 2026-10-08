from datetime import date, timedelta


def create_table(world, number, capacity):
    response = world["api"].post(
        f"/areas/{world['area_id']}/mesas", headers=world["tokens"]["restaurant"],
        json={"numero": number, "capacidad": capacity, "es_fija": False, "combinable": True},
    )
    assert response.status_code == 201, response.text
    return response.json()["id_mesa"]


def create_booking(world, mesa_ids, *, people, token="client", date_offset=20):
    return world["api"].post("/reservas", headers=world["tokens"][token], json={
        "id_restaurante": world["restaurant_id"], "id_area": world["area_id"],
        "fecha_reserva": (date.today() + timedelta(days=date_offset)).isoformat(),
        "hora_inicio": "14:00:00", "hora_fin": "16:00:00",
        "cantidad_personas": people, "mesas": mesa_ids,
    })


def _user_ids(world):
    response = world["api"].get("/usuarios", headers=world["tokens"]["admin"], params={"limite": 100})
    assert response.status_code == 200, response.text
    return {item["correo"]: item["id_usuario"] for item in response.json()["usuarios"]}


def _dish(world, name, price, *, restaurant_id=None, token="restaurant"):
    restaurant_id = restaurant_id or world["restaurant_id"]
    response = world["api"].post(
        f"/restaurantes/{restaurant_id}/platos",
        headers=world["tokens"][token],
        json={"nombre": name, "precio": str(price), "disponible": True,
              "personas_cubiertas": 1, "id_categoria": world["category_id"]},
    )
    assert response.status_code == 201, response.text
    return response.json()["id_plato"]


def test_order_details_can_be_assigned_to_reservation_guests(world):
    api, tokens = world["api"], world["tokens"]
    user_ids = _user_ids(world)
    dish_id = _dish(world, "Guest Meal", "10.50")
    other_dish_id = _dish(world, "Guest Dessert", "4.00")
    table_id = create_table(world, "DISH-GUESTS", 4)
    reservation = create_booking(world, [table_id], people=3)
    assert reservation.status_code == 201, reservation.text
    reservation_id = reservation.json()["id_reserva"]

    registered_invite = api.post(f"/reservas/{reservation_id}/invitados", headers=tokens["client"],
                                 json={"id_usuario": user_ids["test-guest@example.com"]})
    assert registered_invite.status_code == 201, registered_invite.text
    anonymous_invite = api.post(f"/reservas/{reservation_id}/invitados", headers=tokens["client"],
                                json={"nombre": "Walk-in Guest"})
    assert anonymous_invite.status_code == 201, anonymous_invite.text
    registered_id = registered_invite.json()["id_invitado"]
    anonymous_id = anonymous_invite.json()["id_invitado"]

    order = api.post("/pedidos", headers=tokens["client"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [
            # Un cliente que intente enviar un precio no altera el precio histórico.
            {"id_plato": dish_id, "cantidad": 1, "id_invitado": registered_id,
             "precio_unitario": "0.01"},
            {"id_plato": dish_id, "cantidad": 1, "id_invitado": registered_id},
            {"id_plato": dish_id, "cantidad": 1, "id_invitado": anonymous_id},
            {"id_plato": other_dish_id, "cantidad": 1, "id_invitado": registered_id},
        ],
    })
    assert order.status_code == 201, order.text
    result = order.json()
    assert float(result["total"]) == 35.50
    detail_by_guest_dish = {(line["id_plato"], line["id_invitado"]): line for line in result["detalles"]}
    assert set(detail_by_guest_dish) == {(dish_id, registered_id), (dish_id, anonymous_id), (other_dish_id, registered_id)}
    assert detail_by_guest_dish[(dish_id, registered_id)]["cantidad"] == 2
    assert float(detail_by_guest_dish[(dish_id, registered_id)]["subtotal"]) == 21.00
    assert float(detail_by_guest_dish[(dish_id, anonymous_id)]["subtotal"]) == 10.50
    assert float(detail_by_guest_dish[(other_dish_id, registered_id)]["subtotal"]) == 4.00
    assert detail_by_guest_dish[(dish_id, anonymous_id)]["nombre_invitado"] == "Walk-in Guest"

    # A registered guest without explicit assignments may order for their own guest record.
    own_order = api.post("/pedidos", headers=tokens["guest"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": dish_id, "cantidad": 1}],
    })
    assert own_order.status_code == 201, own_order.text
    own_detail = own_order.json()["detalles"][0]
    assert own_detail["id_invitado"] == registered_id
    assert own_detail["nombre_invitado"] == "Test Guest"

    # A registered invitee cannot assign an item to a different guest.
    forbidden_assignment = api.post("/pedidos", headers=tokens["guest"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": dish_id, "cantidad": 1, "id_invitado": anonymous_id}],
    })
    assert forbidden_assignment.status_code == 403

    # A reservation holder cannot assign a foreign reservation's invitee.
    second_table = create_table(world, "DISH-GUESTS-2", 2)
    second_reservation = create_booking(world, [second_table], people=2, token="unlinked", date_offset=21)
    assert second_reservation.status_code == 201, second_reservation.text
    foreign_invite = api.post(
        f"/reservas/{second_reservation.json()['id_reserva']}/invitados",
        headers=tokens["unlinked"], json={"nombre": "Foreign Invite"},
    )
    assert foreign_invite.status_code == 201, foreign_invite.text
    foreign_assignment = api.post("/pedidos", headers=tokens["client"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": dish_id, "cantidad": 1,
                      "id_invitado": foreign_invite.json()["id_invitado"]}],
    })
    assert foreign_assignment.status_code == 400

    # An unrelated account cannot create an order for this reservation.
    unauthorized_order = api.post("/pedidos", headers=tokens["unlinked"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": dish_id, "cantidad": 1, "id_invitado": registered_id}],
    })
    assert unauthorized_order.status_code == 403

    # A restaurant mismatch at the dish level is rejected, regardless of a valid guest.
    other_restaurant = api.post("/restaurantes", headers=tokens["restaurant_2"], json={
        "nombre": "Second Dish Kitchen",
        "ubicacion": {"direccion": "789 Test Avenue", "ciudad": "Santa Cruz"},
    })
    assert other_restaurant.status_code == 201, other_restaurant.text
    foreign_dish = _dish(world, "Foreign Dish", "99.00",
                         restaurant_id=other_restaurant.json()["id_restaurante"], token="restaurant_2")
    wrong_dish = api.post("/pedidos", headers=tokens["client"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": foreign_dish, "cantidad": 1, "id_invitado": registered_id}],
    })
    assert wrong_dish.status_code == 400

    # Assigned anonymous invitees cannot be deleted, preserving order attribution.
    cannot_remove_assigned_guest = api.delete(
        f"/reservas/{reservation_id}/invitados/{anonymous_id}", headers=tokens["client"]
    )
    assert cannot_remove_assigned_guest.status_code == 409


def test_independent_order_keeps_details_unassigned_and_backend_pricing(world):
    dish_id = _dish(world, "Standalone Meal", "7.25")
    response = world["api"].post("/pedidos", headers=world["tokens"]["client"], json={
        "id_restaurante": world["restaurant_id"],
        "detalles": [{"id_plato": dish_id, "cantidad": 2}],
    })
    assert response.status_code == 201, response.text
    result = response.json()
    assert float(result["total"]) == 14.50
    assert result["detalles"][0]["id_invitado"] is None
    assert float(result["detalles"][0]["subtotal"]) == 14.50
