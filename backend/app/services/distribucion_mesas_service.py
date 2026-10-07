# CASO DE USO: CU17 - Crear plano 2D del restaurante & Generación y guardado de distribución
from typing import List, Dict, Any, Set
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.mesa import Mesa
from app.repositories.area_restaurante_repository import AreaRestauranteRepository
from app.repositories.mesa_repository import MesaRepository
from app.schemas.distribucion import (
    GenerarDistribucionRequestSchema,
    GuardarDistribucionRequestSchema,
    DistribucionAreaRespuestaSchema
)
from app.schemas.mesa import MesaRespuestaSchema
from app.services.distribucion_algoritmo import (
    generar_posiciones_normalizadas,
    calcular_siguiente_numero_mesa
)
from app.security.propiedad import verificar_propiedad_area


class DistribucionMesasService:

    @staticmethod
    def generar_distribucion_automatica(
        db: Session,
        id_area: int,
        datos: GenerarDistribucionRequestSchema,
        usuario_actual: Usuario
    ) -> DistribucionAreaRespuestaSchema:
        """
        CU17: Genera mesas automáticamente con algoritmo determinista basado en cuadrícula
        sin superposiciones ni colisiones y las persiste directamente.
        """
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        # 1. Expandir requerimientos por capacidad
        capacidades_expandidas: List[int] = []
        for item in datos.mesas:
            for _ in range(item.cantidad):
                capacidades_expandidas.append(item.capacidad)

        total_nuevas = len(capacidades_expandidas)
        if total_nuevas == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe indicar al menos una mesa para generar."
            )

        # 2. Obtener números existentes para no colisionar correlativos
        mesas_existentes = MesaRepository.listar_por_area(db, id_area, solo_activas=False)
        numeros_usados: Set[str] = {m.numero for m in mesas_existentes}

        # 3. Generar coordenadas normalizadas para la cantidad total
        posiciones = generar_posiciones_normalizadas(total_nuevas)

        # 4. Crear instancias de Mesa
        nuevas_mesas: List[Mesa] = []
        for i, cap in enumerate(capacidades_expandidas):
            num = calcular_siguiente_numero_mesa(numeros_usados, prefijo="M")
            numeros_usados.add(num)

            # Asignar forma lógica según capacidad
            if cap >= 6:
                forma = "RECTANGULAR"
                ancho = Decimal("0.1200")
                alto = Decimal("0.0800")
            elif cap == 2:
                forma = "REDONDA"
                ancho = Decimal("0.0700")
                alto = Decimal("0.0700")
            else:
                forma = "CUADRADA"
                ancho = Decimal("0.0800")
                alto = Decimal("0.0800")

            pos_x, pos_y = posiciones[i]

            m = Mesa(
                id_area=id_area,
                numero=num,
                nombre=f"Mesa {num}",
                capacidad=cap,
                forma=forma,
                posicion_x=pos_x,
                posicion_y=pos_y,
                rotacion=0,
                ancho=ancho,
                alto=alto,
                es_fija=False,
                combinable=True,
                activo=True
            )
            nuevas_mesas.append(m)

        MesaRepository.crear_varias(db, nuevas_mesas)

        # 5. Obtener todas las mesas activas del área y retornar distribución
        mesas_actuales = MesaRepository.listar_por_area(db, id_area, solo_activas=True)
        return DistribucionAreaRespuestaSchema(
            id_area=area.id_area,
            nombre_area=area.nombre,
            ancho_mapa=area.ancho_mapa,
            alto_mapa=area.alto_mapa,
            total_mesas=len(mesas_actuales),
            mesas=[MesaRespuestaSchema.model_validate(m) for m in mesas_actuales]
        )

    @staticmethod
    def restablecer_distribucion(
        db: Session,
        id_area: int,
        usuario_actual: Usuario
    ) -> DistribucionAreaRespuestaSchema:
        """
        CU17: Reorganiza las posiciones de las mesas activas existentes en cuadrícula
        sin modificar sus números, formas, capacidades ni eliminarlas.
        """
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        mesas_activas = MesaRepository.listar_por_area(db, id_area, solo_activas=True)
        if len(mesas_activas) > 0:
            posiciones = generar_posiciones_normalizadas(len(mesas_activas))
            actualizaciones: List[Dict[str, Any]] = []
            for i, m in enumerate(mesas_activas):
                actualizaciones.append({
                    "id_mesa": m.id_mesa,
                    "posicion_x": posiciones[i][0],
                    "posicion_y": posiciones[i][1],
                    "rotacion": 0
                })
            MesaRepository.actualizar_posiciones_masivas(db, actualizaciones)

        mesas_actualizadas = MesaRepository.listar_por_area(db, id_area, solo_activas=True)
        return DistribucionAreaRespuestaSchema(
            id_area=area.id_area,
            nombre_area=area.nombre,
            ancho_mapa=area.ancho_mapa,
            alto_mapa=area.alto_mapa,
            total_mesas=len(mesas_actualizadas),
            mesas=[MesaRespuestaSchema.model_validate(m) for m in mesas_actualizadas]
        )

    @staticmethod
    def guardar_distribucion(
        db: Session,
        id_area: int,
        datos: GuardarDistribucionRequestSchema,
        usuario_actual: Usuario
    ) -> DistribucionAreaRespuestaSchema:
        """
        CU17: Persiste en bloque las posiciones relativas (drag & drop) y rotaciones
        de las mesas de un área de manera atómica, validando que todas las mesas
        pertenezcan estrictamente al área.
        """
        area = AreaRestauranteRepository.obtener_por_id(db, id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Área con ID {id_area} no encontrada."
            )
        verificar_propiedad_area(area, usuario_actual)

        ids_solicitados = [item.id_mesa for item in datos.mesas]
        if not ids_solicitados:
            mesas_actuales = MesaRepository.listar_por_area(db, id_area, solo_activas=True)
            return DistribucionAreaRespuestaSchema(
                id_area=area.id_area,
                nombre_area=area.nombre,
                ancho_mapa=area.ancho_mapa,
                alto_mapa=area.alto_mapa,
                total_mesas=len(mesas_actuales),
                mesas=[MesaRespuestaSchema.model_validate(m) for m in mesas_actuales]
            )

        # Validar pertenencia estricta de todas las mesas a esta área
        mesas_encontradas = MesaRepository.obtener_todas_por_ids(db, ids_solicitados)
        if len(mesas_encontradas) != len(set(ids_solicitados)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Una o más mesas especificadas no existen en el sistema."
            )

        for m in mesas_encontradas:
            if m.id_area != id_area:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La mesa #{m.id_mesa} ({m.numero}) no pertenece al área #{id_area}. Operación rechazada."
                )

        # Aplicar actualización masiva atómica
        actualizaciones = [
            {
                "id_mesa": item.id_mesa,
                "posicion_x": item.posicion_x,
                "posicion_y": item.posicion_y,
                "rotacion": item.rotacion
            }
            for item in datos.mesas
        ]
        MesaRepository.actualizar_posiciones_masivas(db, actualizaciones)

        mesas_actuales = MesaRepository.listar_por_area(db, id_area, solo_activas=True)
        return DistribucionAreaRespuestaSchema(
            id_area=area.id_area,
            nombre_area=area.nombre,
            ancho_mapa=area.ancho_mapa,
            alto_mapa=area.alto_mapa,
            total_mesas=len(mesas_actuales),
            mesas=[MesaRespuestaSchema.model_validate(m) for m in mesas_actuales]
        )
