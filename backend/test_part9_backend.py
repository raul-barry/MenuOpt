"""
Script de verificación integral de la PARTE 9:
CU17: Crear plano 2D del restaurante (Áreas y Distribución)
CU18: Gestionar mesas
CU19: Definir combinación de mesas
"""
import sys
import json
import time
import urllib.request
import urllib.error
from decimal import Decimal

BASE_URL = "http://localhost:8000"
SUFFIX = str(int(time.time()))[-4:]

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
    print("=== INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - PARTE 9 (BACKEND) ===")

    # 1. Login ADMIN
    c, r = request("POST", "/autenticacion/login", {
        "correo": "admin@menuopt.com",
        "contrasena": "Admin1234!"
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

    # Obtener un restaurante perteneciente a RESTAURANTE 1
    c, mis_restos = request("GET", "/restaurantes/mis-restaurantes", token=resto1_token)
    log_test(3, "Obtener restaurante de usuario 1", c == 200 and len(mis_restos) > 0, f"total={len(mis_restos)}")
    id_restaurante_1 = mis_restos[0]["id_restaurante"]

    # PRUEBA 4: Crear Área 1 (Salón Principal)
    c, area_salon = request("POST", f"/restaurantes/{id_restaurante_1}/areas", {
        "nombre": f"Salón Principal {SUFFIX}",
        "descripcion": "Área principal con climatización",
        "ancho_mapa": 1200,
        "alto_mapa": 700,
        "orden": 1
    }, token=resto1_token)
    log_test(4, "Crear Área 1 (Salón Principal)", c == 201, f"code={c}")
    id_area_salon = area_salon["id_area"]

    # PRUEBA 5: Crear Área 2 (Terraza)
    c, area_terraza = request("POST", f"/restaurantes/{id_restaurante_1}/areas", {
        "nombre": f"Terraza {SUFFIX}",
        "descripcion": "Área al aire libre con vista al jardín",
        "ancho_mapa": 1000,
        "alto_mapa": 600,
        "orden": 2
    }, token=resto1_token)
    log_test(5, "Crear Área 2 (Terraza)", c == 201, f"code={c}")
    id_area_terraza = area_terraza["id_area"]

    # PRUEBA 6: Rechazar nombre duplicado en el mismo restaurante
    c, err_dup = request("POST", f"/restaurantes/{id_restaurante_1}/areas", {
        "nombre": f"Salón Principal {SUFFIX}",
        "ancho_mapa": 1200,
        "alto_mapa": 700
    }, token=resto1_token)
    log_test(6, "Rechazar área duplicada en mismo restaurante", c == 400, f"code={c}")

    # PRUEBA 7: CU17 Generar distribución automática (3 mesas de 2p, 5 mesas de 4p, 2 mesas de 6p = 10 mesas)
    c, dist_auto = request("POST", f"/areas/{id_area_salon}/generar-distribucion", {
        "mesas": [
            {"capacidad": 2, "cantidad": 3},
            {"capacidad": 4, "cantidad": 5},
            {"capacidad": 6, "cantidad": 2}
        ]
    }, token=resto1_token)
    log_test(7, "Generar distribución automática (10 mesas)", c == 200 and dist_auto["total_mesas"] == 10, f"total={dist_auto.get('total_mesas')}")

    # PRUEBA 8: Comprobar que ninguna mesa se superponga inicialmente
    posiciones = [(float(m["posicion_x"]), float(m["posicion_y"])) for m in dist_auto["mesas"]]
    posiciones_unicas = set(posiciones)
    log_test(8, "Comprobar posiciones únicas sin colisión inicial", len(posiciones_unicas) == len(posiciones), f"unicas={len(posiciones_unicas)}/{len(posiciones)}")

    # PRUEBA 9: Modificar mesa individual (CU18)
    mesa_1 = dist_auto["mesas"][0]
    id_m1 = mesa_1["id_mesa"]
    c, m1_mod = request("PUT", f"/mesas/{id_m1}", {
        "nombre": "Mesa Presidencial",
        "rotacion": 90,
        "forma": "RECTANGULAR"
    }, token=resto1_token)
    log_test(9, "Modificar mesa (nombre, rotación 90, forma)", c == 200 and m1_mod["rotacion"] == 90 and m1_mod["forma"] == "RECTANGULAR", f"rot={m1_mod.get('rotacion')}")

    # PRUEBA 10: Guardar distribución modificada masivamente (Drag & drop)
    c, dist_guardada = request("PUT", f"/areas/{id_area_salon}/distribucion", {
        "mesas": [
            {"id_mesa": id_m1, "posicion_x": 0.2500, "posicion_y": 0.3500, "rotacion": 90},
            {"id_mesa": dist_auto["mesas"][1]["id_mesa"], "posicion_x": 0.6000, "posicion_y": 0.7000, "rotacion": 0}
        ]
    }, token=resto1_token)
    log_test(10, "Guardar distribución masiva (CU17)", c == 200, f"code={c}")

    # Verificar persistencia consultando mesas
    c, mesas_actuales = request("GET", f"/areas/{id_area_salon}/mesas", token=resto1_token)
    m1_pers = next(m for m in mesas_actuales if m["id_mesa"] == id_m1)
    log_test(11, "Persistencia: coordenadas conservadas tras guardar",
             float(m1_pers["posicion_x"]) == 0.25 and float(m1_pers["posicion_y"]) == 0.35,
             f"x={m1_pers['posicion_x']}, y={m1_pers['posicion_y']}")

    # PRUEBA 12: Restablecer distribución automática (CU17)
    c, dist_restablecida = request("POST", f"/areas/{id_area_salon}/restablecer-distribucion", token=resto1_token)
    log_test(12, "Restablecer distribución", c == 200 and dist_restablecida["total_mesas"] == 10, f"total={dist_restablecida.get('total_mesas')}")

    # PRUEBA 13: Agregar mesa manual (CU18)
    c, mesa_manual = request("POST", f"/areas/{id_area_salon}/mesas", {
        "numero": f"VIP-{SUFFIX}",
        "capacidad": 8,
        "forma": "RECTANGULAR",
        "posicion_x": 0.8500,
        "posicion_y": 0.8500,
        "es_fija": False,
        "combinable": True
    }, token=resto1_token)
    log_test(13, "Crear mesa manual (CU18)", c == 201 and mesa_manual["numero"] == f"VIP-{SUFFIX}", f"num={mesa_manual.get('numero')}")

    # PRUEBA 14: Rechazar número de mesa duplicado dentro de la misma área
    c, err_mesa_dup = request("POST", f"/areas/{id_area_salon}/mesas", {
        "numero": f"VIP-{SUFFIX}",
        "capacidad": 4
    }, token=resto1_token)
    log_test(14, "Rechazar número de mesa duplicado en el área", c == 400, f"code={c}")

    # PRUEBA 15: Independencia de áreas: Terraza tiene 0 mesas inicialmente
    c, mesas_terraza = request("GET", f"/areas/{id_area_terraza}/mesas", token=resto1_token)
    log_test(15, "Independencia de áreas: Terraza vacía", c == 200 and len(mesas_terraza) == 0, f"total={len(mesas_terraza)}")

    # PRUEBA 16: CU19 Combinar mesas: combinar Mesa 1 y Mesa 2
    id_m2 = dist_auto["mesas"][1]["id_mesa"]
    c, comb = request("POST", f"/areas/{id_area_salon}/combinaciones", {
        "id_mesa_origen": id_m1,
        "id_mesa_destino": id_m2,
        "descripcion": "Mesas de salón contiguas"
    }, token=resto1_token)
    log_test(16, "Crear combinación permitida M1 + M2 (CU19)", c == 201 and comb["capacidad_combinada"] > 0, f"cap_comb={comb.get('capacidad_combinada')}")
    id_comb = comb["id_mesa_combinacion"]

    # PRUEBA 17: Regla de simetría: M2 + M1 debe rechazarse como duplicada
    c, err_sym = request("POST", f"/areas/{id_area_salon}/combinaciones", {
        "id_mesa_origen": id_m2,
        "id_mesa_destino": id_m1
    }, token=resto1_token)
    log_test(17, "Simetría: M2 + M1 rechazada por combinación existente", c == 400, f"code={c}")

    # PRUEBA 18: No combinar mesa fija
    c, mesa_fija = request("POST", f"/areas/{id_area_salon}/mesas", {
        "numero": f"FIJA-{SUFFIX}",
        "capacidad": 4,
        "es_fija": True,
        "combinable": False
    }, token=resto1_token)
    c, err_fija = request("POST", f"/areas/{id_area_salon}/combinaciones", {
        "id_mesa_origen": id_m1,
        "id_mesa_destino": mesa_fija["id_mesa"]
    }, token=resto1_token)
    log_test(18, "Rechazar combinación con mesa fija", c == 400, f"code={c}")

    # PRUEBA 19: No combinar mesas de diferentes áreas
    c, mesa_t1 = request("POST", f"/areas/{id_area_terraza}/mesas", {
        "numero": f"T1-{SUFFIX}",
        "capacidad": 4
    }, token=resto1_token)
    c, err_dist_area = request("POST", f"/areas/{id_area_salon}/combinaciones", {
        "id_mesa_origen": id_m1,
        "id_mesa_destino": mesa_t1["id_mesa"]
    }, token=resto1_token)
    log_test(19, "Rechazar combinación de mesas de áreas distintas", c == 400, f"code={c}")

    # PRUEBA 20: Desactivar combinación (baja lógica)
    c, r_del = request("DELETE", f"/combinaciones/{id_comb}", token=resto1_token)
    log_test(20, "Desactivar combinación", c == 200 and r_del["activo"] is False, f"activo={r_del.get('activo')}")

    # PRUEBA 21: Seguridad de propiedad: Restaurante 2 intenta modificar área de Restaurante 1 -> 403 Forbidden
    c, err_sec_area = request("PUT", f"/areas/{id_area_salon}", {
        "nombre": "Hack Area"
    }, token=resto2_token)
    log_test(21, "Seguridad: Restaurante ajeno recibe 403 en Área", c == 403, f"code={c}")

    # PRUEBA 22: Seguridad de propiedad: Restaurante 2 intenta modificar mesa de Restaurante 1 -> 403 Forbidden
    c, err_sec_mesa = request("PUT", f"/mesas/{id_m1}", {
        "nombre": "Hack Mesa"
    }, token=resto2_token)
    log_test(22, "Seguridad: Restaurante ajeno recibe 403 en Mesa", c == 403, f"code={c}")

    print("\n=======================================================")
    print("TODAS LAS 22 PRUEBAS BACKEND DE LA PARTE 9 PASARON EXITOSAMENTE")
    print("=======================================================")

if __name__ == "__main__":
    run()
