from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.plato import Plato
from app.models.plato_ingrediente import PlatoIngrediente
from app.repositories.plato_repository import PlatoRepository
from app.repositories.restaurante_repository import RestauranteRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.repositories.preferencia_repository import PreferenciaRepository
from app.repositories.plato_preferencia_repository import PlatoPreferenciaRepository
from app.schemas.plato import (
    CrearPlatoSchema,
    ActualizarPlatoSchema
)
from app.schemas.plato_ingrediente import (
    AsociarIngredientePlatoSchema,
    ActualizarIngredientePlatoSchema,
    PlatoIngredienteDetalleSchema
)
from app.schemas.plato_preferencia import PlatoPreferenciasRespuestaSchema
from app.security.propiedad import verificar_propiedad_restaurante, verificar_propiedad_plato


class PlatoService:
    """
    Servicio encargado de la gestión de Platos (CU08), relación con Ingredientes (CU09)
    y Disponibilidad (CU10).
    """

    # =========================================================================
    # CASO DE USO: CU08 - GESTIONAR PLATOS
    # Descripción: Permite listar, registrar, consultar, modificar y cambiar el
    #              estado de platos de un restaurante protegiendo la titularidad del negocio.
    # =========================================================================

    # --- CU08: Listar Platos de un Restaurante ---
    @staticmethod
    def listar_platos_por_restaurante(
        db: Session,
        id_restaurante: int,
        id_categoria: Optional[int] = None,
        tipo_comida: Optional[str] = None,
        disponible: Optional[bool] = None,
        estado: Optional[str] = None
    ) -> List[Plato]:
        """
        LÓGICA CU08 - Listar Platos:
        Retorna la carta de platos del restaurante con filtros opcionales.
        """
        restaurante = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not restaurante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el restaurante con ID {id_restaurante}."
            )

        return PlatoRepository.listar_por_restaurante(
            db=db,
            id_restaurante=id_restaurante,
            id_categoria=id_categoria,
            tipo_comida=tipo_comida,
            disponible=disponible,
            estado=estado
        )

    # --- CU08: Consultar Detalle de un Plato ---
    @staticmethod
    def obtener_plato_por_id(db: Session, id_plato: int) -> Plato:
        """
        LÓGICA CU08 - Obtener Detalle de Plato:
        Recupera la información completa de un plato por su ID.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )
        return plato

    # --- CU08: Registrar Nuevo Plato en Restaurante ---
    @staticmethod
    def crear_plato(
        db: Session,
        id_restaurante: int,
        datos: CrearPlatoSchema,
        usuario_actual: Usuario
    ) -> Plato:
        """
        LÓGICA CU08 - Registrar Plato:
        Verifica la propiedad del restaurante, comprueba la validez de la categoría
        y persiste el nuevo plato con precio decimal no negativo y personas > 0.
        """
        restaurante = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not restaurante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el restaurante con ID {id_restaurante}."
            )

        # Regla de propiedad: solo el responsable o ADMINISTRADOR pueden añadir platos
        verificar_propiedad_restaurante(restaurante, usuario_actual)

        # Verificar que el restaurante esté activo
        if restaurante.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden agregar platos a un restaurante inactivo."
            )

        # Verificar existencia de la categoría
        categoria = CategoriaRepository.buscar_por_id(db, datos.id_categoria)
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la categoría con ID {datos.id_categoria}."
            )

        nuevo_plato = Plato(
            nombre=datos.nombre.strip(),
            imagen_url=datos.imagen_url.strip() if datos.imagen_url else None,
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            precio=datos.precio,
            tipo_comida=datos.tipo_comida.strip() if datos.tipo_comida else None,
            personas_cubiertas=datos.personas_cubiertas,
            disponible=datos.disponible,
            estado="ACTIVO",
            id_restaurante=id_restaurante,
            id_categoria=datos.id_categoria
        )

        return PlatoRepository.crear(db, nuevo_plato)

    # --- CU08: Modificar Plato Existente ---
    @staticmethod
    def actualizar_plato(
        db: Session,
        id_plato: int,
        datos: ActualizarPlatoSchema,
        usuario_actual: Usuario
    ) -> Plato:
        """
        LÓGICA CU08 - Modificar Plato:
        Verifica que el plato pertenezca al restaurante del usuario autenticado.
        Permite actualizar características culinarias, categoría y precio.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        verificar_propiedad_plato(plato, usuario_actual)

        if datos.id_categoria is not None:
            categoria = CategoriaRepository.buscar_por_id(db, datos.id_categoria)
            if not categoria:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No se encontró la categoría con ID {datos.id_categoria}."
                )
            plato.id_categoria = datos.id_categoria

        if datos.nombre is not None:
            plato.nombre = datos.nombre.strip()
        if "imagen_url" in datos.model_fields_set:
            plato.imagen_url = datos.imagen_url.strip() if datos.imagen_url else None
        if datos.descripcion is not None:
            plato.descripcion = datos.descripcion.strip() if datos.descripcion else None
        if datos.precio is not None:
            plato.precio = datos.precio
        if datos.tipo_comida is not None:
            plato.tipo_comida = datos.tipo_comida.strip() if datos.tipo_comida else None
        if datos.personas_cubiertas is not None:
            plato.personas_cubiertas = datos.personas_cubiertas
        if datos.disponible is not None:
            plato.disponible = datos.disponible

        return PlatoRepository.actualizar(db, plato)

    # --- CU08: Cambiar Estado del Plato (Activación / Desactivación Lógica) ---
    @staticmethod
    def cambiar_estado(
        db: Session,
        id_plato: int,
        nuevo_estado: str,
        usuario_actual: Usuario
    ) -> Plato:
        """
        LÓGICA CU08 - Cambiar Estado de Plato:
        Habilita o deshabilita lógicamente el plato en el sistema.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        verificar_propiedad_plato(plato, usuario_actual)

        plato.estado = nuevo_estado.upper()
        return PlatoRepository.actualizar(db, plato)

    # =========================================================================
    # CASO DE USO: CU09 - RELACIÓN DE PLATOS CON INGREDIENTES
    # Descripción: Permite asignar ingredientes del catálogo al plato, consultar
    #              su composición, modificar cantidades y eliminar la relación.
    # =========================================================================

    # --- CU09: Relacionar Ingrediente con Plato ---
    @staticmethod
    def asociar_ingrediente(
        db: Session,
        id_plato: int,
        datos: AsociarIngredientePlatoSchema,
        usuario_actual: Usuario
    ) -> PlatoIngredienteDetalleSchema:
        """
        LÓGICA CU09 - Asociar Ingrediente a Plato:
        Valida propiedad, verifica existencia del ingrediente en catálogo y comprueba
        que no esté asignado dos veces al mismo plato (restricción única id_plato + id_ingrediente).
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        verificar_propiedad_plato(plato, usuario_actual)

        ingrediente = IngredienteRepository.buscar_por_id(db, datos.id_ingrediente)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el ingrediente con ID {datos.id_ingrediente}."
            )

        # Verificar duplicidad en la receta
        relacion_existente = PlatoRepository.buscar_relacion_ingrediente(db, id_plato, datos.id_ingrediente)
        if relacion_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El ingrediente '{ingrediente.nombre}' ya se encuentra asignado a este plato."
            )

        nueva_relacion = PlatoIngrediente(
            id_plato=id_plato,
            id_ingrediente=datos.id_ingrediente,
            cantidad=datos.cantidad,
            unidad_medida=datos.unidad_medida.strip()
        )
        guardada = PlatoRepository.asociar_ingrediente(db, nueva_relacion)

        return PlatoIngredienteDetalleSchema(
            id_plato_ingrediente=guardada.id_plato_ingrediente,
            id_ingrediente=ingrediente.id_ingrediente,
            nombre_ingrediente=ingrediente.nombre,
            cantidad=guardada.cantidad,
            unidad_medida=guardada.unidad_medida,
            precio_estimado=ingrediente.precio_estimado
        )

    # --- CU09: Consultar Ingredientes de un Plato ---
    @staticmethod
    def listar_ingredientes_de_plato(db: Session, id_plato: int) -> List[PlatoIngredienteDetalleSchema]:
        """
        LÓGICA CU09 - Consultar Ingredientes del Plato:
        Devuelve la lista detallada de ingredientes que conforman la receta del plato.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        relaciones = PlatoRepository.listar_ingredientes_de_plato(db, id_plato)
        resultado = []
        for r in relaciones:
            resultado.append(
                PlatoIngredienteDetalleSchema(
                    id_plato_ingrediente=r.id_plato_ingrediente,
                    id_ingrediente=r.id_ingrediente,
                    nombre_ingrediente=r.ingrediente.nombre if r.ingrediente else "",
                    cantidad=r.cantidad,
                    unidad_medida=r.unidad_medida,
                    precio_estimado=r.ingrediente.precio_estimado if r.ingrediente else None
                )
            )
        return resultado

    # --- CU09: Modificar Ingrediente de un Plato ---
    @staticmethod
    def actualizar_ingrediente_de_plato(
        db: Session,
        id_plato: int,
        id_ingrediente: int,
        datos: ActualizarIngredientePlatoSchema,
        usuario_actual: Usuario
    ) -> PlatoIngredienteDetalleSchema:
        """
        LÓGICA CU09 - Modificar Ingrediente de Plato:
        Actualiza la cantidad y unidad de medida requerida de un ingrediente asignado a un plato.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        verificar_propiedad_plato(plato, usuario_actual)

        relacion = PlatoRepository.buscar_relacion_ingrediente(db, id_plato, id_ingrediente)
        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El ingrediente ID {id_ingrediente} no está asignado al plato ID {id_plato}."
            )

        relacion.cantidad = datos.cantidad
        relacion.unidad_medida = datos.unidad_medida.strip()
        db.commit()
        db.refresh(relacion)

        return PlatoIngredienteDetalleSchema(
            id_plato_ingrediente=relacion.id_plato_ingrediente,
            id_ingrediente=relacion.id_ingrediente,
            nombre_ingrediente=relacion.ingrediente.nombre if relacion.ingrediente else "",
            cantidad=relacion.cantidad,
            unidad_medida=relacion.unidad_medida,
            precio_estimado=relacion.ingrediente.precio_estimado if relacion.ingrediente else None
        )

    # --- CU09: Quitar Ingrediente de un Plato ---
    @staticmethod
    def eliminar_ingrediente_de_plato(
        db: Session,
        id_plato: int,
        id_ingrediente: int,
        usuario_actual: Usuario
    ) -> dict:
        """
        LÓGICA CU09 - Quitar Ingrediente de Plato:
        Elimina la relación asociativa entre el plato y el ingrediente.
        El ingrediente en el catálogo general permanece intacto.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        verificar_propiedad_plato(plato, usuario_actual)

        relacion = PlatoRepository.buscar_relacion_ingrediente(db, id_plato, id_ingrediente)
        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El ingrediente ID {id_ingrediente} no está asociado a este plato."
            )

        PlatoRepository.eliminar_relacion_ingrediente(db, relacion)
        return {"mensaje": "Ingrediente retirado del plato exitosamente."}

    # =========================================================================
    # CASO DE USO: CU10 - GESTIONAR DISPONIBILIDAD
    # Descripción: Permite activar o desactivar rápidamente la disponibilidad
    #              inmediata de un plato para oferta al consumidor.
    # =========================================================================
    @staticmethod
    def cambiar_disponibilidad(
        db: Session,
        id_plato: int,
        disponible: bool,
        usuario_actual: Usuario
    ) -> Plato:
        """
        LÓGICA CU10 - Cambiar Disponibilidad:
        Modifica el flag 'disponible' (True/False) previa verificación de propiedad.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        verificar_propiedad_plato(plato, usuario_actual)

        plato.disponible = disponible
        return PlatoRepository.actualizar(db, plato)

    # =========================================================================
    # CASO DE USO: CU08 - GESTIONAR PREFERENCIAS EN PLATOS
    # =========================================================================
    @staticmethod
    def listar_preferencias_de_plato(
        db: Session,
        id_plato: int
    ) -> PlatoPreferenciasRespuestaSchema:
        """
        LÓGICA CU08 - Listar Preferencias de Plato:
        Retorna la lista de preferencias asociadas al plato especificado.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        preferencias = PlatoPreferenciaRepository.listar_preferencias_de_plato(db, id_plato)
        return PlatoPreferenciasRespuestaSchema(
            id_plato=plato.id_plato,
            nombre_plato=plato.nombre,
            preferencias=preferencias
        )

    @staticmethod
    def actualizar_preferencias_de_plato(
        db: Session,
        id_plato: int,
        ids_preferencias: List[int],
        usuario_actual: Usuario
    ) -> PlatoPreferenciasRespuestaSchema:
        """
        LÓGICA CU08 - Actualizar Preferencias de Plato:
        Asocia y sincroniza preferencias válidas y activas al plato,
        verificando la titularidad del restaurante.
        """
        plato = PlatoRepository.buscar_por_id(db, id_plato)
        if not plato:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plato con ID {id_plato}."
            )

        verificar_propiedad_plato(plato, usuario_actual)

        # Validar que los IDs de preferencias existan y estén activos
        if ids_preferencias:
            preferencias_activas = PreferenciaRepository.buscar_activas_por_ids(db, ids_preferencias)
            ids_encontrados = {p.id_preferencia for p in preferencias_activas}
            ids_invalidos = set(ids_preferencias) - ids_encontrados
            if ids_invalidos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Las siguientes preferencias no existen o no están activas: {sorted(list(ids_invalidos))}."
                )

        preferencias_actualizadas = PlatoPreferenciaRepository.actualizar_preferencias_de_plato(
            db=db,
            id_plato=id_plato,
            ids_preferencias=ids_preferencias
        )

        return PlatoPreferenciasRespuestaSchema(
            id_plato=plato.id_plato,
            nombre_plato=plato.nombre,
            preferencias=preferencias_actualizadas
        )
