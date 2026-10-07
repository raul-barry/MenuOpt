from typing import TYPE_CHECKING, Any
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.models.restaurante import Restaurante
from app.models.plato import Plato

if TYPE_CHECKING:
    from app.models.planificacion import Planificacion


def verificar_propiedad_restaurante(restaurante: Restaurante, usuario_actual: Usuario) -> None:
    """
    Verifica que el restaurante pertenezca al usuario autenticado o que el usuario sea ADMINISTRADOR.
    Si no cumple, rechaza con HTTP 403 Forbidden.
    """
    rol_nombre = usuario_actual.rol.nombre if usuario_actual.rol else None

    if rol_nombre == "ADMINISTRADOR":
        return

    if restaurante.id_usuario_responsable != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos sobre este restaurante. El recurso pertenece a otro responsable."
        )


def verificar_propiedad_plato(plato: Plato, usuario_actual: Usuario) -> None:
    """
    Verifica que el plato pertenezca a un restaurante a cargo del usuario autenticado o que sea ADMINISTRADOR.
    Si no cumple, rechaza con HTTP 403 Forbidden.
    """
    rol_nombre = usuario_actual.rol.nombre if usuario_actual.rol else None

    if rol_nombre == "ADMINISTRADOR":
        return

    if not plato.restaurante or plato.restaurante.id_usuario_responsable != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos sobre este plato. Pertenece a un restaurante de otro responsable."
        )


def verificar_propiedad_planificacion(planificacion: "Planificacion", usuario_actual: Usuario) -> None:
    """
    Verifica que la planificación pertenezca al usuario autenticado o que el usuario sea ADMINISTRADOR.
    Si no cumple, rechaza con HTTP 403 Forbidden.
    """
    rol_nombre = usuario_actual.rol.nombre if usuario_actual.rol else None

    if rol_nombre == "ADMINISTRADOR":
        return

    if planificacion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos sobre esta planificación. Pertenece a otro usuario."
        )


def verificar_propiedad_area(area: Any, usuario_actual: Usuario) -> None:
    """
    Verifica que el área pertenezca a un restaurante a cargo del usuario autenticado o que sea ADMINISTRADOR.
    Si no cumple, rechaza con HTTP 403 Forbidden.
    """
    rol_nombre = usuario_actual.rol.nombre if usuario_actual.rol else None

    if rol_nombre == "ADMINISTRADOR":
        return

    if not area.restaurante or area.restaurante.id_usuario_responsable != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos sobre esta área. Pertenece a un restaurante de otro responsable."
        )
