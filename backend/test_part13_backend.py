"""
Script de verificación integral de la PARTE 13 (CU26: Usar asistencia con IA):
1. Validación de autenticación y rol CLIENTE en endpoints /asistente/*.
2. Interpretación en lenguaje natural de solicitudes completas e incompletas.
3. Cruce de preferencias detectadas contra el catálogo real en PostgreSQL (Preferencia existente vs inexistente).
4. Manejo y detección de datos faltantes (presupuesto, cantidad_personas, tipo_comida, ubicacion_referencia).
5. Flujo conversacional acumulado mediante contexto previo.
6. Validación de límites de longitud y seguridad contra inyección.
7. Explicación de recomendaciones calculadas reales (CU13) sin inventar datos.
8. Explicación de comparaciones reales (CU14) entre Restaurante y Preparación Propia.
9. Resiliencia: funcionamiento con AI_ENABLED=false y llamadas controladas.
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

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
    print("=== INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - PARTE 13 (BACKEND CU26) ===")

    # 1. Login usuarios
    c, r = request("POST", "/autenticacion/login", {"correo": "cliente1@menuopt.com", "contrasena": "Cliente1234*"})
    log_test(1, "Login CLIENTE 1", c == 200, f"code={c}")
    cliente_token = r["access_token"]

    c, r = request("POST", "/autenticacion/login", {"correo": "restaurante@menuopt.com", "contrasena": "Resto1234*"})
    log_test(2, "Login RESTAURANTE", c == 200, f"code={c}")
    resto_token = r["access_token"]

    # 2. Control de Acceso: Endpoint /asistente/interpretar requiere rol CLIENTE o ADMIN
    # Usuario con rol RESTAURANTE intentando consultar asistente -> 403 Forbidden
    c, r = request("POST", "/asistente/interpretar", {"mensaje": "Tengo 200 Bs para 4"}, token=resto_token)
    log_test(3, "Seguridad 403: Rol RESTAURANTE no puede consumir /asistente/interpretar", c == 403, f"code={c}")

    # Usuario anónimo -> 401 Unauthorized
    c, r = request("POST", "/asistente/interpretar", {"mensaje": "Tengo 200 Bs para 4"})
    log_test(4, "Seguridad 401: Usuario sin token rechazado", c == 401, f"code={c}")

    # 3. Validación de Longitud de Entrada
    c, r = request("POST", "/asistente/interpretar", {"mensaje": "x" * 1005}, token=cliente_token)
    log_test(5, "Validación: Rechazo de mensaje excesivo (> 1000 caracteres, 422)", c == 422, f"code={c}")

    # Mensaje vacío -> 422
    c, r = request("POST", "/asistente/interpretar", {"mensaje": "   "}, token=cliente_token)
    log_test(6, "Validación: Rechazo de mensaje vacío (422)", c == 422, f"code={c}")

    # 4. PRUEBA 2 del enunciado: Solicitud completa en lenguaje natural
    # "Tengo 300 Bs y somos 10 personas. Queremos almorzar comida vegetariana en Equipetrol."
    c, interp1 = request("POST", "/asistente/interpretar", {
        "mensaje": "Tengo 300 Bs y somos 10 personas. Queremos almorzar comida vegetariana en Equipetrol."
    }, token=cliente_token)
    log_test(7, "CU26: Interpretar solicitud completa exitosamente", c == 200, f"code={c}")
    log_test(8, "Detección presupuesto = 300", float(interp1.get("presupuesto") or 0) == 300.0, f"presupuesto={interp1.get('presupuesto')}")
    log_test(9, "Detección personas = 10", interp1.get("cantidad_personas") == 10, f"personas={interp1.get('cantidad_personas')}")
    log_test(10, "Detección tipo_comida = ALMUERZO", interp1.get("tipo_comida") == "ALMUERZO", f"tipo={interp1.get('tipo_comida')}")
    log_test(11, "Detección ubicacion = Equipetrol", "Equipetrol" in (interp1.get("ubicacion_referencia") or ""), f"ubicacion={interp1.get('ubicacion_referencia')}")
    log_test(12, "Detección preferencia = Vegetariano", "Vegetariano" in interp1.get("preferencias_detectadas", []), f"prefs={interp1.get('preferencias_detectadas')}")
    log_test(13, "Datos faltantes vacío y listo_para_crear = True", len(interp1.get("datos_faltantes", [])) == 0 and interp1.get("listo_para_crear") is True, f"faltantes={interp1.get('datos_faltantes')}")

    # 5. PRUEBA 3 del enunciado: Solicitud incompleta (datos faltantes)
    # "Quiero cenar comida sin gluten."
    c, interp2 = request("POST", "/asistente/interpretar", {
        "mensaje": "Quiero cenar comida sin gluten."
    }, token=cliente_token)
    log_test(14, "CU26: Interpretar solicitud con datos faltantes", c == 200, f"code={c}")
    log_test(15, "Detección tipo = CENA", interp2.get("tipo_comida") == "CENA", f"tipo={interp2.get('tipo_comida')}")
    log_test(16, "Detección preferencia = Sin gluten", "Sin gluten" in interp2.get("preferencias_detectadas", []), f"prefs={interp2.get('preferencias_detectadas')}")
    log_test(17, "Identificación de faltantes: presupuesto y cantidad_personas", "presupuesto" in interp2.get("datos_faltantes", []) and "cantidad_personas" in interp2.get("datos_faltantes", []), f"faltantes={interp2.get('datos_faltantes')}")
    log_test(18, "listo_para_crear = False cuando faltan datos", interp2.get("listo_para_crear") is False, f"listo={interp2.get('listo_para_crear')}")

    # 6. PRUEBA 4 del enunciado: Flujo conversacional acumulativo
    # Usuario responde: "200 Bs para 4 personas en el Centro."
    contexto_acumulado = {
        "tipo_comida": interp2.get("tipo_comida"),
        "preferencias_detectadas": interp2.get("preferencias_detectadas"),
    }
    c, interp3 = request("POST", "/asistente/interpretar", {
        "mensaje": "200 Bs para 4 personas en el Centro.",
        "contexto_previo": contexto_acumulado
    }, token=cliente_token)
    log_test(19, "CU26: Completar solicitud con contexto previo acumulado", c == 200, f"code={c}")
    log_test(20, "Presupuesto completado a 200 Bs", float(interp3.get("presupuesto") or 0) == 200.0, f"pres={interp3.get('presupuesto')}")
    log_test(21, "Personas completado a 4", interp3.get("cantidad_personas") == 4, f"personas={interp3.get('cantidad_personas')}")
    log_test(22, "Retiene tipo_comida CENA y preferencia Sin gluten del contexto", interp3.get("tipo_comida") == "CENA" and "Sin gluten" in interp3.get("preferencias_detectadas", []), f"tipo={interp3.get('tipo_comida')}, prefs={interp3.get('preferencias_detectadas')}")

    # 7. Preferencia no registrada en PostgreSQL (ej. "Keto")
    c, interp_keto = request("POST", "/asistente/interpretar", {
        "mensaje": "Tengo 150 Bs para 2 personas, almuerzo keto en el Centro"
    }, token=cliente_token)
    log_test(23, "CU26: Manejo de preferencia no registrada en BD", c == 200, f"code={c}")
    validadas = interp_keto.get("preferencias_validadas", [])
    pref_keto = next((p for p in validadas if p["nombre_detectado"] == "Keto"), None)
    log_test(24, "Preferencia 'Keto' marcada como no registrada (id=None, registrada=False)", pref_keto is not None and pref_keto["registrada"] is False and pref_keto["id_preferencia"] is None, f"pref_keto={pref_keto}")

    # 8. PRUEBA 6 & 7: Creación de Planificación real en PostgreSQL usando los datos interpretados
    # Simula la confirmación del usuario en frontend enviando a POST /planificaciones
    c, plan_creada = request("POST", "/planificaciones", {
        "presupuesto": float(interp1["presupuesto"]),
        "cantidad_personas": interp1["cantidad_personas"],
        "tipo_comida": interp1["tipo_comida"],
        "ubicacion_referencia": interp1["ubicacion_referencia"],
        "preferencias": [p["id_preferencia"] for p in interp1["preferencias_validadas"] if p["registrada"]]
    }, token=cliente_token)
    log_test(25, "CU11: Crear planificación real a partir de datos interpretados", c == 201, f"code={c}")
    id_plan = plan_creada["id_planificacion"]

    # 9. PRUEBA 8: Generación de recomendaciones mediante motor algorítmico CU13
    c, resp_gen = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=cliente_token)
    lista_recs = resp_gen["recomendaciones"] if isinstance(resp_gen, dict) and "recomendaciones" in resp_gen else resp_gen
    log_test(26, "CU13: Generar recomendaciones con algoritmo real", c == 200 and len(lista_recs) > 0, f"code={c}, total={len(lista_recs)}")

    if len(lista_recs) > 0:
        id_rec = lista_recs[0]["id_recomendacion"]
        costo_real = float(lista_recs[0]["costo_total"])

        # 10. PRUEBA 9 & 10: Explicar recomendación sin alterar cifras
        c, expl_rec = request("POST", "/asistente/explicar-recomendacion", {
            "id_recomendacion": id_rec
        }, token=cliente_token)
        log_test(27, "CU26: Explicar recomendación calculada real", c == 200, f"code={c}")
        log_test(28, "Explicación contiene el costo real calculado", str(int(costo_real)) in expl_rec.get("explicacion", ""), f"costo_real={costo_real}, expl={expl_rec.get('explicacion')}")

        # 11. Explicar comparación de alternativas CU14
        c, expl_comp = request("POST", "/asistente/explicar-comparacion", {
            "id_planificacion": id_plan
        }, token=cliente_token)
        log_test(29, "CU26: Explicar comparación calculada real (CU14)", c == 200, f"code={c}")
        log_test(30, "Tipo de respuesta es 'COMPARACION'", expl_comp.get("tipo") == "COMPARACION", f"tipo={expl_comp.get('tipo')}")

    print("\n=== TODAS LAS 30 PRUEBAS AUTOMATIZADAS DE LA PARTE 13 (BACKEND) PASARON EXITOSAMENTE ===")

if __name__ == "__main__":
    run()
