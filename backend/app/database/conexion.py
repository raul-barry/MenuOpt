from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings

# Creación del engine de SQLAlchemy utilizando psycopg 3 (postgresql+psycopg://)
engine = create_engine(
    settings.sqlalchemy_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI para obtener una sesión de base de datos por petición.
    Garantiza el cierre adecuado de la sesión al finalizar la petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
