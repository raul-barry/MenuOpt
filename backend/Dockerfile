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

# Aplicar migraciones y luego iniciar Uvicorn en el puerto asignado por Render.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
