from app.routers.autenticacion import router as autenticacion_router
from app.routers.usuarios import router as usuarios_router
from app.routers.restaurantes import router as restaurantes_router
from app.routers.categorias import router as categorias_router
from app.routers.ingredientes import router as ingredientes_router
from app.routers.platos import router as platos_router
from app.routers.preferencias import router as preferencias_router
from app.routers.planificaciones import router as planificaciones_router

__all__ = [
    "autenticacion_router",
    "usuarios_router",
    "restaurantes_router",
    "categorias_router",
    "ingredientes_router",
    "platos_router",
    "preferencias_router",
    "planificaciones_router",
]
