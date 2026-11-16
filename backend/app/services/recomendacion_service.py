# CASO DE USO: CU13 - Generar recomendación
# CASO DE USO: CU14 - Comparar alternativas (RESTAURANTE vs PREPARACION_PROPIA)
from decimal import Decimal
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.recomendacion import Recomendacion
from app.models.recomendacion_plato import RecomendacionPlato
from app.models.preparacion_propia import PreparacionPropia
from app.models.preparacion_ingrediente import PreparacionIngrediente
from app.repositories.planificacion_repository import PlanificacionRepository
from app.repositories.recomendacion_repository import RecomendacionRepository
from app.security.propiedad import verificar_propiedad_planificacion
from app.services.recomendacion_algoritmo import (
    calcular_cantidad_necesaria,
    calcular_costo_total,
    calcular_costo_por_persona,
    calcular_puntuacion,
    cumple_todas_las_preferencias,
)
from app.services.preparacion_service import PreparacionService
from app.schemas.recomendacion import (
    RecomendacionRespuestaSchema,
    RecomendacionPlatoItemSchema,
)
from app.schemas.comparacion import (
    AlternativaComparacionSchema,
    ComparacionPlanificacionRespuestaSchema,
)


class RecomendacionService:
    """
    Servicio de orquestación de recomendaciones gastronómicas (CU13)
    y comparación analítica de alternativas (CU14) entre RESTAURANTE y PREPARACION_PROPIA.
    """

    # =========================================================================
    # CASO DE USO: CU13 - GENERAR RECOMENDACIÓN (RESTAURANTE Y PREPARACIÓN PROPIA)
    # =========================================================================
    @staticmethod
    def generar_recomendaciones(
        db: Session,
        id_planificacion: int,
        usuario_actual: Usuario
    ) -> List[RecomendacionRespuestaSchema]:
        """
        LÓGICA CU13 - Generar Recomendación:
        Genera en un único flujo determinista y transaccional:
        1. Alternativas de RESTAURANTE basadas en platos ofertados comercialmente.
        2. Alternativas de PREPARACION_PROPIA basadas en el costo de los ingredientes
           calculados a partir de los precios de mercado en lugares de compra activos.
        3. Realiza el reemplazo transaccional de recomendaciones anteriores.
        4. Retorna el catálogo consolidado ordenado por puntuación DESC y costo total ASC.
        """
        planificacion = PlanificacionRepository.buscar_por_id(db, id_planificacion)
        if not planificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la planificación con ID {id_planificacion}."
            )

        verificar_propiedad_planificacion(planificacion, usuario_actual)

        if planificacion.estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se pueden generar recomendaciones para una planificación con estado '{planificacion.estado}'. Debe estar ACTIVA."
            )

        preferencias_plan = {p.id_preferencia for p in planificacion.preferencias}
        ub_ref = (planificacion.ubicacion_referencia or "").strip().lower()
        palabras_ref = [p.strip() for p in ub_ref.replace(",", " ").split() if len(p.strip()) >= 3]

        # ---------------------------------------------------------------------
        # 1. GENERACIÓN DE CANDIDATOS: RESTAURANTE
        # ---------------------------------------------------------------------
        platos_restaurante = RecomendacionRepository.buscar_platos_candidatos(
            db=db,
            tipo_comida=planificacion.tipo_comida
        )

        candidatos_restaurante = []
        for plato in platos_restaurante:
            preferencias_plato = {p.id_preferencia for p in plato.preferencias}

            if not cumple_todas_las_preferencias(preferencias_plan, preferencias_plato):
                continue

            cantidad = calcular_cantidad_necesaria(
                cantidad_personas=planificacion.cantidad_personas,
                personas_cubiertas=plato.personas_cubiertas
            )

            costo_total = calcular_costo_total(
                precio_unitario=plato.precio,
                cantidad=cantidad
            )

            if costo_total > planificacion.presupuesto:
                continue

            costo_pp = calcular_costo_por_persona(
                costo_total=costo_total,
                cantidad_personas=planificacion.cantidad_personas
            )
            puntuacion_base = calcular_puntuacion(
                presupuesto=planificacion.presupuesto,
                costo_total=costo_total
            )

            # Evaluar coincidencia con la zona o ubicación de referencia solicitada
            rest = plato.restaurante
            ubic = rest.ubicacion if rest else None
            zona = (ubic.zona or "").strip().lower() if ubic and ubic.zona else ""
            direccion = (ubic.direccion or "").strip().lower() if ubic and ubic.direccion else ""
            referencia = (ubic.referencia or "").strip().lower() if ubic and ubic.referencia else ""

            coincide_zona = False
            distancia_estimada = None

            if ub_ref:
                coincide_zona = (
                    (ub_ref in zona) or (zona and zona in ub_ref) or
                    (ub_ref in direccion) or (ub_ref in referencia) or
                    any(p in zona or p in direccion or p in referencia for p in palabras_ref)
                )
                if coincide_zona:
                    distancia_estimada = Decimal("0.8")
                    # Bonificación de cercanía para asegurar que los restaurantes en la zona solicitada
                    # sean priorizados y recomendados en los primeros lugares
                    puntuacion = min(Decimal("100.00"), puntuacion_base + Decimal("10.00"))
                else:
                    distancia_estimada = Decimal("6.5")
                    # Penalización por lejanía respecto a la zona explícitamente pedida
                    puntuacion = max(Decimal("10.00"), puntuacion_base - Decimal("30.00"))
            else:
                puntuacion = puntuacion_base

            candidatos_restaurante.append({
                "plato": plato,
                "cantidad": cantidad,
                "costo_total": costo_total,
                "costo_pp": costo_pp,
                "puntuacion": puntuacion,
                "coincide_zona": coincide_zona,
                "distancia_estimada": distancia_estimada
            })

        candidatos_restaurante.sort(
            key=lambda x: (1 if x["coincide_zona"] else 0, x["puntuacion"], -x["costo_total"]),
            reverse=True
        )
        top_restaurantes = candidatos_restaurante[:20]

        # ---------------------------------------------------------------------
        # 2. GENERACIÓN DE CANDIDATOS: PREPARACIÓN PROPIA (Parte 7)
        # ---------------------------------------------------------------------
        platos_con_receta = RecomendacionRepository.buscar_platos_para_preparacion(
            db=db,
            tipo_comida=planificacion.tipo_comida
        )

        candidatos_preparacion = []
        for plato in platos_con_receta:
            preferencias_plato = {p.id_preferencia for p in plato.preferencias}

            if not cumple_todas_las_preferencias(preferencias_plan, preferencias_plato):
                continue

            eval_prep = PreparacionService.evaluar_plato_para_preparacion(
                db=db,
                plato=plato,
                planificacion=planificacion
            )

            if eval_prep is not None:
                candidatos_preparacion.append(eval_prep)

        candidatos_preparacion.sort(key=lambda x: (-x["puntuacion"], x["costo_total"]))
        top_preparaciones = candidatos_preparacion[:20]

        # ---------------------------------------------------------------------
        # 3. REEMPLAZO TRANSACCIONAL DE RECOMENDACIONES PREVIAS
        # ---------------------------------------------------------------------
        RecomendacionRepository.eliminar_recomendaciones_anteriores(
            db=db,
            id_planificacion=id_planificacion
        )

        if not top_restaurantes and not top_preparaciones:
            db.commit()
            return []

        nuevas_entidades: List[Recomendacion] = []

        # Instanciar entidades de Restaurante
        for cand in top_restaurantes:
            plato = cand["plato"]
            ubic = plato.restaurante.ubicacion if plato.restaurante else None
            zona_str = f" ({ubic.zona})" if ubic and ubic.zona else ""
            rec = Recomendacion(
                id_planificacion=id_planificacion,
                tipo_recomendacion="RESTAURANTE",
                descripcion=f"Menú en {plato.restaurante.nombre}{zona_str}: {plato.nombre}",
                costo_estimado=cand["costo_total"],
                costo_por_persona=cand["costo_pp"],
                puntuacion=cand["puntuacion"],
                distancia_estimada=cand["distancia_estimada"],
                id_restaurante=plato.id_restaurante
            )
            item_plato = RecomendacionPlato(
                id_plato=plato.id_plato,
                cantidad=cand["cantidad"],
                subtotal=cand["costo_total"]
            )
            rec.recomendacion_platos.append(item_plato)
            nuevas_entidades.append(rec)

        # Instanciar entidades de Preparación Propia
        for cand in top_preparaciones:
            rec = Recomendacion(
                id_planificacion=id_planificacion,
                tipo_recomendacion="PREPARACION_PROPIA",
                descripcion=cand["descripcion"],
                costo_estimado=cand["costo_total"],
                costo_por_persona=cand["costo_pp"],
                puntuacion=cand["puntuacion"],
                distancia_estimada=None,
                id_restaurante=None
            )
            prep = PreparacionPropia(
                nombre=cand["nombre"],
                descripcion=cand["descripcion"],
                costo_estimado=cand["costo_total"],
                cantidad_personas=cand["cantidad_personas"]
            )
            for ing in cand["ingredientes"]:
                prep.ingredientes.append(PreparacionIngrediente(
                    id_ingrediente=ing["id_ingrediente"],
                    cantidad=ing["cantidad"],
                    unidad_medida=ing["unidad_medida"],
                    precio_unitario_usado=ing["precio_unitario_usado"],
                    costo_estimado=ing["costo_estimado"],
                    id_lugar_compra=ing["id_lugar_compra"]
                ))
            rec.preparacion_propia = prep
            nuevas_entidades.append(rec)

        guardadas = RecomendacionRepository.guardar_recomendaciones(db, nuevas_entidades)

        # Ordenar respuesta general por puntuación DESC y costo total ASC
        guardadas.sort(key=lambda x: (-x.puntuacion, x.costo_estimado))

        return [RecomendacionService._mapear_a_schema(r) for r in guardadas]

    # --- CU13: Listar Recomendaciones Guardadas ---
    @staticmethod
    def listar_recomendaciones(
        db: Session,
        id_planificacion: int,
        usuario_actual: Usuario,
        tipo_recomendacion: Optional[str] = None
    ) -> List[RecomendacionRespuestaSchema]:
        planificacion = PlanificacionRepository.buscar_por_id(db, id_planificacion)
        if not planificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la planificación con ID {id_planificacion}."
            )

        verificar_propiedad_planificacion(planificacion, usuario_actual)

        recomendaciones = RecomendacionRepository.listar_por_planificacion(
            db=db,
            id_planificacion=id_planificacion,
            tipo_recomendacion=tipo_recomendacion
        )

        return [RecomendacionService._mapear_a_schema(r) for r in recomendaciones]

    # --- CU13: Detalle de una Recomendación ---
    @staticmethod
    def obtener_recomendacion(
        db: Session,
        id_recomendacion: int,
        usuario_actual: Usuario
    ) -> RecomendacionRespuestaSchema:
        rec = RecomendacionRepository.buscar_por_id(db, id_recomendacion)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la recomendación con ID {id_recomendacion}."
            )

        verificar_propiedad_planificacion(rec.planificacion, usuario_actual)

        return RecomendacionService._mapear_a_schema(rec)

    # =========================================================================
    # CASO DE USO: CU14 - COMPARAR ALTERNATIVAS (RESTAURANTE vs PREPARACION_PROPIA)
    # =========================================================================
    @staticmethod
    def comparar_alternativas(
        db: Session,
        id_planificacion: int,
        usuario_actual: Usuario
    ) -> ComparacionPlanificacionRespuestaSchema:
        """
        LÓGICA CU14 - Comparar Alternativas Completo:
        Compara las opciones de RESTAURANTE y PREPARACION_PROPIA generadas, calculando
        ahorro neto, porcentaje presupuestario ejecutado, resumen de compras/platos
        y señalando las alternativas más eficientes en costo y puntuación.
        """
        planificacion = PlanificacionRepository.buscar_por_id(db, id_planificacion)
        if not planificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la planificación con ID {id_planificacion}."
            )

        verificar_propiedad_planificacion(planificacion, usuario_actual)

        recomendaciones = RecomendacionRepository.listar_por_planificacion(
            db=db,
            id_planificacion=id_planificacion
        )

        alternativas: List[AlternativaComparacionSchema] = []
        for r in recomendaciones:
            ahorro = planificacion.presupuesto - r.costo_estimado
            porcentaje = (
                (r.costo_estimado / planificacion.presupuesto * Decimal("100.00")).quantize(Decimal("0.01"))
                if planificacion.presupuesto > 0
                else Decimal("0.00")
            )

            if r.tipo_recomendacion == "RESTAURANTE":
                nombre_rest = r.restaurante.nombre if r.restaurante else "Restaurante"
                zona_rest = r.restaurante.ubicacion.zona if r.restaurante and r.restaurante.ubicacion else None
                dir_rest = r.restaurante.ubicacion.direccion if r.restaurante and r.restaurante.ubicacion else None
                platos_info = []
                for item in r.recomendacion_platos:
                    platos_info.append(
                        f"{item.cantidad}x '{item.plato.nombre if item.plato else 'Plato'}'"
                    )
                resumen_platos = ", ".join(platos_info) if platos_info else "Sin platos registrados"
                zona_desc = f" [{zona_rest}]" if zona_rest else ""
                resumen = (
                    f"Opción en restaurante {nombre_rest}{zona_desc} ({resumen_platos}) para {planificacion.cantidad_personas} personas. "
                    f"Costo: {r.costo_estimado} Bs (Ahorro: {ahorro} Bs, {porcentaje}% del presupuesto)."
                )

                alternativas.append(AlternativaComparacionSchema(
                    id_recomendacion=r.id_recomendacion,
                    tipo_recomendacion="RESTAURANTE",
                    nombre=nombre_rest,
                    costo_total=r.costo_estimado,
                    costo_por_persona=r.costo_por_persona,
                    ahorro_respecto_presupuesto=ahorro,
                    porcentaje_presupuesto_utilizado=porcentaje,
                    puntuacion=r.puntuacion,
                    distancia_estimada=r.distancia_estimada,
                    resumen=resumen,
                    id_restaurante=r.id_restaurante,
                    nombre_restaurante=nombre_rest,
                    zona_restaurante=zona_rest,
                    direccion_restaurante=dir_rest,
                    platos=[RecomendacionService._mapear_item_plato(p) for p in r.recomendacion_platos]
                ))

            elif r.tipo_recomendacion == "PREPARACION_PROPIA":
                prep = r.preparacion_propia
                nombre_prep = prep.nombre if prep else "Preparación propia"
                ingredientes_resumen = []
                lugares_set = set()

                if prep:
                    for ing in prep.ingredientes:
                        nom_ing = ing.ingrediente.nombre if ing.ingrediente else "Ingrediente"
                        ingredientes_resumen.append(f"{ing.cantidad} {ing.unidad_medida} de {nom_ing}")
                        if ing.lugar_compra:
                            lugares_set.add(ing.lugar_compra.nombre)

                lugares_resumen = sorted(list(lugares_set))
                resumen = (
                    f"Elaboración casera '{nombre_prep}' para {planificacion.cantidad_personas} personas. "
                    f"Costo en ingredientes: {r.costo_estimado} Bs (Ahorro: {ahorro} Bs, {porcentaje}% del presupuesto)."
                )

                alternativas.append(AlternativaComparacionSchema(
                    id_recomendacion=r.id_recomendacion,
                    tipo_recomendacion="PREPARACION_PROPIA",
                    nombre=nombre_prep,
                    costo_total=r.costo_estimado,
                    costo_por_persona=r.costo_por_persona,
                    ahorro_respecto_presupuesto=ahorro,
                    porcentaje_presupuesto_utilizado=porcentaje,
                    puntuacion=r.puntuacion,
                    distancia_estimada=r.distancia_estimada,
                    resumen=resumen,
                    id_preparacion_propia=prep.id_preparacion_propia if prep else None,
                    nombre_preparacion=nombre_prep,
                    ingredientes_resumen=ingredientes_resumen,
                    lugares_compra_resumen=lugares_resumen
                ))

        # Si la planificación tiene ubicación de referencia y existen opciones en la zona, priorizarlas para mejor costo
        candidatos_para_costo = alternativas
        if planificacion.ubicacion_referencia:
            candidatos_zona = [
                a for a in alternativas
                if a.tipo_recomendacion == "PREPARACION_PROPIA" or (a.distancia_estimada is not None and a.distancia_estimada <= Decimal("2.0"))
            ]
            if candidatos_zona:
                candidatos_para_costo = candidatos_zona

        mejor_costo = min(candidatos_para_costo, key=lambda x: x.costo_total) if candidatos_para_costo else None
        mejor_puntuacion = max(alternativas, key=lambda x: x.puntuacion) if alternativas else None

        return ComparacionPlanificacionRespuestaSchema(
            id_planificacion=planificacion.id_planificacion,
            presupuesto=planificacion.presupuesto,
            cantidad_personas=planificacion.cantidad_personas,
            tipo_comida=planificacion.tipo_comida,
            total_alternativas=len(alternativas),
            alternativas=alternativas,
            mejor_opcion_costo=mejor_costo,
            mejor_opcion_puntuacion=mejor_puntuacion
        )

    # --- Métodos auxiliares de mapeo ---
    @staticmethod
    def _mapear_item_plato(item: RecomendacionPlato) -> RecomendacionPlatoItemSchema:
        precio_unit = item.plato.precio if item.plato else Decimal("0.00")
        return RecomendacionPlatoItemSchema(
            id_recomendacion_plato=item.id_recomendacion_plato,
            id_plato=item.id_plato,
            nombre_plato=item.plato.nombre if item.plato else None,
            personas_cubiertas=item.plato.personas_cubiertas if item.plato else None,
            cantidad=item.cantidad,
            precio_unitario=precio_unit,
            subtotal=item.subtotal
        )

    @staticmethod
    def _mapear_a_schema(rec: Recomendacion) -> RecomendacionRespuestaSchema:
        nombre = None
        id_prep = None
        nom_prep = None
        zona_rest = None
        dir_rest = None

        if rec.tipo_recomendacion == "RESTAURANTE":
            nombre = rec.restaurante.nombre if rec.restaurante else "Restaurante"
            if rec.restaurante and rec.restaurante.ubicacion:
                zona_rest = rec.restaurante.ubicacion.zona
                dir_rest = rec.restaurante.ubicacion.direccion
        elif rec.tipo_recomendacion == "PREPARACION_PROPIA" and rec.preparacion_propia:
            nombre = rec.preparacion_propia.nombre
            id_prep = rec.preparacion_propia.id_preparacion_propia
            nom_prep = rec.preparacion_propia.nombre

        return RecomendacionRespuestaSchema(
            id_recomendacion=rec.id_recomendacion,
            id_planificacion=rec.id_planificacion,
            tipo_recomendacion=rec.tipo_recomendacion,
            nombre=nombre,
            descripcion=rec.descripcion,
            costo_total=rec.costo_estimado,
            costo_por_persona=rec.costo_por_persona,
            puntuacion=rec.puntuacion,
            distancia_estimada=rec.distancia_estimada,
            id_restaurante=rec.id_restaurante,
            nombre_restaurante=rec.restaurante.nombre if rec.restaurante else None,
            zona_restaurante=zona_rest,
            direccion_restaurante=dir_rest,
            id_preparacion_propia=id_prep,
            nombre_preparacion=nom_prep,
            fecha_generacion=rec.fecha_generacion,
            platos=[RecomendacionService._mapear_item_plato(p) for p in rec.recomendacion_platos]
        )
