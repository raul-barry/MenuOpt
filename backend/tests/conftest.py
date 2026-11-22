import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.database.base import Base
from app.database.conexion import engine, SessionLocal
from app.config.settings import settings
from app.main import app
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.security.contrasenas import generar_hash_contrasena


@pytest.fixture(autouse=True)
def clean_isolated_database():
    # This suite must run only with DATABASE_URL pointing at the dedicated test DB.
    if not settings.sqlalchemy_database_url.endswith("/menuopt_test_db"):
        pytest.fail("Refusing to truncate a database other than menuopt_test_db")
    table_names = [table.name for table in reversed(Base.metadata.sorted_tables)]
    if table_names:
        quoted = ", ".join(f'"{name}"' for name in table_names)
        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))
    with SessionLocal() as db:
        roles = {name: Rol(nombre=name, activo=True) for name in ("ADMINISTRADOR", "RESTAURANTE", "CLIENTE", "ADMINISTRADOR_TIENDA")}
        db.add_all(roles.values())
        db.flush()
        for email, names, role in (
            ("test-admin@example.com", ("Test", "Admin"), "ADMINISTRADOR"),
            ("test-restaurant@example.com", ("Test", "Restaurant"), "RESTAURANTE"),
            ("test-restaurant-2@example.com", ("Other", "Restaurant"), "RESTAURANTE"),
            ("test-client@example.com", ("Test", "Client"), "CLIENTE"),
            ("test-guest@example.com", ("Test", "Guest"), "CLIENTE"),
            ("test-unlinked@example.com", ("Unlinked", "Client"), "CLIENTE"),
            ("test-tienda@example.com", ("Test", "Tienda"), "ADMINISTRADOR_TIENDA"),
        ):
            db.add(Usuario(
                nombres=names[0], apellidos=names[1], correo=email,
                contrasena_hash=generar_hash_contrasena("TestPass123!"),
                estado="ACTIVO", id_rol=roles[role].id_rol,
            ))
        db.commit()
    yield
    with engine.begin() as connection:
        if table_names:
            quoted = ", ".join(f'"{name}"' for name in table_names)
            connection.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE"))


@pytest.fixture
def api():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def world(api):
    tokens = {}
    for role, email in (
        ("admin", "test-admin@example.com"),
        ("restaurant", "test-restaurant@example.com"),
        ("restaurant_2", "test-restaurant-2@example.com"),
        ("client", "test-client@example.com"),
        ("guest", "test-guest@example.com"),
        ("unlinked", "test-unlinked@example.com"),
        ("tienda", "test-tienda@example.com"),
    ):
        response = api.post("/autenticacion/login", json={"correo": email, "contrasena": "TestPass123!"})
        assert response.status_code == 200, response.text
        tokens[role] = {"Authorization": f"Bearer {response.json()['access_token']}"}

    restaurant = api.post("/restaurantes", headers=tokens["restaurant"], json={
        "nombre": "Test Kitchen",
        "ubicacion": {"direccion": "123 Test Avenue", "ciudad": "Santa Cruz"},
    })
    assert restaurant.status_code == 201, restaurant.text
    restaurant_id = restaurant.json()["id_restaurante"]

    category = api.post("/categorias", headers=tokens["admin"], json={"nombre": "Test Category"})
    assert category.status_code == 201, category.text
    category_id = category.json()["id_categoria"]

    area = api.post(f"/restaurantes/{restaurant_id}/areas", headers=tokens["restaurant"], json={"nombre": "Main Hall"})
    assert area.status_code == 201, area.text
    area_id = area.json()["id_area"]

    return {"api": api, "tokens": tokens, "restaurant_id": restaurant_id,
            "category_id": category_id, "area_id": area_id,
            # Compatibilidad para suites heredadas que leen tokens por clave directa.
            "admin": tokens["admin"], "client": tokens["client"],
            "restaurant": tokens["restaurant"]}


def create_table(world, number, capacity, *, fixed=False, combinable=True):
    response = world["api"].post(
        f"/areas/{world['area_id']}/mesas", headers=world["tokens"]["restaurant"],
        json={"numero": number, "capacidad": capacity, "es_fija": fixed, "combinable": combinable},
    )
    assert response.status_code == 201, response.text
    return response.json()["id_mesa"]


def create_booking(world, mesa_ids, *, people, start="14:00:00", end="16:00:00", token="client", date_offset=20):
    from datetime import date, timedelta
    date_value = (date.today() + timedelta(days=date_offset)).isoformat()
    response = world["api"].post("/reservas", headers=world["tokens"][token], json={
        "id_restaurante": world["restaurant_id"], "id_area": world["area_id"],
        "fecha_reserva": date_value, "hora_inicio": start, "hora_fin": end,
        "cantidad_personas": people, "mesas": mesa_ids,
    })
    return response
