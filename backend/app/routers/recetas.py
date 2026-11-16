# CASO DE USO: Biblioteca de Recetas
from typing import Optional, List
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.receta import (
    RecetaCrearSchema,
    RecetaRespuestaSchema,
    RecetaConsultaIASchema,
    RecetaConsultaIARespuestaSchema
)
from app.security.dependencias import obtener_usuario_actual, requiere_roles
from app.services.receta_service import RecetaService

router = APIRouter(
    prefix="/recetas",
    tags=["Biblioteca de Recetas"]
)


# --- Consulta Culinaria con IA ---
# Endpoint: POST /recetas/consulta-ia
@router.post(
    "/consulta-ia",
    response_model=RecetaConsultaIARespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="Consultar a la IA sobre preparación con ingredientes disponibles",
    description="Permite al usuario indicar los ingredientes disponibles y recibir platos sugeridos, personas estimadas y tiendas más convenientes."
)
def consultar_ia(
    datos: RecetaConsultaIASchema,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    return RecetaService.consultar_ia(db=db, mensaje=datos.mensaje, comensales=datos.comensales)


# --- Consultar Biblioteca de Recetas ---
# Endpoint: GET /recetas
@router.get(
    "",
    response_model=List[RecetaRespuestaSchema],
    status_code=status.HTTP_200_OK,
    summary="CU15: Consultar biblioteca de recetas gastronómicas",
    description="Devuelve el catálogo de recetas de la biblioteca con opción de filtrado por tipo de comida o búsqueda."
)
def listar_recetas(
    tipo_comida: Optional[str] = Query(None, description="Filtrar por tipo (ej. ALMUERZO, CENA, DESAYUNO)"),
    busqueda: Optional[str] = Query(None, description="Término de búsqueda por nombre o descripción"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    return RecetaService.listar_recetas(db=db, tipo_comida=tipo_comida, busqueda=busqueda)


# --- CU15: Ver Detalle de una Receta ---
# Endpoint: GET /recetas/{id_receta}
@router.get(
    "/{id_receta}",
    response_model=RecetaRespuestaSchema,
    status_code=status.HTTP_200_OK,
    summary="CU15: Ver detalle de una receta de la biblioteca",
    description="Devuelve la ficha completa de una receta con sus ingredientes, porciones y preparación."
)
def obtener_receta(
    id_receta: int = Path(..., ge=1, description="ID de la receta"),
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(obtener_usuario_actual)
):
    return RecetaService.buscar_por_id(db=db, id_receta=id_receta)


# --- CU15: Añadir Nueva Receta a la Biblioteca ---
# Endpoint: POST /recetas
# Acceso exclusivo: Rol ADMINISTRADOR
@router.post(
    "",
    response_model=RecetaRespuestaSchema,
    status_code=status.HTTP_201_CREATED,
    summary="CU15: Añadir nueva receta a la biblioteca (Solo Administrador)",
    description="Permite al administrador enriquecer la biblioteca de recetas con ingredientes y pasos."
)
def crear_receta(
    datos: RecetaCrearSchema,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    return RecetaService.crear_receta(db=db, datos=datos, usuario_actual=usuario_actual)


# --- CU15: Eliminar Receta de la Biblioteca ---
# Endpoint: DELETE /recetas/{id_receta}
# Acceso exclusivo: Rol ADMINISTRADOR
@router.delete(
    "/{id_receta}",
    status_code=status.HTTP_200_OK,
    summary="CU15: Eliminar receta de la biblioteca (Solo Administrador)",
    description="Permite al administrador retirar una receta de la biblioteca."
)
def eliminar_receta(
    id_receta: int = Path(..., ge=1, description="ID de la receta"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_roles("ADMINISTRADOR"))
):
    return RecetaService.eliminar_receta(db=db, id_receta=id_receta, usuario_actual=usuario_actual)
