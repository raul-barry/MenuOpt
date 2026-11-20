"""Utilidades comunes de ejecuciÃ³n segura para seeders demostrativos."""
from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.conexion import SessionLocal


def ejecutar_comando(nombre: str, sembrar: Callable[[Session], dict[str, Any]]) -> None:
    import argparse

    parser = argparse.ArgumentParser(description=f"Seeder MenuOpt: {nombre}")
    parser.add_argument("--apply", action="store_true", help="guardar los cambios en la base configurada")
    parser.add_argument("--allow-production", action="store_true", help="autorizar explícitamente escritura remota/de producción")
    args = parser.parse_args()

    ambiente = (os.getenv("APP_ENV") or os.getenv("ENVIRONMENT") or "development").lower()
    host = (make_url(settings.sqlalchemy_database_url).host or "").lower()
    remoto = host not in {"", "localhost", "127.0.0.1", "::1", "postgres", "db", "host.docker.internal"}
    requiere_confirmacion = ambiente in {"production", "prod"} or remoto
    if args.apply and requiere_confirmacion and not args.allow_production:
        raise SystemExit("Protección: agrega --allow-production para escribir en una base remota/de producción.")

    db = SessionLocal()
    try:
        resumen = sembrar(db)
        if args.apply:
            db.commit()
            prefijo = "APLICADO"
        else:
            db.rollback()
            prefijo = "VISTA PREVIA (sin cambios)"
        print(f"{prefijo} | {nombre} | " + " | ".join(f"{k}: {v}" for k, v in resumen.items()))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
