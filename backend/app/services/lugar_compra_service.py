# CASO DE USO: CU16 - Consultar lugares de compra
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.lugar_compra import LugarCompra
from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
from app.models.ubicacion import Ubicacion
from app.repositories.lugar_compra_repository import LugarCompraRepository
from app.repositories.ingrediente_lugar_compra_repository import IngredienteLugarCompraRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.schemas.lugar_compra import (
    CrearLugarCompraSchema,
    ActualizarLugarCompraSchema,
    LugarCompraRespuestaSchema,
)
from app.schemas.ingrediente_lugar_compra import (
    AsociarIngredienteLugarCompraSchema,
    ActualizarIngredienteLugarCompraSchema,
    IngredienteLugarCompraRespuestaSchema,
    LugarCompraParaIngredienteRespuestaSchema,
)


class LugarCompraService:
    """
    Servicio de administración y consulta de establecimientos de compra de ingredientes (CU16).
    """

    # =========================================================================
    # GESTIÓN DE LUGARES DE COMPRA (ADMIN)
    # =========================================================================

    @staticmethod
    def crear_lugar(
        db: Session,
        datos: CrearLugarCompraSchema,
        usuario_actual: Usuario
    ) -> LugarCompraRespuestaSchema:
        """
        Registra un nuevo lugar de compra y opcionalmente su ubicación.
        Solo accesible por rol ADMINISTRADOR.
        """
        nombre_limpio = datos.nombre.strip()
        existente = LugarCompraRepository.buscar_por_nombre(db, nombre_limpio)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un lugar de compra con el nombre '{nombre_limpio}'."
            )

        id_ubicacion = datos.id_ubicacion
        if datos.ubicacion:
            nueva_ubicacion = Ubicacion(
                direccion=datos.ubicacion.direccion.strip(),
                zona=datos.ubicacion.zona.strip() if datos.ubicacion.zona else None,
                ciudad=datos.ubicacion.ciudad.strip(),
                latitud=datos.ubicacion.latitud,
                longitud=datos.ubicacion.longitud,
                referencia=datos.ubicacion.referencia.strip() if datos.ubicacion.referencia else None
            )
            db.add(nueva_ubicacion)
            db.flush()
            id_ubicacion = nueva_ubicacion.id_ubicacion

        nuevo_lugar = LugarCompra(
            nombre=nombre_limpio,
            tipo=datos.tipo.strip().upper() if datos.tipo else None,
            telefono=datos.telefono.strip() if datos.telefono else None,
            estado="ACTIVO",
            id_ubicacion=id_ubicacion
        )

        creado = LugarCompraRepository.crear(db, nuevo_lugar)
        return LugarCompraRespuestaSchema.model_validate(creado)

    @staticmethod
    def listar_lugares(
        db: Session,
        estado: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> List[LugarCompraRespuestaSchema]:
        lugares = LugarCompraRepository.listar(db, estado=estado, tipo=tipo)
        return [LugarCompraRespuestaSchema.model_validate(l) for l in lugares]

    @staticmethod
    def obtener_lugar(
        db: Session,
        id_lugar_compra: int
    ) -> LugarCompraRespuestaSchema:
        lugar = LugarCompraRepository.buscar_por_id(db, id_lugar_compra)
        if not lugar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el lugar de compra con ID {id_lugar_compra}."
            )
        return LugarCompraRespuestaSchema.model_validate(lugar)

    @staticmethod
    def actualizar_lugar(
        db: Session,
        id_lugar_compra: int,
        datos: ActualizarLugarCompraSchema,
        usuario_actual: Usuario
    ) -> LugarCompraRespuestaSchema:
        lugar = LugarCompraRepository.buscar_por_id(db, id_lugar_compra)
        if not lugar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el lugar de compra con ID {id_lugar_compra}."
            )

        if datos.nombre is not None:
            nombre_limpio = datos.nombre.strip()
            existente = LugarCompraRepository.buscar_por_nombre(db, nombre_limpio)
            if existente and existente.id_lugar_compra != id_lugar_compra:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe otro lugar de compra con el nombre '{nombre_limpio}'."
                )
            lugar.nombre = nombre_limpio

        if datos.tipo is not None:
            lugar.tipo = datos.tipo.strip().upper() if datos.tipo else None
        if datos.telefono is not None:
            lugar.telefono = datos.telefono.strip() if datos.telefono else None

        if datos.id_ubicacion is not None:
            lugar.id_ubicacion = datos.id_ubicacion

        if datos.ubicacion:
            if lugar.ubicacion:
                if datos.ubicacion.direccion is not None:
                    lugar.ubicacion.direccion = datos.ubicacion.direccion.strip()
                if datos.ubicacion.zona is not None:
                    lugar.ubicacion.zona = datos.ubicacion.zona.strip() if datos.ubicacion.zona else None
                if datos.ubicacion.ciudad is not None:
                    lugar.ubicacion.ciudad = datos.ubicacion.ciudad.strip()
                if datos.ubicacion.latitud is not None:
                    lugar.ubicacion.latitud = datos.ubicacion.latitud
                if datos.ubicacion.longitud is not None:
                    lugar.ubicacion.longitud = datos.ubicacion.longitud
                if datos.ubicacion.referencia is not None:
                    lugar.ubicacion.referencia = datos.ubicacion.referencia.strip() if datos.ubicacion.referencia else None
            else:
                nueva_ub = Ubicacion(
                    direccion=datos.ubicacion.direccion.strip() if datos.ubicacion.direccion else "",
                    zona=datos.ubicacion.zona.strip() if datos.ubicacion.zona else None,
                    ciudad=datos.ubicacion.ciudad.strip() if datos.ubicacion.ciudad else "Santa Cruz",
                    latitud=datos.ubicacion.latitud,
                    longitud=datos.ubicacion.longitud,
                    referencia=datos.ubicacion.referencia.strip() if datos.ubicacion.referencia else None
                )
                db.add(nueva_ub)
                db.flush()
                lugar.id_ubicacion = nueva_ub.id_ubicacion

        actualizado = LugarCompraRepository.actualizar(db, lugar)
        return LugarCompraRespuestaSchema.model_validate(actualizado)

    @staticmethod
    def cambiar_estado(
        db: Session,
        id_lugar_compra: int,
        nuevo_estado: str,
        usuario_actual: Usuario
    ) -> LugarCompraRespuestaSchema:
        lugar = LugarCompraRepository.buscar_por_id(db, id_lugar_compra)
        if not lugar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el lugar de compra con ID {id_lugar_compra}."
            )
        lugar.estado = nuevo_estado.strip().upper()
        actualizado = LugarCompraRepository.actualizar(db, lugar)
        return LugarCompraRespuestaSchema.model_validate(actualizado)

    # =========================================================================
    # ASOCIACIÓN DE INGREDIENTES CON LUGARES DE COMPRA (ADMIN)
    # =========================================================================

    @staticmethod
    def asociar_ingrediente(
        db: Session,
        id_lugar_compra: int,
        datos: AsociarIngredienteLugarCompraSchema,
        usuario_actual: Usuario
    ) -> IngredienteLugarCompraRespuestaSchema:
        lugar = LugarCompraRepository.buscar_por_id(db, id_lugar_compra)
        if not lugar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el lugar de compra con ID {id_lugar_compra}."
            )

        ingrediente = IngredienteRepository.buscar_por_id(db, datos.id_ingrediente)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el ingrediente con ID {datos.id_ingrediente}."
            )

        existente = IngredienteLugarCompraRepository.buscar_relacion(db, datos.id_ingrediente, id_lugar_compra)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este ingrediente ya se encuentra registrado en el lugar de compra. Utilice PUT para actualizar su precio o disponibilidad."
            )

        relacion = IngredienteLugarCompra(
            id_ingrediente=datos.id_ingrediente,
            id_lugar_compra=id_lugar_compra,
            precio=datos.precio,
            cantidad_referencia=datos.cantidad_referencia,
            unidad_medida=datos.unidad_medida.strip(),
            disponible=datos.disponible
        )
        guardada = IngredienteLugarCompraRepository.asociar(db, relacion)
        return LugarCompraService._mapear_relacion_schema(guardada)

    @staticmethod
    def actualizar_ingrediente_en_lugar(
        db: Session,
        id_lugar_compra: int,
        id_ingrediente: int,
        datos: ActualizarIngredienteLugarCompraSchema,
        usuario_actual: Usuario
    ) -> IngredienteLugarCompraRespuestaSchema:
        relacion = IngredienteLugarCompraRepository.buscar_relacion(db, id_ingrediente, id_lugar_compra)
        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe registro del ingrediente ID {id_ingrediente} en el lugar ID {id_lugar_compra}."
            )

        if datos.precio is not None:
            relacion.precio = datos.precio
        if datos.cantidad_referencia is not None:
            relacion.cantidad_referencia = datos.cantidad_referencia
        if datos.unidad_medida is not None:
            relacion.unidad_medida = datos.unidad_medida.strip()
        if datos.disponible is not None:
            relacion.disponible = datos.disponible

        actualizada = IngredienteLugarCompraRepository.actualizar(db, relacion)
        return LugarCompraService._mapear_relacion_schema(actualizada)

    @staticmethod
    def listar_ingredientes_de_lugar(
        db: Session,
        id_lugar_compra: int
    ) -> List[IngredienteLugarCompraRespuestaSchema]:
        lugar = LugarCompraRepository.buscar_por_id(db, id_lugar_compra)
        if not lugar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el lugar de compra con ID {id_lugar_compra}."
            )
        relaciones = IngredienteLugarCompraRepository.listar_ingredientes_de_lugar(db, id_lugar_compra)
        return [LugarCompraService._mapear_relacion_schema(r) for r in relaciones]

    @staticmethod
    def listar_lugares_de_ingrediente(
        db: Session,
        id_ingrediente: int
    ) -> List[LugarCompraParaIngredienteRespuestaSchema]:
        ingrediente = IngredienteRepository.buscar_por_id(db, id_ingrediente)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el ingrediente con ID {id_ingrediente}."
            )
        relaciones = IngredienteLugarCompraRepository.listar_lugares_activos_para_ingrediente(db, id_ingrediente)
        resultados = []
        for r in relaciones:
            resultados.append(LugarCompraParaIngredienteRespuestaSchema(
                id_lugar_compra=r.lugar_compra.id_lugar_compra,
                nombre_lugar=r.lugar_compra.nombre,
                tipo_lugar=r.lugar_compra.tipo,
                telefono=r.lugar_compra.telefono,
                estado_lugar=r.lugar_compra.estado,
                precio=r.precio,
                cantidad_referencia=r.cantidad_referencia,
                unidad_medida=r.unidad_medida,
                disponible=r.disponible,
                fecha_actualizacion=r.fecha_actualizacion,
                ubicacion=r.lugar_compra.ubicacion
            ))
        return resultados

    @staticmethod
    def _mapear_relacion_schema(r: IngredienteLugarCompra) -> IngredienteLugarCompraRespuestaSchema:
        return IngredienteLugarCompraRespuestaSchema(
            id_ingrediente_lugar_compra=r.id_ingrediente_lugar_compra,
            id_ingrediente=r.id_ingrediente,
            nombre_ingrediente=r.ingrediente.nombre if r.ingrediente else None,
            id_lugar_compra=r.id_lugar_compra,
            nombre_lugar_compra=r.lugar_compra.nombre if r.lugar_compra else None,
            precio=r.precio,
            cantidad_referencia=r.cantidad_referencia,
            unidad_medida=r.unidad_medida,
            disponible=r.disponible,
            fecha_actualizacion=r.fecha_actualizacion
        )
