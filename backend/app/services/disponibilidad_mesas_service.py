# CASO DE USO: CU20 - Consultar disponibilidad de mesas
from datetime import datetime, date, time
from typing import List, Dict, Any, Set
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.restaurante import Restaurante
from app.models.area_restaurante import AreaRestaurante
from app.models.mesa import Mesa
from app.repositories.restaurante_repository import RestauranteRepository
from app.repositories.area_restaurante_repository import AreaRestauranteRepository
from app.repositories.mesa_repository import MesaRepository
from app.repositories.mesa_combinacion_repository import MesaCombinacionRepository
from app.repositories.reserva_repository import ReservaRepository
from app.schemas.mesa_disponibilidad import (
    MesaDisponibilidadRespuesta,
    CombinacionDisponibleRespuesta,
    DisponibilidadRespuesta
)


class DisponibilidadMesasService:
    @staticmethod
    def existe_conflicto_reserva(
        db: Session,
        id_mesa: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time
    ) -> bool:
        """
        Función centralizada para determinar si una mesa específica tiene conflicto horario.
        Fórmula: reserva.hora_inicio < hora_fin AND reserva.hora_fin > hora_inicio
        """
        conflictos = ReservaRepository.buscar_conflictos_mesas(
            db=db,
            mesas_ids=[id_mesa],
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
        return len(conflictos) > 0

    @staticmethod
    def validar_parametros_consulta(
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        cantidad_personas: int
    ) -> None:
        """
        Valida que el intervalo y la fecha sean válidos y no pertenezcan al pasado.
        """
        if cantidad_personas <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad de personas debe ser mayor a 0."
            )

        if hora_fin <= hora_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La hora de finalización debe ser estrictamente posterior a la hora de inicio."
            )

        # Validación estricta en servidor contra fechas y horas pasadas
        ahora = datetime.now()
        dt_inicio = datetime.combine(fecha, hora_inicio)
        if dt_inicio < ahora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No es posible consultar disponibilidad ni realizar reservas en fechas u horarios pasados."
            )

    @classmethod
    def consultar_disponibilidad(
        cls,
        db: Session,
        id_restaurante: int,
        id_area: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        cantidad_personas: int
    ) -> DisponibilidadRespuesta:
        """
        Algoritmo central de cálculo de disponibilidad horaria y compatibilidad de mesas.
        """
        # 1. Validar parámetros temporales
        cls.validar_parametros_consulta(fecha, hora_inicio, hora_fin, cantidad_personas)

        # 2. Validar existencia y vigencia de restaurante y área
        resto = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not resto or resto.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurante #{id_restaurante} no encontrado o inactivo."
            )

        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area or area.id_restaurante != id_restaurante or not area.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área #{id_area} no encontrada o inactiva en este restaurante."
            )

        # 3. Obtener mesas activas del área (1 consulta)
        mesas_area: List[Mesa] = MesaRepository.listar_por_area(db, id_area, solo_activas=True)
        mesas_dict = {m.id_mesa: m for m in mesas_area}

        # 4. Obtener mesas ocupadas por reservas vigentes en el intervalo solicitado (1 consulta masiva O(1))
        mesas_ocupadas: Set[int] = ReservaRepository.obtener_mesas_ocupadas_en_intervalo(
            db=db,
            id_restaurante=id_restaurante,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )

        max_exceso = settings.MAX_EXCESO_CAPACIDAD_MESA

        # 5. Evaluar cada mesa individual
        mesas_resultado: List[MesaDisponibilidadRespuesta] = []
        for m in mesas_area:
            esta_ocupada = m.id_mesa in mesas_ocupadas

            # Regla de capacidad:
            # Cubre al grupo si su capacidad es >= cantidad_personas
            cubre_capacidad = m.capacidad >= cantidad_personas
            es_optima = cubre_capacidad and m.capacidad <= (cantidad_personas + max_exceso)

            if esta_ocupada:
                estado_disp = "NO_DISPONIBLE"
                seleccionable = False
                compatible_capacidad = False
            elif cubre_capacidad:
                # La mesa cubre holgadamente o de forma exacta al grupo y está libre
                estado_disp = "DISPONIBLE"
                seleccionable = True
                compatible_capacidad = True
            else:
                # Capacidad insuficiente para albergar al grupo individualmente
                estado_disp = "NO_COMPATIBLE"
                seleccionable = False
                compatible_capacidad = False

            mesas_resultado.append(MesaDisponibilidadRespuesta(
                id_mesa=m.id_mesa,
                numero=m.numero,
                nombre=m.nombre,
                capacidad=m.capacidad,
                forma=m.forma,
                posicion_x=float(m.posicion_x),
                posicion_y=float(m.posicion_y),
                rotacion=m.rotacion,
                ancho=float(m.ancho),
                alto=float(m.alto),
                es_fija=m.es_fija,
                combinable=m.combinable,
                estado_disponibilidad=estado_disp,
                compatible_capacidad=compatible_capacidad,
                seleccionable=seleccionable
            ))

        # 6. Evaluar combinaciones permitidas del área
        combinaciones_db = MesaCombinacionRepository.listar_por_area(db, id_area, solo_activas=True)
        combinaciones_resultado: List[CombinacionDisponibleRespuesta] = []

        for comb in combinaciones_db:
            m_origen = mesas_dict.get(comb.id_mesa_origen)
            m_destino = mesas_dict.get(comb.id_mesa_destino)

            # Validar que ambas mesas existan en el área, activas, combinables y no fijas
            if not m_origen or not m_destino:
                continue
            if m_origen.es_fija or m_destino.es_fija or not m_origen.combinable or not m_destino.combinable:
                continue

            cap_total = m_origen.capacidad + m_destino.capacidad
            comb_compatible = cap_total >= cantidad_personas

            # Una combinación está DISPONIBLE únicamente si TODAS sus mesas están libres
            comb_disponible = (
                comb.id_mesa_origen not in mesas_ocupadas and
                comb.id_mesa_destino not in mesas_ocupadas
            )
            comb_seleccionable = comb_disponible and comb_compatible

            combinaciones_resultado.append(CombinacionDisponibleRespuesta(
                id_combinacion=comb.id_mesa_combinacion,
                mesas=[comb.id_mesa_origen, comb.id_mesa_destino],
                numeros_mesas=[m_origen.numero, m_destino.numero],
                capacidad_total=cap_total,
                disponible=comb_disponible,
                seleccionable=comb_seleccionable,
                descripcion=comb.descripcion
            ))

        # 7. Ordenar priorizando opciones más adecuadas (menor exceso de capacidad)
        def criterio_orden_mesa(m: MesaDisponibilidadRespuesta):
            # Prioridad 0: Disponible y seleccionable
            # Prioridad 1: No disponible (ocupada)
            # Prioridad 2: Incompatible
            prio_estado = 0 if m.seleccionable else (1 if m.estado_disponibilidad == "NO_DISPONIBLE" else 2)
            exceso = abs(m.capacidad - cantidad_personas)
            return (prio_estado, exceso, m.numero)

        mesas_resultado.sort(key=criterio_orden_mesa)

        # Ordenar combinaciones por adecuación
        combinaciones_resultado.sort(
            key=lambda c: (0 if c.seleccionable else 1, abs(c.capacidad_total - cantidad_personas))
        )

        return DisponibilidadRespuesta(
            id_area=area.id_area,
            nombre_area=area.nombre,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            cantidad_personas=cantidad_personas,
            mesas=mesas_resultado,
            combinaciones=combinaciones_resultado
        )
