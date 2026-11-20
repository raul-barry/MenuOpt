from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.restaurante import Restaurante
from app.models.ubicacion import Ubicacion
from app.repositories.restaurante_repository import RestauranteRepository
from app.schemas.restaurante import (
    RegistrarRestauranteSchema,
    ActualizarRestauranteSchema
)
from app.security.propiedad import verificar_propiedad_restaurante


class RestauranteService:
    """
    Servicio encargado de la lógica de negocio de Restaurantes (CU05 y CU06).
    """

    # =========================================================================
    # CASO DE USO: CU05 - REGISTRAR RESTAURANTE
    # Descripción: Registra un nuevo restaurante junto a su ubicación de forma
    #              atómica. Asigna automáticamente al usuario autenticado como responsable.
    # =========================================================================
    @staticmethod
    def registrar_restaurante(
        db: Session,
        datos: RegistrarRestauranteSchema,
        usuario_actual: Usuario
    ) -> Restaurante:
        """
        LÓGICA CU05 - REGISTRAR RESTAURANTE:
        Valida que el NIT no esté duplicado, crea la entidad Ubicacion y el Restaurante,
        vincula al responsable autenticado y guarda ambos en una sola transacción.
        """
        # Validar NIT único si se provee
        if datos.nit and datos.nit.strip():
            nit_limpio = datos.nit.strip()
            restaurante_existente = RestauranteRepository.buscar_por_nit(db, nit_limpio)
            if restaurante_existente:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un restaurante registrado con el NIT '{nit_limpio}'."
                )

        # Crear entidad Ubicación
        nueva_ubicacion = Ubicacion(
            direccion=datos.ubicacion.direccion.strip(),
            zona=datos.ubicacion.zona.strip() if datos.ubicacion.zona else None,
            ciudad=datos.ubicacion.ciudad.strip(),
            latitud=datos.ubicacion.latitud,
            longitud=datos.ubicacion.longitud,
            referencia=datos.ubicacion.referencia.strip() if datos.ubicacion.referencia else None
        )

        # Crear entidad Restaurante asignando responsable autenticado
        nuevo_restaurante = Restaurante(
            nombre=datos.nombre.strip(),
            imagen_url=datos.imagen_url.strip() if datos.imagen_url else None,
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            nit=datos.nit.strip() if datos.nit else None,
            telefono=datos.telefono.strip() if datos.telefono else None,
            correo=datos.correo.strip().lower() if datos.correo else None,
            horario_apertura=datos.horario_apertura,
            horario_cierre=datos.horario_cierre,
            estado="ACTIVO",
            id_usuario_responsable=usuario_actual.id_usuario,
            id_ubicacion=0  # Se asigna dinámicamente en el repositorio tras flush
        )

        return RestauranteRepository.crear_con_ubicacion(db, nuevo_restaurante, nueva_ubicacion)

    # =========================================================================
    # CASO DE USO: CU06 - GESTIONAR RESTAURANTE
    # Descripción: Permite listar restaurantes propios, consultar detalle,
    #              modificar datos/ubicación y cambiar estado lógico protegiendo la propiedad.
    # =========================================================================

    # --- CU06: Consultar Mis Restaurantes ---
    @staticmethod
    def listar_mis_restaurantes(db: Session, usuario_actual: Usuario) -> List[Restaurante]:
        """
        LÓGICA CU06 - Listar Mis Restaurantes:
        Devuelve los restaurantes registrados a cargo del usuario autenticado.
        Si es ADMINISTRADOR, puede listar todos los restaurantes del sistema.
        """
        if usuario_actual.rol and usuario_actual.rol.nombre == "ADMINISTRADOR":
            return RestauranteRepository.listar_todos(db)
        return RestauranteRepository.listar_por_usuario(db, usuario_actual.id_usuario)

    # --- CU06: Consultar Detalle de un Restaurante ---
    @staticmethod
    def obtener_restaurante_por_id(
        db: Session,
        id_restaurante: int,
        usuario_actual: Usuario
    ) -> Restaurante:
        """
        LÓGICA CU06 - Obtener Detalle de Restaurante:
        Recupera los datos del restaurante validando existencia.
        """
        restaurante = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not restaurante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el restaurante con ID {id_restaurante}."
            )
        return restaurante

    # --- CU06: Modificar Información del Restaurante ---
    @staticmethod
    def actualizar_restaurante(
        db: Session,
        id_restaurante: int,
        datos: ActualizarRestauranteSchema,
        usuario_actual: Usuario
    ) -> Restaurante:
        """
        LÓGICA CU06 - Modificar Restaurante:
        Verifica la propiedad del restaurante. Modifica datos comerciales y ubicación.
        No permite alterar id_restaurante, id_usuario_responsable ni fecha_registro.
        """
        restaurante = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not restaurante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el restaurante con ID {id_restaurante}."
            )

        # Regla de propiedad obligatoria: solo el dueño o ADMINISTRADOR pueden modificar
        verificar_propiedad_restaurante(restaurante, usuario_actual)

        # Validar NIT único si se actualiza
        if datos.nit is not None:
            nit_limpio = datos.nit.strip() if datos.nit else None
            if nit_limpio and nit_limpio != restaurante.nit:
                existente = RestauranteRepository.buscar_por_nit(db, nit_limpio)
                if existente and existente.id_restaurante != id_restaurante:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El NIT '{nit_limpio}' ya pertenece a otro restaurante."
                    )
            restaurante.nit = nit_limpio

        if datos.nombre is not None:
            restaurante.nombre = datos.nombre.strip()
        if "imagen_url" in datos.model_fields_set:
            restaurante.imagen_url = datos.imagen_url.strip() if datos.imagen_url else None
        if datos.descripcion is not None:
            restaurante.descripcion = datos.descripcion.strip() if datos.descripcion else None
        if datos.telefono is not None:
            restaurante.telefono = datos.telefono.strip() if datos.telefono else None
        if datos.correo is not None:
            restaurante.correo = datos.correo.strip().lower() if datos.correo else None
        if datos.horario_apertura is not None:
            restaurante.horario_apertura = datos.horario_apertura
        if datos.horario_cierre is not None:
            restaurante.horario_cierre = datos.horario_cierre

        # Actualizar datos de ubicación si se proporcionan
        if datos.ubicacion is not None and restaurante.ubicacion:
            u_datos = datos.ubicacion
            if u_datos.direccion is not None:
                restaurante.ubicacion.direccion = u_datos.direccion.strip()
            if u_datos.zona is not None:
                restaurante.ubicacion.zona = u_datos.zona.strip() if u_datos.zona else None
            if u_datos.ciudad is not None:
                restaurante.ubicacion.ciudad = u_datos.ciudad.strip()
            if u_datos.latitud is not None:
                restaurante.ubicacion.latitud = u_datos.latitud
            if u_datos.longitud is not None:
                restaurante.ubicacion.longitud = u_datos.longitud
            if u_datos.referencia is not None:
                restaurante.ubicacion.referencia = u_datos.referencia.strip() if u_datos.referencia else None

        return RestauranteRepository.actualizar(db, restaurante)

    # --- CU06: Cambiar Estado del Restaurante (Activación / Desactivación Lógica) ---
    @staticmethod
    def cambiar_estado(
        db: Session,
        id_restaurante: int,
        nuevo_estado: str,
        usuario_actual: Usuario
    ) -> Restaurante:
        """
        LÓGICA CU06 - Cambiar Estado:
        Aplica desactivación o activación lógica al restaurante previa verificación de propiedad.
        """
        restaurante = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not restaurante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el restaurante con ID {id_restaurante}."
            )

        verificar_propiedad_restaurante(restaurante, usuario_actual)

        restaurante.estado = nuevo_estado.upper()
        return RestauranteRepository.actualizar(db, restaurante)
