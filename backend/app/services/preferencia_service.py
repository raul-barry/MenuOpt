from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.preferencia import Preferencia
from app.models.usuario import Usuario
from app.repositories.preferencia_repository import PreferenciaRepository
from app.schemas.preferencia import (
    CrearPreferenciaSchema,
    ActualizarPreferenciaSchema,
    ActualizarPreferenciasUsuarioSchema
)


class PreferenciaService:
    """
    Servicio encargado de la lógica de negocio del catálogo de preferencias y
    de las preferencias asociadas al usuario (CU12).
    """

    # =========================================================================
    # CASO DE USO: CU12 - DEFINIR PREFERENCIAS
    # =========================================================================

    @staticmethod
    def listar_catalogo(db: Session, solo_activas: bool = True) -> List[Preferencia]:
        """
        Consulta el catálogo de preferencias. Por defecto devuelve las activas.
        """
        if solo_activas:
            return PreferenciaRepository.listar_activas(db)
        return PreferenciaRepository.listar_todas(db)

    @staticmethod
    def obtener_preferencias_usuario(db: Session, usuario_actual: Usuario) -> List[Preferencia]:
        """
        Devuelve las preferencias gastronómicas habituales del usuario autenticado.
        """
        return PreferenciaRepository.obtener_preferencias_usuario(db, usuario_actual.id_usuario)

    @staticmethod
    def actualizar_preferencias_usuario(
        db: Session,
        usuario_actual: Usuario,
        datos: ActualizarPreferenciasUsuarioSchema
    ) -> List[Preferencia]:
        """
        Actualiza y sincroniza las preferencias habituales del usuario autenticado.
        Valida existencia, estado activo y elimina duplicados de entrada.
        """
        # Eliminar duplicados manteniendo orden
        ids_unicos = list(dict.fromkeys(datos.preferencias))

        if ids_unicos:
            activas = PreferenciaRepository.buscar_activas_por_ids(db, ids_unicos)
            ids_encontrados = {p.id_preferencia for p in activas}
            no_encontrados = [i for i in ids_unicos if i not in ids_encontrados]

            if no_encontrados:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Las siguientes preferencias no existen o no se encuentran activas en el catálogo: {no_encontrados}"
                )

        return PreferenciaRepository.sincronizar_preferencias_usuario(
            db=db,
            id_usuario=usuario_actual.id_usuario,
            ids_preferencias=ids_unicos
        )

    # --- Métodos de Administración del Catálogo (Solo ADMINISTRADOR) ---

    @staticmethod
    def crear_preferencia(db: Session, datos: CrearPreferenciaSchema) -> Preferencia:
        """
        Registra una nueva preferencia en el catálogo global (Solo Administrador).
        """
        existente = PreferenciaRepository.buscar_por_nombre(db, datos.nombre)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una preferencia registrada con el nombre '{datos.nombre.strip()}'."
            )

        nueva = Preferencia(
            nombre=datos.nombre.strip(),
            tipo=datos.tipo.strip().upper() if datos.tipo else None,
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            activo=datos.activo
        )
        return PreferenciaRepository.crear(db, nueva)

    @staticmethod
    def actualizar_preferencia(
        db: Session,
        id_preferencia: int,
        datos: ActualizarPreferenciaSchema
    ) -> Preferencia:
        """
        Modifica una preferencia existente del catálogo global (Solo Administrador).
        """
        preferencia = PreferenciaRepository.buscar_por_id(db, id_preferencia)
        if not preferencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preferencia con ID {id_preferencia} no encontrada."
            )

        if datos.nombre is not None:
            nombre_limpio = datos.nombre.strip()
            otro = PreferenciaRepository.buscar_por_nombre(db, nombre_limpio)
            if otro and otro.id_preferencia != id_preferencia:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe otra preferencia registrada con el nombre '{nombre_limpio}'."
                )
            preferencia.nombre = nombre_limpio

        if datos.tipo is not None:
            preferencia.tipo = datos.tipo.strip().upper() if datos.tipo else None

        if datos.descripcion is not None:
            preferencia.descripcion = datos.descripcion.strip() if datos.descripcion else None

        if datos.activo is not None:
            preferencia.activo = datos.activo

        return PreferenciaRepository.actualizar(db, preferencia)

    @staticmethod
    def cambiar_estado(db: Session, id_preferencia: int, activo: bool) -> Preferencia:
        """
        Activa o desactiva una preferencia del catálogo (Solo Administrador).
        """
        preferencia = PreferenciaRepository.buscar_por_id(db, id_preferencia)
        if not preferencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Preferencia con ID {id_preferencia} no encontrada."
            )

        preferencia.activo = activo
        return PreferenciaRepository.actualizar(db, preferencia)
