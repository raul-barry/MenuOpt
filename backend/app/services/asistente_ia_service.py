# CASO DE USO: CU26 - Usar asistencia con IA
# Servicio de orquestación segura entre la IA, Pydantic y los servicios de MenuOpt
from decimal import Decimal
from typing import Optional, Dict, Any, List
import logging
import math
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.config.settings import settings
from app.models.usuario import Usuario
from app.models.plato import Plato
from app.models.restaurante import Restaurante
from app.repositories.preferencia_repository import PreferenciaRepository
from app.repositories.recomendacion_repository import RecomendacionRepository
from app.repositories.planificacion_repository import PlanificacionRepository
from app.security.propiedad import verificar_propiedad_planificacion
from app.services.recomendacion_service import RecomendacionService
from app.ai.proveedor import obtener_proveedor_ia
from app.ai.schemas import (
    SolicitudInterpretar,
    SolicitudInterpretada,
    PreferenciaCoincidencia,
    ExplicacionRespuesta
)

logger = logging.getLogger(__name__)


class AsistenteIAService:
    """
    Servicio backend para la asistencia con IA (CU26).
    Garantiza que la IA solo interprete y explique, validando todas las salidas con Pydantic
    y cruzando preferencias detectadas contra la base de datos PostgreSQL.
    """

    TIPOS_PERMITIDOS = {"DESAYUNO", "ALMUERZO", "CENA", "MERIENDA", "OTRO"}

    @classmethod
    def interpretar_solicitud(
        cls,
        db: Session,
        solicitud: SolicitudInterpretar,
        usuario_actual: Usuario
    ) -> SolicitudInterpretada:
        """
        CU26: Interpreta una solicitud en lenguaje natural.
        - Valida el modo sin IA (AI_ENABLED).
        - Consulta el proveedor abstracto (Gemini / Mock).
        - Valida y normaliza la salida (presupuesto, personas, tipo_comida).
        - Cruza preferencias detectadas con el catálogo real en PostgreSQL.
        - Determina si la información está completa para ofrecer el botón de 'Crear Planificación'.
        """
        # 1. Comprobar si la IA está deshabilitada en la configuración
        if not settings.AI_ENABLED:
            return SolicitudInterpretada(
                presupuesto=None,
                cantidad_personas=None,
                tipo_comida=None,
                ubicacion_referencia=None,
                preferencias_detectadas=[],
                preferencias_validadas=[],
                datos_faltantes=["presupuesto", "cantidad_personas", "tipo_comida", "ubicacion_referencia"],
                mensaje_asistente=(
                    "El asistente de IA se encuentra actualmente desactivado (AI_ENABLED=false). "
                    "Puedes registrar tu planificación gastronómica manualmente desde el formulario de MenuOpt."
                ),
                listo_para_crear=False
            )

        # 2. Contexto previo estructurado e inyección del catálogo real de tiendas y precios
        ctx_dict = {}
        if solicitud.contexto_previo:
            ctx_dict = solicitud.contexto_previo.model_dump(mode="json", exclude_none=True)

        try:
            catalogo_resumen = cls.obtener_resumen_precios_ingredientes(db)
            if catalogo_resumen:
                ctx_dict["catalogo_tiendas_ingredientes"] = catalogo_resumen
            catalogo_resto = cls.obtener_resumen_restaurantes(db)
            if catalogo_resto:
                ctx_dict["catalogo_restaurantes_platos"] = catalogo_resto
        except Exception as e:
            logger.warning(f"No se pudo cargar el catálogo de tiendas o restaurantes: {e}")

        # 3. Invocar al proveedor de IA
        proveedor = obtener_proveedor_ia()
        try:
            raw_resultado = proveedor.interpretar_solicitud(
                mensaje=solicitud.mensaje,
                contexto_previo=ctx_dict
            )
        except Exception as e:
            logger.error(f"Error al invocar proveedor IA: {str(e)}")
            return SolicitudInterpretada(
                presupuesto=None,
                cantidad_personas=None,
                tipo_comida=None,
                ubicacion_referencia=None,
                preferencias_detectadas=[],
                preferencias_validadas=[],
                datos_faltantes=["presupuesto", "cantidad_personas", "tipo_comida", "ubicacion_referencia"],
                mensaje_asistente=(
                    "El asistente no está disponible en este momento debido a un problema de conexión. "
                    "Puedes continuar creando tu planificación gastronómica de forma manual."
                ),
                listo_para_crear=False
            )

        # 4. Validar y normalizar los datos extraídos combinando con contexto previo
        ctx = solicitud.contexto_previo

        presupuesto_val: Optional[Decimal] = None
        raw_pres = raw_resultado.get("presupuesto")
        if raw_pres is not None:
            try:
                dec = Decimal(str(raw_pres)).quantize(Decimal("0.01"))
                if dec > 0:
                    presupuesto_val = dec
            except Exception:
                pass
        if presupuesto_val is None and ctx and ctx.presupuesto:
            presupuesto_val = ctx.presupuesto

        personas_val: Optional[int] = None
        raw_personas = raw_resultado.get("cantidad_personas")
        if raw_personas is not None:
            try:
                cant = int(raw_personas)
                if cant > 0:
                    personas_val = cant
            except Exception:
                pass
        if personas_val is None and ctx and ctx.cantidad_personas:
            personas_val = ctx.cantidad_personas

        tipo_val: Optional[str] = None
        raw_tipo = raw_resultado.get("tipo_comida")
        txt_eval = f"{raw_tipo or ''} {solicitud.mensaje}".lower()
        if any(w in txt_eval for w in ["almuerz", "almorz"]):
            tipo_val = "ALMUERZO"
        elif any(w in txt_eval for w in ["cen"]):
            tipo_val = "CENA"
        elif any(w in txt_eval for w in ["desayun"]):
            tipo_val = "DESAYUNO"
        elif any(w in txt_eval for w in ["meriend"]):
            tipo_val = "MERIENDA"
        elif raw_tipo and isinstance(raw_tipo, str):
            t_upper = raw_tipo.strip().upper()
            if t_upper in cls.TIPOS_PERMITIDOS:
                tipo_val = t_upper
            else:
                tipo_val = "ALMUERZO"
        if not tipo_val and ctx and ctx.tipo_comida:
            tipo_val = ctx.tipo_comida

        ubicacion_val: Optional[str] = None
        raw_ub = raw_resultado.get("ubicacion_referencia")
        if raw_ub and isinstance(raw_ub, str):
            ub_clean = raw_ub.strip()
            if len(ub_clean) >= 2:
                ubicacion_val = ub_clean[:255]
        if not ubicacion_val and ctx and ctx.ubicacion_referencia:
            ubicacion_val = ctx.ubicacion_referencia

        # 5. Normalizar y verificar preferencias contra catálogo real de PostgreSQL
        raw_prefs = list(raw_resultado.get("preferencias_detectadas", []))
        if ctx and ctx.preferencias_detectadas:
            for p_prev in ctx.preferencias_detectadas:
                if p_prev and p_prev not in raw_prefs:
                    raw_prefs.append(p_prev)
        preferencias_validadas: List[PreferenciaCoincidencia] = []
        preferencias_nombres_detectados: List[str] = []

        preferencias_bd = PreferenciaRepository.listar_activas(db)
        mapa_bd = {p.nombre.lower().strip(): p for p in preferencias_bd}

        for pref_str in raw_prefs:
            if not isinstance(pref_str, str) or not pref_str.strip():
                continue
            nombre_limpio = pref_str.strip()
            preferencias_nombres_detectados.append(nombre_limpio)
            clave = nombre_limpio.lower()

            if clave in mapa_bd:
                obj_p = mapa_bd[clave]
                preferencias_validadas.append(PreferenciaCoincidencia(
                    nombre_detectado=obj_p.nombre,
                    id_preferencia=obj_p.id_preferencia,
                    registrada=True
                ))
            else:
                preferencias_validadas.append(PreferenciaCoincidencia(
                    nombre_detectado=nombre_limpio,
                    id_preferencia=None,
                    registrada=False
                ))

        # 6. Clasificación Integral de Consultas:
        # A) RECETAS, TIENDAS, PRECIOS, COMPARACIONES Y CONSULTAS CULINARIAS ABIERTAS
        # B) PLANIFICACIÓN FORMAL DE SALIDAS A RESTAURANTES
        intencion = str(raw_resultado.get("intencion") or "").upper().strip()
        msg_lower = solicitud.mensaje.lower()

        palabras_receta_y_tienda = [
            "ingrediente", "ingredientes", "receta", "recetas", "preparar", "prepararme", "cocinar",
            "podria prepararme", "podría prepararme", "que puedo preparar", "qué puedo preparar",
            "despensa", "tengo estos", "opciones de comida", "puedo cocinar", "cómo hacer", "como hacer",
            "hacer", "hamburguesa", "hamburguesas", "tienda", "tiendas", "precio", "precios",
            "mercado", "mercados", "supermercado", "comprar", "más barato", "mas barato", "barato",
            "cuánto cuesta", "cuanto cuesta", "kilo de", "kilo", "docena", "costo", "ahorro", "carne",
            "pollo", "queso", "huevo", "tomate", "cebolla", "arroz", "fideo", "aceite"
        ]

        palabras_planificacion = [
            "planificar", "planificacion", "planificación", "salir a comer", "restaurante", "restaurantes",
            "para cenar fuera", "almorzar fuera", "organizar salida", "presupuesto de",
            "a donde ir", "a dónde ir", "donde comer", "dónde comer"
        ]

        # Es consulta culinaria/tiendas/precios si el modelo lo clasificó así o si contiene términos temáticos,
        # salvo que el usuario esté pidiendo explícitamente planificar una salida con presupuesto o personas.
        es_consulta_abierta = (
            intencion in ("RECETA", "TIENDAS_PRECIOS", "RECETA_COTIZADA", "DESPENSA", "COMPARACION", "CONSULTA")
            or any(p in msg_lower for p in palabras_receta_y_tienda)
        ) and not (
            any(p in msg_lower for p in palabras_planificacion) and
            (presupuesto_val is not None and personas_val is not None)
        )

        if es_consulta_abierta:
            # Caso 1: Recetas, Técnicas, Ingredientes, Tiendas, Precios y Comparativas
            datos_faltantes = []
            listo = False
            opcion_recomendada = None
            mensaje_asistente = raw_resultado.get("mensaje_asistente", "")
            if not mensaje_asistente or len(mensaje_asistente.strip()) < 30:
                if "hamburguesa" in msg_lower:
                    mensaje_asistente = (
                        "### 🍔 Ingredientes para Hamburguesas Caseras y Mejores Tiendas:\n\n"
                        "• **Carne Molida Especial:** **Mercado Abasto Mayorista** a **Bs 34.00/kg** (o Carnicería San Carlos a Bs 35.00/kg).\n"
                        "• **Queso Chaqueño Criollo:** **Mercado Los Pozos** a **Bs 30.00/kg**.\n"
                        "• **Huevos de Granja:** **Distribuidora Avícola Sofía** a **Bs 11.50/docena**.\n"
                        "• **Tomate y Cebolla:** **Mercado Abasto Mayorista** a **Bs 6.00/kg** y **Bs 5.00/kg**.\n"
                        "• **Aceite Vegetal:** **Mercado Abasto Mayorista** a **Bs 13.00/litro**.\n\n"
                        "📍 **Recomendación de ahorro:** En el **Mercado Abasto Mayorista** consigues la mayor parte de los ingredientes con el menor precio de la ciudad."
                    )
                else:
                    mensaje_asistente = (
                        "Con esos ingredientes puedes preparar excelentes opciones caseras:\n\n"
                        "1. **Arroz con Pollo y Verduras:** Saltea la cebolla y tomate picado, dora la pechuga en cubos e incorpóralo con arroz graneado.\n\n"
                        "2. **Tortilla de Pollo y Huevo:** Bate los huevos con pechuga desmenuzada, cebolla y tomate, cocinada a la sartén y servida con arroz.\n\n"
                        "3. **Salteado Rápido de Pollo:** Saltea las tiras de pechuga con cebolla y tomate a fuego vivo para acompañar el arroz."
                    )
        else:
            # Caso 2: Planificación Gastronómica y Salidas a Comer
            try:
                num_pres_check = float(presupuesto_val) if presupuesto_val is not None else 0
            except (ValueError, TypeError):
                num_pres_check = 0

            try:
                num_pers_check = int(personas_val) if personas_val is not None else 0
            except (ValueError, TypeError):
                num_pers_check = 0

            datos_faltantes = []
            if num_pres_check <= 0:
                datos_faltantes.append("presupuesto")
            if num_pers_check <= 0:
                datos_faltantes.append("cantidad_personas")
            if not tipo_val:
                datos_faltantes.append("tipo_comida")
            if not ubicacion_val:
                datos_faltantes.append("ubicacion_referencia")

            listo = (len(datos_faltantes) == 0)

            # 7. Si los datos están listos o el usuario pregunta directamente opciones / a dónde ir:
            opcion_recomendada = None
            es_consulta_opciones = any(w in solicitud.mensaje.lower() for w in [
                "donde", "dónde", "ir", "opcion", "opción", "recomiend", "restaurante", "comer", "plato", "menu", "menú"
            ])

            if listo or (num_pres_check > 0 and num_pers_check > 0 and es_consulta_opciones):
                opcion_recomendada = cls.buscar_mejor_opcion_restaurante(
                    db=db,
                    presupuesto=presupuesto_val if presupuesto_val else Decimal(str(num_pres_check)),
                    cantidad_personas=personas_val if personas_val else num_pers_check,
                    tipo_comida=tipo_val,
                    ubicacion=ubicacion_val,
                    preferencias_ids=[p.id_preferencia for p in preferencias_validadas if p.id_preferencia],
                    mensaje_usuario=solicitud.mensaje
                )

            if opcion_recomendada:
                nombre_rest = opcion_recomendada["nombre_restaurante"]
                dir_rest = opcion_recomendada.get("direccion") or opcion_recomendada.get("zona") or ""
                loc_txt = f" ({dir_rest})" if dir_rest else ""
                costo_tot = opcion_recomendada["costo_total"]
                ahorro_tot = opcion_recomendada["ahorro"]

                lineas_platos = []
                for p in opcion_recomendada["platos"]:
                    lineas_platos.append(
                        f"• {p['cantidad']}x {p['nombre']} (Bs {p['precio_unitario']:.2f} c/u) = Bs {p['subtotal']:.2f}"
                    )
                platos_str = "\n".join(lineas_platos)

                presup_str = f"{presupuesto_val:.2f}" if presupuesto_val else f"{num_pres_check:.2f}"
                pers_str = f"{personas_val}" if personas_val else f"{num_pers_check}"

                alt_txt = ""
                if opcion_recomendada.get("alternativas"):
                    lineas_alt = [
                        f"• **{alt['nombre_restaurante']}**: {alt['plato_nombre']} (Total: Bs {alt['costo_total']:.2f}, te sobran Bs {alt['ahorro']:.2f})"
                        for alt in opcion_recomendada["alternativas"]
                    ]
                    alt_txt = "\n\n💡 **Otra alternativa disponible:**\n" + "\n".join(lineas_alt)

                antojo_str = ""
                if opcion_recomendada.get("antojo_detectado"):
                    antojo_str = f" para tu deseo de **{opcion_recomendada['antojo_detectado'].title()}**"

                mensaje_asistente = (
                    f"¡Planificación lista para {pers_str} personas ({tipo_val or 'Comida'}) con Bs {presup_str}!\n\n"
                    f"🍽️ **Mejor opción recomendada{antojo_str}:**\n"
                    f"**Restaurante:** {nombre_rest}{loc_txt}\n\n"
                    f"📋 **Platos a comprar dentro de tu presupuesto:**\n"
                    f"{platos_str}\n\n"
                    f"💰 **Total:** Bs {costo_tot:.2f}  |  **Ahorro restante:** Bs {ahorro_tot:.2f}"
                    f"{alt_txt}\n\n"
                    f"👉 Pulsa **'Crear Planificación'** en el panel lateral para confirmarla."
                )
            elif listo:
                mensaje_asistente = (
                    f"Registrado: {personas_val} personas, {tipo_val or 'comida'}, Bs {presupuesto_val:.2f} en {ubicacion_val or 'zona general'}.\n"
                    f"No encontramos restaurantes en el catálogo que cubran a {personas_val} comensales por menos de Bs {presupuesto_val:.2f}. "
                    f"Puedes crear la planificación para evaluar 'Preparación Propia'."
                )
            else:
                # Entrevista en curso: modo ultra corto y puntual sin gastar tokens
                preguntas = []
                if "presupuesto" in datos_faltantes and "cantidad_personas" in datos_faltantes:
                    preguntas.append("¿cuál es tu presupuesto y para cuántas personas?")
                elif "presupuesto" in datos_faltantes:
                    preguntas.append("¿cuál es tu presupuesto en Bs?")
                elif "cantidad_personas" in datos_faltantes:
                    preguntas.append("¿para cuántas personas sería?")
                if "tipo_comida" in datos_faltantes:
                    preguntas.append("¿para qué comida (almuerzo, cena, desayuno)?")
                if "ubicacion_referencia" in datos_faltantes:
                    preguntas.append("¿en qué zona o barrio prefieres buscar?")

                capturados = []
                if num_pres_check > 0:
                    capturados.append(f"{num_pres_check:.0f} Bs")
                if num_pers_check > 0:
                    capturados.append(f"{num_pers_check} personas")
                if tipo_val:
                    capturados.append(tipo_val.lower())
                if ubicacion_val:
                    capturados.append(ubicacion_val)

                prefijo = f"Registrado: {', '.join(capturados)}. " if capturados else ""
                # Si el modelo Groq dio un mensaje conciso de una línea, usarlo si es corto; si es largo o relleno, usar el directo
                raw_msg = raw_resultado.get("mensaje_asistente", "")
                if raw_msg and len(raw_msg.strip()) < 140 and not any(f in raw_msg.lower() for f in ["explorar los restaurantes", "te recomiendo ingresar"]):
                    mensaje_asistente = raw_msg.strip()
                else:
                    mensaje_asistente = f"{prefijo}{' '.join(preguntas)}"

        # Filtrar términos comunes de comida que NO son preferencias dietarias
        terminos_comunes = {
            "pizza", "pizzas", "carne", "carnes", "pollo", "pollos", "hamburguesa", "hamburguesas",
            "pasta", "pastas", "pescado", "pescados", "sushi", "tacos", "comida", "almuerzo", "cena"
        }
        no_registradas = [
            p.nombre_detectado for p in preferencias_validadas
            if not p.registrada and p.nombre_detectado.lower().strip() not in terminos_comunes
        ]
        # Solo informar si el usuario solicitó una restricción dietaria especial no soportada (ej: Kosher, Halal)
        palabras_dietarias = ["dieta", "alergia", "intolerancia", "regimen", "restriccion", "libre de", "sin"]
        debe_informar = any(w in solicitud.mensaje.lower() for w in palabras_dietarias)
        if no_registradas and debe_informar:
            mensaje_asistente += (
                f"\n(Nota: La preferencia dietaria '{', '.join(no_registradas)}' no se encuentra registrada en el catálogo de restricciones del sistema)."
            )

        return SolicitudInterpretada(
            presupuesto=presupuesto_val,
            cantidad_personas=personas_val,
            tipo_comida=tipo_val,
            ubicacion_referencia=ubicacion_val,
            preferencias_detectadas=preferencias_nombres_detectados,
            preferencias_validadas=preferencias_validadas,
            datos_faltantes=datos_faltantes,
            mensaje_asistente=mensaje_asistente,
            listo_para_crear=listo,
            opcion_recomendada=opcion_recomendada
        )

    @classmethod
    def buscar_mejor_opcion_restaurante(
        cls,
        db: Session,
        presupuesto: Decimal,
        cantidad_personas: int,
        tipo_comida: Optional[str] = None,
        ubicacion: Optional[str] = None,
        preferencias_ids: Optional[List[int]] = None,
        mensaje_usuario: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Consulta en PostgreSQL el mejor restaurante y los platos que el usuario puede
        comprar con su presupuesto para la cantidad de personas solicitada, respetando
        antojos de comida específicos (pizza, carne, hamburguesa, pollo, etc.).
        """
        if not presupuesto or presupuesto <= 0 or not cantidad_personas or cantidad_personas <= 0:
            return None

        # 1. Detección de antojo o tipo de comida deseada en el mensaje del usuario
        palabras_antojo = []
        if mensaje_usuario:
            msg_u_low = mensaje_usuario.lower()
            terminos_clave = [
                "pizza", "pizzas", "carne", "carnes", "parrilla", "parrillada", "churrasco", "bife", "picaña", "cuadril",
                "hamburguesa", "hamburguesas", "burger", "lomito",
                "pollo", "pollos", "broaster", "brasa",
                "pasta", "pastas", "lasagna", "lasaña", "spaghetti", "fettuccine", "ravioles", "italiana",
                "sushi", "chifa", "chaufa", "oriental", "asiatica", "asiática",
                "tacos", "taqueria", "taquería", "mexicana", "quesadilla", "quesadillas",
                "pescado", "pescados", "surubi", "surubí", "pacu", "pacú", "marisco", "mariscos", "mar",
                "tipica", "típica", "cruceña", "cruceño", "majadito", "keperi", "keperí", "silpancho", "sopa de mani", "sopa de maní",
                "salteña", "salteñas", "cuñapé", "cuñapes", "empanada", "empanadas",
                "vegetariano", "vegano", "ensalada", "ensaladas", "saludable", "fit", "quinoa",
                "cafe", "café", "postre", "postres", "helado", "helados", "torta"
            ]
            for tk in terminos_clave:
                if tk in msg_u_low:
                    palabras_antojo.append(tk)

        platos = (
            db.query(Plato)
            .join(Restaurante, Plato.id_restaurante == Restaurante.id_restaurante)
            .options(
                joinedload(Plato.restaurante).joinedload(Restaurante.ubicacion),
                joinedload(Plato.categoria),
                joinedload(Plato.preferencias)
            )
            .filter(
                Plato.estado == "ACTIVO",
                Plato.disponible.is_(True),
                Restaurante.estado == "ACTIVO"
            )
            .all()
        )

        if not platos:
            return None

        candidatos = []
        prefs_set = set(preferencias_ids or [])

        for plato in platos:
            plato_prefs = {p.id_preferencia for p in plato.preferencias}
            if prefs_set and plato_prefs and not prefs_set.issubset(plato_prefs):
                continue

            pers_cub = plato.personas_cubiertas if (plato.personas_cubiertas and plato.personas_cubiertas > 0) else 1
            cant_necesaria = math.ceil(cantidad_personas / pers_cub)
            costo_total = (Decimal(str(plato.precio)) * Decimal(cant_necesaria)).quantize(Decimal("0.01"))

            if costo_total > presupuesto:
                continue

            ahorro = presupuesto - costo_total
            score = float(ahorro) / float(presupuesto) * 50.0

            if tipo_comida and plato.tipo_comida:
                if plato.tipo_comida.strip().upper() == tipo_comida.strip().upper():
                    score += 25.0

            rest = plato.restaurante
            zona = ""
            direccion = ""
            if rest.ubicacion:
                zona = rest.ubicacion.zona or ""
                direccion = rest.ubicacion.direccion or ""
                ciudad = rest.ubicacion.ciudad or ""
                ref_ub = rest.ubicacion.referencia or ""
                if ubicacion:
                    ub_low = ubicacion.strip().lower()
                    if (ub_low in zona.lower() or ub_low in direccion.lower() or
                        ub_low in ciudad.lower() or ub_low in ref_ub.lower()):
                        score += 40.0

            if prefs_set and prefs_set.issubset(plato_prefs):
                score += 20.0

            # Evaluar coincidencia con el antojo o tipo de comida solicitado
            coincide_antojo = False
            if palabras_antojo:
                nom_p = plato.nombre.lower()
                desc_p = (plato.descripcion or "").lower()
                cat_p = (plato.categoria.nombre if plato.categoria else "").lower()
                nom_r = rest.nombre.lower()
                desc_r = (rest.descripcion or "").lower()

                for pa in palabras_antojo:
                    if pa in nom_p or pa in cat_p:
                        score += 300.0
                        coincide_antojo = True
                    elif pa in nom_r or pa in desc_r or pa in desc_p:
                        score += 150.0
                        coincide_antojo = True

            candidatos.append({
                "id_restaurante": rest.id_restaurante,
                "nombre_restaurante": rest.nombre,
                "direccion": direccion,
                "zona": zona,
                "plato": plato,
                "cantidad": cant_necesaria,
                "costo_total": costo_total,
                "costo_pp": (costo_total / Decimal(cantidad_personas)).quantize(Decimal("0.01")),
                "ahorro": ahorro,
                "score": score,
                "coincide_antojo": coincide_antojo
            })

        if not candidatos:
            return None

        # Ordenar priorizando platos que cumplan con el antojo del usuario
        candidatos.sort(key=lambda x: (1 if x["coincide_antojo"] else 0, x["score"]), reverse=True)
        mejor = candidatos[0]
        alternativas = []
        rest_ids_vistos = {mejor["id_restaurante"]}
        for c in candidatos[1:]:
            if c["id_restaurante"] not in rest_ids_vistos:
                rest_ids_vistos.add(c["id_restaurante"])
                alternativas.append({
                    "id_restaurante": c["id_restaurante"],
                    "nombre_restaurante": c["nombre_restaurante"],
                    "plato_nombre": c["plato"].nombre,
                    "costo_total": float(c["costo_total"]),
                    "ahorro": float(c["ahorro"])
                })
                if len(alternativas) >= 2:
                    break

        antojo_nombre = palabras_antojo[0] if (palabras_antojo and mejor["coincide_antojo"]) else None

        return {
            "id_restaurante": mejor["id_restaurante"],
            "nombre_restaurante": mejor["nombre_restaurante"],
            "direccion": mejor["direccion"],
            "zona": mejor["zona"],
            "antojo_detectado": antojo_nombre,
            "platos": [
                {
                    "id_plato": mejor["plato"].id_plato,
                    "nombre": mejor["plato"].nombre,
                    "cantidad": mejor["cantidad"],
                    "precio_unitario": float(mejor["plato"].precio),
                    "subtotal": float(mejor["costo_total"])
                }
            ],
            "costo_total": float(mejor["costo_total"]),
            "ahorro": float(mejor["ahorro"]),
            "costo_por_persona": float(mejor["costo_pp"]),
            "puntuacion": round(mejor["score"], 2),
            "alternativas": alternativas
        }

    @classmethod
    def explicar_recomendacion(
        cls,
        db: Session,
        id_recomendacion: int,
        usuario_actual: Usuario
    ) -> ExplicacionRespuesta:
        """
        CU26: Explica una recomendación gastronómica calculada previamente por CU13.
        Verifica titularidad, obtiene los datos reales y solicita una explicación objetiva a la IA.
        """
        rec = RecomendacionRepository.buscar_por_id(db, id_recomendacion)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recomendación #{id_recomendacion} no encontrada."
            )

        verificar_propiedad_planificacion(rec.planificacion, usuario_actual)

        nombre_opcion = rec.restaurante.nombre if rec.tipo_recomendacion == "RESTAURANTE" and rec.restaurante else (
            rec.preparacion_propia.nombre if rec.preparacion_propia else "Opción recomendada"
        )

        datos_contexto = {
            "nombre": nombre_opcion,
            "tipo_recomendacion": rec.tipo_recomendacion,
            "costo_total": float(rec.costo_estimado),
            "costo_por_persona": float(rec.costo_por_persona),
            "puntuacion": float(rec.puntuacion),
            "presupuesto": float(rec.planificacion.presupuesto),
            "cantidad_personas": rec.planificacion.cantidad_personas,
            "tipo_comida": rec.planificacion.tipo_comida,
        }

        proveedor = obtener_proveedor_ia()
        explicacion_texto = proveedor.explicar_recomendacion(datos_contexto)

        detalles = [
            f"Costo estimado: {rec.costo_estimado} Bs",
            f"Costo por persona: {rec.costo_por_persona} Bs/persona",
            f"Puntuación de afinidad: {rec.puntuacion}/100"
        ]

        return ExplicacionRespuesta(
            id_referencia=id_recomendacion,
            tipo="RECOMENDACION",
            explicacion=explicacion_texto,
            detalles_clave=detalles
        )

    @classmethod
    def explicar_comparacion(
        cls,
        db: Session,
        id_planificacion: int,
        usuario_actual: Usuario
    ) -> ExplicacionRespuesta:
        """
        CU26: Explica la comparativa real entre RESTAURANTE y PREPARACION_PROPIA obtenida por CU14.
        """
        comparativa = RecomendacionService.comparar_alternativas(
            db=db,
            id_planificacion=id_planificacion,
            usuario_actual=usuario_actual
        )

        mejor_resto = next((a for a in comparativa.alternativas if a.tipo_recomendacion == "RESTAURANTE"), None)
        mejor_prep = next((a for a in comparativa.alternativas if a.tipo_recomendacion == "PREPARACION_PROPIA"), None)

        costo_resto = float(mejor_resto.costo_total) if mejor_resto else None
        nombre_resto = mejor_resto.nombre if mejor_resto else None
        costo_prep = float(mejor_prep.costo_total) if mejor_prep else None

        diferencia = 0.0
        if costo_resto is not None and costo_prep is not None:
            diferencia = abs(round(costo_resto - costo_prep, 2))

        datos_contexto = {
            "presupuesto": float(comparativa.presupuesto),
            "cantidad_personas": comparativa.cantidad_personas,
            "costo_restaurante": costo_resto,
            "nombre_restaurante": nombre_resto,
            "costo_preparacion": costo_prep,
            "diferencia": diferencia
        }

        proveedor = obtener_proveedor_ia()
        explicacion_texto = proveedor.explicar_comparacion(datos_contexto)

        detalles = [
            f"Presupuesto: {comparativa.presupuesto} Bs",
            f"Total opciones evaluadas: {comparativa.total_alternativas}"
        ]
        if costo_resto is not None:
            detalles.append(f"Restaurante viabilizado: {nombre_resto} ({costo_resto} Bs)")
        if costo_prep is not None:
            detalles.append(f"Preparación en casa: {costo_prep} Bs")
        if costo_resto is not None and costo_prep is not None:
            detalles.append(f"Diferencia económica: {diferencia} Bs")

        return ExplicacionRespuesta(
            id_referencia=id_planificacion,
            tipo="COMPARACION",
            explicacion=explicacion_texto,
            detalles_clave=detalles
        )

    @classmethod
    def obtener_resumen_precios_ingredientes(cls, db: Session) -> str:
        """
        CU16/CU26: Retorna un resumen compacto de ingredientes y las tiendas con el mejor precio
        para que el motor de IA conozca las tiendas reales y los precios disponibles en BD.
        """
        from app.models.ingrediente import Ingrediente
        from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
        from app.models.lugar_compra import LugarCompra

        ingredientes = db.query(Ingrediente).filter(Ingrediente.estado == "ACTIVO").all()
        lineas = []
        for ing in ingredientes:
            precios = (
                db.query(IngredienteLugarCompra, LugarCompra)
                .join(LugarCompra, IngredienteLugarCompra.id_lugar_compra == LugarCompra.id_lugar_compra)
                .filter(
                    IngredienteLugarCompra.id_ingrediente == ing.id_ingrediente,
                    IngredienteLugarCompra.disponible == True,
                    LugarCompra.estado == "ACTIVO"
                )
                .order_by(IngredienteLugarCompra.precio.asc())
                .all()
            )
            if precios:
                mejor = precios[0]
                tienda_nombre = mejor[1].nombre
                precio_val = mejor[0].precio
                unidad = mejor[0].unidad_medida
                otras = [f"{p[1].nombre} (Bs {p[0].precio:.2f})" for p in precios[1:3]]
                alt_txt = f", alternativas: {', '.join(otras)}" if otras else ""
                lineas.append(f"- {ing.nombre}: Mejor precio Bs {precio_val:.2f}/{unidad} en '{tienda_nombre}'{alt_txt}")
            elif ing.precio_estimado:
                lineas.append(f"- {ing.nombre}: Precio referencial Bs {ing.precio_estimado:.2f}/{ing.unidad_medida}")
        return "\n".join(lineas)

    @classmethod
    def obtener_resumen_restaurantes(cls, db: Session) -> str:
        """
        CU03/CU26: Retorna un resumen de restaurantes disponibles y platos representativos
        para que la IA conozca los menús y precios reales del catálogo.
        """
        from app.models.restaurante import Restaurante
        from app.models.plato import Plato

        restaurantes = db.query(Restaurante).filter(Restaurante.estado == "ACTIVO").all()
        lineas = []
        for r in restaurantes:
            platos = db.query(Plato).filter(Plato.id_restaurante == r.id_restaurante, Plato.disponible == True).all()
            platos_txt = ", ".join([f"{p.nombre} (Bs {p.precio:.2f})" for p in platos[:5]])
            zona = r.ubicacion.zona if r.ubicacion and r.ubicacion.zona else (r.ubicacion.direccion if r.ubicacion else "Santa Cruz")
            lineas.append(f"- {r.nombre} (Zona: {zona}): Platos: {platos_txt if platos_txt else 'Menú variado'}")
        return "\n".join(lineas)
