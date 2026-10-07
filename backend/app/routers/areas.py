# CASO DE USO: CU17 - Crear plano 2D del restaurante (Gestión de Áreas)
from typing import List
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.area_restaurante import (
    CrearAreaRestauranteSchema,
    ActualizarAreaRestauranteSchema,
    CambiarEstadoAreaSchema,
    AreaRestauranteRespuestaSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.area_restaurante_service import AreaRestauranteService

router = APIRouter(
    tags=["Áreas de Restaurante"]
)


@router.get(
    "/restaurantes/{id_restaurante}/areas",
    response_model=List[AreaRestauranteRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU17: Listar áreas de un restaurante",
    description="Obtiene todas las áreas físicas (salón, terraza, patio, etc.) de un restaurante."
)
def listar_areas(
    id_restaurante: int = Path(..., ge=1, description="ID del restaurante"),
    solo_activas: bool = Query(False, description="Filtrar únicamente áreas activas"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return AreaRestauranteService.listar_areas(
        db=db,
        id_restaurante=id_restaurante,
        usuario_actual=usuario_actual,
        solo_activas=solo_activas
    )


@router.post(
    "/restaurantes/{id_restaurante}/areas",
    response_model=AreaRestauranteRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU17: Crear nueva área en un restaurante",
    description="Registra una nueva área independiente con dimensiones lógicas de lienzo 2D asignando el restaurante de la ruta."
)
def crear_area(
    datos: CrearAreaRestauranteSchema,
    id_restaurante: int = Path(..., ge=1, description="ID del restaurante"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    nueva = AreaRestauranteService.crear_area(
        db=db,
        id_restaurante=id_restaurante,
        datos=datos,
        usuario_actual=usuario_actual
    )
    return AreaRestauranteService.obtener_area(db, nueva.id_area, usuario_actual)


@router.get(
    "/areas/{id_area}",
    response_model=AreaRestauranteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU17: Consultar detalle de un área",
    description="Devuelve la información de un área incluyendo dimensiones y conteo de mesas."
)
def obtener_area(
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return AreaRestauranteService.obtener_area(
        db=db,
        id_area=id_area,
        usuario_actual=usuario_actual
    )


@router.put(
    "/areas/{id_area}",
    response_model=AreaRestauranteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU17: Actualizar datos de un área",
    description="Permite modificar el nombre, dimensiones lógicas u orden de un área del restaurante."
)
def actualizar_area(
    datos: ActualizarAreaRestauranteSchema,
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    actualizada = AreaRestauranteService.actualizar_area(
        db=db,
        id_area=id_area,
        datos=datos,
        usuario_actual=usuario_actual
    )
    return AreaRestauranteService.obtener_area(db, actualizada.id_area, usuario_actual)


@router.patch(
    "/areas/{id_area}/estado",
    response_model=AreaRestauranteRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU17: Cambiar estado lógico de un área",
    description="Activa o desactiva lógicamente un área del restaurante."
)
def cambiar_estado_area(
    datos: CambiarEstadoAreaSchema,
    id_area: int = Path(..., ge=1, description="ID del área"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("RESTAURANTE", "ADMINISTRADOR"))
):
    actualizada = AreaRestauranteService.cambiar_estado(
        db=db,
        id_area=id_area,
        activo=datos.activo,
        usuario_actual=usuario_actual
    )
    return AreaRestauranteService.obtener_area(db, actualizada.id_area, usuario_actual)
