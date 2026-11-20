FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y habilitar salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema mínimas requeridas si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y archivos de configuración
COPY . .

# Exponer el puerto de la aplicación
EXPOSE 8000

# Aplicar migraciones; permitir una carga demo temporal antes de iniciar la API.
CMD ["sh", "-c", "alembic upgrade head && case \"${MENUOPT_SEED_BASE_MODE:-off}\" in preview) python -m app.database.seed_datos_base_demo ;; apply) python -m app.database.seed_datos_base_demo --apply --allow-production ;; off) ;; *) echo \"MENUOPT_SEED_BASE_MODE debe ser off, preview o apply\" >&2; exit 1 ;; esac && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
