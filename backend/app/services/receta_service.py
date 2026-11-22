# CASO DE USO: CU15 - Biblioteca de Recetas
import re
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.receta import Receta, RecetaIngrediente
from app.models.usuario import Usuario
from app.models.ingrediente import Ingrediente
from app.repositories.ingrediente_lugar_compra_repository import IngredienteLugarCompraRepository
from app.services.recomendacion_algoritmo import son_unidades_compatibles
from app.ai.proveedor import obtener_proveedor_ia
from app.ai.proveedor import MockProveedorIA
from app.ai.formato import normalizar_respuesta
from app.schemas.receta import (
    RecetaCrearSchema,
    RecetaRespuestaSchema,
    RecetaIngredienteRespuestaSchema,
    RecetaConsultaIARespuestaSchema,
    RecetaIngredienteFaltanteSchema,
    RecetaTiendaRecomendadaSchema
)


def _normalizar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(caracter for caracter in texto if not unicodedata.combining(caracter))


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

        def ingrediente_mencionado(item: RecetaIngrediente) -> bool:
            if item.id_ingrediente is not None and item.id_ingrediente in ids_detectados:
                return True
            nombre_item = _normalizar_texto(item.nombre_ingrediente)
            return any(
                nombre_item in _normalizar_texto(detectado.nombre)
                or _normalizar_texto(detectado.nombre) in nombre_item
                for detectado in ingredientes_detectados
            )

        ranking = []
        for receta in todas_recetas:
            total = sum(1 for item in receta.ingredientes if ingrediente_mencionado(item))
            faltan = max(len(receta.ingredientes) - total, 0)
            cobertura = total / len(receta.ingredientes) if receta.ingredientes else 0
            ranking.append((receta, total, cobertura, faltan))

        ranking.sort(
            key=lambda item: (item[1], item[2], -item[3], -item[0].tiempo_minutos),
            reverse=True,
        )

        mejores = [item[0] for item in ranking if item[1] > 0][:3]
        receta_principal = mejores[0] if mejores else None

        # 4. Calcular ingredientes faltantes y mejores tiendas para la receta principal
        ingredientes_faltantes = []
        tiendas_map: Dict[str, Dict[str, Any]] = {}

        if receta_principal:
            factor_escala = (Decimal(str(personas)) / Decimal(str(receta_principal.porciones))) if receta_principal.porciones > 0 else Decimal("1.00")
            faltantes_receta = [
                item for item in receta_principal.ingredientes
                if not ingrediente_mencionado(item)
            ]
            precios_disponibles = IngredienteLugarCompraRepository.listar_precios_disponibles(
                db,
                [item.id_ingrediente for item in faltantes_receta if item.id_ingrediente is not None],
            )

            for item in faltantes_receta:
                cantidad = (item.cantidad * factor_escala).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                nombre = item.ingrediente.nombre if item.ingrediente else item.nombre_ingrediente
                precios_compatibles = [
                    precio for precio in precios_disponibles.get(item.id_ingrediente, [])
                    if item.id_ingrediente
                    and son_unidades_compatibles(item.unidad_medida, precio.unidad_medida)
                    and precio.cantidad_referencia > 0
                ]
                mejor_precio = min(
                    precios_compatibles,
                    key=lambda precio: precio.precio / precio.cantidad_referencia,
                    default=None,
                )

                tienda = mejor_precio.lugar_compra if mejor_precio else None
                if tienda:
                    ubicacion = tienda.ubicacion
                    direccion = ", ".join(
                        valor for valor in (
                            ubicacion.zona if ubicacion else None,
                            ubicacion.direccion if ubicacion else None,
                            ubicacion.ciudad if ubicacion else None,
                        ) if valor
                    ) or None
                    if tienda.nombre not in tiendas_map:
                        tiendas_map[tienda.nombre] = {
                            "tipo": tienda.tipo,
                            "ubicacion": direccion,
                            "insumos": [],
                            "costo": Decimal("0.00"),
                        }
                    tiendas_map[tienda.nombre]["insumos"].append(nombre)
                    subtotal = (
                        (cantidad / mejor_precio.cantidad_referencia) * mejor_precio.precio
                    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    tiendas_map[tienda.nombre]["costo"] += subtotal

                ingredientes_faltantes.append(RecetaIngredienteFaltanteSchema(
                    nombre=nombre,
                    cantidad_requerida=cantidad,
                    unidad_medida=item.unidad_medida,
                    tienda_sugerida=tienda.nombre if tienda else None,
                    precio_referencial=mejor_precio.precio if mejor_precio else None,
                ))

        tiendas_recomendadas = [
            RecetaTiendaRecomendadaSchema(
                nombre_tienda=k,
                tipo=v["tipo"],
                ubicacion=v["ubicacion"],
                insumos_disponibles=v["insumos"],
                costo_estimado=v["costo"]
            )
            for k, v in sorted(tiendas_map.items(), key=lambda item: item[1]["costo"])
        ]

        receta_contexto = None
        if receta_principal:
            factor_contexto = (
                Decimal(str(personas)) / Decimal(str(receta_principal.porciones))
                if receta_principal.porciones > 0 else Decimal("1.00")
            )
            receta_contexto = {
                "nombre": receta_principal.nombre,
                "tipo_comida": receta_principal.tipo_comida,
                "dificultad": receta_principal.dificultad,
                "tiempo_minutos": receta_principal.tiempo_minutos,
                "instrucciones": receta_principal.instrucciones,
                "ingredientes": [
                    {
                        "nombre": item.ingrediente.nombre if item.ingrediente else item.nombre_ingrediente,
                        "cantidad": str((item.cantidad * factor_contexto).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                        "unidad": item.unidad_medida,
                        "disponible": ingrediente_mencionado(item),
                    }
                    for item in receta_principal.ingredientes
                ],
            }

        datos_verificados = {
            "comensales": personas,
            "ingredientes_disponibles": [item.nombre for item in ingredientes_detectados],
            "receta": receta_contexto,
            "ingredientes_faltantes": [
                {
                    "nombre": item.nombre,
                    "cantidad": str(item.cantidad_requerida),
                    "unidad": item.unidad_medida,
                    "tienda": item.tienda_sugerida,
                    "precio": str(item.precio_referencial) if item.precio_referencial is not None else None,
                }
                for item in ingredientes_faltantes
            ],
            "tiendas_recomendadas": [
                {
                    "nombre": item.nombre_tienda,
                    "tipo": item.tipo,
                    "ubicacion": item.ubicacion,
                    "insumos": item.insumos_disponibles,
                    "costo_estimado": str(item.costo_estimado) if item.costo_estimado is not None else None,
                }
                for item in tiendas_recomendadas
            ],
        }
        if receta_principal:
            respuesta_ia = obtener_proveedor_ia().orientar_sobre_receta(mensaje, datos_verificados)
        else:
            respuesta_ia = MockProveedorIA().orientar_sobre_receta(mensaje, datos_verificados)

        platos_schemas = [cls._mapear_receta_a_schema(db, r) for r in mejores]

        return RecetaConsultaIARespuestaSchema(
            mensaje_usuario=mensaje,
            respuesta_ia=normalizar_respuesta(respuesta_ia),
            porciones_sugeridas=personas,
            platos_sugeridos=platos_schemas,
            ingredientes_faltantes=ingredientes_faltantes,
            tiendas_recomendadas=tiendas_recomendadas
        )


    @classmethod
    def _mapear_receta_a_schema(cls, db: Session, receta: Receta) -> RecetaRespuestaSchema:
        ids_ing = [ri.id_ingrediente for ri in receta.ingredientes if ri.id_ingrediente is not None]
        precios_por_ingrediente = IngredienteLugarCompraRepository.listar_precios_disponibles(db, ids_ing) if ids_ing else {}

        items_resp: List[RecetaIngredienteRespuestaSchema] = []
        costo_total = Decimal("0.00")

        for ri in receta.ingredientes:
            precio_ref = None
            costo_sub = None

            precios_compatibles = [
                precio for precio in precios_por_ingrediente.get(ri.id_ingrediente, [])
                if ri.id_ingrediente
                and son_unidades_compatibles(ri.unidad_medida, precio.unidad_medida)
                and precio.cantidad_referencia > 0
            ]
            if precios_compatibles:
                rel = min(precios_compatibles, key=lambda precio: precio.precio / precio.cantidad_referencia)
                precio_ref = rel.precio
                # Subtotal = (cantidad / cantidad_referencia) * precio
                cant_ref = rel.cantidad_referencia if rel.cantidad_referencia > 0 else Decimal("1.00")
                costo_sub = ((ri.cantidad / cant_ref) * rel.precio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                costo_total += costo_sub

            items_resp.append(RecetaIngredienteRespuestaSchema(
                id_receta_ingrediente=ri.id_receta_ingrediente,
                id_receta=ri.id_receta,
                id_ingrediente=ri.id_ingrediente,
                nombre_ingrediente=ri.ingrediente.nombre if ri.ingrediente else ri.nombre_ingrediente,
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
