# CASO DE USO: CU17 - Crear plano 2D del restaurante
# CASO DE USO: CU18 - Gestionar mesas
# CASO DE USO: CU19 - Definir combinación de mesas
from typing import List
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.mesa import (
    CrearMesaSchema,
    ActualizarMesaSchema,
    CambiarEstadoMesaSchema,
    MesaRespuestaSchema
)
from app.schemas.distribucion import (
    GenerarDistribucionRequestSchema,
    GuardarDistribucionRequestSchema,
    DistribucionAreaRespuestaSchema
)
from app.schemas.mesa_combinacion import (
    CrearMesaCombinacionSchema,
    ActualizarMesaCombinacionSchema,
    MesaCombinacionRespuestaSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.mesa_service import MesaService
from app.services.distribucion_mesas_service import DistribucionMesasService
from app.services.mesa_combinacion_service import MesaCombinacionService

router = APIRouter(
    tags=["Mesas y Distribución 2D"]
)


# =========================================================================
# CU18: GESTIONAR MESAS
# =========================================================================

@router.get(
    "/areas/{id_area}/mesas",
    response_model=List[MesaRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU18: Listar mesas de un área",
    description="Retorna todas las mesas pertenecientes al área indicada."
)
def listar_mesas_area(
    id_area: int = Path(..., ge=1, description="ID del área"),
    solo_activas: bool = Query(False, description="Filtrar únicamente mesas activas"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return MesaService.listar_mesas_area(
        db=db,
        id_area=id_area,
        usuario_actual=usuario_actual,
        solo_activas=solo_activas
    )


@router.post(
    "/areas/{id_area}/mesas",
    response_model=MesaRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU18: Crear mesa individual en un área",
    description="Crea una mesa en la posición normalizada indicada asociando el área de la ruta."
)
def crear_mesa(
    datos: CrearMesaSchema,
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return MesaService.crear_mesa(
        db=db,
        id_area=id_area,
        datos=datos,
        usuario_actual=usuario_actual
    )


@router.get(
    "/mesas/{id_mesa}",
    response_model=MesaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU18: Consultar detalle de una mesa",
    description="Obtiene las propiedades de una mesa física específica."
)
def obtener_mesa(
    id_mesa: int = Path(..., ge=1, description="ID de la mesa"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return MesaService.obtener_mesa(
        db=db,
        id_mesa=id_mesa,
        usuario_actual=usuario_actual
    )


@router.put(
    "/mesas/{id_mesa}",
    response_model=MesaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU18: Actualizar datos de una mesa",
    description="Modifica atributos como número, capacidad, forma, rotación o propiedades fijas/combinables."
)
def actualizar_mesa(
    datos: ActualizarMesaSchema,
    id_mesa: int = Path(..., ge=1, description="ID de la mesa"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return MesaService.actualizar_mesa(
        db=db,
        id_mesa=id_mesa,
        datos=datos,
        usuario_actual=usuario_actual
    )


@router.patch(
    "/mesas/{id_mesa}/estado",
    response_model=MesaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU18: Cambiar estado lógico de una mesa",
    description="Activa o desactiva lógicamente una mesa del restaurante."
)
def cambiar_estado_mesa(
    datos: CambiarEstadoMesaSchema,
    id_mesa: int = Path(..., ge=1, description="ID de la mesa"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return MesaService.cambiar_estado(
        db=db,
        id_mesa=id_mesa,
        activo=datos.activo,
        usuario_actual=usuario_actual
    )


@router.delete(
    "/mesas/{id_mesa}",
    response_model=MesaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU18: Eliminar o desactivar mesa (baja lógica)",
    description="Desactiva lógicamente una mesa del área verificando permisos de propiedad."
)
def eliminar_mesa(
    id_mesa: int = Path(..., ge=1, description="ID de la mesa"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return MesaService.cambiar_estado(
        db=db,
        id_mesa=id_mesa,
        activo=False,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CU17: DISTRIBUCIÓN 2D AUTOMÁTICA Y GUARDADO
# =========================================================================

@router.post(
    "/areas/{id_area}/generar-distribucion",
    response_model=DistribucionAreaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU17: Generar distribución automática de mesas",
    description="Crea un lote de mesas según las capacidades solicitadas distribuyéndolas en cuadrícula sin colisiones."
)
def generar_distribucion_automatica(
    datos: GenerarDistribucionRequestSchema,
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return DistribucionMesasService.generar_distribucion_automatica(
        db=db,
        id_area=id_area,
        datos=datos,
        usuario_actual=usuario_actual
    )


@router.post(
    "/areas/{id_area}/restablecer-distribucion",
    response_model=DistribucionAreaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU17: Restablecer distribución de mesas existentes",
    description="Reorganiza en cuadrícula las mesas activas existentes en el área conservando sus identidades y capacidades."
)
def restablecer_distribucion(
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return DistribucionMesasService.restablecer_distribucion(
        db=db,
        id_area=id_area,
        usuario_actual=usuario_actual
    )


@router.put(
    "/areas/{id_area}/distribucion",
    response_model=DistribucionAreaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU17: Guardar distribución modificada (drag & drop)",
    description="Actualiza masivamente en una transacción las coordenadas y rotaciones de las mesas tras acomodarlas en el lienzo."
)
def guardar_distribucion(
    datos: GuardarDistribucionRequestSchema,
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return DistribucionMesasService.guardar_distribucion(
        db=db,
        id_area=id_area,
        datos=datos,
        usuario_actual=usuario_actual
    )


# =========================================================================
# CU19: DEFINIR COMBINACIÓN DE MESAS
# =========================================================================

@router.get(
    "/areas/{id_area}/combinaciones",
    response_model=List[MesaCombinacionRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU19: Listar combinaciones permitidas de un área",
    description="Obtiene todas las combinaciones registradas entre pares de mesas para el área indicada."
)
def listar_combinaciones_area(
    id_area: int = Path(..., ge=1, description="ID del área"),
    solo_activas: bool = Query(False, description="Filtrar únicamente combinaciones activas"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return MesaCombinacionService.listar_combinaciones_area(
        db=db,
        id_area=id_area,
        usuario_actual=usuario_actual,
        solo_activas=solo_activas
    )


@router.post(
    "/areas/{id_area}/combinaciones",
    response_model=MesaCombinacionRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU19: Registrar combinación permitida entre dos mesas",
    description="Define que dos mesas no fijas del área pueden unirse para atender grupos mayores."
)
def crear_combinacion(
    datos: CrearMesaCombinacionSchema,
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return MesaCombinacionService.crear_combinacion(
        db=db,
        id_area=id_area,
        datos=datos,
        usuario_actual=usuario_actual
    )


@router.post(
    "/combinaciones",
    response_model=MesaCombinacionRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU19: Registrar combinación permitida entre dos mesas (directa)",
    description="Registra la combinación infiriendo el área física a partir de la mesa de origen."
)
def crear_combinacion_directa(
    datos: CrearMesaCombinacionSchema,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    mesa = MesaRepository.obtener_por_id(db, datos.id_mesa_origen)
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa de origen con ID {datos.id_mesa_origen} no encontrada."
        )
    return MesaCombinacionService.crear_combinacion(
        db=db,
        id_area=mesa.id_area,
        datos=datos,
        usuario_actual=usuario_actual
    )


@router.put(
    "/combinaciones/{id_combinacion}",
    response_model=MesaCombinacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU19: Actualizar combinación de mesas",
    description="Modifica si la combinación está permitida, su descripción o su estado activo."
)
def actualizar_combinacion(
    datos: ActualizarMesaCombinacionSchema,
    id_combinacion: int = Path(..., ge=1, description="ID de la combinación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return MesaCombinacionService.actualizar_combinacion(
        db=db,
        id_combinacion=id_combinacion,
        datos=datos,
        usuario_actual=usuario_actual
    )


@router.delete(
    "/combinaciones/{id_combinacion}",
    response_model=MesaCombinacionRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU19: Desactivar combinación de mesas (baja lógica)",
    description="Desactiva lógicamente una combinación de mesas sin eliminarla físicamente."
)
def desactivar_combinacion(
    id_combinacion: int = Path(..., ge=1, description="ID de la combinación"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    return MesaCombinacionService.desactivar_combinacion(
        db=db,
        id_combinacion=id_combinacion,
        usuario_actual=usuario_actual
    )
