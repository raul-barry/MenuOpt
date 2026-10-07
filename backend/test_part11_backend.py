"""
Script de verificación integral de la PARTE 11:
CU23: Enviar pedido (validación de restaurante, platos activos/disponibles, precios históricos con Decimal, reserva opcional)
CU24: Gestionar pedidos (historial de cliente, detalle, cancelación de cliente sólo en PENDIENTE, transiciones de estado de restaurante, filtros, 403 entre restaurantes y clientes)
"""
import sys
import json
import time
from datetime import date, timedelta
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"
FECHA_FUTURA = (date.today() + timedelta(days=12)).isoformat()

def request(method, path, body=None, token=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            code = resp.getcode()
            res_data = resp.read().decode("utf-8")
            json_data = json.loads(res_data) if res_data else None
            return code, json_data
    except urllib.error.HTTPError as e:
        code = e.code
        res_data = e.read().decode("utf-8")
        try:
            json_data = json.loads(res_data)
        except Exception:
            json_data = res_data
        return code, json_data
    except Exception as e:
        return 500, str(e)

def log_test(num, name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] PRUEBA {num}: {name} - {detail}")
    if not passed:
        print(f"ERROR DETALLE: {detail}")
        sys.exit(1)

def run():
    print("=== INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - PARTE 11 (BACKEND) ===")

    # 1. Login usuarios
    c, r = request("POST", "/autenticacion/login", {"correo": "admin@menuopt.com", "contrasena": "Admin1234!"})
    log_test(1, "Login ADMIN", c == 200, f"code={c}")
    admin_token = r["access_token"]

    c, r = request("POST", "/autenticacion/login", {"correo": "restaurante@menuopt.com", "contrasena": "Resto1234*"})
    log_test(2, "Login RESTAURANTE 1", c == 200, f"code={c}")
    resto1_token = r["access_token"]

    c, r = request("POST", "/autenticacion/login", {"correo": "restaurante2@menuopt.com", "contrasena": "Resto1234*"})
    log_test(3, "Login RESTAURANTE 2", c == 200, f"code={c}")
    resto2_token = r["access_token"]

    c, r = request("POST", "/autenticacion/login", {"correo": "cliente1@menuopt.com", "contrasena": "Cliente1234*"})
    log_test(4, "Login CLIENTE 1", c == 200, f"code={c}")
    cliente1_token = r["access_token"]
    cliente1_id = r["usuario"]["id_usuario"]

    c, r = request("POST", "/autenticacion/login", {"correo": "cliente2@menuopt.com", "contrasena": "Cliente1234*"})
    log_test(5, "Login CLIENTE 2", c == 200, f"code={c}")
    cliente2_token = r["access_token"]

    # 2. Obtener Restaurante 1 y Restaurante 2 (o crearlo si restaurante 2 no tiene uno)
    c, mis_restos1 = request("GET", "/restaurantes/mis-restaurantes", token=resto1_token)
    id_resto1 = mis_restos1[0]["id_restaurante"]

    c, mis_restos2 = request("GET", "/restaurantes/mis-restaurantes", token=resto2_token)
    if c == 200 and len(mis_restos2) > 0:
        id_resto2 = mis_restos2[0]["id_restaurante"]
    else:
        # Registrar restaurante 2
        c, nuevo_r2 = request("POST", "/restaurantes", {
            "nombre": f"Restaurante Secundario P11 {int(time.time())}",
            "descripcion": "Restaurante para pruebas de aislamiento",
            "ubicacion": {
                "direccion": "Av. Secundaria 456",
                "ciudad": "Santa Cruz",
                "latitud": -17.7833,
                "longitud": -63.1821
            }
        }, token=resto2_token)
        id_resto2 = nuevo_r2["id_restaurante"]

    log_test(6, "Identificar Restaurantes de prueba", bool(id_resto1 and id_resto2), f"resto1={id_resto1}, resto2={id_resto2}")

    # Asegurar que Restaurante 2 tenga al menos una categoría y un plato
    c, platos2 = request("GET", f"/restaurantes/{id_resto2}/platos", token=cliente1_token)
    if not platos2:
        # Crear categoría y plato en resto 2
        c, cat2 = request("POST", "/categorias", {"nombre": f"Cat P11 {int(time.time())}"}, token=admin_token)
        id_cat2 = cat2["id_categoria"]
        c, nuevo_p2 = request("POST", f"/restaurantes/{id_resto2}/platos", {
            "nombre": "Plato Especial Resto 2",
            "precio": 45.0,
            "disponible": True,
            "personas_cubiertas": 1,
            "id_categoria": id_cat2
        }, token=resto2_token)
        platos2 = [nuevo_p2]

    # 3. Obtener platos de Restaurante 1 y Restaurante 2
    c, platos1 = request("GET", f"/restaurantes/{id_resto1}/platos", token=cliente1_token)
    log_test(7, "Listar platos Restaurante 1", c == 200 and len(platos1) >= 1, f"total_platos={len(platos1)}")
    # Seleccionar un plato activo y disponible de Restaurante 1
    platos1_disp = [p for p in platos1 if p.get("disponible") and p.get("estado") == "ACTIVO"]
    if not platos1_disp:
        # habilitar el primero
        request("PATCH", f"/platos/{platos1[0]['id_plato']}/disponibilidad", {"disponible": True}, token=resto1_token)
        platos1[0]["disponible"] = True
        platos1_disp = [platos1[0]]
    plato1_r1 = platos1_disp[0]
    id_plato1 = plato1_r1["id_plato"]
    precio_plato1 = float(plato1_r1["precio"])

    c, platos2 = request("GET", f"/restaurantes/{id_resto2}/platos", token=cliente1_token)
    log_test(8, "Listar platos Restaurante 2", c == 200 and len(platos2) >= 1, f"total_platos={len(platos2)}")
    plato1_r2 = platos2[0]
    id_plato_r2 = plato1_r2["id_plato"]

    # 4. CU23: Enviar pedido con platos de OTRO restaurante -> RECHAZAR (400)
    c, r = request("POST", "/pedidos", {
        "id_restaurante": id_resto1,
        "detalles": [
            {"id_plato": id_plato_r2, "cantidad": 2}
        ]
    }, token=cliente1_token)
    log_test(9, "CU23: Rechazar plato de otro restaurante (400)", c == 400, f"code={c}, resp={r}")

    # 5. CU23: Enviar pedido con cantidad <= 0 -> RECHAZAR (422 o 400)
    c, r = request("POST", "/pedidos", {
        "id_restaurante": id_resto1,
        "detalles": [
            {"id_plato": id_plato1, "cantidad": 0}
        ]
    }, token=cliente1_token)
    log_test(10, "CU23: Rechazar pedido con cantidad 0 (422)", c == 422, f"code={c}")

    # 6. CU23: Enviar pedido con plato inexistente -> RECHAZAR (404)
    c, r = request("POST", "/pedidos", {
        "id_restaurante": id_resto1,
        "detalles": [
            {"id_plato": 999999, "cantidad": 1}
        ]
    }, token=cliente1_token)
    log_test(11, "CU23: Rechazar pedido con plato inexistente (404)", c == 404, f"code={c}")

    # 7. CU23: Enviar pedido con reserva de OTRO restaurante -> RECHAZAR (400)
    # Crear una reserva válida para cliente1 en resto2
    # Primero obtener o crear área y mesa en resto2
    c, areas_r2 = request("GET", f"/restaurantes/{id_resto2}/areas", token=admin_token)
    if areas_r2:
        id_area_r2 = areas_r2[0]["id_area"]
        c, mesas_r2 = request("GET", f"/areas/{id_area_r2}/mesas", token=admin_token)
        if mesas_r2:
            id_mesa_r2 = mesas_r2[0]["id_mesa"]
        else:
            c, nm = request("POST", f"/areas/{id_area_r2}/mesas", {
                "numero": f"M-R2-{int(time.time())}", "capacidad": 4, "forma": "CUADRADA", "posicion_x": 0.5, "posicion_y": 0.5
            }, token=resto2_token)
            id_mesa_r2 = nm["id_mesa"]
    else:
        c, na = request("POST", f"/restaurantes/{id_resto2}/areas", {
            "nombre": f"Salón R2 {int(time.time())}", "ancho_mapa": 800, "alto_mapa": 600
        }, token=resto2_token)
        id_area_r2 = na["id_area"]
        c, nm = request("POST", f"/areas/{id_area_r2}/mesas", {
            "numero": f"M-R2-{int(time.time())}", "capacidad": 4, "forma": "CUADRADA", "posicion_x": 0.5, "posicion_y": 0.5
        }, token=resto2_token)
        id_mesa_r2 = nm["id_mesa"]
    # Crear mesa fresca en resto2 para evitar solapamiento entre ejecuciones de tests
    c, nm = request("POST", f"/areas/{id_area_r2}/mesas", {
        "numero": f"M-TEST-{int(time.time()*1000)%100000}", "capacidad": 4, "forma": "CUADRADA", "posicion_x": 0.5, "posicion_y": 0.5
    }, token=resto2_token)
    id_mesa_r2 = nm["id_mesa"]

    c, reserva_r2 = request("POST", "/reservas", {
        "id_restaurante": id_resto2,
        "id_area": id_area_r2,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "13:00:00",
        "hora_fin": "14:30:00",
        "cantidad_personas": 2,
        "mesas": [id_mesa_r2]
    }, token=cliente1_token)
    log_test(12, "Crear reserva en Restaurante 2 para prueba cruzada", c == 201, f"code={c}")
    id_reserva_r2 = reserva_r2["id_reserva"]

    # Intentar asociar reserva de resto2 a pedido de resto1
    c, r = request("POST", "/pedidos", {
        "id_restaurante": id_resto1,
        "id_reserva": id_reserva_r2,
        "detalles": [
            {"id_plato": id_plato1, "cantidad": 1}
        ]
    }, token=cliente1_token)
    log_test(13, "CU23: Rechazar pedido asociando reserva de otro restaurante (400)", c == 400, f"code={c}, resp={r}")

    # 8. CU23: Enviar pedido con reserva de OTRO usuario -> RECHAZAR (403)
    # Cliente 2 intenta usar la reserva de Cliente 1
    c, r = request("POST", "/pedidos", {
        "id_restaurante": id_resto2,
        "id_reserva": id_reserva_r2,
        "detalles": [
            {"id_plato": id_plato_r2, "cantidad": 1}
        ]
    }, token=cliente2_token)
    log_test(14, "CU23: Rechazar pedido asociando reserva ajena (403)", c == 403, f"code={c}, resp={r}")

    # 9. CU23: Crear pedido exitoso por Cliente 1 con consolidación de items duplicados
    c, pedido1 = request("POST", "/pedidos", {
        "id_restaurante": id_resto1,
        "observaciones": "Sin picante, por favor",
        "detalles": [
            {"id_plato": id_plato1, "cantidad": 2},
            {"id_plato": id_plato1, "cantidad": 1} # Repetido: consolidará a 3
        ]
    }, token=cliente1_token)
    log_test(15, "CU23: Crear pedido exitoso con consolidación de plato", c == 201, f"code={c}, resp={pedido1}")
    id_pedido1 = pedido1["id_pedido"]
    total_esperado = round(precio_plato1 * 3, 2)
    log_test(16, "CU23: Verificación de estado inicial 'PENDIENTE'", pedido1["estado"] == "PENDIENTE", f"estado={pedido1['estado']}")
    log_test(17, "CU23: Verificación de consolidación y total", float(pedido1["total"]) == total_esperado and len(pedido1["detalles"]) == 1, f"total={pedido1['total']}, expected={total_esperado}")
    log_test(18, "CU23: Verificación de cantidad consolidada = 3", pedido1["detalles"][0]["cantidad"] == 3, f"cantidad={pedido1['detalles'][0]['cantidad']}")

    # 10. CU23: Precios históricos inmutables
    # Modificar precio del plato con admin/resto1 y verificar que el pedido anterior mantiene el precio histórico
    nuevo_precio = precio_plato1 + 15.00
    c, _ = request("PUT", f"/platos/{id_plato1}", {
        "nombre": plato1_r1["nombre"],
        "precio": nuevo_precio,
        "disponible": True,
        "estado": "ACTIVO",
        "personas_cubiertas": plato1_r1.get("personas_cubiertas", 1),
        "id_categoria": plato1_r1["id_categoria"]
    }, token=admin_token)
    log_test(19, "Actualizar precio del plato en catálogo", c == 200, f"nuevo_precio={nuevo_precio}")

    c, pedido1_recargado = request("GET", f"/pedidos/{id_pedido1}", token=cliente1_token)
    log_test(20, "CU23: Inmutabilidad de precio histórico en pedido existente", float(pedido1_recargado["total"]) == total_esperado, f"total={pedido1_recargado['total']}, esperado={total_esperado}")

    # Restaurar precio original del plato
    request("PUT", f"/platos/{id_plato1}", {
        "nombre": plato1_r1["nombre"],
        "precio": precio_plato1,
        "disponible": True,
        "estado": "ACTIVO",
        "personas_cubiertas": plato1_r1.get("personas_cubiertas", 1),
        "id_categoria": plato1_r1["id_categoria"]
    }, token=admin_token)

    # 11. CU24: Listar 'mis-pedidos' del Cliente 1
    c, mis_pedidos = request("GET", "/pedidos/mis-pedidos", token=cliente1_token)
    log_test(21, "CU24: Listar mis pedidos del cliente", c == 200 and any(p["id_pedido"] == id_pedido1 for p in mis_pedidos), f"cant={len(mis_pedidos)}")

    # 12. CU24: Control de acceso 403 - Cliente 2 intenta consultar el pedido de Cliente 1
    c, r = request("GET", f"/pedidos/{id_pedido1}", token=cliente2_token)
    log_test(22, "CU24: Cliente 2 no puede consultar pedido de Cliente 1 (403)", c == 403, f"code={c}")

    # 13. CU24: Control de acceso 403 - Restaurante 2 intenta consultar pedido de Restaurante 1
    c, r = request("GET", f"/pedidos/{id_pedido1}", token=resto2_token)
    log_test(23, "CU24: Restaurante 2 no puede consultar pedido de Restaurante 1 (403)", c == 403, f"code={c}")

    # 14. CU24: Listar pedidos del Restaurante 1
    c, pedidos_r1 = request("GET", f"/restaurantes/{id_resto1}/pedidos", token=resto1_token)
    log_test(24, "CU24: Restaurante 1 lista sus pedidos recibidos", c == 200 and any(p["id_pedido"] == id_pedido1 for p in pedidos_r1), f"cant={len(pedidos_r1)}")

    # 15. CU24: Control de acceso 403 - Restaurante 2 intenta listar pedidos de Restaurante 1
    c, r = request("GET", f"/restaurantes/{id_resto1}/pedidos", token=resto2_token)
    log_test(25, "CU24: Restaurante 2 no puede listar pedidos de Restaurante 1 (403)", c == 403, f"code={c}")

    # 16. CU24: Transición de estado por Restaurante: PENDIENTE -> ACEPTADO
    c, ped_act = request("PATCH", f"/pedidos/{id_pedido1}/estado", {"estado": "ACEPTADO"}, token=resto1_token)
    log_test(26, "CU24: Transición PENDIENTE -> ACEPTADO (Restaurante)", c == 200 and ped_act["estado"] == "ACEPTADO", f"code={c}, estado={ped_act.get('estado')}")

    # 17. CU24: Cliente intenta cancelar un pedido ya ACEPTADO -> RECHAZAR (400)
    c, r = request("PATCH", f"/pedidos/{id_pedido1}/cancelar", token=cliente1_token)
    log_test(27, "CU24: Cliente no puede cancelar pedido en estado ACEPTADO (400)", c == 400, f"code={c}, resp={r}")

    # 18. CU24: Transición ilegal: ACEPTADO -> ENTREGADO directamente -> RECHAZAR (400)
    c, r = request("PATCH", f"/pedidos/{id_pedido1}/estado", {"estado": "ENTREGADO"}, token=resto1_token)
    log_test(28, "CU24: Rechazar salto directo ACEPTADO -> ENTREGADO (400)", c == 400, f"code={c}")

    # 19. CU24: Flujo completo de transiciones:
    # ACEPTADO -> EN_PREPARACION
    c, ped_act = request("PATCH", f"/pedidos/{id_pedido1}/estado", {"estado": "EN_PREPARACION"}, token=resto1_token)
    log_test(29, "CU24: Transición ACEPTADO -> EN_PREPARACION", c == 200 and ped_act["estado"] == "EN_PREPARACION", f"estado={ped_act.get('estado')}")

    # EN_PREPARACION -> LISTO
    c, ped_act = request("PATCH", f"/pedidos/{id_pedido1}/estado", {"estado": "LISTO"}, token=resto1_token)
    log_test(30, "CU24: Transición EN_PREPARACION -> LISTO", c == 200 and ped_act["estado"] == "LISTO", f"estado={ped_act.get('estado')}")

    # LISTO -> ENTREGADO
    c, ped_act = request("PATCH", f"/pedidos/{id_pedido1}/estado", {"estado": "ENTREGADO"}, token=resto1_token)
    log_test(31, "CU24: Transición LISTO -> ENTREGADO", c == 200 and ped_act["estado"] == "ENTREGADO", f"estado={ped_act.get('estado')}")

    # ENTREGADO es terminal: no se puede cancelar ni retroceder
    c, r = request("PATCH", f"/pedidos/{id_pedido1}/estado", {"estado": "CANCELADO"}, token=resto1_token)
    log_test(32, "CU24: Rechazar modificación sobre pedido ENTREGADO (terminal, 400)", c == 400, f"code={c}")

    # 20. CU24: Cancelación válida por el Cliente en estado PENDIENTE
    c, pedido2 = request("POST", "/pedidos", {
        "id_restaurante": id_resto1,
        "detalles": [
            {"id_plato": id_plato1, "cantidad": 1}
        ]
    }, token=cliente1_token)
    log_test(33, "Crear segundo pedido para prueba de cancelación cliente", c == 201, f"id_pedido={pedido2['id_pedido']}")
    id_pedido2 = pedido2["id_pedido"]

    c, ped2_cancelado = request("PATCH", f"/pedidos/{id_pedido2}/cancelar", token=cliente1_token)
    log_test(34, "CU24: Cliente cancela exitosamente pedido en PENDIENTE", c == 200 and ped2_cancelado["estado"] == "CANCELADO", f"estado={ped2_cancelado.get('estado')}")

    # 21. Filtrado de pedidos en Restaurante 1 por estado
    c, filtrados = request("GET", f"/restaurantes/{id_resto1}/pedidos?estado=CANCELADO", token=resto1_token)
    log_test(35, "CU24: Filtrar pedidos por estado CANCELADO", c == 200 and all(p["estado"] == "CANCELADO" for p in filtrados), f"total_cancelados={len(filtrados)}")

    print("\n=== TODAS LAS 35 PRUEBAS DE LA PARTE 11 (BACKEND) PASARON SATISFACTORIAMENTE ===")

if __name__ == "__main__":
    run()
