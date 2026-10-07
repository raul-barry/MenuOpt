"""
Script de verificación integral de la PARTE 6 usando urllib:
CU13: Generar recomendación
CU14: Comparar alternativas (primera etapa: RESTAURANTE)
CU08: Gestión de preferencias en platos
"""
import sys
import json
import urllib.request
import urllib.error
from decimal import Decimal

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
    print("=== INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - PARTE 6 ===")

    # 1. Login Admin
    c, r = request("POST", "/autenticacion/login", {
        "correo": "admin@menuopt.com",
        "contrasena": "Admin1234!"
    })
    log_test(1, "Login ADMIN", c == 200, f"code={c}, resp={r}")
    admin_token = r["access_token"]

    # 2. Login o Registro Usuario Cliente 1
    email_c1 = "cliente_p6_1@test.com"
    pwd_c1 = "Pass1234!"
    request("POST", "/autenticacion/registro", {
        "nombres": "Cliente",
        "apellidos": "P6 Uno",
        "correo": email_c1,
        "contrasena": pwd_c1,
        "telefono": "70011223"
    })
    c, r = request("POST", "/autenticacion/login", {
        "correo": email_c1,
        "contrasena": pwd_c1
    })
    log_test(2, "Login Cliente 1", c == 200, f"code={c}, resp={r}")
    c1_token = r["access_token"]

    # 3. Login o Registro Usuario Cliente 2 (para probar 403 Forbidden)
    email_c2 = "cliente_p6_2@test.com"
    pwd_c2 = "Pass1234!"
    request("POST", "/autenticacion/registro", {
        "nombres": "Cliente",
        "apellidos": "P6 Dos",
        "correo": email_c2,
        "contrasena": pwd_c2,
        "telefono": "70011224"
    })
    c, r = request("POST", "/autenticacion/login", {
        "correo": email_c2,
        "contrasena": pwd_c2
    })
    log_test(3, "Login Cliente 2 (para pruebas de titularidad)", c == 200, f"code={c}, resp={r}")
    c2_token = r["access_token"]

    # 4. Asegurar Restaurante existente
    c, rest_list = request("GET", "/restaurantes/mis-restaurantes", token=admin_token)
    if not rest_list or not isinstance(rest_list, list) or len(rest_list) == 0:
        c, crear_rest = request("POST", "/restaurantes", {
            "nombre": "Restaurante P6 Gourmet",
            "telefono": "77788990",
            "ubicacion": {
                "direccion": "Av. Principal 123",
                "zona": "Equipetrol",
                "ciudad": "Santa Cruz"
            }
        }, token=admin_token)
        id_restaurante = crear_rest["id_restaurante"]
    else:
        id_restaurante = rest_list[0]["id_restaurante"]

    # 5. Asegurar Categoría y Preferencia
    c, pref_res = request("GET", "/preferencias", token=admin_token)
    if not pref_res:
        c, pref_crear = request("POST", "/preferencias", {
            "nombre": "Vegetariano",
            "tipo": "DIETARIA",
            "descripcion": "Sin carne animal"
        }, token=admin_token)
        id_pref_veg = pref_crear["id_preferencia"]
    else:
        id_pref_veg = pref_res[0]["id_preferencia"]

    c, cats = request("GET", "/categorias", token=admin_token)
    if not cats:
        c, cat_crear = request("POST", "/categorias", {
            "nombre": "Platos Fuertes",
            "descripcion": "Principales"
        }, token=admin_token)
        id_cat = cat_crear["id_categoria"]
    else:
        id_cat = cats[0]["id_categoria"]

    # 6. Crear Platos de prueba para el escenario presupuestario y de compatibilidad:
    # Plato 1: "Menu Familiar Aceptado", precio: 70 Bs, personas_cubiertas: 5, tipo_comida: "ALMUERZO"
    # Para 20 personas -> ceil(20/5) = 4 unidades * 70 = 280 Bs. Presupuesto 300 Bs -> CUMPLE.
    c, plato1_res = request("POST", f"/restaurantes/{id_restaurante}/platos", {
        "nombre": "Bandeja Familiar Aceptada P6",
        "descripcion": "Almuerzo completo para 5 personas",
        "precio": 70.00,
        "tipo_comida": "ALMUERZO",
        "personas_cubiertas": 5,
        "disponible": True,
        "id_categoria": id_cat
    }, token=admin_token)
    log_test(4, "Creación de Plato 1 (70 Bs / 5 comensales)", c == 201, f"code={c}")
    id_plato1 = plato1_res["id_plato"]

    # Plato 2: "Menu Familiar Caro Rechazado", precio: 90 Bs, personas_cubiertas: 5, tipo_comida: "ALMUERZO"
    # Para 20 personas -> ceil(20/5) = 4 unidades * 90 = 360 Bs. Presupuesto 300 Bs -> EXCEDE (RECHAZADO).
    c, plato2_res = request("POST", f"/restaurantes/{id_restaurante}/platos", {
        "nombre": "Bandeja Premium Cara P6",
        "descripcion": "Almuerzo premium para 5 personas",
        "precio": 90.00,
        "tipo_comida": "ALMUERZO",
        "personas_cubiertas": 5,
        "disponible": True,
        "id_categoria": id_cat
    }, token=admin_token)
    log_test(5, "Creación de Plato 2 (90 Bs / 5 comensales)", c == 201, f"code={c}")
    id_plato2 = plato2_res["id_plato"]

    # Plato 3: Plato de otro tipo de comida (CENA)
    c, plato3_res = request("POST", f"/restaurantes/{id_restaurante}/platos", {
        "nombre": "Cena Ligera P6",
        "descripcion": "Cena para 5 personas",
        "precio": 50.00,
        "tipo_comida": "CENA",
        "personas_cubiertas": 5,
        "disponible": True,
        "id_categoria": id_cat
    }, token=admin_token)
    log_test(6, "Creación de Plato 3 (CENA)", c == 201, f"code={c}")
    id_plato3 = plato3_res["id_plato"]

    # Plato 4: Plato no disponible
    c, plato4_res = request("POST", f"/restaurantes/{id_restaurante}/platos", {
        "nombre": "Almuerzo No Disponible P6",
        "descripcion": "Agotado",
        "precio": 40.00,
        "tipo_comida": "ALMUERZO",
        "personas_cubiertas": 5,
        "disponible": False,
        "id_categoria": id_cat
    }, token=admin_token)
    log_test(7, "Creación de Plato 4 (No disponible)", c == 201, f"code={c}")
    id_plato4 = plato4_res["id_plato"]

    # 7. CU08: Gestión de preferencias en platos
    # GET /platos/{id_plato}/preferencias sin auth -> 401
    c, r = request("GET", f"/platos/{id_plato1}/preferencias")
    log_test(8, "GET /platos/{id}/preferencias sin autenticación -> 401", c == 401, f"code={c}")

    # PUT /platos/{id_plato}/preferencias como CLIENTE (no responsable) -> 403
    c, r = request("PUT", f"/platos/{id_plato1}/preferencias", {
        "preferencias": [id_pref_veg]
    }, token=c1_token)
    log_test(9, "PUT /platos/{id}/preferencias por Cliente ajeno -> 403 Forbidden", c == 403, f"code={c}")

    # PUT /platos/{id_plato}/preferencias como ADMIN -> 200 OK
    c, r = request("PUT", f"/platos/{id_plato1}/preferencias", {
        "preferencias": [id_pref_veg]
    }, token=admin_token)
    log_test(10, "PUT /platos/{id}/preferencias como ADMIN asignando preferencia -> 200 OK", c == 200 and len(r["preferencias"]) == 1, f"code={c}")

    # GET /platos/{id_plato}/preferencias -> 200 OK
    c, r = request("GET", f"/platos/{id_plato1}/preferencias", token=c1_token)
    log_test(11, "GET /platos/{id}/preferencias consulta preferencias del plato -> 200 OK", c == 200 and r["preferencias"][0]["id_preferencia"] == id_pref_veg, f"code={c}")

    # PUT /platos/{id_plato}/preferencias con preferencia inexistente -> 400 Bad Request
    c, r = request("PUT", f"/platos/{id_plato1}/preferencias", {
        "preferencias": [999999]
    }, token=admin_token)
    log_test(12, "PUT /platos/{id}/preferencias con ID inexistente -> 400 Bad Request", c == 400, f"code={c}")

    # 8. CU11 / CU13: Planificación de prueba
    # Presupuesto: 300 Bs, Personas: 20, Tipo: ALMUERZO, Preferencia: [id_pref_veg]
    c, plan_res = request("POST", "/planificaciones", {
        "presupuesto": 300.00,
        "cantidad_personas": 20,
        "tipo_comida": "ALMUERZO",
        "ubicacion_referencia": "Zona Central",
        "preferencias": [id_pref_veg]
    }, token=c1_token)
    log_test(13, "Crear planificación de prueba (300 Bs, 20 personas, ALMUERZO)", c == 201, f"code={c}")
    id_plan = plan_res["id_planificacion"]

    # 9. CU13: Generar recomendaciones
    # Intentar generar sin token -> 401
    c, r = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar")
    log_test(14, "POST recomendaciones/generar sin autenticación -> 401", c == 401, f"code={c}")

    # Intentar generar con Cliente 2 (no propietario) -> 403
    c, r = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c2_token)
    log_test(15, "POST recomendaciones/generar por usuario no propietario -> 403 Forbidden", c == 403, f"code={c}")

    # Generar con Cliente 1 (propietario) -> 200 OK
    c, recs = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c1_token)
    log_test(16, "POST recomendaciones/generar por propietario -> 200 OK", c == 200, f"code={c}")

    # Validaciones del algoritmo:
    # Plato 1 (70 Bs * 4 = 280 Bs) debe estar incluido.
    # Plato 2 (90 Bs * 4 = 360 Bs) NO debe estar porque excede 300 Bs.
    # Plato 3 (CENA) NO debe estar.
    # Plato 4 (No disponible) NO debe estar.
    ids_platos_recomendados = [item["id_plato"] for r in recs for item in r["platos"]]
    incluye_plato1 = id_plato1 in ids_platos_recomendados
    excluye_plato2 = id_plato2 not in ids_platos_recomendados
    excluye_plato3 = id_plato3 not in ids_platos_recomendados
    excluye_plato4 = id_plato4 not in ids_platos_recomendados

    log_test(17, "Validación algorítmica: Plato 1 (280 Bs <= 300 Bs) aceptado", incluye_plato1, f"Platos incluidos: {ids_platos_recomendados}")
    log_test(18, "Validación algorítmica: Plato 2 (360 Bs > 300 Bs) rechazado por presupuesto", excluye_plato2)
    log_test(19, "Validación algorítmica: Filtros de tipo de comida y disponibilidad respetados", excluye_plato3 and excluye_plato4)

    # Validar campos de la recomendación: costo_total, costo_por_persona, puntuacion (0 - 100)
    rec_obj = [r for r in recs if any(item["id_plato"] == id_plato1 for item in r["platos"])][0]
    id_rec = rec_obj["id_recomendacion"]
    costo_total = Decimal(str(rec_obj["costo_total"]))
    costo_pp = Decimal(str(rec_obj["costo_por_persona"]))
    puntuacion = Decimal(str(rec_obj["puntuacion"]))
    distancia = rec_obj["distancia_estimada"]

    log_test(20, "Validación de cálculos: costo_total == 280.00", costo_total == Decimal("280.00"), f"Costo: {costo_total}")
    log_test(21, "Validación de cálculos: costo_por_persona == 14.00 (280 / 20)", costo_pp == Decimal("14.00"), f"Costo pp: {costo_pp}")
    log_test(22, "Validación de score y distancia: 0 <= score <= 100 y distancia is None", (Decimal("0.00") <= puntuacion <= Decimal("100.00")) and distancia is None, f"Score: {puntuacion}, Distancia: {distancia}")

    # Re-ejecutar generación (idempotencia y reemplazo sin duplicar)
    c, res_rec_reejecutar = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c1_token)
    log_test(23, "Re-ejecución transaccional: no duplica registros", c == 200 and len(res_rec_reejecutar) == len(recs), f"len={len(res_rec_reejecutar)}")

    # 10. CU13: Consultar listado y detalle
    c, res_listar = request("GET", f"/planificaciones/{id_plan}/recomendaciones", token=c1_token)
    log_test(24, "GET /planificaciones/{id}/recomendaciones -> 200 OK", c == 200 and len(res_listar) >= 1, f"len={len(res_listar)}")

    id_rec_actual = res_listar[0]["id_recomendacion"]
    c, res_detalle = request("GET", f"/recomendaciones/{id_rec_actual}", token=c1_token)
    log_test(25, "GET /recomendaciones/{id_rec} detalle -> 200 OK", c == 200 and res_detalle.get("id_recomendacion") == id_rec_actual, f"resp={res_detalle}")

    # Detalle con cliente ajeno -> 403
    c, res_detalle_c2 = request("GET", f"/recomendaciones/{id_rec_actual}", token=c2_token)
    log_test(26, "GET /recomendaciones/{id_rec} por usuario no propietario -> 403 Forbidden", c == 403, f"code={c}")

    # 11. CU14: Comparar alternativas
    c, r = request("GET", f"/planificaciones/{id_plan}/comparacion")
    log_test(27, "GET /planificaciones/{id}/comparacion sin auth -> 401", c == 401, f"code={c}")

    c, r = request("GET", f"/planificaciones/{id_plan}/comparacion", token=c2_token)
    log_test(28, "GET /planificaciones/{id}/comparacion usuario ajeno -> 403 Forbidden", c == 403, f"code={c}")

    c, comp_data = request("GET", f"/planificaciones/{id_plan}/comparacion", token=c1_token)
    log_test(29, "GET /planificaciones/{id}/comparacion propietario -> 200 OK", c == 200, f"code={c}")

    tiene_alternativas = comp_data["total_alternativas"] >= 1
    tiene_mejor_costo = comp_data["mejor_opcion_costo"] is not None
    tiene_mejor_score = comp_data["mejor_opcion_puntuacion"] is not None
    ahorro_valido = Decimal(str(comp_data["alternativas"][0]["ahorro_respecto_presupuesto"])) == Decimal("20.00") # 300 - 280 = 20

    log_test(30, "CU14 Comparación contiene métricas de ahorro y mejores opciones destacadas", tiene_alternativas and tiene_mejor_costo and tiene_mejor_score and ahorro_valido, f"Ahorro: {comp_data['alternativas'][0]['ahorro_respecto_presupuesto']}, Mejor costo: {comp_data['mejor_opcion_costo']['costo_total']}")

    print("\n=======================================================")
    print("TODAS LAS 30 PRUEBAS AUTOMATIZADAS PASARON SATISFACTORIAMENTE")
    print("=======================================================")

if __name__ == "__main__":
    run()
