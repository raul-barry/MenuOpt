import math
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import (
    ActualizarPerfilSchema,
    CambiarContrasenaSchema,
    UsuariosPaginadosSchema
)
from app.security.contrasenas import generar_hash_contrasena, verificar_contrasena


class UsuarioService:
    """
    Servicio encargado de la lógica de perfil (CU03) y administración de usuarios (CU04).
    """

    # =========================================================================
    # CASO DE USO: CU03 - GESTIONAR PERFIL
    # =========================================================================

    # --- CU03: Consultar Perfil del Usuario Autenticado ---
    @staticmethod
    def consultar_perfil(usuario_actual: Usuario) -> Usuario:
        """
        LÓGICA CU03 - Consultar Perfil:
        Retorna la información del perfil del usuario autenticado en sesión.
        """
        return usuario_actual

    # --- CU03: Modificar Perfil del Usuario Autenticado ---
    @staticmethod
    def actualizar_perfil(
        db: Session,
        usuario_actual: Usuario,
        datos: ActualizarPerfilSchema
    ) -> Usuario:
        """
        LÓGICA CU03 - Modificar Perfil:
        Modifica los datos permitidos del perfil del usuario actual (nombres, apellidos, teléfono, correo).
        Valida que el nuevo correo no esté en uso por otra cuenta.
        Protege campos inmutables: no permite cambiar id_usuario, rol, estado ni fecha_registro.
        """
        # Si se solicita cambio de correo, validar unicidad
        if datos.correo is not None:
            correo_normalizado = datos.correo.strip().lower()
            if correo_normalizado != usuario_actual.correo.lower():
                existente = UsuarioRepository.buscar_por_correo(db, correo_normalizado)
                if existente and existente.id_usuario != usuario_actual.id_usuario:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="El nuevo correo electrónico ya está en uso por otra cuenta."
                    )
                usuario_actual.correo = correo_normalizado

        if datos.nombres is not None:
            usuario_actual.nombres = datos.nombres.strip()

        if datos.apellidos is not None:
            usuario_actual.apellidos = datos.apellidos.strip()

        if datos.telefono is not None:
            usuario_actual.telefono = datos.telefono.strip() if datos.telefono.strip() else None

        return UsuarioRepository.actualizar_usuario(db, usuario_actual)

    # --- CU03: Cambiar Contraseña de Forma Segura ---
    @staticmethod
    def cambiar_contrasena(
        db: Session,
        usuario_actual: Usuario,
        datos: CambiarContrasenaSchema
    ) -> dict:
        """
        LÓGICA CU03 - Cambiar Contraseña:
        Comprueba la contraseña actual contra el hash almacenado, verifica que la nueva
        contraseña no sea idéntica a la anterior y guarda el nuevo hash con bcrypt.
        """
        if not verificar_contrasena(datos.contrasena_actual, usuario_actual.contrasena_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual ingresada es incorrecta."
            )

        if datos.contrasena_actual == datos.contrasena_nueva:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña no puede ser idéntica a la contraseña actual."
            )

        usuario_actual.contrasena_hash = generar_hash_contrasena(datos.contrasena_nueva)
        UsuarioRepository.actualizar_usuario(db, usuario_actual)

        return {"mensaje": "Contraseña actualizada exitosamente."}

    # =========================================================================
    # CASO DE USO: CU04 - GESTIONAR USUARIOS (Solo ADMINISTRADOR)
    # =========================================================================

    # --- CU04: Listar Usuarios con Paginación y Filtros ---
    @staticmethod
    def listar_usuarios_paginado(
        db: Session,
        pagina: int = 1,
        limite: int = 10,
        estado: Optional[str] = None,
        rol: Optional[str] = None,
        busqueda: Optional[str] = None
    ) -> UsuariosPaginadosSchema:
        """
        LÓGICA CU04 - Listar Usuarios:
        Consulta usuarios de forma paginada aplicando filtros opcionales de estado,
        nombre de rol o término de búsqueda.
        """
        skip = (pagina - 1) * limite
        total, usuarios = UsuarioRepository.listar_usuarios(
            db=db,
            skip=skip,
            limit=limite,
            estado=estado,
            rol=rol,
            busqueda=busqueda
        )

        total_paginas = math.ceil(total / limite) if total > 0 else 1

        return UsuariosPaginadosSchema(
            total=total,
            pagina=pagina,
            limite=limite,
            total_paginas=total_paginas,
            usuarios=usuarios
        )

    # --- CU04: Obtener Detalle de un Usuario por ID ---
    @staticmethod
    def obtener_usuario_por_id(db: Session, id_usuario: int) -> Usuario:
        """
        LÓGICA CU04 - Obtener Detalle de Usuario:
        Obtiene los detalles del usuario solicitado verificando su existencia.
        """
        usuario = UsuarioRepository.buscar_por_id(db, id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró ningún usuario con el ID {id_usuario}."
            )
        return usuario

    # --- CU04: Cambiar Estado Lógico del Usuario (Desactivación / Activación) ---
    @staticmethod
    def cambiar_estado(
        db: Session,
        id_usuario: int,
        nuevo_estado: str,
        admin_actual: Usuario
    ) -> Usuario:
        """
        LÓGICA CU04 - Cambiar Estado:
        Aplica activación o desactivación lógica (ACTIVO / INACTIVO).
        Protege al administrador impidiendo que desactive su propia cuenta.
        """
        usuario = UsuarioRepository.buscar_por_id(db, id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró ningún usuario con el ID {id_usuario}."
            )

        estado_upper = nuevo_estado.upper()
        if id_usuario == admin_actual.id_usuario and estado_upper == "INACTIVO":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puede desactivar su propia cuenta de administrador."
            )

        usuario.estado = estado_upper
        return UsuarioRepository.actualizar_usuario(db, usuario)
