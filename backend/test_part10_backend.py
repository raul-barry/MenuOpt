"""
Script de verificación integral de la PARTE 10:
CU20: Consultar disponibilidad de mesas (según fecha, horario y solapamiento)
CU21: Realizar y cancelar reserva (concurrencia, SELECT FOR UPDATE, 409)
CU22: Gestionar reservas de restaurante (filtros, transiciones de estado, 403)
"""
import sys
import json
import time
from datetime import date, timedelta
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"
SUFFIX = str(int(time.time()))[-4:]
FECHA_FUTURA = (date.today() + timedelta(days=10)).isoformat()

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
    print("=== INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - PARTE 10 (BACKEND) ===")

    # 1. Login ADMIN
    c, r = request("POST", "/autenticacion/login", {
        "correo": "admin@menuopt.com",
        "contrasena": "Admin1234*"
    })
    log_test(0, "Login ADMIN", c == 200, f"code={c}")
    admin_token = r["access_token"]

    # 2. Login RESTAURANTE 1
    c, r = request("POST", "/autenticacion/login", {
        "correo": "restaurante@menuopt.com",
        "contrasena": "Resto1234*"
    })
    log_test(1, "Login RESTAURANTE 1", c == 200, f"code={c}")
    resto1_token = r["access_token"]

    # 3. Login RESTAURANTE 2 (para pruebas de titularidad 403)
    c, r = request("POST", "/autenticacion/login", {
        "correo": "restaurante2@menuopt.com",
        "contrasena": "Resto1234*"
    })
    log_test(2, "Login RESTAURANTE 2", c == 200, f"code={c}")
    resto2_token = r["access_token"]

    # 4. Login CLIENTE 1
    c, r = request("POST", "/autenticacion/login", {
        "correo": "cliente1@menuopt.com",
        "contrasena": "Cliente1234*"
    })
    log_test(3, "Login CLIENTE 1", c == 200, f"code={c}")
    cli1_token = r["access_token"]

    # 5. Login CLIENTE 2
    c, r = request("POST", "/autenticacion/login", {
        "correo": "cliente2@menuopt.com",
        "contrasena": "Cliente1234*"
    })
    log_test(4, "Login CLIENTE 2", c == 200, f"code={c}")
    cli2_token = r["access_token"]

    # 6. Obtener restaurante de usuario 1
    c, mis_restos = request("GET", "/restaurantes/mis-restaurantes", token=resto1_token)
    log_test(5, "Obtener restaurante de usuario 1", c == 200 and len(mis_restos) > 0, f"total={len(mis_restos)}")
    id_restaurante = mis_restos[0]["id_restaurante"]

    # 7. Crear Área de Referencia (Terraza P10)
    c, area = request("POST", f"/restaurantes/{id_restaurante}/areas", {
        "nombre": f"Terraza P10 {SUFFIX}",
        "descripcion": "Área de prueba para reservas",
        "ancho_mapa": 1000,
        "alto_mapa": 600
    }, token=resto1_token)
    log_test(6, "Crear Área Terraza P10", c == 201, f"code={c}")
    id_area = area["id_area"]

    # 8. Crear Mesas de Caso de Referencia: M1 (2p), M2 (4p), M3 (6p), M4 (4p), M5 (6p)
    mesas_data = [
        {"numero": f"M1-{SUFFIX}", "capacidad": 2, "forma": "REDONDA", "posicion_x": 0.15, "posicion_y": 0.20, "combinable": True},
        {"numero": f"M2-{SUFFIX}", "capacidad": 4, "forma": "CUADRADA", "posicion_x": 0.40, "posicion_y": 0.20, "combinable": True},
        {"numero": f"M3-{SUFFIX}", "capacidad": 6, "forma": "RECTANGULAR", "posicion_x": 0.70, "posicion_y": 0.20, "combinable": True},
        {"numero": f"M4-{SUFFIX}", "capacidad": 4, "forma": "CUADRADA", "posicion_x": 0.30, "posicion_y": 0.60, "combinable": True},
        {"numero": f"M5-{SUFFIX}", "capacidad": 6, "forma": "RECTANGULAR", "posicion_x": 0.60, "posicion_y": 0.60, "combinable": True},
    ]
    mesas_creadas = {}
    for m in mesas_data:
        c, mesa_obj = request("POST", f"/areas/{id_area}/mesas", m, token=resto1_token)
        log_test(7, f"Crear Mesa {m['numero']} ({m['capacidad']}p)", c == 201, f"code={c}")
        mesas_creadas[m["numero"]] = mesa_obj

    id_m1 = mesas_creadas[f"M1-{SUFFIX}"]["id_mesa"]
    id_m2 = mesas_creadas[f"M2-{SUFFIX}"]["id_mesa"]
    id_m3 = mesas_creadas[f"M3-{SUFFIX}"]["id_mesa"]
    id_m4 = mesas_creadas[f"M4-{SUFFIX}"]["id_mesa"]
    id_m5 = mesas_creadas[f"M5-{SUFFIX}"]["id_mesa"]

    # 9. Crear combinación permitida M4 + M5 (Capacidad: 10p)
    c, comb = request("POST", f"/areas/{id_area}/combinaciones", {
        "id_mesa_origen": id_m4,
        "id_mesa_destino": id_m5,
        "descripcion": "Combinación M4 + M5 para grupos grandes"
    }, token=resto1_token)
    log_test(8, "Crear Combinación M4 + M5", c == 201 and comb.get("capacidad_combinada") == 10, f"cap={comb.get('capacidad_combinada')}")

    # 10. CU20: Consultar disponibilidad para 4 personas (20:00 a 22:00)
    c, disp = request("GET", f"/restaurantes/{id_restaurante}/mesas-disponibles?id_area={id_area}&fecha={FECHA_FUTURA}&hora_inicio=20:00:00&hora_fin=22:00:00&cantidad_personas=4", token=cli1_token)
    log_test(9, "CU20: Consultar disponibilidad (4 personas)", c == 200, f"code={c}")

    mapa_disp = {m["id_mesa"]: m for m in disp["mesas"]}
    log_test(10, "M1 (2p) para 4 personas es NO_COMPATIBLE", mapa_disp[id_m1]["estado_disponibilidad"] == "NO_COMPATIBLE", f"disp={mapa_disp[id_m1]['estado_disponibilidad']}")
    log_test(11, "M2 (4p) para 4 personas es DISPONIBLE", mapa_disp[id_m2]["estado_disponibilidad"] == "DISPONIBLE" and mapa_disp[id_m2]["seleccionable"] is True, f"disp={mapa_disp[id_m2]['estado_disponibilidad']}")
    log_test(12, "M3 (6p) para 4 personas es DISPONIBLE (exceso <= 2)", mapa_disp[id_m3]["estado_disponibilidad"] == "DISPONIBLE", f"disp={mapa_disp[id_m3]['estado_disponibilidad']}")

    # 11. CU21: Cliente 1 reserva M2 (20:00 a 22:00)
    c, res_m2 = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "20:00:00",
        "hora_fin": "22:00:00",
        "cantidad_personas": 4,
        "mesas": [id_m2],
        "observaciones": "Cena de aniversario"
    }, token=cli1_token)
    log_test(13, "CU21: Cliente 1 reserva M2 (20:00 - 22:00)", c == 201 and res_m2["estado"] == "CONFIRMADA", f"code={c}, estado={res_m2.get('estado')}")
    id_res_m2 = res_m2["id_reserva"]

    # 12. CU20: Consultar nuevamente mismo horario (20:00 a 22:00) -> M2 debe estar NO_DISPONIBLE
    c, disp2 = request("GET", f"/restaurantes/{id_restaurante}/mesas-disponibles?id_area={id_area}&fecha={FECHA_FUTURA}&hora_inicio=20:00:00&hora_fin=22:00:00&cantidad_personas=4", token=cli2_token)
    mapa_disp2 = {m["id_mesa"]: m for m in disp2["mesas"]}
    log_test(14, "M2 ahora aparece NO_DISPONIBLE en 20:00-22:00", mapa_disp2[id_m2]["estado_disponibilidad"] == "NO_DISPONIBLE" and mapa_disp2[id_m2]["seleccionable"] is False, f"disp={mapa_disp2[id_m2]['estado_disponibilidad']}")

    # 13. CU20: Consultar otro horario no solapado (17:00 a 19:30) -> M2 debe estar DISPONIBLE
    c, disp3 = request("GET", f"/restaurantes/{id_restaurante}/mesas-disponibles?id_area={id_area}&fecha={FECHA_FUTURA}&hora_inicio=17:00:00&hora_fin=19:30:00&cantidad_personas=4", token=cli2_token)
    mapa_disp3 = {m["id_mesa"]: m for m in disp3["mesas"]}
    log_test(15, "M2 está DISPONIBLE en horario no solapado (17:00-19:30)", mapa_disp3[id_m2]["estado_disponibilidad"] == "DISPONIBLE", f"disp={mapa_disp3[id_m2]['estado_disponibilidad']}")

    # 14. Regla de Concurrencia y Conflicto 409: Cliente 2 intenta reservar M2 en 20:00-22:00
    c, conf = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "20:00:00",
        "hora_fin": "22:00:00",
        "cantidad_personas": 4,
        "mesas": [id_m2]
    }, token=cli2_token)
    log_test(16, "Doble reserva rechazada con HTTP 409 Conflict", c == 409, f"code={c}, resp={conf}")

    # 15. Regla de Solapamiento: Intentar 19:30 a 20:30 (se solapa con 20:00 a 22:00) -> 409
    c, conf_solape = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "19:30:00",
        "hora_fin": "20:30:00",
        "cantidad_personas": 4,
        "mesas": [id_m2]
    }, token=cli2_token)
    log_test(17, "Intervalo solapado 19:30-20:30 rechazado con 409", c == 409, f"code={c}")

    # 16. Regla de Intervalo Consecutivo: 18:00 a 20:00 (termina exactamente cuando empieza la otra) -> permitido
    c, res_consec = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "18:00:00",
        "hora_fin": "20:00:00",
        "cantidad_personas": 4,
        "mesas": [id_m2]
    }, token=cli2_token)
    log_test(18, "Intervalo consecutivo 18:00-20:00 permitido", c == 201, f"code={c}")

    # 17. CU21: Cancelar reserva M2 de Cliente 1 (PATCH /reservas/{id}/cancelar)
    c, res_canc = request("PATCH", f"/reservas/{id_res_m2}/cancelar", token=cli1_token)
    log_test(19, "Cancelar reserva como cliente", c == 200 and res_canc["estado"] == "CANCELADA", f"code={c}, estado={res_canc.get('estado')}")

    # 18. Verificar que cancelación libera la mesa en 20:00-22:00
    c, disp4 = request("GET", f"/restaurantes/{id_restaurante}/mesas-disponibles?id_area={id_area}&fecha={FECHA_FUTURA}&hora_inicio=20:00:00&hora_fin=22:00:00&cantidad_personas=4", token=cli2_token)
    mapa_disp4 = {m["id_mesa"]: m for m in disp4["mesas"]}
    log_test(20, "Mesa M2 vuelve a estar DISPONIBLE tras cancelación", mapa_disp4[id_m2]["estado_disponibilidad"] == "DISPONIBLE", f"disp={mapa_disp4[id_m2]['estado_disponibilidad']}")

    # 19. Validación en fecha pasada: debe rechazarse con 400
    c, err_pasado = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": "2020-01-01",
        "hora_inicio": "20:00:00",
        "hora_fin": "22:00:00",
        "cantidad_personas": 4,
        "mesas": [id_m2]
    }, token=cli1_token)
    log_test(21, "Rechazar reserva en fecha pasada con 400", c == 400, f"code={c}")

    # 20. Validación hora_fin anterior a hora_inicio: debe rechazarse con 400/422
    c, err_horas = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "22:00:00",
        "hora_fin": "20:00:00",
        "cantidad_personas": 4,
        "mesas": [id_m2]
    }, token=cli1_token)
    log_test(22, "Rechazar hora_fin <= hora_inicio", c in (400, 422), f"code={c}")

    # 21. Caso Combinación: Consultar disponibilidad para 10 personas
    c, disp_comb = request("GET", f"/restaurantes/{id_restaurante}/mesas-disponibles?id_area={id_area}&fecha={FECHA_FUTURA}&hora_inicio=21:00:00&hora_fin=23:00:00&cantidad_personas=10", token=cli1_token)
    log_test(23, "Consultar disponibilidad para 10 personas", c == 200, f"code={c}")
    combs_disp = disp_comb.get("combinaciones", [])
    comb_encontrada = next((cb for cb in combs_disp if set(cb["mesas"]) == {id_m4, id_m5}), None)
    log_test(24, "Combinación M4 + M5 (10p) es seleccionable para 10 personas", comb_encontrada is not None and comb_encontrada["seleccionable"] is True, f"comb={comb_encontrada}")

    # 22. Reservar combinación M4 + M5 para 10 personas
    c, res_combinada = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "21:00:00",
        "hora_fin": "23:00:00",
        "cantidad_personas": 10,
        "mesas": [id_m4, id_m5],
        "observaciones": "Cena empresarial 10 personas"
    }, token=cli1_token)
    log_test(25, "Reservar combinación M4 + M5 exitosa", c == 201 and len(res_combinada["mesas"]) == 2, f"code={c}, mesas={len(res_combinada.get('mesas', []))}")

    # 23. Verificar que ambas mesas M4 y M5 quedaron bloqueadas en 21:00-23:00
    c, conf_m4 = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "21:30:00",
        "hora_fin": "22:30:00",
        "cantidad_personas": 4,
        "mesas": [id_m4]
    }, token=cli2_token)
    log_test(26, "M4 individual bloqueada por reserva combinada (409)", c == 409, f"code={c}")

    # 24. Rechazar combinación arbitraria no registrada (ej. M1 + M3)
    c, conf_no_reg = request("POST", "/reservas", {
        "id_restaurante": id_restaurante,
        "id_area": id_area,
        "fecha_reserva": FECHA_FUTURA,
        "hora_inicio": "15:00:00",
        "hora_fin": "16:00:00",
        "cantidad_personas": 8,
        "mesas": [id_m1, id_m3]
    }, token=cli1_token)
    log_test(27, "Rechazar combinación no registrada (400)", c == 400, f"code={c}")

    # 25. CU21: Consultar mis reservas como Cliente 1
    c, mis_reservas = request("GET", "/reservas/mis-reservas", token=cli1_token)
    log_test(28, "CU21: Consultar mis reservas", c == 200 and len(mis_reservas) >= 2, f"total={len(mis_reservas)}")

    # 26. CU22: Restaurante 1 consulta reservas de su establecimiento
    c, reservas_resto = request("GET", f"/restaurantes/{id_restaurante}/reservas", token=resto1_token)
    log_test(29, "CU22: Restaurante consulta sus reservas", c == 200 and len(reservas_resto) >= 3, f"total={len(reservas_resto)}")

    # 27. Seguridad 403: Restaurante 2 intenta consultar reservas de Restaurante 1
    c, sec_resto2 = request("GET", f"/restaurantes/{id_restaurante}/reservas", token=resto2_token)
    log_test(30, "Seguridad 403: Restaurante ajeno no puede ver reservas", c == 403, f"code={c}")

    # 28. Seguridad 403: Cliente 2 intenta cancelar reserva de Cliente 1
    id_res_comb = res_combinada["id_reserva"]
    c, sec_cli2 = request("PATCH", f"/reservas/{id_res_comb}/cancelar", token=cli2_token)
    log_test(31, "Seguridad 403: Cliente ajeno no puede cancelar reserva", c == 403, f"code={c}")

    # 29. CU22: Restaurante 1 actualiza reserva a FINALIZADA
    c, act_fin = request("PATCH", f"/reservas/{id_res_comb}/estado", {"estado": "FINALIZADA"}, token=resto1_token)
    log_test(32, "CU22: Restaurante actualiza reserva a FINALIZADA", c == 200 and act_fin["estado"] == "FINALIZADA", f"code={c}, estado={act_fin.get('estado')}")

    # 30. CU22: Rechazar transición prohibida FINALIZADA -> CANCELADA
    c, act_err = request("PATCH", f"/reservas/{id_res_comb}/estado", {"estado": "CANCELADA"}, token=resto1_token)
    log_test(33, "CU22: Rechazar transición no permitida de FINALIZADA", c == 400, f"code={c}")

    print("\n=======================================================")
    print("TODAS LAS 34 PRUEBAS BACKEND DE LA PARTE 10 PASARON EXITOSAMENTE")
    print("=======================================================")

if __name__ == "__main__":
    run()
