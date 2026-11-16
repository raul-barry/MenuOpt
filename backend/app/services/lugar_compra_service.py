# CASO DE USO: CU16 - Consultar lugares de compra
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.models.lugar_compra import LugarCompra
from app.models.ingrediente import Ingrediente
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
from app.services.bitacora_service import BitacoraService


class LugarCompraService:
    """
    Servicio de administración y consulta de establecimientos de compra de ingredientes (CU09 y CU16).
    """

    @staticmethod
    def _validar_permiso_tienda(lugar: LugarCompra, usuario_actual: Usuario) -> None:
        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol == "ADMINISTRADOR":
            return
        if rol == "ADMINISTRADOR_TIENDA":
            if lugar.id_usuario_responsable != usuario_actual.id_usuario:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permiso para administrar los insumos o datos de otra tienda/proveedor."
                )
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado para gestionar este comercio."
        )

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

        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        id_responsable = None
        if rol == "ADMINISTRADOR_TIENDA":
            id_responsable = usuario_actual.id_usuario
        elif rol == "ADMINISTRADOR":
            id_responsable = datos.id_usuario_responsable or usuario_actual.id_usuario

        nuevo_lugar = LugarCompra(
            nombre=nombre_limpio,
            tipo=datos.tipo.strip().upper() if datos.tipo else None,
            telefono=datos.telefono.strip() if datos.telefono else None,
            estado="ACTIVO",
            id_ubicacion=id_ubicacion,
            id_usuario_responsable=id_responsable
        )

        creado = LugarCompraRepository.crear(db, nuevo_lugar)

        BitacoraService.registrar_evento(
            db=db,
            accion="CREAR_PROVEEDOR",
            modulo="PROVEEDORES",
            descripcion=f"Proveedor / Tienda '{creado.nombre}' registrado por {usuario_actual.correo}",
            id_usuario=usuario_actual.id_usuario,
            detalles={"id_lugar_compra": creado.id_lugar_compra, "tipo": creado.tipo}
        )

        return LugarCompraRespuestaSchema.model_validate(creado)

    @staticmethod
    def listar_mis_tiendas(
        db: Session,
        usuario_actual: Usuario
    ) -> List[LugarCompraRespuestaSchema]:
        """
        Lista las tiendas o proveedores administrados por el usuario autenticado.
        """
        rol = usuario_actual.rol.nombre if usuario_actual.rol else ""
        if rol == "ADMINISTRADOR":
            lugares = LugarCompraRepository.listar(db)
        else:
            lugares = LugarCompraRepository.listar_por_usuario(db, usuario_actual.id_usuario)
        return [LugarCompraRespuestaSchema.model_validate(l) for l in lugares]

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
        LugarCompraService._validar_permiso_tienda(lugar, usuario_actual)

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
        LugarCompraService._validar_permiso_tienda(lugar, usuario_actual)

        ingrediente = None
        if datos.id_ingrediente:
            ingrediente = IngredienteRepository.buscar_por_id(db, datos.id_ingrediente)

        if not ingrediente and datos.nombre_ingrediente:
            nombre_limpio = datos.nombre_ingrediente.strip()
            if nombre_limpio:
                ingrediente = IngredienteRepository.buscar_por_nombre(db, nombre_limpio)
                if not ingrediente:
                    # Crear nuevo ingrediente en el catálogo automáticamente
                    nuevo_ing = Ingrediente(
                        nombre=nombre_limpio,
                        unidad_medida=datos.unidad_medida.strip() if datos.unidad_medida else "kg",
                        precio_estimado=datos.precio,
                        estado="ACTIVO"
                    )
                    ingrediente = IngredienteRepository.crear(db, nuevo_ing)

        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe ingresar el nombre del ingrediente o seleccionar uno del catálogo."
            )

        id_ing = ingrediente.id_ingrediente
        existente = IngredienteLugarCompraRepository.buscar_relacion(db, id_ing, id_lugar_compra)
        if existente:
            existente.precio = datos.precio
            if datos.cantidad_referencia:
                existente.cantidad_referencia = datos.cantidad_referencia
            if datos.unidad_medida:
                existente.unidad_medida = datos.unidad_medida.strip()
            existente.disponible = datos.disponible
            guardada = IngredienteLugarCompraRepository.actualizar(db, existente)
            accion_bitacora = "ACTUALIZAR_PRECIO_PROVEEDOR"
            desc_bitacora = f"Precio de '{ingrediente.nombre}' en '{lugar.nombre}' actualizado a Bs. {datos.precio}"
        else:
            relacion = IngredienteLugarCompra(
                id_ingrediente=id_ing,
                id_lugar_compra=id_lugar_compra,
                precio=datos.precio,
                cantidad_referencia=datos.cantidad_referencia,
                unidad_medida=datos.unidad_medida.strip() if datos.unidad_medida else ingrediente.unidad_medida,
                disponible=datos.disponible
            )
            guardada = IngredienteLugarCompraRepository.asociar(db, relacion)
            accion_bitacora = "ASOCIAR_PRECIO_PROVEEDOR"
            desc_bitacora = f"Ingrediente '{ingrediente.nombre}' asociado a '{lugar.nombre}' con precio Bs. {datos.precio}"

        BitacoraService.registrar_evento(
            db=db,
            accion=accion_bitacora,
            modulo="PROVEEDORES",
            descripcion=desc_bitacora,
            id_usuario=usuario_actual.id_usuario,
            detalles={"id_lugar_compra": id_lugar_compra, "id_ingrediente": id_ing, "precio": float(datos.precio)}
        )

        return LugarCompraService._mapear_relacion_schema(guardada)

    @staticmethod
    def actualizar_ingrediente_en_lugar(
        db: Session,
        id_lugar_compra: int,
        id_ingrediente: int,
        datos: ActualizarIngredienteLugarCompraSchema,
        usuario_actual: Usuario
    ) -> IngredienteLugarCompraRespuestaSchema:
        lugar = LugarCompraRepository.buscar_por_id(db, id_lugar_compra)
        if not lugar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el lugar de compra con ID {id_lugar_compra}."
            )
        LugarCompraService._validar_permiso_tienda(lugar, usuario_actual)

        relacion = IngredienteLugarCompraRepository.buscar_relacion(db, id_ingrediente, id_lugar_compra)
        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe registro del ingrediente ID {id_ingrediente} en el lugar ID {id_lugar_compra}."
            )

        precio_anterior = float(relacion.precio)
        if datos.precio is not None:
            relacion.precio = datos.precio
        if datos.cantidad_referencia is not None:
            relacion.cantidad_referencia = datos.cantidad_referencia
        if datos.unidad_medida is not None:
            relacion.unidad_medida = datos.unidad_medida.strip()
        if datos.disponible is not None:
            relacion.disponible = datos.disponible

        actualizada = IngredienteLugarCompraRepository.actualizar(db, relacion)

        BitacoraService.registrar_evento(
            db=db,
            accion="ACTUALIZAR_PRECIO_PROVEEDOR",
            modulo="PROVEEDORES",
            descripcion=f"Precio actualizado de ingrediente #{id_ingrediente} en '{lugar.nombre}' de Bs. {precio_anterior} a Bs. {relacion.precio}",
            id_usuario=usuario_actual.id_usuario,
            detalles={"id_lugar_compra": id_lugar_compra, "id_ingrediente": id_ingrediente, "precio": float(relacion.precio)}
        )

        return LugarCompraService._mapear_relacion_schema(actualizada)

    @staticmethod
    def quitar_ingrediente_de_lugar(
        db: Session,
        id_lugar_compra: int,
        id_ingrediente: int,
        usuario_actual: Usuario
    ) -> dict:
        lugar = LugarCompraRepository.buscar_por_id(db, id_lugar_compra)
        if not lugar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el lugar de compra con ID {id_lugar_compra}."
            )
        LugarCompraService._validar_permiso_tienda(lugar, usuario_actual)

        relacion = IngredienteLugarCompraRepository.buscar_relacion(db, id_ingrediente, id_lugar_compra)
        if not relacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe registro del ingrediente ID {id_ingrediente} en el lugar ID {id_lugar_compra}."
            )

        IngredienteLugarCompraRepository.eliminar(db, relacion)

        BitacoraService.registrar_evento(
            db=db,
            accion="QUITAR_PRECIO_PROVEEDOR",
            modulo="PROVEEDORES",
            descripcion=f"Ingrediente #{id_ingrediente} retirado del catálogo de '{lugar.nombre}'",
            id_usuario=usuario_actual.id_usuario
        )

        return {"mensaje": "Ingrediente retirado exitosamente del proveedor."}

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
