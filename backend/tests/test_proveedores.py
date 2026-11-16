"""Pruebas funcionales y de seguridad para CU09 - Gestionar proveedores."""
import pytest
from fastapi.testclient import TestClient


def test_proveedores_permisos_y_creacion(api: TestClient, world):
    """
    Verifica que ADMINISTRADOR_TIENDA y ADMINISTRADOR puedan gestionar tiendas/proveedores,
    mientras que CLIENTE o anónimo sean rechazados.
    """
    token_tienda = world["tokens"]["tienda"]
    token_admin = world["tokens"]["admin"]
    token_cliente = world["tokens"]["client"]

    # 1. Petición sin autenticación -> 401
    resp_anon = api.get("/lugares-compra/mis-tiendas")
    assert resp_anon.status_code == 401

    # 2. Petición con rol CLIENTE -> 403
    resp_cliente = api.get("/lugares-compra/mis-tiendas", headers=token_cliente)
    assert resp_cliente.status_code == 403

    # 3. Rol ADMINISTRADOR_TIENDA puede crear su tienda
    crear_payload = {
        "nombre": "Mercado Abasto Norte",
        "tipo": "MERCADO",
        "descripcion": "Puesto de verduras y lácteos",
        "telefono": "71122334",
        "ubicacion": {
            "direccion": "Av. Circunvalación #450",
            "ciudad": "Santa Cruz",
            "latitud": -17.7833,
            "longitud": -63.1821
        }
    }
    resp_crear = api.post("/lugares-compra", headers=token_tienda, json=crear_payload)
    assert resp_crear.status_code == 201
    tienda = resp_crear.json()
    assert tienda["nombre"] == "Mercado Abasto Norte"
    id_tienda = tienda["id_lugar_compra"]

    # 4. Listar mis tiendas como ADMINISTRADOR_TIENDA
    resp_mis = api.get("/lugares-compra/mis-tiendas", headers=token_tienda)
    assert resp_mis.status_code == 200
    mis_tiendas = resp_mis.json()
    assert any(t["id_lugar_compra"] == id_tienda for t in mis_tiendas)


def test_proveedores_gestion_precios_ingredientes(api: TestClient, world):
    """
    Verifica la asociación de ingredientes y actualización de precios unitarios.
    """
    token_tienda = world["tokens"]["tienda"]
    token_admin = world["tokens"]["admin"]

    # Crear ingrediente primero como admin
    resp_ing = api.post("/ingredientes", headers=token_admin, json={
        "nombre": "Tomate Pera Fresco",
        "unidad_medida": "kg",
        "costo_unitario": 8.5
    })
    assert resp_ing.status_code == 201
    id_ing = resp_ing.json()["id_ingrediente"]

    # Crear tienda como admin_tienda
    resp_tienda = api.post("/lugares-compra", headers=token_tienda, json={
        "nombre": "Fruver La Huertita",
        "tipo": "TIENDA",
        "ubicacion": {"direccion": "Calle Sucre #100", "ciudad": "Cochabamba"}
    })
    assert resp_tienda.status_code == 201
    id_tienda = resp_tienda.json()["id_lugar_compra"]

    # Asociar ingrediente y precio al comercio
    resp_asoc = api.post(f"/lugares-compra/{id_tienda}/ingredientes", headers=token_tienda, json={
        "id_ingrediente": id_ing,
        "precio": 7.50,
        "cantidad_referencia": 1.0,
        "unidad_medida": "kg",
        "disponible": True
    })
    assert resp_asoc.status_code == 201
    asoc_data = resp_asoc.json()
    assert float(asoc_data["precio"]) == 7.50

    # Actualizar precio
    resp_upd = api.put(f"/lugares-compra/{id_tienda}/ingredientes/{id_ing}", headers=token_tienda, json={
        "precio": 7.00,
        "cantidad_referencia": 1.0,
        "unidad_medida": "kg",
        "disponible": True
    })
    assert resp_upd.status_code == 200
    assert float(resp_upd.json()["precio"]) == 7.00

    # Eliminar asociación
    resp_del = api.delete(f"/lugares-compra/{id_tienda}/ingredientes/{id_ing}", headers=token_tienda)
    assert resp_del.status_code == 200


def test_proveedores_asociar_ingrediente_manual(api: TestClient, world):
    """
    Verifica que se pueda registrar un ingrediente manualmente por su nombre,
    creándolo automáticamente en el catálogo si aún no existía.
    """
    token_tienda = world["tokens"]["tienda"]

    # Crear tienda
    resp_tienda = api.post("/lugares-compra", headers=token_tienda, json={
        "nombre": "Distribuidora Los Valles",
        "tipo": "DISTRIBUIDOR",
        "ubicacion": {"direccion": "Km 6 Doble Vía", "ciudad": "Santa Cruz"}
    })
    assert resp_tienda.status_code == 201
    id_tienda = resp_tienda.json()["id_lugar_compra"]

    # Asociar ingrediente ingresado MANUALMENTE por nombre
    resp_manual = api.post(f"/lugares-compra/{id_tienda}/ingredientes", headers=token_tienda, json={
        "nombre_ingrediente": "Pimienta Negra en Grano",
        "precio": 15.00,
        "cantidad_referencia": 1.0,
        "unidad_medida": "bolsa 250g",
        "disponible": True
    })
    assert resp_manual.status_code == 201
    data = resp_manual.json()
    assert data["nombre_ingrediente"] == "Pimienta Negra en Grano"
    assert float(data["precio"]) == 15.00

    # Si se vuelve a enviar con el mismo nombre y nuevo precio, se actualiza sin conflicto
    resp_upd_manual = api.post(f"/lugares-compra/{id_tienda}/ingredientes", headers=token_tienda, json={
        "nombre_ingrediente": "Pimienta Negra en Grano",
        "precio": 14.50,
        "cantidad_referencia": 1.0,
        "unidad_medida": "bolsa 250g",
        "disponible": True
    })
    assert resp_upd_manual.status_code == 201
    assert float(resp_upd_manual.json()["precio"]) == 14.50

