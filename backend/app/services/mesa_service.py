# CASO DE USO: CU18 - Gestionar mesas
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.mesa import Mesa
from app.repositories.mesa_repository import MesaRepository
from app.repositories.area_restaurante_repository import AreaRestauranteRepository
from app.schemas.mesa import CrearMesaSchema, ActualizarMesaSchema
from app.security.propiedad import verificar_propiedad_area


class MesaService:

    @staticmethod
    def crear_mesa(
        db: Session,
        id_area: int,
        datos: CrearMesaSchema,
        usuario_actual: Usuario
    ) -> Mesa:
        # 1. Validar existencia de área y permisos
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        # 2. Validar que no exista otra mesa activa con el mismo número en el área
        numero_limpio = datos.numero.strip()
        mesa_existente = MesaRepository.obtener_por_area_y_numero(db, id_area, numero_limpio)
        if mesa_existente and mesa_existente.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una mesa activa con el número '{numero_limpio}' en esta área."
            )

        # 3. Crear mesa
        nueva_mesa = Mesa(
            id_area=id_area,
            numero=numero_limpio,
            nombre=datos.nombre.strip() if datos.nombre else None,
            capacidad=datos.capacidad,
            forma=datos.forma,
            posicion_x=datos.posicion_x,
            posicion_y=datos.posicion_y,
            rotacion=datos.rotacion,
            ancho=datos.ancho,
            alto=datos.alto,
            es_fija=datos.es_fija,
            combinable=datos.combinable,
            activo=True
        )
        return MesaRepository.crear(db, nueva_mesa)

    @staticmethod
    def obtener_mesa(db: Session, id_mesa: int, usuario_actual: Usuario) -> Mesa:
        mesa = MesaRepository.obtener_por_id(db, id_mesa)
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesa con ID {id_mesa} no encontrada."
            )
        verificar_propiedad_area(mesa.area, usuario_actual)
        return mesa

    @staticmethod
    def listar_mesas_area(
        db: Session,
        id_area: int,
        usuario_actual: Usuario,
        solo_activas: bool = False
    ) -> List[Mesa]:
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)
        return MesaRepository.listar_por_area(db, id_area, solo_activas=solo_activas)

    @staticmethod
    def actualizar_mesa(
        db: Session,
        id_mesa: int,
        datos: ActualizarMesaSchema,
        usuario_actual: Usuario
    ) -> Mesa:
        mesa = MesaRepository.obtener_por_id(db, id_mesa)
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesa con ID {id_mesa} no encontrada."
            )
        verificar_propiedad_area(mesa.area, usuario_actual)

        if datos.numero is not None:
            numero_limpio = datos.numero.strip()
            if numero_limpio.lower() != mesa.numero.lower():
                existente = MesaRepository.obtener_por_area_y_numero(db, mesa.id_area, numero_limpio)
                if existente and existente.id_mesa != mesa.id_mesa and existente.activo:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ya existe otra mesa activa con el número '{numero_limpio}' en esta área."
                    )
            mesa.numero = numero_limpio

        if datos.nombre is not None:
            mesa.nombre = datos.nombre.strip() if datos.nombre else None
        if datos.capacidad is not None:
            mesa.capacidad = datos.capacidad
        if datos.forma is not None:
            mesa.forma = datos.forma
        if datos.posicion_x is not None:
            mesa.posicion_x = datos.posicion_x
        if datos.posicion_y is not None:
            mesa.posicion_y = datos.posicion_y
        if datos.rotacion is not None:
            mesa.rotacion = datos.rotacion
        if datos.ancho is not None:
            mesa.ancho = datos.ancho
        if datos.alto is not None:
            mesa.alto = datos.alto
        if datos.es_fija is not None:
            mesa.es_fija = datos.es_fija
        if datos.combinable is not None:
            mesa.combinable = datos.combinable
        if datos.activo is not None:
            mesa.activo = datos.activo

        return MesaRepository.actualizar(db, mesa)

    @staticmethod
    def cambiar_estado(db: Session, id_mesa: int, activo: bool, usuario_actual: Usuario) -> Mesa:
        mesa = MesaRepository.obtener_por_id(db, id_mesa)
        if not mesa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mesa con ID {id_mesa} no encontrada."
            )
        verificar_propiedad_area(mesa.area, usuario_actual)

        mesa.activo = activo
        return MesaRepository.actualizar(db, mesa)
