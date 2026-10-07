from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ingrediente import Ingrediente
from app.repositories.ingrediente_repository import IngredienteRepository
from app.schemas.ingrediente import CrearIngredienteSchema, ActualizarIngredienteSchema


class IngredienteService:
    """
    Servicio encargado de la lógica de negocio del catálogo de Ingredientes (CU09).
    """

    # =========================================================================
    # CASO DE USO: CU09 - GESTIONAR INGREDIENTES
    # Descripción: Permite consultar el catálogo general de ingredientes,
    #              registrar nuevos ingredientes y actualizar sus características.
    # =========================================================================

    # --- CU09: Consultar Catálogo de Ingredientes ---
    @staticmethod
    def listar_ingredientes(db: Session, estado: Optional[str] = None) -> List[Ingrediente]:
        """
        LÓGICA CU09 - Listar Ingredientes:
        Obtiene los ingredientes disponibles en el catálogo general.
        """
        return IngredienteRepository.listar(db, estado=estado)

    # --- CU09: Obtener Detalle de un Ingrediente ---
    @staticmethod
    def obtener_por_id(db: Session, id_ingrediente: int) -> Ingrediente:
        """
        LÓGICA CU09 - Obtener Ingrediente:
        Recupera los datos de un ingrediente por su identificador.
        """
        ingrediente = IngredienteRepository.buscar_por_id(db, id_ingrediente)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el ingrediente con ID {id_ingrediente}."
            )
        return ingrediente

    # --- CU09: Registrar Nuevo Ingrediente ---
    @staticmethod
    def crear_ingrediente(db: Session, datos: CrearIngredienteSchema) -> Ingrediente:
        """
        LÓGICA CU09 - Crear Ingrediente:
        Valida que el nombre del ingrediente no esté duplicado en el catálogo.
        """
        nombre_limpio = datos.nombre.strip()
        existente = IngredienteRepository.buscar_por_nombre(db, nombre_limpio)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un ingrediente registrado con el nombre '{nombre_limpio}'."
            )

        nuevo_ingrediente = Ingrediente(
            nombre=nombre_limpio,
            unidad_medida=datos.unidad_medida.strip(),
            precio_estimado=datos.precio_estimado,
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            estado=datos.estado.upper() if datos.estado else "ACTIVO"
        )
        return IngredienteRepository.crear(db, nuevo_ingrediente)

    # --- CU09: Modificar Ingrediente Existente ---
    @staticmethod
    def actualizar_ingrediente(
        db: Session,
        id_ingrediente: int,
        datos: ActualizarIngredienteSchema
    ) -> Ingrediente:
        """
        LÓGICA CU09 - Modificar Ingrediente:
        Actualiza los datos del ingrediente en el catálogo general.
        """
        ingrediente = IngredienteRepository.buscar_por_id(db, id_ingrediente)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el ingrediente con ID {id_ingrediente}."
            )

        if datos.nombre is not None:
            nombre_limpio = datos.nombre.strip()
            if nombre_limpio.lower() != ingrediente.nombre.lower():
                existente = IngredienteRepository.buscar_por_nombre(db, nombre_limpio)
                if existente and existente.id_ingrediente != id_ingrediente:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El nombre '{nombre_limpio}' ya está en uso por otro ingrediente."
                    )
            ingrediente.nombre = nombre_limpio

        if datos.unidad_medida is not None:
            ingrediente.unidad_medida = datos.unidad_medida.strip()

        if datos.precio_estimado is not None:
            ingrediente.precio_estimado = datos.precio_estimado

        if datos.descripcion is not None:
            ingrediente.descripcion = datos.descripcion.strip() if datos.descripcion else None

        if datos.estado is not None:
            ingrediente.estado = datos.estado.upper()

        return IngredienteRepository.actualizar(db, ingrediente)
