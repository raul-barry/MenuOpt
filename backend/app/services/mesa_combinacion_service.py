# CASO DE USO: CU19 - Definir combinación de mesas
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.mesa_combinacion import MesaCombinacion
from app.repositories.mesa_combinacion_repository import MesaCombinacionRepository
from app.repositories.mesa_repository import MesaRepository
from app.repositories.area_restaurante_repository import AreaRestauranteRepository
from app.schemas.mesa_combinacion import (
    CrearMesaCombinacionSchema,
    ActualizarMesaCombinacionSchema,
    MesaCombinacionRespuestaSchema
)
from app.security.propiedad import verificar_propiedad_area


class MesaCombinacionService:

    @staticmethod
    def _mapear_respuesta(combinacion: MesaCombinacion) -> MesaCombinacionRespuestaSchema:
        cap_orig = combinacion.mesa_origen.capacidad if combinacion.mesa_origen else 0
        cap_dest = combinacion.mesa_destino.capacidad if combinacion.mesa_destino else 0
        return MesaCombinacionRespuestaSchema(
            id_mesa_combinacion=combinacion.id_mesa_combinacion,
            id_mesa_origen=combinacion.id_mesa_origen,
            numero_mesa_origen=combinacion.mesa_origen.numero if combinacion.mesa_origen else None,
            capacidad_mesa_origen=cap_orig,
            id_mesa_destino=combinacion.id_mesa_destino,
            numero_mesa_destino=combinacion.mesa_destino.numero if combinacion.mesa_destino else None,
            capacidad_mesa_destino=cap_dest,
            capacidad_combinada=cap_orig + cap_dest,
            permitida=combinacion.permitida,
            descripcion=combinacion.descripcion,
            activo=combinacion.activo,
            fecha_creacion=combinacion.fecha_creacion
        )

    @staticmethod
    def crear_combinacion(
        db: Session,
        id_area: int,
        datos: CrearMesaCombinacionSchema,
        usuario_actual: Usuario
    ) -> MesaCombinacionRespuestaSchema:
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        # 1. Regla: no se puede combinar una mesa consigo misma
        if datos.id_mesa_origen == datos.id_mesa_destino:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No es posible combinar una mesa consigo misma."
            )

        # 2. Obtener ambas mesas
        m1 = MesaRepository.obtener_por_id(db, datos.id_mesa_origen)
        m2 = MesaRepository.obtener_por_id(db, datos.id_mesa_destino)
        if not m1 or not m2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Una o ambas mesas a combinar no existen en el sistema."
            )

        # 3. Regla: ambas mesas deben pertenecer a la misma área
        if m1.id_area != id_area or m2.id_area != id_area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ambas mesas deben pertenecer a la misma área para poder combinarse."
            )

        # 4. Regla: ambas deben estar activas
        if not m1.activo or not m2.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden combinar mesas inactivas."
            )

        # 5. Regla: ninguna mesa fija puede combinarse
        if m1.es_fija or m2.es_fija:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las mesas fijas no admiten combinación con otras mesas."
            )

        # 6. Regla: ambas mesas deben tener combinable = True
        if not m1.combinable or not m2.combinable:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ambas mesas deben tener la propiedad 'combinable' activada."
            )

        # 7. Regla de simetría: guardar siempre ordenado (min, max) para que M1+M2 == M2+M1
        id_menor = min(datos.id_mesa_origen, datos.id_mesa_destino)
        id_mayor = max(datos.id_mesa_origen, datos.id_mesa_destino)

        existente = MesaCombinacionRepository.obtener_por_par_ordenado(db, id_menor, id_mayor)
        if existente:
            if existente.activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La combinación entre la mesa {m1.numero} y {m2.numero} ya está registrada."
                )
            # Reactivar si estaba inactiva
            existente.activo = True
            existente.permitida = True
            if datos.descripcion is not None:
                existente.descripcion = datos.descripcion.strip() if datos.descripcion else None
            actualizada = MesaCombinacionRepository.actualizar(db, existente)
            # Recargar con relaciones
            return MesaCombinacionService._mapear_respuesta(
                MesaCombinacionRepository.obtener_por_id(db, actualizada.id_mesa_combinacion)
            )

        # Crear nueva combinación
        nueva_comb = MesaCombinacion(
            id_mesa_origen=id_menor,
            id_mesa_destino=id_mayor,
            permitida=True,
            descripcion=datos.descripcion.strip() if datos.descripcion else None,
            activo=True
        )
        guardada = MesaCombinacionRepository.crear(db, nueva_comb)
        return MesaCombinacionService._mapear_respuesta(
            MesaCombinacionRepository.obtener_por_id(db, guardada.id_mesa_combinacion)
        )

    @staticmethod
    def listar_combinaciones_area(
        db: Session,
        id_area: int,
        usuario_actual: Usuario,
        solo_activas: bool = False
    ) -> List[MesaCombinacionRespuestaSchema]:
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        combinaciones = MesaCombinacionRepository.listar_por_area(db, id_area, solo_activas=solo_activas)
        return [MesaCombinacionService._mapear_respuesta(c) for c in combinaciones]

    @staticmethod
    def actualizar_combinacion(
        db: Session,
        id_combinacion: int,
        datos: ActualizarMesaCombinacionSchema,
        usuario_actual: Usuario
    ) -> MesaCombinacionRespuestaSchema:
        combinacion = MesaCombinacionRepository.obtener_por_id(db, id_combinacion)
        if not combinacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Combinación con ID {id_combinacion} no encontrada."
            )
        verificar_propiedad_area(combinacion.mesa_origen.area, usuario_actual)

        if datos.permitida is not None:
            combinacion.permitida = datos.permitida
        if datos.descripcion is not None:
            combinacion.descripcion = datos.descripcion.strip() if datos.descripcion else None
        if datos.activo is not None:
            combinacion.activo = datos.activo

        actualizada = MesaCombinacionRepository.actualizar(db, combinacion)
        return MesaCombinacionService._mapear_respuesta(actualizada)

    @staticmethod
    def desactivar_combinacion(
        db: Session,
        id_combinacion: int,
        usuario_actual: Usuario
    ) -> MesaCombinacionRespuestaSchema:
        combinacion = MesaCombinacionRepository.obtener_por_id(db, id_combinacion)
        if not combinacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Combinación con ID {id_combinacion} no encontrada."
            )
        verificar_propiedad_area(combinacion.mesa_origen.area, usuario_actual)

        combinacion.activo = False
        actualizada = MesaCombinacionRepository.actualizar(db, combinacion)
        return MesaCombinacionService._mapear_respuesta(actualizada)
