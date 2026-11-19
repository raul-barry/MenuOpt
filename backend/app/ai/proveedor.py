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
    SYSTEM_PROMPT_EXPLICAR_COMPARACION,
    SYSTEM_PROMPT_RECETA_COTIZADA,
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


    @abstractmethod
    def orientar_sobre_receta(self, mensaje: str, datos_verificados: Dict[str, Any]) -> str:
        """Redacta una orientaciÃ³n culinaria basada en receta y precios verificados."""
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

        # Detección de consulta de recetas o elaboración casera
        palabras_receta = ["ingrediente", "ingredientes", "receta", "recetas", "prepararme", "cocinar", "podria prepararme", "podría prepararme", "que puedo preparar", "qué puedo preparar", "despensa", "hamburguesa", "hamburguesas", "precio", "tienda", "tiendas"]
        if ("hamburguesa" in msg_lower or "hamburguesas" in msg_lower) and any(w in msg_lower for w in ["ingrediente", "ingredientes", "tienda", "tiendas", "precio", "preparar", "comprar"]):
            return {
                "intencion": "RECETA",
                "presupuesto": None,
                "cantidad_personas": None,
                "tipo_comida": None,
                "ubicacion_referencia": None,
                "preferencias_detectadas": [],
                "ingredientes_mencionados": [
                    "Carne Molida Especial",
                    "Queso Chaqueño Criollo",
                    "Huevos de Granja Seleccionados",
                    "Tomate Manzano Criollo",
                    "Cebolla Roja Seleccionada",
                    "Aceite Vegetal Fino"
                ],
                "datos_faltantes": [],
                "mensaje_asistente": (
                    "### 🍔 Ingredientes para Hamburguesas Caseras (4 porciones) y Mejores Precios:\n\n"
                    "• **Carne Molida Especial (500 g):** **Mercado Abasto Mayorista** a **Bs 34.00/kg** (o Carnicería y Frial San Carlos a Bs 35.00/kg).\n"
                    "• **Queso Chaqueño Criollo (150 g):** **Mercado Los Pozos - Sector Abarrotes** a **Bs 30.00/kg** (o Frial San Carlos a Bs 32.00/kg).\n"
                    "• **Huevos de Granja (1 unidad):** **Distribuidora Avícola Sofía Central** a **Bs 11.50/docena**.\n"
                    "• **Tomate Manzano Criollo (2 unid.):** **Mercado Abasto Mayorista** a **Bs 6.00/kg**.\n"
                    "• **Cebolla Roja (1 unid.):** **Mercado Abasto Mayorista** a **Bs 5.00/kg**.\n"
                    "• **Aceite Vegetal Fino:** **Mercado Abasto Mayorista** a **Bs 13.00/litro**.\n\n"
                    "📍 **Ruta más económica recomendada:**\n"
                    "El **Mercado Abasto Mayorista** concentra la carne molida, verduras y aceite con el mayor ahorro de la ciudad. Para el queso chaqueño, el **Mercado Los Pozos** o el **Frial San Carlos** en el centro te darán el mejor precio.\n\n"
                    "👩‍🍳 **Pasos breves de preparación:**\n"
                    "1. Sazona la carne molida con cebolla finamente picada, huevo, sal y pimienta. Forma 4 medallones.\n"
                    "2. Cocina en sartén caliente con poco aceite 4 minutos por lado.\n"
                    "3. Coloca el queso chaqueño encima en el último minuto para que gratine.\n"
                    "4. Monta con tomate fresco y pan tostado."
                )
            }

        if any(w in msg_lower for w in palabras_receta):
            return {
                "intencion": "RECETA",
                "presupuesto": None,
                "cantidad_personas": None,
                "tipo_comida": None,
                "ubicacion_referencia": None,
                "preferencias_detectadas": [],
                "ingredientes_mencionados": [],
                "datos_faltantes": [],
                "mensaje_asistente": (
                    "Con los ingredientes que tienes a mano puedes preparar excelentes opciones caseras:\n\n"
                    "1. **Arroz con pollo y verduras:** Saltea la cebolla y tomate picado, añade la pechuga en cubos hasta dorar y mezcla con el arroz cocido.\n\n"
                    "2. **Tortilla de huevo y pollo con guarnición:** Bate los huevos, mezcla con pollo desmenuzado, cocínalo a la sartén y acompaña con arroz y ensalada de tomate y cebolla.\n\n"
                    "3. **Salteado rápido de pechuga:** Saltea la pechuga en tiras con cebolla y tomate a fuego vivo, acompañado de una porción de arroz caliente.\n\n"
                    "¡Son preparaciones fáciles, ricas y aprovechan al máximo tus ingredientes disponibles!"
                )
            }

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

        # 4. Detectar Ubicación de Referencia (ej: "en Equipetrol", "en el centro", "centro", "cerca de Calacoto")
        match_ub = re.search(r"(?:en|cerca\s+de|por|zona)\s+(?:el\s+|la\s+|los\s+|las\s+)?([0-9A-Za-zÁÉÍÓÚáéíóúñÑ\s]+?)(?:[.,]|$)", mensaje, re.IGNORECASE)
        if match_ub:
            candidato = match_ub.group(1).strip()
            palabras_filtro = ["almuerzo", "cena", "desayuno", "familia", "amigos", "comida", "mi móvil", "mi celular", "mi movil"]
            if not any(pf in candidato.lower() for pf in palabras_filtro) and len(candidato) >= 2:
                ubicacion_referencia = candidato.title()
        elif not ubicacion_referencia:
            msg_clean = re.sub(r"^(?:en|por|cerca\s+de|zona)\s+", "", mensaje.strip(), flags=re.IGNORECASE)
            msg_clean = re.sub(r"^(?:el|la|los|las)\s+", "", msg_clean.strip(), flags=re.IGNORECASE).strip()
            if len(msg_clean) >= 3 and not any(w in msg_clean.lower() for w in ["almuerzo", "cena", "desayuno", "personas", "bs", "bolivianos"]):
                ubicacion_referencia = msg_clean.title()

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
        num_pres = None
        if presupuesto is not None:
            try:
                num_pres = float(str(presupuesto).replace(",", "."))
            except (ValueError, TypeError):
                num_pres = None

        num_pers = None
        if cantidad_personas is not None:
            try:
                num_pers = int(str(cantidad_personas))
            except (ValueError, TypeError):
                num_pers = None

        datos_faltantes = []
        if num_pres is None or num_pres <= 0:
            datos_faltantes.append("presupuesto")
        if num_pers is None or num_pers <= 0:
            datos_faltantes.append("cantidad_personas")
        if not tipo_comida:
            datos_faltantes.append("tipo_comida")
        if not ubicacion_referencia:
            datos_faltantes.append("ubicacion_referencia")

        # 7. Redactar Mensaje Asistente (Modo conciso sin desperdicio de tokens)
        if not datos_faltantes:
            mensaje_asistente = (
                f"Datos registrados: {num_pers} personas, {tipo_comida or 'comida'}, "
                f"{num_pres} Bs en {ubicacion_referencia}."
            )
        else:
            preguntas = []
            if "presupuesto" in datos_faltantes and "cantidad_personas" in datos_faltantes:
                preguntas.append("¿cuál es tu presupuesto y para cuántas personas?")
            elif "presupuesto" in datos_faltantes:
                preguntas.append("¿cuál es tu presupuesto estimado en Bs?")
            elif "cantidad_personas" in datos_faltantes:
                preguntas.append("¿para cuántas personas sería?")
            if "tipo_comida" in datos_faltantes:
                preguntas.append("¿qué comida (almuerzo, cena, desayuno)?")
            if "ubicacion_referencia" in datos_faltantes:
                preguntas.append("¿en qué zona o barrio prefieres buscar?")

            capturados = []
            if num_pres:
                capturados.append(f"{num_pres} Bs")
            if num_pers:
                capturados.append(f"{num_pers} personas")
            if tipo_comida:
                capturados.append(tipo_comida.lower())
            if ubicacion_referencia:
                capturados.append(ubicacion_referencia)

            prefijo = f"Registrado: {', '.join(capturados)}. " if capturados else ""
            mensaje_asistente = f"{prefijo}{' '.join(preguntas)}"

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


    def orientar_sobre_receta(self, mensaje: str, datos_verificados: Dict[str, Any]) -> str:
        receta = datos_verificados.get("receta")
        if not receta:
            return (
                "No encontrÃ© una receta de la biblioteca que coincida con esos ingredientes. "
                "Prueba indicando ingredientes del catÃ¡logo, por ejemplo arroz, tomate, cebolla o pollo."
            )

        personas = datos_verificados.get("comensales", 2)
        partes = [f"## {receta.get('nombre', 'Sugerencia culinaria')}",
                  f"Receta de {receta.get('tipo_comida', 'comida').lower()} para {personas} persona(s)."]
        disponibles = datos_verificados.get("ingredientes_disponibles", [])
        if disponibles:
            partes.append("**Tienes:** " + ", ".join(disponibles) + ".")

        faltantes = datos_verificados.get("ingredientes_faltantes", [])
        if faltantes:
            partes.append("**Te falta comprar:**")
            for item in faltantes:
                linea = f"- {item['nombre']}: {item['cantidad']} {item['unidad']}"
                if item.get("tienda"):
                    linea += f" en {item['tienda']}"
                if item.get("precio") is not None:
                    linea += f" (precio registrado: Bs {item['precio']})"
                elif not item.get("tienda"):
                    linea += " (sin precio de tienda registrado)"
                partes.append(linea + ".")
        else:
            partes.append("Con los ingredientes indicados tienes lo necesario para esta receta.")

        instrucciones = receta.get("instrucciones")
        if instrucciones:
            partes.extend(["**PreparaciÃ³n:**", instrucciones])
        return "\n\n".join(partes)


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
        data = json.dumps(payload, default=str).encode("utf-8")
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
        prompt_user = f"Contexto acumulado previo: {json.dumps(contexto_previo or {}, default=str)}\nMensaje actual: {mensaje}"
        try:
            texto_gen = self._invocar_gemini(SYSTEM_PROMPT_INTERPRETAR, prompt_user)
            json_extraido = ParserIA.extraer_json(texto_gen)
            if not json_extraido:
                # Si el modelo no devolvió JSON válido, fallback al mock para no romper FastAPI
                return MockProveedorIA().interpretar_solicitud(mensaje, contexto_previo)
            return json_extraido
        except Exception:
            # Fallback defensivo si hay error de cuota o red con la API
            return MockProveedorIA().interpretar_solicitud(mensaje, contexto_previo)

    def explicar_recomendacion(self, datos_recomendacion: Dict[str, Any]) -> str:
        prompt_user = f"Datos reales de la recomendación calculada: {json.dumps(datos_recomendacion, default=str)}"
        try:
            texto = self._invocar_gemini(SYSTEM_PROMPT_EXPLICAR_RECOMENDACION, prompt_user)
            return texto.strip() if texto.strip() else MockProveedorIA().explicar_recomendacion(datos_recomendacion)
        except Exception:
            return MockProveedorIA().explicar_recomendacion(datos_recomendacion)

    def explicar_comparacion(self, datos_comparacion: Dict[str, Any]) -> str:
        prompt_user = f"Datos reales de la comparación calculada: {json.dumps(datos_comparacion, default=str)}"
        try:
            texto = self._invocar_gemini(SYSTEM_PROMPT_EXPLICAR_COMPARACION, prompt_user)
            return texto.strip() if texto.strip() else MockProveedorIA().explicar_comparacion(datos_comparacion)
        except Exception:
            return MockProveedorIA().explicar_comparacion(datos_comparacion)


    def orientar_sobre_receta(self, mensaje: str, datos_verificados: Dict[str, Any]) -> str:
        prompt = json.dumps(
            {"consulta_usuario": mensaje, "datos_verificados": datos_verificados},
            default=str,
            ensure_ascii=False,
        )
        try:
            texto = self._invocar_gemini(SYSTEM_PROMPT_RECETA_COTIZADA, prompt).strip()
            return texto or MockProveedorIA().orientar_sobre_receta(mensaje, datos_verificados)
        except Exception:
            return MockProveedorIA().orientar_sobre_receta(mensaje, datos_verificados)


class GroqProveedorIA(ProveedorIA):
    """
    Proveedor real de ultra-alta velocidad para Groq Cloud API (OpenAI-compatible) usando HTTP estándar (urllib).
    Modelos soportados con auto-detección y tolerancia a fallos:
    - 'openai/gpt-oss-120b' (Máxima capacidad de razonamiento y JSON estructurado)
    - 'openai/gpt-oss-20b' (Respuesta instantánea y liviana)
    - 'llama-3.3-70b-versatile'
    - 'allam-2-7b'
    - 'llama-3.1-8b-instant'
    """

    MODELOS_CANDIDATOS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "allam-2-7b",
        "llama-3.1-8b-instant"
    ]

    def __init__(self, api_key: str, model: str = "openai/gpt-oss-120b", timeout: int = 15):
        self.api_key = api_key
        self.model = model or "openai/gpt-oss-120b"
        self.timeout = timeout
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def _invocar_groq(self, prompt_sistema: str, prompt_usuario: str) -> str:
        modelos_a_probar = [self.model] + [m for m in self.MODELOS_CANDIDATOS if m != self.model]
        ultimo_error = None

        for modelo_actual in modelos_a_probar:
            payload = {
                "model": modelo_actual,
                "messages": [
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                "temperature": 0.1,
                "max_tokens": 1600
            }
            data = json.dumps(payload, default=str).encode("utf-8")
            req = urllib.request.Request(
                self.endpoint,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "MenuOpt/1.0"
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    resultado = json.loads(resp.read().decode("utf-8"))
                    choices = resultado.get("choices", [])
                    if choices and "message" in choices[0]:
                        self.model = modelo_actual
                        return choices[0]["message"].get("content", "")
                    return ""
            except urllib.error.HTTPError as e:
                ultimo_error = e
                # Probar el siguiente modelo candidato si es 404 (no existe) o 429 (rate limit) o 400
                if e.code in (400, 404, 429):
                    continue
                raise RuntimeError(f"Error al comunicar con la API de Groq: HTTP {e.code} {e.reason}")
            except Exception as e:
                ultimo_error = e
                raise RuntimeError(f"Error al comunicar con la API de Groq: {str(e)}")

        raise RuntimeError(f"Error al comunicar con la API de Groq: {str(ultimo_error)}")

    def interpretar_solicitud(
        self,
        mensaje: str,
        contexto_previo: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        ctx = dict(contexto_previo or {})
        catalogo_tiendas = ctx.pop("catalogo_tiendas_ingredientes", None)
        catalogo_restaurantes = ctx.pop("catalogo_restaurantes_platos", None)
        partes_prompt = []
        if catalogo_tiendas:
            partes_prompt.append(f"### Catálogo de Tiendas e Ingredientes Disponibles en BD (Precios Reales en Santa Cruz):\n{catalogo_tiendas}")
        if catalogo_restaurantes:
            partes_prompt.append(f"### Catálogo de Restaurantes y Menús Disponibles en BD:\n{catalogo_restaurantes}")
        if ctx:
            partes_prompt.append(f"Contexto acumulado previo:\n{json.dumps(ctx, default=str, ensure_ascii=False)}")
        partes_prompt.append(f"Mensaje del usuario:\n{mensaje}")
        prompt_user = "\n\n".join(partes_prompt)

        try:
            texto_gen = self._invocar_groq(SYSTEM_PROMPT_INTERPRETAR, prompt_user)
            json_extraido = ParserIA.extraer_json(texto_gen)
            if not json_extraido:
                return MockProveedorIA().interpretar_solicitud(mensaje, contexto_previo)
            return json_extraido
        except Exception:
            return MockProveedorIA().interpretar_solicitud(mensaje, contexto_previo)

    def explicar_recomendacion(self, datos_recomendacion: Dict[str, Any]) -> str:
        prompt_user = f"Datos reales de la recomendación calculada: {json.dumps(datos_recomendacion, default=str)}"
        try:
            texto = self._invocar_groq(SYSTEM_PROMPT_EXPLICAR_RECOMENDACION, prompt_user)
            return texto.strip() if texto.strip() else MockProveedorIA().explicar_recomendacion(datos_recomendacion)
        except Exception:
            return MockProveedorIA().explicar_recomendacion(datos_recomendacion)

    def explicar_comparacion(self, datos_comparacion: Dict[str, Any]) -> str:
        prompt_user = f"Datos reales de la comparación calculada: {json.dumps(datos_comparacion, default=str)}"
        try:
            texto = self._invocar_groq(SYSTEM_PROMPT_EXPLICAR_COMPARACION, prompt_user)
            return texto.strip() if texto.strip() else MockProveedorIA().explicar_comparacion(datos_comparacion)
        except Exception:
            return MockProveedorIA().explicar_comparacion(datos_comparacion)


    def orientar_sobre_receta(self, mensaje: str, datos_verificados: Dict[str, Any]) -> str:
        prompt = json.dumps(
            {"consulta_usuario": mensaje, "datos_verificados": datos_verificados},
            default=str,
            ensure_ascii=False,
        )
        try:
            texto = self._invocar_groq(SYSTEM_PROMPT_RECETA_COTIZADA, prompt).strip()
            return texto or MockProveedorIA().orientar_sobre_receta(mensaje, datos_verificados)
        except Exception:
            return MockProveedorIA().orientar_sobre_receta(mensaje, datos_verificados)


class GrokProveedorIA(GroqProveedorIA):
    """Proveedor para xAI Grok mediante su endpoint compatible con OpenAI."""

    MODELOS_CANDIDATOS = []

    def __init__(self, api_key: str, model: str = "grok-4.7", timeout: int = 30):
        super().__init__(api_key=api_key, model=model or "grok-4.7", timeout=timeout)
        self.endpoint = "https://api.x.ai/v1/chat/completions"

    def _invocar_groq(self, prompt_sistema: str, prompt_usuario: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario},
            ],
            "temperature": 0.1,
            "max_tokens": 1600,
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload, default=str).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "MenuOpt/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                resultado = json.loads(response.read().decode("utf-8"))
            choices = resultado.get("choices", [])
            if choices and "message" in choices[0]:
                return choices[0]["message"].get("content", "")
            return ""
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"Error al comunicar con la API de xAI: HTTP {error.code} {error.reason}")
        except Exception as error:
            raise RuntimeError(f"Error al comunicar con la API de xAI: {str(error)}")


def obtener_proveedor_ia() -> ProveedorIA:
    """
    Fábrica de proveedor IA según la configuración de variables de entorno.
    Soporta:
    - 'groq': Groq Cloud API (Llama 3.3 70B Versatile, Llama 3.1 8B, etc.)
    - 'grok' o 'xai': xAI Grok API
    - 'gemini' o 'google': Google Gemini API (Gemini 1.5 Flash, etc.)
    - 'mock': Simulador autónomo determinista

    Detección automática: si la API key empieza con 'gsk_', se activa Groq automáticamente.
    """
    if not settings.AI_ENABLED:
        return MockProveedorIA()

    api_key_limpia = (settings.AI_API_KEY or "").strip()
    proveedor = (settings.AI_PROVIDER or "mock").lower().strip()

    if not api_key_limpia or proveedor == "mock_forced":
        return MockProveedorIA()

    if proveedor in ("grok", "xai", "x.ai"):
        return GrokProveedorIA(
            api_key=api_key_limpia,
            model=settings.AI_MODEL or "grok-4.7",
            timeout=settings.AI_TIMEOUT_SECONDS,
        )

    # 1. Detección o selección de Groq (clave inicia típicamente con 'gsk_')
    if proveedor in ("groq", "llama") or api_key_limpia.startswith("gsk_"):
        modelo = settings.AI_MODEL if settings.AI_MODEL else "openai/gpt-oss-120b"
        return GroqProveedorIA(
            api_key=api_key_limpia,
            model=modelo,
            timeout=settings.AI_TIMEOUT_SECONDS
        )

    # 2. Detección o selección de Gemini / Google (clave inicia con 'AIzaSy')
    if proveedor in ("gemini", "google") or api_key_limpia.startswith("AIzaSy"):
        modelo = settings.AI_MODEL if (settings.AI_MODEL and "gemini" in settings.AI_MODEL.lower()) else "gemini-1.5-flash"
        return GeminiProveedorIA(
            api_key=api_key_limpia,
            model=modelo,
            timeout=settings.AI_TIMEOUT_SECONDS
        )

    # 3. Fallback genérico a Groq si la key existe
    if api_key_limpia:
        return GroqProveedorIA(
            api_key=api_key_limpia,
            model=settings.AI_MODEL or "openai/gpt-oss-120b",
            timeout=settings.AI_TIMEOUT_SECONDS
        )

    return MockProveedorIA()
