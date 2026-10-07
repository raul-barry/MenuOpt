# CASO DE USO: CU15 - Consultar ingredientes para preparación propia
# CASO DE USO: CU16 - Consultar lugares de compra
from decimal import Decimal
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.plato import Plato
from app.models.planificacion import Planificacion
from app.models.recomendacion import Recomendacion
from app.repositories.recomendacion_repository import RecomendacionRepository
from app.repositories.preparacion_repository import PreparacionRepository
from app.repositories.ingrediente_lugar_compra_repository import IngredienteLugarCompraRepository
from app.security.propiedad import verificar_propiedad_planificacion
from app.services.recomendacion_algoritmo import (
    calcular_factor_preparacion,
    calcular_cantidad_ingrediente,
    son_unidades_compatibles,
    calcular_costo_ingrediente,
    calcular_costo_por_persona,
    calcular_puntuacion,
)
from app.schemas.preparacion_propia import (
    PreparacionPropiaRespuestaSchema,
    ItemCompraLugarSchema,
    AgrupacionCompraLugarItemSchema,
    LugaresCompraRecomendacionRespuestaSchema,
)
from app.schemas.preparacion_ingrediente import PreparacionIngredienteItemSchema


class PreparacionService:
    """
    Servicio encargado del cálculo, consulta de ingredientes (CU15) y lugares de compra (CU16)
    para alternativas gastronómicas de preparación propia.
    """

    # =========================================================================
    # LÓGICA DE EVALUACIÓN Y CÁLCULO DE RECETAS PARA PREPARACIÓN PROPIA
    # =========================================================================

    @staticmethod
    def evaluar_plato_para_preparacion(
        db: Session,
        plato: Plato,
        planificacion: Planificacion
    ) -> Optional[Dict[str, Any]]:
        """
        Evalúa si la receta del plato puede convertirse en una alternativa viable de preparación propia:
        1. Escala cantidades según personas_cubiertas y comensales.
        2. Busca los precios más económicos disponibles en lugares de compra activos.
        3. Valida compatibilidad estricta de unidades de medida (sin conversiones inventadas).
        4. Si algún ingrediente carece de precio, disponibilidad o unidad compatible, se descarta.
        5. Valida que el costo total de ingredientes no supere el presupuesto.
        """
        if not plato.plato_ingredientes:
            return None

        factor = calcular_factor_preparacion(
            cantidad_personas=planificacion.cantidad_personas,
            personas_cubiertas=plato.personas_cubiertas
        )

        ids_ingredientes = [pi.id_ingrediente for pi in plato.plato_ingredientes]
        mejores_precios = IngredienteLugarCompraRepository.buscar_mejores_precios(db, ids_ingredientes)

        items_calculados = []
        costo_total = Decimal("0.00")

        for pi in plato.plato_ingredientes:
            rel = mejores_precios.get(pi.id_ingrediente)
            if not rel:
                # Ingrediente sin precio o sin lugar activo disponible
                return None

            # Validar compatibilidad de unidades de medida
            if not son_unidades_compatibles(pi.unidad_medida, rel.unidad_medida):
                # Unidades no compatibles: no se inventan conversiones
                return None

            cant_total = calcular_cantidad_ingrediente(pi.cantidad, factor)
            costo_ing = calcular_costo_ingrediente(
                cantidad_total=cant_total,
                cantidad_referencia=rel.cantidad_referencia,
                precio=rel.precio
            )
            costo_total += costo_ing

            items_calculados.append({
                "id_ingrediente": pi.id_ingrediente,
                "nombre_ingrediente": pi.ingrediente.nombre if pi.ingrediente else None,
                "cantidad": cant_total,
                "unidad_medida": pi.unidad_medida,
                "precio_unitario_usado": rel.precio,
                "costo_estimado": costo_ing,
                "id_lugar_compra": rel.id_lugar_compra,
                "lugar_compra": rel.lugar_compra
            })

        # Validar restricción presupuestaria estricta
        if costo_total > planificacion.presupuesto:
            return None

        costo_pp = calcular_costo_por_persona(costo_total, planificacion.cantidad_personas)
        puntuacion = calcular_puntuacion(planificacion.presupuesto, costo_total)

        return {
            "plato_base": plato,
            "nombre": f"Preparación propia: {plato.nombre}",
            "descripcion": f"Elaboración casera basada en la receta de {plato.nombre}",
            "costo_total": costo_total,
            "costo_pp": costo_pp,
            "puntuacion": puntuacion,
            "cantidad_personas": planificacion.cantidad_personas,
            "ingredientes": items_calculados
        }

    # =========================================================================
    # CASO DE USO: CU15 - CONSULTAR INGREDIENTES PARA PREPARACIÓN PROPIA
    # =========================================================================

    @staticmethod
    def obtener_preparacion_por_recomendacion(
        db: Session,
        id_recomendacion: int,
        usuario_actual: Usuario
    ) -> PreparacionPropiaRespuestaSchema:
        """
        LÓGICA CU15 - Consultar Ingredientes para Preparación Propia:
        Retorna el detalle desglosado de ingredientes requeridos, cantidades escaladas,
        costos y el lugar sugerido de compra para una alternativa de tipo PREPARACION_PROPIA.
        """
        rec = RecomendacionRepository.buscar_por_id(db, id_recomendacion)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la recomendación con ID {id_recomendacion}."
            )

        verificar_propiedad_planificacion(rec.planificacion, usuario_actual)

        if rec.tipo_recomendacion != "PREPARACION_PROPIA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La recomendación con ID {id_recomendacion} es de tipo '{rec.tipo_recomendacion}'. Solo aplica a PREPARACION_PROPIA."
            )

        prep = PreparacionRepository.buscar_por_recomendacion(db, id_recomendacion)
        if not prep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el detalle de preparación para la recomendación ID {id_recomendacion}."
            )

        ingredientes_schema = []
        for item in prep.ingredientes:
            ingredientes_schema.append(PreparacionIngredienteItemSchema(
                id_preparacion_ingrediente=item.id_preparacion_ingrediente,
                id_ingrediente=item.id_ingrediente,
                nombre_ingrediente=item.ingrediente.nombre if item.ingrediente else None,
                cantidad=item.cantidad,
                unidad_medida=item.unidad_medida,
                precio_unitario_usado=item.precio_unitario_usado,
                costo_estimado=item.costo_estimado,
                id_lugar_compra=item.id_lugar_compra,
                nombre_lugar_compra=item.lugar_compra.nombre if item.lugar_compra else None
            ))

        return PreparacionPropiaRespuestaSchema(
            id_preparacion_propia=prep.id_preparacion_propia,
            id_recomendacion=prep.id_recomendacion,
            nombre=prep.nombre,
            descripcion=prep.descripcion,
            cantidad_personas=prep.cantidad_personas,
            costo_estimado=prep.costo_estimado,
            costo_por_persona=rec.costo_por_persona,
            ingredientes=ingredientes_schema
        )

    # =========================================================================
    # CASO DE USO: CU16 - CONSULTAR LUGARES DE COMPRA
    # =========================================================================

    @staticmethod
    def obtener_lugares_compra_recomendacion(
        db: Session,
        id_recomendacion: int,
        usuario_actual: Usuario
    ) -> LugaresCompraRecomendacionRespuestaSchema:
        """
        LÓGICA CU16 - Consultar Lugares de Compra:
        Retorna la lista de ingredientes agrupados por establecimiento comercial de compra
        para optimizar y planificar las compras físicas del consumidor.
        """
        rec = RecomendacionRepository.buscar_por_id(db, id_recomendacion)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la recomendación con ID {id_recomendacion}."
            )

        verificar_propiedad_planificacion(rec.planificacion, usuario_actual)

        if rec.tipo_recomendacion != "PREPARACION_PROPIA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La recomendación con ID {id_recomendacion} es de tipo '{rec.tipo_recomendacion}'. Solo aplica a PREPARACION_PROPIA."
            )

        prep = PreparacionRepository.buscar_por_recomendacion(db, id_recomendacion)
        if not prep:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el registro de preparación para la recomendación ID {id_recomendacion}."
            )

        # Agrupación por lugar de compra
        mapa_lugares: Dict[Optional[int], Dict[str, Any]] = {}

        for item in prep.ingredientes:
            id_lugar = item.id_lugar_compra
            lugar_obj = item.lugar_compra

            if id_lugar not in mapa_lugares:
                nombre_lugar = lugar_obj.nombre if lugar_obj else "Establecimiento no asignado"
                tipo_lugar = lugar_obj.tipo if lugar_obj else None
                telefono = lugar_obj.telefono if lugar_obj else None
                direccion = lugar_obj.ubicacion.direccion if lugar_obj and lugar_obj.ubicacion else None
                zona = lugar_obj.ubicacion.zona if lugar_obj and lugar_obj.ubicacion else None
                ciudad = lugar_obj.ubicacion.ciudad if lugar_obj and lugar_obj.ubicacion else None

                mapa_lugares[id_lugar] = {
                    "id_lugar_compra": id_lugar,
                    "nombre_lugar": nombre_lugar,
                    "tipo_lugar": tipo_lugar,
                    "telefono": telefono,
                    "direccion": direccion,
                    "zona": zona,
                    "ciudad": ciudad,
                    "items": [],
                    "subtotal": Decimal("0.00")
                }

            mapa_lugares[id_lugar]["items"].append(ItemCompraLugarSchema(
                id_ingrediente=item.id_ingrediente,
                nombre_ingrediente=item.ingrediente.nombre if item.ingrediente else "Ingrediente",
                cantidad_requerida=item.cantidad,
                unidad_medida=item.unidad_medida,
                precio_referencia=item.precio_unitario_usado or Decimal("0.00"),
                subtotal=item.costo_estimado
            ))
            mapa_lugares[id_lugar]["subtotal"] += item.costo_estimado

        lugares_agrupados = []
        for datos in mapa_lugares.values():
            lugares_agrupados.append(AgrupacionCompraLugarItemSchema(
                id_lugar_compra=datos["id_lugar_compra"],
                nombre_lugar=datos["nombre_lugar"],
                tipo_lugar=datos["tipo_lugar"],
                telefono=datos["telefono"],
                direccion=datos["direccion"],
                zona=datos["zona"],
                ciudad=datos["ciudad"],
                items=datos["items"],
                subtotal_estimado=datos["subtotal"]
            ))

        return LugaresCompraRecomendacionRespuestaSchema(
            id_recomendacion=rec.id_recomendacion,
            id_planificacion=rec.id_planificacion,
            nombre_preparacion=prep.nombre,
            costo_total_estimado=prep.costo_estimado,
            cantidad_personas=prep.cantidad_personas,
            total_lugares=len(lugares_agrupados),
            lugares=lugares_agrupados
        )
