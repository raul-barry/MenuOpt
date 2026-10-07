# CASO DE USO: CU13 - Generar recomendación
# Algoritmo de optimización y cálculo gastronómico
import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Set


def calcular_cantidad_necesaria(cantidad_personas: int, personas_cubiertas: int) -> int:
    """
    Calcula la cantidad entera de porciones o platos requeridos para cubrir
    a todos los comensales: ceil(cantidad_personas / personas_cubiertas).
    """
    if personas_cubiertas <= 0:
        personas_cubiertas = 1
    return math.ceil(cantidad_personas / personas_cubiertas)


def calcular_costo_total(precio_unitario: Decimal, cantidad: int) -> Decimal:
    """
    Calcula el subtotal o costo total para una cantidad dada de platos.
    """
    return (Decimal(precio_unitario) * Decimal(cantidad)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_costo_por_persona(costo_total: Decimal, cantidad_personas: int) -> Decimal:
    """
    Calcula el costo prorrateado por comensal.
    """
    if cantidad_personas <= 0:
        return Decimal("0.00")
    return (Decimal(costo_total) / Decimal(cantidad_personas)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def cumple_todas_las_preferencias(
    preferencias_requeridas: Set[int],
    preferencias_plato: Set[int]
) -> bool:
    """
    Verifica si el plato cumple con TODAS las preferencias requeridas por la planificación.
    Si la planificación no tiene preferencias declaradas, cualquier plato califica.
    """
    if not preferencias_requeridas:
        return True
    return preferencias_requeridas.issubset(preferencias_plato)


def calcular_puntuacion(presupuesto: Decimal, costo_total: Decimal) -> Decimal:
    """
    Calcula la puntuación (score 0.00 a 100.00) de la alternativa.
    Prioriza opciones dentro del presupuesto, premiando la eficiencia económica (ahorro).
    Fórmula acotada determinista:
      50.0 + 50.0 * (ahorro / presupuesto)
    Rango estrictamente acotado entre 0.00 y 100.00.
    """
    if presupuesto <= Decimal("0.00"):
        return Decimal("0.00")

    if costo_total > presupuesto:
        # Si excede el presupuesto la puntuación es 0.00
        return Decimal("0.00")

    ahorro = presupuesto - costo_total
    ratio_ahorro = float(ahorro) / float(presupuesto)
    puntuacion = 50.0 + (50.0 * ratio_ahorro)

    # Asegurar cota estricta [0.00, 100.00]
    puntuacion_acotada = max(0.0, min(100.0, puntuacion))
    return Decimal(str(puntuacion_acotada)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# =========================================================================
# FUNCIONES DE CÁLCULO PARA PREPARACIÓN PROPIA (CU14 / CU15 / CU16)
# =========================================================================

def calcular_factor_preparacion(cantidad_personas: int, personas_cubiertas: int) -> int:
    """
    Calcula el factor de escala de la receta base para cubrir a los comensales:
    ceil(cantidad_personas / personas_cubiertas).
    """
    return calcular_cantidad_necesaria(cantidad_personas, personas_cubiertas)


def calcular_cantidad_ingrediente(cantidad_receta: Decimal, factor: int) -> Decimal:
    """
    Calcula la cantidad total de un ingrediente multiplicando la cantidad base por el factor.
    """
    return (Decimal(cantidad_receta) * Decimal(factor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def son_unidades_compatibles(unidad_receta: str, unidad_precio: str) -> bool:
    """
    Verifica compatibilidad estricta de unidades de medida (sin conversiones inventadas).
    Ejemplo: 'kg' y 'kg' son compatibles. 'g' y 'kg' no son compatibles automáticamente.
    """
    if not unidad_receta or not unidad_precio:
        return False
    return unidad_receta.strip().lower() == unidad_precio.strip().lower()


def calcular_costo_ingrediente(
    cantidad_total: Decimal,
    cantidad_referencia: Decimal,
    precio: Decimal
) -> Decimal:
    """
    Calcula el costo del ingrediente en función del precio y cantidad de referencia registrada:
    costo = (cantidad_total / cantidad_referencia) * precio.
    """
    if cantidad_referencia <= Decimal("0.00"):
        return Decimal("0.00")
    costo = (Decimal(cantidad_total) / Decimal(cantidad_referencia)) * Decimal(precio)
    return costo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

