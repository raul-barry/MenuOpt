from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config.settings import settings
from app.database.conexion import get_db

from app.routers.autenticacion import router as autenticacion_router
from app.routers.usuarios import router as usuarios_router
from app.routers.restaurantes import router as restaurantes_router
from app.routers.categorias import router as categorias_router
from app.routers.ingredientes import router as ingredientes_router
from app.routers.platos import router as platos_router
from app.routers.preferencias import router as preferencias_router
from app.routers.planificaciones import router as planificaciones_router
from app.routers.recomendaciones import router as recomendaciones_router
from app.routers.lugares_compra import router as lugares_compra_router
from app.routers.areas import router as areas_router
from app.routers.mesas import router as mesas_router
from app.routers.reservas import router as reservas_router
from app.routers.pedidos import router as pedidos_router
from app.routers.asistente_ia import router as asistente_ia_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API backend del proyecto MenuOpt - Ingeniería de Software 1"
)

# Configuración de CORS controlada para Angular
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de enrutadores de casos de uso (Sprint 1 - Partes 2, 3, 5, 6, 7 y 9)
app.include_router(autenticacion_router)
app.include_router(usuarios_router)
app.include_router(restaurantes_router)
app.include_router(categorias_router)
app.include_router(ingredientes_router)
app.include_router(platos_router)
app.include_router(preferencias_router)
app.include_router(planificaciones_router)
app.include_router(recomendaciones_router)
app.include_router(lugares_compra_router)
app.include_router(areas_router)
app.include_router(mesas_router)
app.include_router(reservas_router)
app.include_router(pedidos_router)
app.include_router(asistente_ia_router)


@app.get("/", tags=["General"])
def read_root():
    """
    Ruta raíz para verificar la disponibilidad y estado básico del servicio FastAPI.
    """
    return {
        "proyecto": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "estado": "en_linea",
        "documentacion": "/docs"
    }


@app.get("/salud/base-datos", tags=["Infraestructura"])
def comprobar_salud_base_datos(db: Session = Depends(get_db)):
    """
    Comprobación técnica de conexión entre FastAPI y PostgreSQL mediante 'SELECT 1'.
    No contiene lógica de negocio.
    """
    try:
        resultado = db.execute(text("SELECT 1")).scalar()
        if resultado == 1:
            return {
                "estado": "ok",
                "base_datos": "conectada"
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Respuesta inesperada al verificar la base de datos."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error de conexión con la base de datos: {str(e)}"
        )
