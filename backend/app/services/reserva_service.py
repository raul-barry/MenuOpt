# CASO DE USO: CU21 - Realizar reserva & CU22 - Gestionar reservas
from datetime import datetime, date, time
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.usuario import Usuario
from app.models.restaurante import Restaurante
from app.models.area_restaurante import AreaRestaurante
from app.models.mesa import Mesa
from app.models.reserva import Reserva
from app.models.planificacion import Planificacion
from app.repositories.restaurante_repository import RestauranteRepository
from app.repositories.area_restaurante_repository import AreaRestauranteRepository
from app.repositories.mesa_repository import MesaRepository
from app.repositories.mesa_combinacion_repository import MesaCombinacionRepository
from app.repositories.reserva_repository import ReservaRepository
from app.schemas.reserva import (
    ReservaCrear,
    ReservaRespuesta,
    MesaResumenReserva
)
from app.services.disponibilidad_mesas_service import DisponibilidadMesasService


class ReservaService:
    TRANSICIONES_PERMITIDAS = {
        "PENDIENTE": {"CONFIRMADA", "CANCELADA"},
        "CONFIRMADA": {"FINALIZADA", "CANCELADA"},
        "FINALIZADA": set(),
        "CANCELADA": set()
    }

    @staticmethod
    def validar_capacidad_maxima(capacidad: int, cantidad_personas: int) -> None:
        capacidad_maxima = cantidad_personas + settings.MAX_EXCESO_CAPACIDAD_MESA
        if capacidad > capacidad_maxima:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"La capacidad seleccionada ({capacidad}p) supera "
                    f"el maximo permitido de {capacidad_maxima}p para "
                    f"{cantidad_personas} personas."
                )
            )

    @classmethod
    def _mapear_respuesta(cls, reserva: Reserva) -> ReservaRespuesta:
        area_obj = None
        if reserva.mesas and len(reserva.mesas) > 0:
            area_obj = reserva.mesas[0].area

        mesas_resumen = [
            MesaResumenReserva(
                id_mesa=m.id_mesa,
                numero=m.numero,
                nombre=m.nombre,
                capacidad=m.capacidad
            )
            for m in reserva.mesas
        ]

        cliente = reserva.usuario
        return ReservaRespuesta(
            id_reserva=reserva.id_reserva,
            id_restaurante=reserva.id_restaurante,
            nombre_restaurante=reserva.restaurante.nombre if reserva.restaurante else f"Restaurante #{reserva.id_restaurante}",
            id_area=area_obj.id_area if area_obj else None,
            nombre_area=area_obj.nombre if area_obj else None,
            fecha_reserva=reserva.fecha_reserva,
            hora_inicio=reserva.hora_inicio,
            hora_fin=reserva.hora_fin,
            cantidad_personas=reserva.cantidad_personas,
            estado=reserva.estado,
            observaciones=reserva.observaciones,
            id_usuario=reserva.id_usuario,
            nombre_cliente=f"{cliente.nombres} {cliente.apellidos}" if cliente else None,
            correo_cliente=cliente.correo if cliente else None,
            telefono_cliente=cliente.telefono if cliente else None,
            id_planificacion=reserva.id_planificacion,
            mesas=mesas_resumen,
            fecha_creacion=reserva.fecha_creacion
        )

    @classmethod
    def crear_reserva(
        cls,
        db: Session,
        datos: ReservaCrear,
        usuario_actual: Usuario
    ) -> ReservaRespuesta:
        """
        CU21: Realizar reserva con control estricto de concurrencia y validaciones de negocio.
        Aplica SELECT ... FOR UPDATE determinístico sobre las mesas solicitadas.
        """
        # 1. Validar parámetros temporales contra fechas y horas pasadas
        DisponibilidadMesasService.validar_parametros_consulta(
            datos.fecha_reserva,
            datos.hora_inicio,
            datos.hora_fin,
            datos.cantidad_personas
        )

        # 2. Validar restaurante y área
        resto = RestauranteRepository.buscar_por_id(db, datos.id_restaurante)
        if not resto or resto.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurante #{datos.id_restaurante} no encontrado o inactivo."
            )

        area = AreaRestauranteRepository.obtener_por_id(db, datos.id_area)
        if not area or area.id_restaurante != datos.id_restaurante or not area.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área #{datos.id_area} no encontrada o inactiva en el restaurante."
            )

        # 3. Validar planificación si fue provista
        if datos.id_planificacion is not None:
            plan = db.query(Planificacion).filter(
                Planificacion.id_planificacion == datos.id_planificacion
            ).first()
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Planificación #{datos.id_planificacion} no encontrada."
                )
            if plan.id_usuario != usuario_actual.id_usuario and (not usuario_actual.rol or usuario_actual.rol.nombre != "ADMINISTRADOR"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="La planificación no pertenece al usuario autenticado."
                )

        # 4. CONTROL DE CONCURRENCIA: Bloqueo determinístico de mesas con SELECT ... FOR UPDATE
        mesas_ordenadas = sorted(set(datos.mesas))
        if not mesas_ordenadas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe seleccionar al menos una mesa para reservar."
            )

        mesas_bloqueadas: List[Mesa] = (
            db.query(Mesa)
            .filter(Mesa.id_mesa.in_(mesas_ordenadas))
            .with_for_update()
            .all()
        )

        if len(mesas_bloqueadas) != len(mesas_ordenadas):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Una o más mesas seleccionadas no existen."
            )

        # Validar pertenencia, vigencia y propiedades de las mesas
        capacidad_acumulada = 0
        for m in mesas_bloqueadas:
            if not m.activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La mesa {m.numero} está inactiva."
                )
            if m.id_area != datos.id_area:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La mesa {m.numero} no pertenece al área #{datos.id_area} seleccionada."
                )
            capacidad_acumulada += m.capacidad

        # 5. Validación de combinación o mesa individual
        if len(mesas_bloqueadas) == 1:
            m = mesas_bloqueadas[0]
            if m.capacidad < datos.cantidad_personas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La mesa {m.numero} tiene capacidad {m.capacidad}p, insuficiente para {datos.cantidad_personas} personas."
                )
        elif len(mesas_bloqueadas) == 2:
            m1, m2 = mesas_bloqueadas[0], mesas_bloqueadas[1]
            if m1.es_fija or m2.es_fija:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pueden combinar mesas fijas (inmovibles)."
                )
            if not m1.combinable or not m2.combinable:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Una o más mesas no están configuradas como aptas para combinación."
                )

            # Verificar que exista la combinación autorizada en base de datos
            id_menor = min(m1.id_mesa, m2.id_mesa)
            id_mayor = max(m1.id_mesa, m2.id_mesa)
            comb_db = MesaCombinacionRepository.obtener_por_par_ordenado(db, id_menor, id_mayor)
            if not comb_db or not comb_db.permitida or not comb_db.activo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Las mesas seleccionadas no forman una combinación permitida registrada por el restaurante."
                )

            if capacidad_acumulada < datos.cantidad_personas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La combinación seleccionada (capacidad {capacidad_acumulada}p) es insuficiente para {datos.cantidad_personas} personas."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="En esta versión solo se admiten reservas individuales o combinaciones de 2 mesas autorizadas."
            )

        # Mantener la misma regla de capacidad que CU20 al crear la reserva.
        cls.validar_capacidad_maxima(capacidad_acumulada, datos.cantidad_personas)
        # 6. VERIFICACIÓN DE CONFLICTOS DENTRO DE LA TRANSACCIÓN BLOQUEADA
        conflictos = ReservaRepository.buscar_conflictos_mesas(
            db=db,
            mesas_ids=mesas_ordenadas,
            fecha=datos.fecha_reserva,
            hora_inicio=datos.hora_inicio,
            hora_fin=datos.hora_fin
        )

        if conflictos:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La mesa seleccionada ya no está disponible para el horario solicitado. Actualiza el mapa y selecciona otra opción."
            )

        # 7. Creación atómica de la reserva (estado inicial CONFIRMADA para bloqueo inmediato)
        nueva_reserva = Reserva(
            fecha_reserva=datos.fecha_reserva,
            hora_inicio=datos.hora_inicio,
            hora_fin=datos.hora_fin,
            cantidad_personas=datos.cantidad_personas,
            estado="CONFIRMADA",
            observaciones=datos.observaciones,
            id_usuario=usuario_actual.id_usuario,
            id_restaurante=datos.id_restaurante,
            id_planificacion=datos.id_planificacion
        )

        reserva_creada = ReservaRepository.crear_reserva(db, nueva_reserva, mesas_ordenadas)
        db.commit()

        # Recargar con relaciones
        reserva_completa = ReservaRepository.obtener_por_id(db, reserva_creada.id_reserva)
        return cls._mapear_respuesta(reserva_completa)

    @classmethod
    def listar_mis_reservas(cls, db: Session, usuario_actual: Usuario) -> List[ReservaRespuesta]:
        """
        CU21: Lista reservas pertenecientes al cliente autenticado.
        """
        reservas = ReservaRepository.listar_por_usuario(db, usuario_actual.id_usuario)
        return [cls._mapear_respuesta(r) for r in reservas]

    @classmethod
    def obtener_detalle(cls, db: Session, id_reserva: int, usuario_actual: Usuario) -> ReservaRespuesta:
        """
        Obtiene detalle con verificación estricta de propiedad (CLIENTE o RESTAURANTE propietario).
        """
        reserva = ReservaRepository.obtener_por_id(db, id_reserva)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva #{id_reserva} no encontrada."
            )

        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol == "ADMINISTRADOR":
            pass
        elif rol == "CLIENTE":
            if reserva.id_usuario != usuario_actual.id_usuario:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permiso para consultar esta reserva ajena."
                )
        elif rol == "RESTAURANTE":
            if reserva.restaurante.id_usuario_responsable != usuario_actual.id_usuario:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permiso para consultar reservas de otro establecimiento."
                )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado.")

        return cls._mapear_respuesta(reserva)

    @classmethod
    def cancelar_reserva_cliente(cls, db: Session, id_reserva: int, usuario_actual: Usuario) -> ReservaRespuesta:
        """
        CU21: Cancela la reserva si pertenece al cliente y no está finalizada o cancelada.
        Libera inmediatamente las mesas para el intervalo.
        """
        reserva = ReservaRepository.obtener_por_id(db, id_reserva)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva #{id_reserva} no encontrada."
            )

        if reserva.id_usuario != usuario_actual.id_usuario and (not usuario_actual.rol or usuario_actual.rol.nombre != "ADMINISTRADOR"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el titular de la reserva puede cancelarla."
            )

        if reserva.estado in ("FINALIZADA", "CANCELADA"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede cancelar una reserva que ya se encuentra {reserva.estado}."
            )

        reserva.estado = "CANCELADA"
        db.commit()
        db.refresh(reserva)
        return cls._mapear_respuesta(reserva)

    @classmethod
    def listar_reservas_restaurante(
        cls,
        db: Session,
        id_restaurante: int,
        usuario_actual: Usuario,
        fecha: Optional[date] = None,
        estado: Optional[str] = None,
        id_area: Optional[int] = None
    ) -> List[ReservaRespuesta]:
        """
        CU22: Consultar y filtrar reservas recibidas por el restaurante.
        """
        resto = RestauranteRepository.buscar_por_id(db, id_restaurante)
        if not resto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Restaurante #{id_restaurante} no encontrado."
            )

        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol != "ADMINISTRADOR" and resto.id_usuario_responsable != usuario_actual.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para consultar reservas de otro establecimiento."
            )

        reservas = ReservaRepository.listar_por_restaurante(
            db=db,
            id_restaurante=id_restaurante,
            fecha=fecha,
            estado=estado,
            id_area=id_area
        )
        return [cls._mapear_respuesta(r) for r in reservas]

    @classmethod
    def actualizar_estado_restaurante(
        cls,
        db: Session,
        id_reserva: int,
        nuevo_estado: str,
        usuario_actual: Usuario
    ) -> ReservaRespuesta:
        """
        CU22: Actualiza el estado de la reserva aplicando transiciones controladas.
        """
        reserva = ReservaRepository.obtener_por_id(db, id_reserva)
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva #{id_reserva} no encontrada."
            )

        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol != "ADMINISTRADOR" and reserva.restaurante.id_usuario_responsable != usuario_actual.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para modificar reservas de otro restaurante."
            )

        estado_actual = reserva.estado
        nuevo_upper = nuevo_estado.upper().strip()

        permitidas = cls.TRANSICIONES_PERMITIDAS.get(estado_actual, set())
        if nuevo_upper not in permitidas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transición de estado no permitida de '{estado_actual}' a '{nuevo_upper}'. Permitidas: {list(permitidas) or 'Ninguna'}"
            )

        reserva.estado = nuevo_upper
        db.commit()
        db.refresh(reserva)
        return cls._mapear_respuesta(reserva)
