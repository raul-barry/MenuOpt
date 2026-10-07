import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación y variables de entorno usando Pydantic Settings.
    """
    # Configuración de base de datos PostgreSQL
    POSTGRES_DB: str = "menuopt_db"
    POSTGRES_USER: str = "menuopt"
    POSTGRES_PASSWORD: str = "menuopt_dev_password_2026"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    # URL explícita de base de datos (opcional)
    DATABASE_URL: Optional[str] = None

    # Configuración general de la API
    PROJECT_NAME: str = "MenuOpt API"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Configuración de Seguridad y JWT
    JWT_SECRET_KEY: str = "menuopt_jwt_secret_key_development_only_2026_super_secure_random"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Configuración de Reservas y Disponibilidad (CU20, CU21)
    MAX_EXCESO_CAPACIDAD_MESA: int = 2

    # Configuración de Asistencia con IA (CU26)
    AI_ENABLED: bool = True
    AI_PROVIDER: str = "mock"  # "mock", "gemini", "openai"
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gemini-1.5-flash"
    AI_TIMEOUT_SECONDS: int = 15

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @computed_field
    def sqlalchemy_database_url(self) -> str:
        """
        Retorna la URL formateada para SQLAlchemy con el driver psycopg 3.
        Si DATABASE_URL viene provista en el entorno se utiliza; de lo contrario se construye.
        """
        if self.DATABASE_URL and self.DATABASE_URL.strip():
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
