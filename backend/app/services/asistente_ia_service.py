# CASO DE USO: CU26 - Usar asistencia con IA
# Servicio de orquestación segura entre la IA, Pydantic y los servicios de MenuOpt
from decimal import Decimal
from typing import Optional, Dict, Any, List
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.usuario import Usuario
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

        # 2. Contexto previo estructurado
        ctx_dict = {}
        if solicitud.contexto_previo:
            ctx_dict = solicitud.contexto_previo.model_dump(exclude_none=True)

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

        # 4. Validar y normalizar los datos extraídos
        presupuesto_val: Optional[Decimal] = None
        raw_pres = raw_resultado.get("presupuesto")
        if raw_pres is not None:
            try:
                dec = Decimal(str(raw_pres)).quantize(Decimal("0.01"))
                if dec > 0:
                    presupuesto_val = dec
            except Exception:
                pass

        personas_val: Optional[int] = None
        raw_personas = raw_resultado.get("cantidad_personas")
        if raw_personas is not None:
            try:
                cant = int(raw_personas)
                if cant > 0:
                    personas_val = cant
            except Exception:
                pass

        tipo_val: Optional[str] = None
        raw_tipo = raw_resultado.get("tipo_comida")
        if raw_tipo and isinstance(raw_tipo, str):
            t_upper = raw_tipo.strip().upper()
            if t_upper in cls.TIPOS_PERMITIDOS:
                tipo_val = t_upper

        ubicacion_val: Optional[str] = None
        raw_ub = raw_resultado.get("ubicacion_referencia")
        if raw_ub and isinstance(raw_ub, str):
            ub_clean = raw_ub.strip()
            if len(ub_clean) >= 2:
                ubicacion_val = ub_clean[:255]

        # 5. Normalizar y verificar preferencias contra catálogo real de PostgreSQL
        raw_prefs = raw_resultado.get("preferencias_detectadas", [])
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

        # 6. Recalcular datos faltantes reales
        datos_faltantes = []
        if presupuesto_val is None or presupuesto_val <= 0:
            datos_faltantes.append("presupuesto")
        if personas_val is None or personas_val <= 0:
            datos_faltantes.append("cantidad_personas")
        if not tipo_val:
            datos_faltantes.append("tipo_comida")
        if not ubicacion_val:
            datos_faltantes.append("ubicacion_referencia")

        listo = (len(datos_faltantes) == 0)

        mensaje_asistente = raw_resultado.get("mensaje_asistente", "")
        if not mensaje_asistente or not mensaje_asistente.strip():
            if listo:
                mensaje_asistente = (
                    f"¡Excelente! Tengo los datos completos: {personas_val} personas para {tipo_val} "
                    f"con {presupuesto_val} Bs en {ubicacion_val}. Puedes revisar y confirmar tu planificación."
                )
            else:
                mensaje_asistente = (
                    f"He procesado tu solicitud. Para completar la planificación gastronómica, "
                    f"aún necesitamos especificar: {', '.join(datos_faltantes)}."
                )

        # Informar si alguna preferencia detectada no existe en el catálogo
        no_registradas = [p.nombre_detectado for p in preferencias_validadas if not p.registrada]
        if no_registradas:
            mensaje_asistente += (
                f"\n(Nota: La preferencia '{', '.join(no_registradas)}' no está registrada actualmente "
                f"en el catálogo oficial de MenuOpt, por lo que no se aplicará como filtro)."
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
            listo_para_crear=listo
        )

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
