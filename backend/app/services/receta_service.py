# CASO DE USO: CU15 - Biblioteca de Recetas
import re
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.receta import Receta, RecetaIngrediente
from app.models.usuario import Usuario
from app.models.ingrediente import Ingrediente
from app.models.lugar_compra import LugarCompra
from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
from app.repositories.ingrediente_lugar_compra_repository import IngredienteLugarCompraRepository
from app.schemas.receta import (
    RecetaCrearSchema,
    RecetaRespuestaSchema,
    RecetaIngredienteRespuestaSchema,
    RecetaConsultaIARespuestaSchema,
    RecetaIngredienteFaltanteSchema,
    RecetaTiendaRecomendadaSchema
)


class RecetaService:
    """
    Servicio exclusivo para la Biblioteca de Recetas (CU15).
    Permite consultar recetas gastronómicas y que el administrador añada nuevas recetas.
    """

    @classmethod
    def listar_recetas(
        cls,
        db: Session,
        tipo_comida: Optional[str] = None,
        busqueda: Optional[str] = None
    ) -> List[RecetaRespuestaSchema]:
        query = db.query(Receta).options(
            joinedload(Receta.usuario_creador),
            joinedload(Receta.ingredientes).joinedload(RecetaIngrediente.ingrediente)
        )

        if tipo_comida and tipo_comida.strip().upper() != "TODAS":
            query = query.filter(func.upper(Receta.tipo_comida) == tipo_comida.strip().upper())

        if busqueda and busqueda.strip():
            filtro = f"%{busqueda.strip().lower()}%"
            query = query.filter(
                func.lower(Receta.nombre).like(filtro) |
                func.lower(Receta.descripcion).like(filtro) |
                func.lower(Receta.origen).like(filtro)
            )

        recetas = query.order_by(Receta.id_receta.desc()).all()
        return [cls._mapear_receta_a_schema(db, r) for r in recetas]

    @classmethod
    def buscar_por_id(cls, db: Session, id_receta: int) -> RecetaRespuestaSchema:
        receta = db.query(Receta).options(
            joinedload(Receta.usuario_creador),
            joinedload(Receta.ingredientes).joinedload(RecetaIngrediente.ingrediente)
        ).filter(Receta.id_receta == id_receta).first()

        if not receta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la receta con ID {id_receta} en la biblioteca."
            )

        return cls._mapear_receta_a_schema(db, receta)

    @classmethod
    def crear_receta(
        cls,
        db: Session,
        datos: RecetaCrearSchema,
        usuario_actual: Usuario
    ) -> RecetaRespuestaSchema:
        # Validación: solo Administrador puede añadir recetas a la biblioteca
        if usuario_actual.rol.nombre != "ADMINISTRADOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden añadir nuevas recetas a la biblioteca."
            )

        nueva_receta = Receta(
            nombre=datos.nombre.strip(),
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            instrucciones=datos.instrucciones.strip() if datos.instrucciones else None,
            tipo_comida=datos.tipo_comida.strip().upper(),
            porciones=datos.porciones,
            tiempo_minutos=datos.tiempo_minutos,
            dificultad=datos.dificultad.strip().upper(),
            origen=datos.origen.strip() if datos.origen else "Tradicional Cruceña",
            imagen_url=datos.imagen_url.strip() if datos.imagen_url else None,
            id_usuario_creador=usuario_actual.id_usuario
        )

        for item in datos.ingredientes:
            # Si id_ingrediente está presente, verificar existencia
            nom_ing = item.nombre_ingrediente.strip()
            if item.id_ingrediente:
                ing_db = db.query(Ingrediente).filter_by(id_ingrediente=item.id_ingrediente).first()
                if ing_db:
                    nom_ing = ing_db.nombre

            ri = RecetaIngrediente(
                id_ingrediente=item.id_ingrediente,
                nombre_ingrediente=nom_ing,
                cantidad=item.cantidad,
                unidad_medida=item.unidad_medida.strip().lower()
            )
            nueva_receta.ingredientes.append(ri)

        db.add(nueva_receta)
        db.commit()
        db.refresh(nueva_receta)

        return cls._mapear_receta_a_schema(db, nueva_receta)

    @classmethod
    def eliminar_receta(
        cls,
        db: Session,
        id_receta: int,
        usuario_actual: Usuario
    ) -> dict:
        if usuario_actual.rol.nombre != "ADMINISTRADOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden eliminar recetas de la biblioteca."
            )

        receta = db.query(Receta).filter_by(id_receta=id_receta).first()
        if not receta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la receta con ID {id_receta}."
            )

        db.delete(receta)
        db.commit()
        return {"mensaje": f"Receta '{receta.nombre}' eliminada correctamente de la biblioteca."}

    @classmethod
    def consultar_ia(
        cls,
        db: Session,
        mensaje: str,
        comensales: Optional[int] = None
    ) -> RecetaConsultaIARespuestaSchema:
        msg_lower = mensaje.lower()

        # 1. Determinar comensales
        personas = comensales
        if not personas or personas <= 0:
            m_pers = re.search(r"(?:para|somos|alcanza para|comensales)?\s*(\d+)\s*(?:personas|comensales|platos|amigos)?", msg_lower)
            if m_pers and m_pers.group(1):
                val = int(m_pers.group(1))
                if 1 <= val <= 30:
                    personas = val
            if not personas:
                personas = 2

        # 2. Detectar ingredientes del catálogo presentes en el mensaje
        catalogo = db.query(Ingrediente).all()
        ingredientes_detectados = []
        ids_detectados = set()

        palabras_clave = {
            "pollo": "pechuga de pollo",
            "pechuga": "pechuga de pollo",
            "carne": "carne de res",
            "lomo": "carne de res",
            "pulpa": "carne de res",
            "molida": "carne molida",
            "arroz": "arroz grano de oro",
            "papa": "papa holandesa",
            "papas": "papa holandesa",
            "fideo": "fideos espagueti",
            "fideos": "fideos espagueti",
            "espagueti": "fideos espagueti",
            "pasta": "fideos espagueti",
            "huevo": "huevos",
            "huevos": "huevos",
            "tomate": "tomate manzano",
            "tomates": "tomate manzano",
            "cebolla": "cebolla roja",
            "cebollas": "cebolla roja",
            "queso": "queso chaqueño",
            "leche": "leche entera",
            "harina": "harina de trigo",
            "zanahoria": "zanahoria",
            "pimiento": "pimiento morrón",
            "morron": "pimiento morrón",
            "morrón": "pimiento morrón",
            "aceite": "aceite vegetal"
        }

        for ing in catalogo:
            ing_nombre_lower = ing.nombre.lower()
            if ing_nombre_lower in msg_lower:
                ingredientes_detectados.append(ing)
                ids_detectados.add(ing.id_ingrediente)

        for kw, ing_target in palabras_clave.items():
            if re.search(r"\b" + re.escape(kw) + r"\b", msg_lower):
                for ing in catalogo:
                    if ing_target in ing.nombre.lower() and ing.id_ingrediente not in ids_detectados:
                        ingredientes_detectados.append(ing)
                        ids_detectados.add(ing.id_ingrediente)

        # 3. Evaluar y rankear todas las recetas de la biblioteca
        todas_recetas = db.query(Receta).options(
            joinedload(Receta.usuario_creador),
            joinedload(Receta.ingredientes).joinedload(RecetaIngrediente.ingrediente)
        ).all()

        ranking = []
        for r in todas_recetas:
            ids_receta = {ri.id_ingrediente for ri in r.ingredientes if ri.id_ingrediente is not None}
            nombres_receta = [ri.nombre_ingrediente.lower() for ri in r.ingredientes]

            coincidencias_id = ids_receta.intersection(ids_detectados)
            coincidencias_texto = set()
            for kw in palabras_clave:
                if re.search(r"\b" + re.escape(kw) + r"\b", msg_lower):
                    for nom_r in nombres_receta:
                        if kw in nom_r:
                            coincidencias_texto.add(nom_r)

            total_coincidencias = len(coincidencias_id) + len(coincidencias_texto)
            porcentaje = (total_coincidencias / len(r.ingredientes)) if len(r.ingredientes) > 0 else 0
            ranking.append((r, total_coincidencias, porcentaje))

        ranking.sort(key=lambda x: (x[1], x[2]), reverse=True)

        mejores = [item[0] for item in ranking[:3]] if ranking else []
        receta_principal = mejores[0] if mejores else None

        # 4. Calcular ingredientes faltantes y mejores tiendas para la receta principal
        ingredientes_faltantes = []
        tiendas_map: Dict[str, Dict[str, Any]] = {}

        if receta_principal:
            factor_escala = (Decimal(str(personas)) / Decimal(str(receta_principal.porciones))) if receta_principal.porciones > 0 else Decimal("1.00")

            for ri in receta_principal.ingredientes:
                es_coincidente = False
                if ri.id_ingrediente and ri.id_ingrediente in ids_detectados:
                    es_coincidente = True
                else:
                    for d in ingredientes_detectados:
                        if d.nombre.lower() in ri.nombre_ingrediente.lower() or ri.nombre_ingrediente.lower() in d.nombre.lower():
                            es_coincidente = True
                            break

                if not es_coincidente:
                    cant_requerida = (ri.cantidad * factor_escala).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    tienda_nom = None
                    precio_ref = None

                    if ri.id_ingrediente:
                        mejor_ilc = db.query(IngredienteLugarCompra).options(
                            joinedload(IngredienteLugarCompra.lugar_compra)
                        ).filter(
                            IngredienteLugarCompra.id_ingrediente == ri.id_ingrediente,
                            IngredienteLugarCompra.disponible == True
                        ).order_by(IngredienteLugarCompra.precio.asc()).first()

                        if mejor_ilc:
                            tienda_nom = mejor_ilc.lugar_compra.nombre
                            precio_ref = mejor_ilc.precio
                            t_key = mejor_ilc.lugar_compra.nombre
                            if t_key not in tiendas_map:
                                tiendas_map[t_key] = {
                                    "tipo": mejor_ilc.lugar_compra.tipo,
                                    "insumos": [],
                                    "costo": Decimal("0.00")
                                }
                            tiendas_map[t_key]["insumos"].append(ri.nombre_ingrediente)
                            costo_item = ((cant_requerida / mejor_ilc.cantidad_referencia) * mejor_ilc.precio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                            tiendas_map[t_key]["costo"] += costo_item

                    ingredientes_faltantes.append(RecetaIngredienteFaltanteSchema(
                        nombre=ri.nombre_ingrediente,
                        cantidad_requerida=cant_requerida,
                        unidad_medida=ri.unidad_medida,
                        tienda_sugerida=tienda_nom or "Mercado Abasto Mayorista",
                        precio_referencial=precio_ref
                    ))

        tiendas_recomendadas = [
            RecetaTiendaRecomendadaSchema(
                nombre_tienda=k,
                tipo=v["tipo"],
                insumos_disponibles=v["insumos"],
                costo_estimado=v["costo"]
            )
            for k, v in tiendas_map.items()
        ]

        # 5. Generar respuesta comprensible y estructurada
        nombres_detectados_str = ", ".join([ing.nombre for ing in ingredientes_detectados]) if ingredientes_detectados else "los insumos disponibles"
        nombre_plato = receta_principal.nombre if receta_principal else "Plato Casero Familiar"
        tiempo_plato = receta_principal.tiempo_minutos if receta_principal else 35

        lineas_resp = []
        lineas_resp.append("### 👨‍🍳 Sugerencia del Asistente Culinario IA")
        lineas_resp.append(f"Con los ingredientes que tienes a mano (**{nombres_detectados_str}**), la mejor opción culinaria para preparar es:")
        lineas_resp.append(f"👉 **{nombre_plato}** ({receta_principal.tipo_comida if receta_principal else 'ALMUERZO'} - {receta_principal.dificultad if receta_principal else 'FÁCIL'}, ~{tiempo_plato} min).")
        lineas_resp.append("")
        lineas_resp.append("#### 👥 ¿Para cuántas personas?")
        lineas_resp.append(f"Con las proporciones calculadas, esta preparación te alcanza perfectamente para **{personas} persona{'s' if personas > 1 else ''}**.")
        lineas_resp.append("")

        if ingredientes_faltantes:
            lineas_resp.append("#### 🛒 ¿Dónde conseguir lo que falta y a qué precio?")
            lineas_resp.append("Para completar tu plato de forma óptima, te recomendamos los siguientes establecimientos en Santa Cruz:")
            for faltante in ingredientes_faltantes:
                pr_str = f" a aprox. **Bs {faltante.precio_referencial:.2f}**" if faltante.precio_referencial else ""
                lineas_resp.append(f"• **{faltante.nombre}** ({faltante.cantidad_requerida} {faltante.unidad_medida}): Puedes adquirirlo en **{faltante.tienda_sugerida}**{pr_str}.")
            if tiendas_recomendadas:
                mejor_tienda = tiendas_recomendadas[0]
                lineas_resp.append("")
                lineas_resp.append(f"💡 **Recomendación de compra:** Visitar **{mejor_tienda.nombre_tienda}** ({mejor_tienda.tipo}) te permitirá concentrar insumos con un estimado de **Bs {mejor_tienda.costo_estimado:.2f}**.")
        else:
            lineas_resp.append("#### 🛒 ¿Dónde comprar?")
            lineas_resp.append("¡Buenas noticias! Tienes prácticamente todos los insumos necesarios en tu cocina para preparar este plato sin necesidad de hacer compras adicionales.")

        if receta_principal and receta_principal.instrucciones:
            lineas_resp.append("")
            lineas_resp.append("#### 📝 Paso a paso de preparación:")
            lineas_resp.append(receta_principal.instrucciones)

        platos_schemas = [cls._mapear_receta_a_schema(db, r) for r in mejores]

        return RecetaConsultaIARespuestaSchema(
            mensaje_usuario=mensaje,
            respuesta_ia="\n".join(lineas_resp),
            porciones_sugeridas=personas,
            platos_sugeridos=platos_schemas,
            ingredientes_faltantes=ingredientes_faltantes,
            tiendas_recomendadas=tiendas_recomendadas
        )


    @classmethod
    def _mapear_receta_a_schema(cls, db: Session, receta: Receta) -> RecetaRespuestaSchema:
        ids_ing = [ri.id_ingrediente for ri in receta.ingredientes if ri.id_ingrediente is not None]
        mejores_precios = IngredienteLugarCompraRepository.buscar_mejores_precios(db, ids_ing) if ids_ing else {}

        items_resp: List[RecetaIngredienteRespuestaSchema] = []
        costo_total = Decimal("0.00")

        for ri in receta.ingredientes:
            precio_ref = None
            costo_sub = None

            if ri.id_ingrediente and ri.id_ingrediente in mejores_precios:
                rel = mejores_precios[ri.id_ingrediente]
                precio_ref = rel.precio
                # Subtotal = (cantidad / cantidad_referencia) * precio
                cant_ref = rel.cantidad_referencia if rel.cantidad_referencia > 0 else Decimal("1.00")
                costo_sub = ((ri.cantidad / cant_ref) * rel.precio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                costo_total += costo_sub

            items_resp.append(RecetaIngredienteRespuestaSchema(
                id_receta_ingrediente=ri.id_receta_ingrediente,
                id_receta=ri.id_receta,
                id_ingrediente=ri.id_ingrediente,
                nombre_ingrediente=ri.nombre_ingrediente,
                cantidad=ri.cantidad,
                unidad_medida=ri.unidad_medida,
                precio_referencial=precio_ref,
                costo_subtotal=costo_sub
            ))

        nombre_creador = None
        if receta.usuario_creador:
            nombre_creador = f"{receta.usuario_creador.nombres} {receta.usuario_creador.apellidos}".strip()

        return RecetaRespuestaSchema(
            id_receta=receta.id_receta,
            nombre=receta.nombre,
            descripcion=receta.descripcion,
            instrucciones=receta.instrucciones,
            tipo_comida=receta.tipo_comida,
            porciones=receta.porciones,
            tiempo_minutos=receta.tiempo_minutos,
            dificultad=receta.dificultad,
            origen=receta.origen,
            imagen_url=receta.imagen_url,
            fecha_creacion=receta.fecha_creacion,
            id_usuario_creador=receta.id_usuario_creador,
            nombre_creador=nombre_creador,
            ingredientes=items_resp,
            total_ingredientes=len(items_resp),
            costo_estimado_insumos=costo_total if costo_total > 0 else None
        )
