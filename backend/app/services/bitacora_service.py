import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.bitacora import Bitacora
from app.repositories.bitacora_repository import BitacoraRepository
from app.schemas.bitacora import BitacoraRespuestaSchema, BitacoraListadoPaginadoSchema

logger = logging.getLogger(__name__)


class BitacoraService:
    """
    Servicio de dominio para registro y consulta de auditoría del sistema (CU25).
    """

    @staticmethod
    def registrar_evento(
        db: Session,
        accion: str,
        modulo: str,
        descripcion: str,
        id_usuario: Optional[int] = None,
        direccion_ip: Optional[str] = None,
        detalles: Optional[Dict[str, Any]] = None
    ) -> Optional[Bitacora]:
        """
        Registra de forma segura un evento en la bitácora del sistema sin interrumpir
        el flujo principal en caso de fallo no crítico de registro.
        """
        try:
            registro = Bitacora(
                id_usuario=id_usuario,
                accion=accion.strip().upper(),
                modulo=modulo.strip().upper(),
                descripcion=descripcion.strip(),
                direccion_ip=direccion_ip,
                detalles=detalles
            )
            return BitacoraRepository.crear(db, registro)
        except Exception as e:
            logger.error(f"Error al registrar evento en bitácora: {e}", exc_info=True)
            return None

    @staticmethod
    def listar(
        db: Session,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        modulo: Optional[str] = None,
        accion: Optional[str] = None,
        id_usuario: Optional[int] = None,
        busqueda: Optional[str] = None,
        pagina: int = 1,
        limite: int = 20
    ) -> BitacoraListadoPaginadoSchema:
        if pagina < 1:
            pagina = 1
        if limite < 1 or limite > 100:
            limite = 20

        items, total = BitacoraRepository.listar_con_filtros(
            db=db,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            modulo=modulo,
            accion=accion,
            id_usuario=id_usuario,
            busqueda=busqueda,
            pagina=pagina,
            limite=limite
        )

        total_paginas = (total + limite - 1) // limite if total > 0 else 1

        items_respuesta = []
        for reg in items:
            correo = reg.usuario.correo if reg.usuario else None
            nombre = f"{reg.usuario.nombres} {reg.usuario.apellidos}" if reg.usuario else None
            items_respuesta.append(
                BitacoraRespuestaSchema(
                    id_bitacora=reg.id_bitacora,
                    id_usuario=reg.id_usuario,
                    correo_usuario=correo,
                    nombre_usuario=nombre,
                    accion=reg.accion,
                    modulo=reg.modulo,
                    descripcion=reg.descripcion,
                    direccion_ip=reg.direccion_ip,
                    detalles=reg.detalles,
                    fecha_hora=reg.fecha_hora
                )
            )

        return BitacoraListadoPaginadoSchema(
            total=total,
            pagina=pagina,
            limite=limite,
            total_paginas=total_paginas,
            items=items_respuesta
        )
