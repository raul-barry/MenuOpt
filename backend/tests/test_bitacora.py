"""Pruebas funcionales y de seguridad para CU25 - Consultar bitácora del sistema."""
import pytest
from fastapi.testclient import TestClient
from app.services.bitacora_service import BitacoraService
from app.database.conexion import SessionLocal


def test_bitacora_seguridad_roles(api: TestClient, world):
    """
    Verifica que solo usuarios con rol ADMINISTRADOR puedan consultar la bitácora.
    """
    # 1. Petición sin autenticación -> 401
    resp_anon = api.get("/bitacora")
    assert resp_anon.status_code == 401

    # 2. Petición con rol CLIENTE -> 403
    resp_cliente = api.get("/bitacora", headers=world["client"])
    assert resp_cliente.status_code == 403

    # 3. Petición con rol RESTAURANTE -> 403
    resp_resto = api.get("/bitacora", headers=world["restaurant"])
    assert resp_resto.status_code == 403

    # 4. Petición con rol ADMINISTRADOR -> 200
    resp_admin = api.get("/bitacora", headers=world["admin"])
    assert resp_admin.status_code == 200
    datos = resp_admin.json()
    assert "total" in datos
    assert "items" in datos
    assert "total_paginas" in datos
    assert isinstance(datos["items"], list)


def test_bitacora_registro_y_filtros(api: TestClient, world):
    """
    Verifica el registro programático y el filtrado por módulo, acción y texto.
    """
    with SessionLocal() as db:
        BitacoraService.registrar_evento(
            db=db,
            accion="TEST_EVENTO_A",
            modulo="SEGURIDAD",
            descripcion="Descripción de prueba evento alfa",
            detalles={"ip": "127.0.0.1", "prueba": True}
        )
        BitacoraService.registrar_evento(
            db=db,
            accion="TEST_EVENTO_B",
            modulo="CONFIGURACION",
            descripcion="Descripción de prueba evento beta",
            detalles={"clave": "valor"}
        )

    # Filtrar por módulo SEGURIDAD
    resp_mod = api.get("/bitacora?modulo=SEGURIDAD", headers=world["admin"])
    assert resp_mod.status_code == 200
    items_mod = resp_mod.json()["items"]
    assert any(it["accion"] == "TEST_EVENTO_A" for it in items_mod)
    assert not any(it["accion"] == "TEST_EVENTO_B" for it in items_mod)

    # Filtrar por búsqueda textual "beta"
    resp_busq = api.get("/bitacora?busqueda=beta", headers=world["admin"])
    assert resp_busq.status_code == 200
    items_busq = resp_busq.json()["items"]
    assert any(it["accion"] == "TEST_EVENTO_B" for it in items_busq)
    assert not any(it["accion"] == "TEST_EVENTO_A" for it in items_busq)

    # Paginación
    resp_pag = api.get("/bitacora?pagina=1&limite=1", headers=world["admin"])
    assert resp_pag.status_code == 200
    datos_pag = resp_pag.json()
    assert datos_pag["limite"] == 1
    assert len(datos_pag["items"]) <= 1
    assert datos_pag["total_paginas"] >= 1
