# CASO DE USO: CU26 - Usar asistencia con IA
# Abstracción e implementaciones del Proveedor de IA
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
import re
import urllib.request
import urllib.error

from app.config.settings import settings
from app.ai.prompts import (
    SYSTEM_PROMPT_INTERPRETAR,
    SYSTEM_PROMPT_EXPLICAR_RECOMENDACION,
    SYSTEM_PROMPT_EXPLICAR_COMPARACION
)
from app.ai.parser import ParserIA


class ProveedorIA(ABC):
    """
    Interfaz abstracta del proveedor de Inteligencia Artificial.
    Permite desacoplar MenuOpt de cualquier proveedor específico (Gemini, OpenAI, Anthropic, Mock).
    """

    @abstractmethod
    def interpretar_solicitud(
        self,
        mensaje: str,
        contexto_previo: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Interpreta la solicitud y retorna un diccionario con los campos estructurados."""
        pass

    @abstractmethod
    def explicar_recomendacion(
        self,
        datos_recomendacion: Dict[str, Any]
    ) -> str:
        """Genera una explicación breve y objetiva de una recomendación real."""
        pass

    @abstractmethod
    def explicar_comparacion(
        self,
        datos_comparacion: Dict[str, Any]
    ) -> str:
        """Genera una explicación concisa y objetiva de la comparativa CU14."""
        pass


class MockProveedorIA(ProveedorIA):
    """
    Proveedor simulado de alta fidelidad basado en reglas deterministas y regex.
    Permite funcionamiento autónomo sin requerir claves de API externas, con soporte
    completo de pruebas unitarias y cobertura de requerimientos.
    """

    def interpretar_solicitud(
        self,
        mensaje: str,
        contexto_previo: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        msg_lower = mensaje.lower()

        # Contexto inicial
        ctx = contexto_previo or {}
        presupuesto = ctx.get("presupuesto")
        cantidad_personas = ctx.get("cantidad_personas")
        tipo_comida = ctx.get("tipo_comida")
        ubicacion_referencia = ctx.get("ubicacion_referencia")
        preferencias: List[str] = list(ctx.get("preferencias_detectadas", []))

        # 1. Detectar Presupuesto (ej: "300 bs", "300bs", "tengo 250", "con 150 bs", "presupuesto de 200")
        match_presupuesto = re.search(r"(?:tengo|con|presupuesto(?:\s+de)?|unos)?\s*(\d+(?:[.,]\d{1,2})?)\s*(?:bs|bolivianos)?", msg_lower)
        # Buscar específicamente números asociados a 'bs' o cantidades monetarias
        match_bs = re.search(r"(\d+(?:[.,]\d{1,2})?)\s*(?:bs|bolivianos)", msg_lower)
        if match_bs:
            presupuesto = float(match_bs.group(1).replace(",", "."))
        elif "bs" in msg_lower and match_presupuesto:
            presupuesto = float(match_presupuesto.group(1).replace(",", "."))
        elif not presupuesto:
            # Buscar mención genérica de número si parece presupuesto
            m = re.search(r"(?:presupuesto|tengo|con)\s+(\d+)", msg_lower)
            if m:
                presupuesto = float(m.group(1))

        # 2. Detectar Cantidad de Personas (ej: "somos 10 personas", "para 4", "somos 6", "10 personas", "4 comensales")
        match_personas = re.search(r"(?:somos|para|seremos)?\s*(\d+)\s*(?:personas|comensales|amigos|familiares)?", msg_lower)
        match_directo = re.search(r"(?:somos\s+(\d+)|para\s+(\d+)\s+personas|(\d+)\s+personas)", msg_lower)
        if match_directo:
            val = next(g for g in match_directo.groups() if g is not None)
            cantidad_personas = int(val)
        elif "somos" in msg_lower or "para" in msg_lower:
            m = re.search(r"(?:somos|para)\s+(\d+)", msg_lower)
            if m:
                cantidad_personas = int(m.group(1))

        # 3. Detectar Tipo de Comida (DESAYUNO, ALMUERZO, CENA, MERIENDA)
        if any(w in msg_lower for w in ["almuerzo", "almorzar", "almuerzos"]):
            tipo_comida = "ALMUERZO"
        elif any(w in msg_lower for w in ["cena", "cenar", "cenas"]):
            tipo_comida = "CENA"
        elif any(w in msg_lower for w in ["desayuno", "desayunar"]):
            tipo_comida = "DESAYUNO"
        elif any(w in msg_lower for w in ["merienda", "merendar"]):
            tipo_comida = "MERIENDA"

        # 4. Detectar Ubicación de Referencia (ej: "en Equipetrol", "cerca de Calacoto", "en el centro", "en 16 de julio", "en Santa Cruz")
        match_ub = re.search(r"(?:en|cerca\s+de|por|zona)\s+([0-9A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)(?:[.,]|$)", mensaje)
        if match_ub:
            candidato = match_ub.group(1).strip()
            # Limpiar palabras comunes
            palabras_filtro = ["el almuerzo", "la cena", "familia", "amigos", "comida", "mi móvil", "mi celular", "mi movil"]
            if not any(pf in candidato.lower() for pf in palabras_filtro) and len(candidato) >= 3:
                ubicacion_referencia = candidato.title()

        # 5. Detectar Preferencias (vegetariano, vegano, sin gluten, sin lactosa, keto, silpancho, etc.)
        if "silpancho" in msg_lower and "Silpancho" not in preferencias:
            preferencias.append("Silpancho")

        keywords_pref = {
            "vegetariano": "Vegetariano",
            "vegetariana": "Vegetariano",
            "vegano": "Vegano",
            "vegana": "Vegano",
            "sin gluten": "Sin gluten",
            "celiaco": "Sin gluten",
            "sin lactosa": "Sin lactosa",
            "saludable": "Saludable",
            "keto": "Keto"
        }
        for kw, nombre_canon in keywords_pref.items():
            if kw in msg_lower and nombre_canon not in preferencias:
                preferencias.append(nombre_canon)

        # 6. Evaluar Datos Faltantes
        datos_faltantes = []
        if not presupuesto or presupuesto <= 0:
            datos_faltantes.append("presupuesto")
        if not cantidad_personas or cantidad_personas <= 0:
            datos_faltantes.append("cantidad_personas")
        if not tipo_comida:
            datos_faltantes.append("tipo_comida")
        if not ubicacion_referencia:
            datos_faltantes.append("ubicacion_referencia")

        # 7. Redactar Mensaje Asistente
        if not datos_faltantes:
            mensaje_asistente = (
                f"¡Entendido! He extraído todos los datos necesarios para tu planificación: "
                f"{cantidad_personas} personas, {tipo_comida}, presupuesto de {presupuesto} Bs en {ubicacion_referencia}. "
                f"Revisa el resumen y pulsa 'Crear Planificación'."
            )
        else:
            preguntas = []
            if "presupuesto" in datos_faltantes and "cantidad_personas" in datos_faltantes:
                preguntas.append("¿cuál es tu presupuesto total y para cuántas personas será?")
            elif "presupuesto" in datos_faltantes:
                preguntas.append("¿cuál es tu presupuesto estimado en Bs?")
            elif "cantidad_personas" in datos_faltantes:
                preguntas.append("¿para cuántas personas sería la comida?")
            if "tipo_comida" in datos_faltantes:
                preguntas.append("¿para qué momento del día (almuerzo, cena, desayuno)?")
            if "ubicacion_referencia" in datos_faltantes:
                preguntas.append("¿en qué zona o barrio prefieres buscar?")

            mensaje_asistente = (
                f"He tomado nota de tu solicitud. Para poder ayudarte a planificar, por favor indícame: "
                f"{' '.join(preguntas)}"
            )

        return {
            "presupuesto": presupuesto,
            "cantidad_personas": cantidad_personas,
            "tipo_comida": tipo_comida,
            "ubicacion_referencia": ubicacion_referencia,
            "preferencias_detectadas": preferencias,
            "datos_faltantes": datos_faltantes,
            "mensaje_asistente": mensaje_asistente
        }

    def explicar_recomendacion(self, datos_recomendacion: Dict[str, Any]) -> str:
        costo_total = datos_recomendacion.get("costo_total", 0)
        costo_pp = datos_recomendacion.get("costo_por_persona", 0)
        personas = datos_recomendacion.get("cantidad_personas", 0)
        presupuesto = datos_recomendacion.get("presupuesto", 0)
        ahorro = max(0, float(presupuesto) - float(costo_total))
        nombre = datos_recomendacion.get("nombre", "Esta alternativa")

        return (
            f"{nombre} tiene un costo estimado de {costo_total} Bs para {personas} personas "
            f"({costo_pp} Bs por persona). Esta opción te permite un ahorro de {ahorro:.2f} Bs "
            f"respecto a tu presupuesto límite de {presupuesto} Bs y cumple con las preferencias seleccionadas."
        )

    def explicar_comparacion(self, datos_comparacion: Dict[str, Any]) -> str:
        costo_resto = datos_comparacion.get("costo_restaurante")
        costo_prep = datos_comparacion.get("costo_preparacion")
        diferencia = datos_comparacion.get("diferencia", 0)
        nombre_resto = datos_comparacion.get("nombre_restaurante", "Restaurante")

        if costo_resto is not None and costo_prep is not None:
            if costo_prep < costo_resto:
                return (
                    f"La preparación propia tiene un costo estimado de {costo_prep} Bs, mientras que la "
                    f"alternativa en restaurante ({nombre_resto}) cuesta {costo_resto} Bs. "
                    f"La preparación en casa representa una opción más económica con una diferencia de {diferencia} Bs a tu favor."
                )
            else:
                return (
                    f"La alternativa en restaurante ({nombre_resto}) cuesta {costo_resto} Bs, frente a "
                    f"{costo_prep} Bs de preparación propia. La opción comercial resulta competitiva "
                    f"con una diferencia de {diferencia} Bs."
                )

        return "La comparativa analiza los costos calculados entre las alternativas disponibles."


class GeminiProveedorIA(ProveedorIA):
    """
    Proveedor real para Google Gemini API (v1beta) usando HTTP estándar (urllib) con timeout controlado.
    """

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", timeout: int = 15):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def _invocar_gemini(self, prompt_sistema: str, prompt_usuario: str) -> str:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt_sistema}\n\nSOLICITUD DEL USUARIO:\n{prompt_usuario}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 800
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resultado = json.loads(resp.read().decode("utf-8"))
                candidatos = resultado.get("candidates", [])
                if candidatos and "content" in candidatos[0]:
                    parts = candidatos[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
                return ""
        except Exception as e:
            raise RuntimeError(f"Error al comunicar con la API de Gemini: {str(e)}")

    def interpretar_solicitud(
        self,
        mensaje: str,
        contexto_previo: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        prompt_user = f"Contexto acumulado previo: {json.dumps(contexto_previo or {})}\nMensaje actual: {mensaje}"
        texto_gen = self._invocar_gemini(SYSTEM_PROMPT_INTERPRETAR, prompt_user)
        json_extraido = ParserIA.extraer_json(texto_gen)
        if not json_extraido:
            # Si el modelo no devolvió JSON válido, fallback al mock para no romper FastAPI
            return MockProveedorIA().interpretar_solicitud(mensaje, contexto_previo)
        return json_extraido

    def explicar_recomendacion(self, datos_recomendacion: Dict[str, Any]) -> str:
        prompt_user = f"Datos reales de la recomendación calculada: {json.dumps(datos_recomendacion)}"
        try:
            texto = self._invocar_gemini(SYSTEM_PROMPT_EXPLICAR_RECOMENDACION, prompt_user)
            return texto.strip() if texto.strip() else MockProveedorIA().explicar_recomendacion(datos_recomendacion)
        except Exception:
            return MockProveedorIA().explicar_recomendacion(datos_recomendacion)

    def explicar_comparacion(self, datos_comparacion: Dict[str, Any]) -> str:
        prompt_user = f"Datos reales de la comparación calculada: {json.dumps(datos_comparacion)}"
        try:
            texto = self._invocar_gemini(SYSTEM_PROMPT_EXPLICAR_COMPARACION, prompt_user)
            return texto.strip() if texto.strip() else MockProveedorIA().explicar_comparacion(datos_comparacion)
        except Exception:
            return MockProveedorIA().explicar_comparacion(datos_comparacion)


def obtener_proveedor_ia() -> ProveedorIA:
    """
    Fábrica de proveedor IA según la configuración de variables de entorno.
    """
    if not settings.AI_ENABLED:
        return MockProveedorIA()

    proveedor = (settings.AI_PROVIDER or "mock").lower().strip()
    if proveedor in ("gemini", "google") and settings.AI_API_KEY and settings.AI_API_KEY.strip():
        return GeminiProveedorIA(
            api_key=settings.AI_API_KEY,
            model=settings.AI_MODEL,
            timeout=settings.AI_TIMEOUT_SECONDS
        )

    return MockProveedorIA()
