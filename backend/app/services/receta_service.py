# CASO DE USO: CU15 - Biblioteca de Recetas
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.receta import Receta, RecetaIngrediente
from app.models.usuario import Usuario
from app.models.ingrediente import Ingrediente
from app.repositories.ingrediente_lugar_compra_repository import IngredienteLugarCompraRepository
from app.schemas.receta import (
    RecetaCrearSchema,
    RecetaRespuestaSchema,
    RecetaIngredienteRespuestaSchema
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
