# CASO DE USO: CU17 - Algoritmo matemático para distribución 2D de mesas
import math
import re
from decimal import Decimal
from typing import List, Tuple, Set


def calcular_columnas_y_filas(total_mesas: int) -> Tuple[int, int]:
    """
    Calcula determinísticamente la cuadrícula de distribución:
    columnas = ceil(sqrt(N))
    filas = ceil(N / columnas)
    """
    if total_mesas <= 0:
        return 0, 0
    columnas = math.ceil(math.sqrt(total_mesas))
    filas = math.ceil(total_mesas / columnas)
    return columnas, filas


def generar_posiciones_normalizadas(total_mesas: int) -> List[Tuple[Decimal, Decimal]]:
    """
    Genera coordenadas (posicion_x, posicion_y) normalizadas entre 0.0 y 1.0,
    distribuidas simétricamente sin superposición ni cruces.
    """
    if total_mesas <= 0:
        return []
    if total_mesas == 1:
        return [(Decimal("0.5000"), Decimal("0.5000"))]

    columnas, filas = calcular_columnas_y_filas(total_mesas)
    posiciones: List[Tuple[Decimal, Decimal]] = []

    for i in range(total_mesas):
        fila = i // columnas
        columna = i % columnas

        # x = (columna + 1) / (columnas + 1)
        # y = (fila + 1) / (filas + 1)
        x_val = Decimal(str(round((columna + 1) / (columnas + 1), 4)))
        y_val = Decimal(str(round((fila + 1) / (filas + 1), 4)))

        # Garantizar límites estrictos [0.0, 1.0]
        x_val = max(Decimal("0.0500"), min(Decimal("0.9500"), x_val))
        y_val = max(Decimal("0.0500"), min(Decimal("0.9500"), y_val))

        posiciones.append((x_val, y_val))

    return posiciones


def calcular_siguiente_numero_mesa(numeros_existentes: Set[str], prefijo: str = "M") -> str:
    """
    Busca el correlativo más alto basado en prefijo (ej. M1, M2 -> M3).
    Si hay números personalizados, asigna el primer correlativo disponible.
    """
    max_num = 0
    pattern = re.compile(rf"^{prefijo}(\d+)$", re.IGNORECASE)

    for num in numeros_existentes:
        match = pattern.match(num.strip())
        if match:
            val = int(match.group(1))
            if val > max_num:
                max_num = val

    candidato = max_num + 1
    # Asegurar que no esté en uso
    while f"{prefijo}{candidato}".upper() in {n.upper() for n in numeros_existentes}:
        candidato += 1

    return f"{prefijo}{candidato}"
