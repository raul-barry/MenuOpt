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

        # 4. Recuperación defensiva si el JSON fue cortado por límite de tokens
        pos_inicio = texto_limpio.find("{")
        if pos_inicio != -1:
            segmento = texto_limpio[pos_inicio:]
            # Intentar cerrar comillas y llaves si se quedó abierto
            for cierre in ['"}', '"]}', '"\n}', '\n}']:
                try:
                    return json.loads(segmento + cierre)
                except Exception:
                    continue

            # Extracción manual por regex de los campos esenciales
            resultado_salvado: Dict[str, Any] = {}
            m_int = re.search(r'"intencion"\s*:\s*"([^"]+)"', segmento)
            if m_int:
                resultado_salvado["intencion"] = m_int.group(1)

            m_msg = re.search(r'"mensaje_asistente"\s*:\s*"(.*)', segmento, re.DOTALL)
            if m_msg:
                msg_val = m_msg.group(1)
                # Limpiar terminaciones residuales
                msg_val = re.sub(r'"\s*,?\s*"\w+.*$', "", msg_val, flags=re.DOTALL)
                msg_val = re.sub(r'"\s*\}\s*$', "", msg_val)
                msg_val = msg_val.replace('\\"', '"').replace('\\n', '\n')
                if len(msg_val.strip()) > 10:
                    resultado_salvado["mensaje_asistente"] = msg_val.strip()
                    resultado_salvado.setdefault("intencion", "RECETA")
                    resultado_salvado.setdefault("datos_faltantes", [])
                    return resultado_salvado

        return None
