from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.categoria import CrearCategoriaSchema, ActualizarCategoriaSchema


class CategoriaService:
    """
    Servicio encargado de la lógica de negocio del catálogo de Categorías (CU07).
    """

    # =========================================================================
    # CASO DE USO: CU07 - GESTIONAR CATEGORÍAS
    # Descripción: Permite consultar el catálogo general de categorías activas,
    #              así como la creación y modificación protegida por administradores.
    # =========================================================================

    # --- CU07: Consultar Categorías Activas ---
    @staticmethod
    def listar_categorias(db: Session, solo_activas: bool = True) -> List[Categoria]:
        """
        LÓGICA CU07 - Listar Categorías:
        Retorna las categorías disponibles en el sistema.
        """
        if solo_activas:
            return CategoriaRepository.listar_activas(db)
        return CategoriaRepository.listar_todas(db)

    # --- CU07: Crear Nueva Categoría ---
    @staticmethod
    def crear_categoria(db: Session, datos: CrearCategoriaSchema) -> Categoria:
        """
        LÓGICA CU07 - Crear Categoría:
        Valida que el nombre de la categoría sea único y persiste la nueva entidad.
        """
        nombre_limpio = datos.nombre.strip()
        existente = CategoriaRepository.buscar_por_nombre(db, nombre_limpio)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoría registrada con el nombre '{nombre_limpio}'."
            )

        nueva_categoria = Categoria(
            nombre=nombre_limpio,
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            activo=datos.activo
        )
        return CategoriaRepository.crear(db, nueva_categoria)

    # --- CU07: Modificar Categoría Existente ---
    @staticmethod
    def actualizar_categoria(
        db: Session,
        id_categoria: int,
        datos: ActualizarCategoriaSchema
    ) -> Categoria:
        """
        LÓGICA CU07 - Modificar Categoría:
        Verifica existencia, previene duplicidad de nombres y actualiza la categoría.
        """
        categoria = CategoriaRepository.buscar_por_id(db, id_categoria)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la categoría con ID {id_categoria}."
            )

        if datos.nombre is not None:
            nombre_limpio = datos.nombre.strip()
            if nombre_limpio.lower() != categoria.nombre.lower():
                existente = CategoriaRepository.buscar_por_nombre(db, nombre_limpio)
                if existente and existente.id_categoria != id_categoria:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El nombre '{nombre_limpio}' ya está en uso por otra categoría."
                    )
            categoria.nombre = nombre_limpio

        if datos.descripcion is not None:
            categoria.descripcion = datos.descripcion.strip() if datos.descripcion else None

        if datos.activo is not None:
            categoria.activo = datos.activo

        return CategoriaRepository.actualizar(db, categoria)
