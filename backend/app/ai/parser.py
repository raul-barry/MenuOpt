# CASO DE USO: CU26 - Usar asistencia con IA
# Parser seguro para interpretar respuestas de modelos LLM y convertirlas a JSON válido
import json
import re
from typing import Dict, Any, Optional


class ParserIA:
    """
    Parser robusto y defensivo para extraer objetos JSON de las respuestas generadas por LLMs,
    soportando bloques markdown (```json ... ```), texto introductorio o JSON directo.
    """

    @staticmethod
    def extraer_json(texto: str) -> Optional[Dict[str, Any]]:
        if not texto or not texto.strip():
            return None

        texto_limpio = texto.strip()

        # 1. Intentar parseo directo
        try:
            return json.loads(texto_limpio)
        except Exception:
            pass

        # 2. Intentar extraer de bloque de código Markdown ```json ... ```
        patron_bloque = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto_limpio, re.DOTALL)
        if patron_bloque:
            try:
                return json.loads(patron_bloque.group(1))
            except Exception:
                pass

        # 3. Intentar extraer el primer bloque entre llaves { ... }
        patron_llaves = re.search(r"(\{.*\})", texto_limpio, re.DOTALL)
        if patron_llaves:
            try:
                return json.loads(patron_llaves.group(1))
            except Exception:
                pass

        return None
