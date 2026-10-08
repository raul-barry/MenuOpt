from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


def create_table(world, number, capacity, *, fixed=False, combinable=True):
    response = world["api"].post(
        f"/areas/{world['area_id']}/mesas", headers=world["tokens"]["restaurant"],
        json={"numero": number, "capacidad": capacity, "es_fija": fixed, "combinable": combinable},
    )
    assert response.status_code == 201, response.text
    return response.json()["id_mesa"]


def create_booking(world, mesa_ids, *, people, start="14:00:00", end="16:00:00", token="client", date_offset=20):
    date_value = (date.today() + timedelta(days=date_offset)).isoformat()
    return world["api"].post("/reservas", headers=world["tokens"][token], json={
        "id_restaurante": world["restaurant_id"], "id_area": world["area_id"],
        "fecha_reserva": date_value, "hora_inicio": start, "hora_fin": end,
        "cantidad_personas": people, "mesas": mesa_ids,
    })


def test_authentication_permissions_restaurant_and_menu(world):
    api, tokens = world["api"], world["tokens"]
    assert api.get(f"/restaurantes/{world['restaurant_id']}/platos").status_code == 401
    assert api.get("/usuarios", headers=tokens["client"]).status_code == 403
    assert api.post("/restaurantes", headers=tokens["client"], json={
        "nombre": "Unauthorized", "ubicacion": {"direccion": "123 Test Avenue", "ciudad": "Santa Cruz"},
    }).status_code == 403

    dish = api.post(f"/restaurantes/{world['restaurant_id']}/platos", headers=tokens["restaurant"], json={
        "nombre": "Soup", "precio": "12.50", "disponible": True,
        "personas_cubiertas": 1, "id_categoria": world["category_id"],
    })
    assert dish.status_code == 201, dish.text
    assert api.get(f"/restaurantes/{world['restaurant_id']}/platos", headers=tokens["client"]).json()[0]["nombre"] == "Soup"
    assert api.post(f"/restaurantes/{world['restaurant_id']}/platos", headers=tokens["restaurant_2"], json={
        "nombre": "Foreign Dish", "precio": 9, "id_categoria": world["category_id"],
    }).status_code == 403


def test_individual_combined_capacity_and_time_conflicts(world):
    individual = create_table(world, "T1", 4)
    too_large = create_table(world, "T2", 5)
    left = create_table(world, "T3", 2)
    right = create_table(world, "T4", 2)

    date_value = (date.today() + timedelta(days=20)).isoformat()
    availability = world["api"].get(
        f"/restaurantes/{world['restaurant_id']}/mesas-disponibles",
        headers=world["tokens"]["client"],
        params={"id_area": world["area_id"], "fecha": date_value,
                "hora_inicio": "14:00:00", "hora_fin": "16:00:00", "cantidad_personas": 2},
    )
    assert availability.status_code == 200, availability.text
    too_large_option = next(m for m in availability.json()["mesas"] if m["id_mesa"] == too_large)
    assert too_large_option["estado_disponibilidad"] == "NO_COMPATIBLE"
    assert too_large_option["seleccionable"] is False

    assert create_booking(world, [individual], people=2).status_code == 201
    assert create_booking(world, [too_large], people=2).status_code == 400

    combo = world["api"].post(f"/areas/{world['area_id']}/combinaciones", headers=world["tokens"]["restaurant"], json={
        "id_mesa_origen": right, "id_mesa_destino": left, "descripcion": "Adjacent tables",
    })
    assert combo.status_code == 201, combo.text
    combined_booking = create_booking(world, [left, right], people=3)
    assert combined_booking.status_code == 201, combined_booking.text

    overlap = create_booking(world, [individual], people=2, start="15:00:00", end="17:00:00", token="guest")
    assert overlap.status_code == 409, overlap.text
    touching = create_booking(world, [individual], people=2, start="16:00:00", end="17:00:00", token="guest")
    assert touching.status_code == 201, touching.text

    too_large_combo = create_booking(world, [left, right], people=1, start="18:00:00", end="19:00:00")
    assert too_large_combo.status_code == 400, too_large_combo.text


def test_concurrent_requests_cannot_double_book_same_table(world):
    table_id = create_table(world, "CONCURRENT", 4)
    barrier = Barrier(2)

    def reserve(token):
        barrier.wait(timeout=10)
        return create_booking(world, [table_id], people=2, token=token).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(reserve, ("client", "guest")))
    assert sorted(results) == [201, 409]


def test_reservation_orders_authorize_only_holder_and_registered_guest(world):
    api, tokens = world["api"], world["tokens"]
    dish = api.post(f"/restaurantes/{world['restaurant_id']}/platos", headers=tokens["restaurant"], json={
        "nombre": "Shared Meal", "precio": "18.25", "disponible": True,
        "personas_cubiertas": 1, "id_categoria": world["category_id"],
    })
    assert dish.status_code == 201, dish.text
    dish_id = dish.json()["id_plato"]

    table_id = create_table(world, "ORDER-GUEST", 4)
    reservation = create_booking(world, [table_id], people=2)
    assert reservation.status_code == 201, reservation.text

    users_response = api.get("/usuarios", headers=tokens["admin"], params={"limite": 100})
    assert users_response.status_code == 200, users_response.text
    user_ids = {user["correo"]: user["id_usuario"] for user in users_response.json()["usuarios"]}
    reservation_id = reservation.json()["id_reserva"]
    invite = api.post(f"/reservas/{reservation_id}/invitados", headers=tokens["client"], json={
        "id_usuario": user_ids["test-guest@example.com"],
    })
    assert invite.status_code == 201, invite.text

    holder_order = api.post("/pedidos", headers=tokens["client"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation.json()["id_reserva"],
        "detalles": [{"id_plato": dish_id, "cantidad": 1}],
    })
    assert holder_order.status_code == 201, holder_order.text
    assert holder_order.json()["id_usuario"] == user_ids["test-client@example.com"]

    linked_guest_order = api.post("/pedidos", headers=tokens["guest"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": dish_id, "cantidad": 1}],
    })
    assert linked_guest_order.status_code == 201, linked_guest_order.text
    assert linked_guest_order.json()["id_usuario"] == user_ids["test-guest@example.com"]

    unlinked_guest_order = api.post("/pedidos", headers=tokens["unlinked"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": dish_id, "cantidad": 1}],
    })
    assert unlinked_guest_order.status_code == 403

    impersonation = api.post("/pedidos", headers=tokens["guest"], json={
        "id_restaurante": world["restaurant_id"], "id_reserva": reservation_id,
        "id_usuario": user_ids["test-client@example.com"],
        "detalles": [{"id_plato": dish_id, "cantidad": 1}],
    })
    assert impersonation.status_code == 422

    other_restaurant = api.post("/restaurantes", headers=tokens["restaurant_2"], json={
        "nombre": "Other Kitchen",
        "ubicacion": {"direccion": "456 Test Avenue", "ciudad": "Santa Cruz"},
    })
    assert other_restaurant.status_code == 201, other_restaurant.text
    wrong_restaurant_order = api.post("/pedidos", headers=tokens["guest"], json={
        "id_restaurante": other_restaurant.json()["id_restaurante"], "id_reserva": reservation_id,
        "detalles": [{"id_plato": dish_id, "cantidad": 1}],
    })
    assert wrong_restaurant_order.status_code == 400

    # Independent orders remain available and visible only to each account.
    orders = []
    for guest in ("client", "guest"):
        response = api.post("/pedidos", headers=tokens[guest], json={
            "id_restaurante": world["restaurant_id"],
            "detalles": [{"id_plato": dish_id, "cantidad": 1}],
        })
        assert response.status_code == 201, response.text
        orders.append(response.json())

    assert orders[0]["id_pedido"] != orders[1]["id_pedido"]
    assert orders[0]["id_usuario"] != orders[1]["id_usuario"]
    assert all(float(order["total"]) == 18.25 for order in orders)
    expected_orders = {
        "client": {holder_order.json()["id_pedido"], orders[0]["id_pedido"]},
        "guest": {linked_guest_order.json()["id_pedido"], orders[1]["id_pedido"]},
    }
    for guest in ("client", "guest"):
        history = api.get("/pedidos/mis-pedidos", headers=tokens[guest])
        assert history.status_code == 200
        assert {item["id_pedido"] for item in history.json()} == expected_orders[guest]
