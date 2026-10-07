"""
Script de verificación integral de la PARTE 7:
CU15: Consultar ingredientes para preparación propia
CU16: Consultar lugares de compra
CU14: Comparar alternativas (RESTAURANTE vs PREPARACION_PROPIA)
Administración de lugares de compra e ingredientes
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
    print("=== INICIANDO SUITE DE PRUEBAS AUTOMATIZADAS - PARTE 7 ===")

    # 1. Login Admin
    c, r = request("POST", "/autenticacion/login", {
        "correo": "admin@menuopt.com",
        "contrasena": "Admin1234!"
    })
    log_test(0, "Login ADMIN", c == 200, f"code={c}")
    admin_token = r["access_token"]

    # 2. Login Clientes
    email_c1 = f"cliente_p7_1_{SUFFIX}@test.com"
    pwd_c1 = "Pass1234!"
    request("POST", "/autenticacion/registro", {
        "nombres": "Cliente",
        "apellidos": "P7 Uno",
        "correo": email_c1,
        "contrasena": pwd_c1,
        "telefono": f"70{SUFFIX}"
    })
    c, r = request("POST", "/autenticacion/login", {
        "correo": email_c1,
        "contrasena": pwd_c1
    })
    c1_token = r["access_token"]

    email_c2 = f"cliente_p7_2_{SUFFIX}@test.com"
    pwd_c2 = "Pass1234!"
    request("POST", "/autenticacion/registro", {
        "nombres": "Cliente",
        "apellidos": "P7 Dos",
        "correo": email_c2,
        "contrasena": pwd_c2,
        "telefono": f"71{SUFFIX}"
    })
    c, r = request("POST", "/autenticacion/login", {
        "correo": email_c2,
        "contrasena": pwd_c2
    })
    c2_token = r["access_token"]

    # PRUEBA 1: Registrar lugares de compra
    # Lugar A: Mercado Mutualista
    c, lug_a = request("POST", "/lugares-compra", {
        "nombre": f"Mercado Mutualista P7 {SUFFIX}",
        "tipo": "MERCADO",
        "telefono": "71122334",
        "ubicacion": {
            "direccion": "3er Anillo Interno",
            "zona": "Mutualista",
            "ciudad": "Santa Cruz"
        }
    }, token=admin_token)
    log_test(1, "Registrar lugar de compra (Mercado)", c == 201, f"code={c}")
    id_lugar_a = lug_a["id_lugar_compra"]

    # Lugar B: Hipermaxi Norte
    c, lug_b = request("POST", "/lugares-compra", {
        "nombre": f"Hipermaxi Norte P7 {SUFFIX}",
        "tipo": "SUPERMERCADO",
        "telefono": "71122335",
        "ubicacion": {
            "direccion": "Av. Banzer 4to Anillo",
            "zona": "Norte",
            "ciudad": "Santa Cruz"
        }
    }, token=admin_token)
    id_lugar_b = lug_b["id_lugar_compra"]

    # Crear 2 ingredientes en catálogo para receta de referencia:
    # Pollo (kg) y Arroz (kg)
    c, ing_pollo = request("POST", "/ingredientes", {
        "nombre": f"Pollo Entero P7 {SUFFIX}",
        "unidad_medida": "kg",
        "descripcion": "Carne de pollo fresca"
    }, token=admin_token)
    id_ing_pollo = ing_pollo["id_ingrediente"]

    c, ing_arroz = request("POST", "/ingredientes", {
        "nombre": f"Arroz Grano de Oro P7 {SUFFIX}",
        "unidad_medida": "kg",
        "descripcion": "Arroz de grano largo"
    }, token=admin_token)
    id_ing_arroz = ing_arroz["id_ingrediente"]

    # PRUEBA 2 y PRUEBA 3: Relacionar ingrediente con lugar y registrar precio
    # En Mercado A:
    # Pollo: 25.00 Bs / 1 kg (Económico)
    c, r = request("POST", f"/lugares-compra/{id_lugar_a}/ingredientes", {
        "id_ingrediente": id_ing_pollo,
        "precio": 25.00,
        "cantidad_referencia": 1.00,
        "unidad_medida": "kg",
        "disponible": True
    }, token=admin_token)
    log_test(2, "Relacionar ingrediente con lugar (Pollo en Mercado A)", c == 201, f"code={c}")
    log_test(3, "Registrar precio (25 Bs/kg)", c == 201 and Decimal(str(r["precio"])) == Decimal("25.00"), f"precio={r.get('precio')}")

    # En Supermercado B:
    # Pollo: 30.00 Bs / 1 kg (Más caro, para probar selección del menor precio)
    request("POST", f"/lugares-compra/{id_lugar_b}/ingredientes", {
        "id_ingrediente": id_ing_pollo,
        "precio": 30.00,
        "cantidad_referencia": 1.00,
        "unidad_medida": "kg",
        "disponible": True
    }, token=admin_token)

    # Arroz: En Supermercado B está a 12.50 Bs / 1 kg
    request("POST", f"/lugares-compra/{id_lugar_b}/ingredientes", {
        "id_ingrediente": id_ing_arroz,
        "precio": 12.50,
        "cantidad_referencia": 1.00,
        "unidad_medida": "kg",
        "disponible": True
    }, token=admin_token)

    # PRUEBA 4: Cambiar disponibilidad
    c, r = request("PUT", f"/lugares-compra/{id_lugar_b}/ingredientes/{id_ing_pollo}", {
        "disponible": False
    }, token=admin_token)
    log_test(4, "Cambiar disponibilidad de un ingrediente", c == 200 and r["disponible"] is False, f"disp={r.get('disponible')}")

    # Reactivar para no alterar otras pruebas
    request("PUT", f"/lugares-compra/{id_lugar_b}/ingredientes/{id_ing_pollo}", {
        "disponible": True
    }, token=admin_token)

    # PRUEBA 5: Consultar lugares de un ingrediente (GET /ingredientes/{id}/lugares-compra)
    c, r = request("GET", f"/ingredientes/{id_ing_pollo}/lugares-compra", token=c1_token)
    log_test(5, "Consultar lugares activos de un ingrediente", c == 200 and len(r) >= 2 and r[0]["precio"] <= r[1]["precio"], f"lugares={len(r)}")

    # PRUEBA 6: Crear un plato con ingredientes
    # Restaurante y categoría existentes
    c, rest_list = request("GET", "/restaurantes/mis-restaurantes", token=admin_token)
    id_rest = rest_list[0]["id_restaurante"]
    c, cat_list = request("GET", "/categorias", token=admin_token)
    id_cat = cat_list[0]["id_categoria"]

    # Plato: "Pollo al Horno con Arroz Familiar P7"
    # precio comercial: 70 Bs, personas_cubiertas: 5
    # Receta base para 5 personas:
    # 2 kg de Pollo (2 * 25 Bs = 50 Bs)
    # 1 kg de Arroz (1 * 12.50 Bs = 12.50 Bs)
    # Costo insumos para 5 personas: 62.50 Bs
    # Para 20 personas (factor 4):
    # Pollo: 2 * 4 = 8 kg * 25 Bs = 200 Bs
    # Arroz: 1 * 4 = 4 kg * 12.50 Bs = 50 Bs
    nombre_plato_test = f"Pollo al Horno con Arroz Familiar P7 {SUFFIX}"
    c, plato = request("POST", f"/restaurantes/{id_rest}/platos", {
        "nombre": nombre_plato_test,
        "descripcion": "Pollo dorado con guarnición de arroz",
        "precio": 70.00,
        "tipo_comida": "ALMUERZO",
        "personas_cubiertas": 5,
        "disponible": True,
        "id_categoria": id_cat
    }, token=admin_token)
    id_plato = plato["id_plato"]

    # Asociar 2 kg de pollo
    request("POST", f"/platos/{id_plato}/ingredientes", {
        "id_ingrediente": id_ing_pollo,
        "cantidad": 2.00,
        "unidad_medida": "kg"
    }, token=admin_token)

    # Asociar 1 kg de arroz
    request("POST", f"/platos/{id_plato}/ingredientes", {
        "id_ingrediente": id_ing_arroz,
        "cantidad": 1.00,
        "unidad_medida": "kg"
    }, token=admin_token)

    log_test(6, "Crear plato con ingredientes estructurados", plato["id_plato"] > 0)

    # PRUEBA 7: Crear planificación de prueba (Presupuesto 300 Bs, 20 personas, ALMUERZO)
    c, plan = request("POST", "/planificaciones", {
        "presupuesto": 300.00,
        "cantidad_personas": 20,
        "tipo_comida": "ALMUERZO",
        "ubicacion_referencia": "Zona Norte",
        "preferencias": []
    }, token=c1_token)
    log_test(7, "Crear planificación (300 Bs, 20 personas)", c == 201)
    id_plan = plan["id_planificacion"]

    # PRUEBA 8: Generar recomendaciones
    c, recs = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c1_token)
    log_test(8, "Generar recomendaciones", c == 200 and len(recs) >= 2, f"total={len(recs)}")

    # PRUEBA 9: Comprobar alternativa RESTAURANTE
    rec_rest = next((r for r in recs if r["tipo_recomendacion"] == "RESTAURANTE" and any(p["id_plato"] == id_plato for p in r.get("platos", []))), None)
    log_test(9, "Comprobar alternativa RESTAURANTE (Costo 280 Bs, 14 Bs/persona)",
             rec_rest is not None and Decimal(str(rec_rest["costo_total"])) == Decimal("280.00") and Decimal(str(rec_rest["costo_por_persona"])) == Decimal("14.00"),
             f"rec_rest={rec_rest}")

    # PRUEBA 10: Comprobar alternativa PREPARACION_PROPIA
    rec_prep = next((r for r in recs if r["tipo_recomendacion"] == "PREPARACION_PROPIA" and nombre_plato_test in (r.get("nombre") or "")), None)
    log_test(10, "Comprobar alternativa PREPARACION_PROPIA (Costo 250 Bs, 12.50 Bs/persona)",
             rec_prep is not None and Decimal(str(rec_prep["costo_total"])) == Decimal("250.00") and Decimal(str(rec_prep["costo_por_persona"])) == Decimal("12.50"),
             f"rec_prep={rec_prep}")

    id_rec_prep = rec_prep["id_recomendacion"]

    # PRUEBA 11, 12, 13, 14, 15: CU15 Consultar ingredientes para preparación propia
    c, prep_det = request("GET", f"/recomendaciones/{id_rec_prep}/preparacion", token=c1_token)
    log_test(11, "Ver cantidades escaladas (Pollo: 8 kg, Arroz: 4 kg)",
             c == 200 and any(i["id_ingrediente"] == id_ing_pollo and Decimal(str(i["cantidad"])) == Decimal("8.00") for i in prep_det["ingredientes"]),
             f"ingredientes={prep_det.get('ingredientes')}")

    pollo_item = next(i for i in prep_det["ingredientes"] if i["id_ingrediente"] == id_ing_pollo)
    arroz_item = next(i for i in prep_det["ingredientes"] if i["id_ingrediente"] == id_ing_arroz)

    log_test(12, "Ver costo de cada ingrediente (Pollo: 200 Bs, Arroz: 50 Bs)",
             Decimal(str(pollo_item["costo_estimado"])) == Decimal("200.00") and Decimal(str(arroz_item["costo_estimado"])) == Decimal("50.00"),
             f"pollo={pollo_item['costo_estimado']}, arroz={arroz_item['costo_estimado']}")

    log_test(13, "Ver costo total (250 Bs)", Decimal(str(prep_det["costo_estimado"])) == Decimal("250.00"), f"costo={prep_det['costo_estimado']}")
    log_test(14, "Ver costo por persona (12.50 Bs)", Decimal(str(prep_det["costo_por_persona"])) == Decimal("12.50"), f"costo_pp={prep_det['costo_por_persona']}")

    # PRUEBA 16: Selección del precio disponible más económico (Pollo eligió 25 Bs en Mercado A y no 30 Bs en Supermercado B)
    log_test(16, "Comprobar selección del precio más económico (25 Bs vs 30 Bs)",
             pollo_item["id_lugar_compra"] == id_lugar_a and Decimal(str(pollo_item["precio_unitario_usado"])) == Decimal("25.00"),
             f"lugar={pollo_item.get('nombre_lugar_compra')}, precio={pollo_item.get('precio_unitario_usado')}")

    # CU16: Consultar lugares de compra agrupados (PRUEBA 15)
    c, lug_agrup = request("GET", f"/recomendaciones/{id_rec_prep}/lugares-compra", token=c1_token)
    log_test(15, "Ver lugares agrupados por establecimiento (Mercado A y Supermercado B)",
             c == 200 and lug_agrup["total_lugares"] == 2 and Decimal(str(lug_agrup["costo_total_estimado"])) == Decimal("250.00"),
             f"total_lugares={lug_agrup.get('total_lugares')}")

    # PRUEBA 17: Ingrediente sin precio registrado -> Plato no se inventa precio y se excluye de preparación
    c, ing_sin_precio = request("POST", "/ingredientes", {
        "nombre": f"Azafrán Exótico P7 {SUFFIX}",
        "unidad_medida": "g"
    }, token=admin_token)
    id_ing_sin_precio = ing_sin_precio["id_ingrediente"]

    nom_plato_inc = f"Plato Incompleto Sin Precio P7 {SUFFIX}"
    c, plato_incompleto = request("POST", f"/restaurantes/{id_rest}/platos", {
        "nombre": nom_plato_inc,
        "precio": 50.00,
        "tipo_comida": "ALMUERZO",
        "personas_cubiertas": 5,
        "disponible": True,
        "id_categoria": id_cat
    }, token=admin_token)
    request("POST", f"/platos/{plato_incompleto['id_plato']}/ingredientes", {
        "id_ingrediente": id_ing_sin_precio,
        "cantidad": 10.00,
        "unidad_medida": "g"
    }, token=admin_token)

    # Regenerar y validar que "Plato Incompleto Sin Precio P7" NO genere PREPARACION_PROPIA
    c, recs_v2 = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c1_token)
    no_inventa_precio = not any(r["tipo_recomendacion"] == "PREPARACION_PROPIA" and nom_plato_inc in (r.get("nombre") or "") for r in recs_v2)
    log_test(17, "Ingrediente sin precio: la alternativa no inventa precio y se descarta", no_inventa_precio)

    # PRUEBA 18: Ingrediente no disponible -> no genera si no hay stock alternativo
    # Crear plato con ingrediente único disponible solo en Lugar A, y desactivarlo
    c, ing_solo_disp = request("POST", "/ingredientes", {
        "nombre": f"Pera Especial P7 {SUFFIX}",
        "unidad_medida": "kg"
    }, token=admin_token)
    request("POST", f"/lugares-compra/{id_lugar_a}/ingredientes", {
        "id_ingrediente": ing_solo_disp["id_ingrediente"],
        "precio": 15.00,
        "cantidad_referencia": 1.00,
        "unidad_medida": "kg",
        "disponible": False # No disponible
    }, token=admin_token)

    nom_plato_nodisp = f"Plato No Disponible Insumo P7 {SUFFIX}"
    c, plato_nodisp = request("POST", f"/restaurantes/{id_rest}/platos", {
        "nombre": nom_plato_nodisp,
        "precio": 60.00,
        "tipo_comida": "ALMUERZO",
        "personas_cubiertas": 5,
        "disponible": True,
        "id_categoria": id_cat
    }, token=admin_token)
    request("POST", f"/platos/{plato_nodisp['id_plato']}/ingredientes", {
        "id_ingrediente": ing_solo_disp["id_ingrediente"],
        "cantidad": 2.00,
        "unidad_medida": "kg"
    }, token=admin_token)

    c, recs_v3 = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c1_token)
    no_usa_nodisp = not any(r["tipo_recomendacion"] == "PREPARACION_PROPIA" and nom_plato_nodisp in (r.get("nombre") or "") for r in recs_v3)
    log_test(18, "Ingrediente no disponible: se maneja correctamente y se descarta", no_usa_nodisp)

    # PRUEBA 19: Unidades incompatibles (ej. receta en gramos vs precio en kg sin conversión inventada)
    c, ing_unidad = request("POST", "/ingredientes", {
        "nombre": f"Sal Marina P7 {SUFFIX}",
        "unidad_medida": "g"
    }, token=admin_token)
    # Registrar precio en 'bolsa' o 'litro'
    request("POST", f"/lugares-compra/{id_lugar_a}/ingredientes", {
        "id_ingrediente": ing_unidad["id_ingrediente"],
        "precio": 5.00,
        "cantidad_referencia": 1.00,
        "unidad_medida": "litro", # Incompatible con 'g'
        "disponible": True
    }, token=admin_token)

    nom_plato_unid = f"Plato Unidad Incompatible P7 {SUFFIX}"
    c, plato_unid = request("POST", f"/restaurantes/{id_rest}/platos", {
        "nombre": nom_plato_unid,
        "precio": 45.00,
        "tipo_comida": "ALMUERZO",
        "personas_cubiertas": 5,
        "disponible": True,
        "id_categoria": id_cat
    }, token=admin_token)
    request("POST", f"/platos/{plato_unid['id_plato']}/ingredientes", {
        "id_ingrediente": ing_unidad["id_ingrediente"],
        "cantidad": 50.00,
        "unidad_medida": "g"
    }, token=admin_token)

    c, recs_v4 = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c1_token)
    no_inventa_unidades = not any(r["tipo_recomendacion"] == "PREPARACION_PROPIA" and nom_plato_unid in (r.get("nombre") or "") for r in recs_v4)
    log_test(19, "Unidades incompatibles: no inventa conversiones y se descarta", no_inventa_unidades)

    # PRUEBA 20 y 21: CU14 Comparar Restaurante vs Preparación Propia y calcular Ahorro
    c, comp = request("GET", f"/planificaciones/{id_plan}/comparacion", token=c1_token)
    alt_rest = next((a for a in comp["alternativas"] if a["tipo_recomendacion"] == "RESTAURANTE" and Decimal(str(a["costo_total"])) == Decimal("280.00")), None)
    alt_prep = next((a for a in comp["alternativas"] if a["tipo_recomendacion"] == "PREPARACION_PROPIA" and Decimal(str(a["costo_total"])) == Decimal("250.00")), None)

    log_test(20, "CU14 Comparar alternativas (RESTAURANTE vs PREPARACION_PROPIA)",
             c == 200 and alt_rest is not None and alt_prep is not None,
             f"total_alt={comp.get('total_alternativas')}, alt_rest={alt_rest is not None}, alt_prep={alt_prep is not None}")

    ahorro_rest = Decimal(str(alt_rest["ahorro_respecto_presupuesto"]))
    ahorro_prep = Decimal(str(alt_prep["ahorro_respecto_presupuesto"]))
    log_test(21, "Comprobar cálculo de ahorros (Restaurante: 20 Bs, Preparación propia: 50 Bs)",
             ahorro_rest == Decimal("20.00") and ahorro_prep == Decimal("50.00"),
             f"ahorro_rest={ahorro_rest}, ahorro_prep={ahorro_prep}")

    # PRUEBA 22: Regenerar recomendaciones -> No deben duplicarse
    c, recs_dup = request("POST", f"/planificaciones/{id_plan}/recomendaciones/generar", token=c1_token)
    c, comp_dup = request("GET", f"/planificaciones/{id_plan}/comparacion", token=c1_token)
    log_test(22, "Regenerar recomendaciones: reemplazo transaccional sin duplicación",
             c == 200 and len(recs_dup) == comp_dup["total_alternativas"],
             f"total={comp_dup.get('total_alternativas')}")

    # PRUEBA 23: Intentar acceder a preparación de otro usuario -> 403 Forbidden
    id_rec_actual_prep = next(r["id_recomendacion"] for r in recs_dup if r["tipo_recomendacion"] == "PREPARACION_PROPIA")
    c, r = request("GET", f"/recomendaciones/{id_rec_actual_prep}/preparacion", token=c2_token)
    log_test(23, "Seguridad de titularidad: cliente ajeno recibe 403 Forbidden", c == 403, f"code={c}")

    print("\n=======================================================")
    print("TODAS LAS 23 PRUEBAS ESPECÍFICAS DE LA PARTE 7 PASARON EXITOSAMENTE")
    print("=======================================================")

if __name__ == "__main__":
    run()
