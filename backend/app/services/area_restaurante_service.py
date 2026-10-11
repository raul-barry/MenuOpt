# CASO DE USO: CU17 - Crear plano 2D del restaurante
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.area_restaurante import AreaRestaurante
from app.repositories.area_restaurante_repository import AreaRestauranteRepository
from app.repositories.restaurante_repository import RestauranteRepository
from app.schemas.area_restaurante import (
    CrearAreaRestauranteSchema,
    ActualizarAreaRestauranteSchema,
    AreaRestauranteRespuestaSchema
)
from app.security.propiedad import verificar_propiedad_restaurante, verificar_propiedad_area


class AreaRestauranteService:

    @staticmethod
    def crear_area(
        db: Session,
        id_restaurante: int,
        datos: CrearAreaRestauranteSchema,
        usuario_actual: Usuario
    ) -> AreaRestaurante:
        # 1. Obtener restaurante y validar propiedad
        restaurante = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not restaurante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurante con ID {id_restaurante} no encontrado."
            )
        verificar_propiedad_restaurante(restaurante, usuario_actual)

        # 2. Validar que no exista un área activa con el mismo nombre en este restaurante
        nombre_limpio = datos.nombre.strip()
        area_existente = AreaRestauranteRepository.obtener_por_restaurante_y_nombre(db, id_restaurante, nombre_limpio)
        if area_existente and area_existente.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un área activa con el nombre '{nombre_limpio}' en este restaurante."
            )

        # 3. Crear área
        nueva_area = AreaRestaurante(
            id_restaurante=id_restaurante,
            nombre=nombre_limpio,
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            ancho_mapa=datos.ancho_mapa,
            alto_mapa=datos.alto_mapa,
            orden=datos.orden,
            activo=True
        )
        return AreaRestauranteRepository.crear(db, nueva_area)

    @staticmethod
    def obtener_area(db: Session, id_area: int, usuario_actual: Usuario) -> AreaRestauranteRespuestaSchema:
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        rol_nombre = usuario_actual.rol.nombre if usuario_actual.rol else None
        if rol_nombre != "CLIENTE":
            verificar_propiedad_area(area, usuario_actual)

        total_mesas = AreaRestauranteRepository.contar_mesas_por_area(db, id_area)
        respuesta = AreaRestauranteRespuestaSchema.model_validate(area)
        respuesta.total_mesas = total_mesas
        return respuesta

    @staticmethod
    def listar_areas(
        db: Session,
        id_restaurante: int,
        usuario_actual: Usuario,
        solo_activas: bool = False
    ) -> List[AreaRestauranteRespuestaSchema]:
        restaurante = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not restaurante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurante con ID {id_restaurante} no encontrado."
            )
        rol_nombre = usuario_actual.rol.nombre if usuario_actual.rol else None
        if rol_nombre != "CLIENTE":
            verificar_propiedad_restaurante(restaurante, usuario_actual)

        areas = AreaRestauranteRepository.listar_por_restaurante(db, id_restaurante, solo_activas=solo_activas)

        # Automatización CU17: Si el restaurante no cuenta con áreas registradas, autogenerar "Salón Principal"
        if not areas:
            area_default = AreaRestaurante(
                id_restaurante=id_restaurante,
                nombre="Salón Principal",
                descripcion="Área física principal del establecimiento",
                ancho_mapa=1200,
                alto_mapa=700,
                orden=1,
                activo=True
            )
            db.add(area_default)
            db.commit()
            db.refresh(area_default)
            areas = [area_default]

        respuestas: List[AreaRestauranteRespuestaSchema] = []
        for a in areas:
            resp = AreaRestauranteRespuestaSchema.model_validate(a)
            resp.total_mesas = AreaRestauranteRepository.contar_mesas_por_area(db, a.id_area)
            respuestas.append(resp)
        return respuestas

    @staticmethod
    def actualizar_area(
        db: Session,
        id_area: int,
        datos: ActualizarAreaRestauranteSchema,
        usuario_actual: Usuario
    ) -> AreaRestaurante:
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        if datos.nombre is not None:
            nombre_limpio = datos.nombre.strip()
            if nombre_limpio.lower() != area.nombre.lower():
                existente = AreaRestauranteRepository.obtener_por_restaurante_y_nombre(db, area.id_restaurante, nombre_limpio)
                if existente and existente.id_area != area.id_area and existente.activo:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe otra área activa con el nombre '{nombre_limpio}' en este restaurante."
                    )
            area.nombre = nombre_limpio

        if datos.descripcion is not None:
            area.descripcion = datos.descripcion.strip() if datos.descripcion else None
        if datos.ancho_mapa is not None:
            area.ancho_mapa = datos.ancho_mapa
        if datos.alto_mapa is not None:
            area.alto_mapa = datos.alto_mapa
        if datos.orden is not None:
            area.orden = datos.orden
        if datos.activo is not None:
            area.activo = datos.activo

        return AreaRestauranteRepository.actualizar(db, area)

    @staticmethod
    def cambiar_estado(db: Session, id_area: int, activo: bool, usuario_actual: Usuario) -> AreaRestaurante:
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        area.activo = activo
        return AreaRestauranteRepository.actualizar(db, area)
