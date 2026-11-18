"""Smoke test del seeder sobre SQLite en memoria, sin tocar PostgreSQL ni datos locales."""
from types import SimpleNamespace
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import *  # registra todas las tablas y relaciones en Base.metadata
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.security.contrasenas import generar_hash_contrasena
from app.database.seed_bloque2 import sembrar, limpiar, _validar_destino


def test_seed_and_cleanup_bloque2_isolated():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with Session() as db:
        db.add_all([
            Rol(nombre="RESTAURANTE", activo=True),
            Rol(nombre="CLIENTE", activo=True),
            Usuario(nombres="Registro", apellidos="Ajeno", correo="keep@example.test",
                    contrasena_hash=generar_hash_contrasena("irrelevante"), estado="ACTIVO", id_rol=1),
        ])
        db.commit()

        resumen = sembrar(db, "ClaveTemporalB2!2026")
        db.commit()
        assert resumen == {
            "usuarios": 5, "restaurantes": 2, "areas": 4, "mesas": 20,
            "categorias": 4, "platos": 8, "ingredientes": 6,
            "reservas": 10, "invitados": 10, "pedidos": 12,
        }
        assert db.query(PlatoIngrediente).count() == 16
        assert db.query(Plato).filter_by(disponible=False).count() == 2
        assert all(p.total >= 0 for p in db.query(Pedido).all())

        # El segundo intento falla limpiamente en lugar de duplicar datos.
        try:
            sembrar(db, "ClaveTemporalB2!2026")
        except RuntimeError as exc:
            assert "--clean" in str(exc)
        else:
            raise AssertionError("El seeder debe impedir duplicados en una segunda ejecución")
        db.rollback()

        resultado = limpiar(db)
        db.commit()
        assert resultado["restaurantes"] == 2
        assert db.query(Usuario).filter_by(correo="keep@example.test").count() == 1
        assert db.query(Rol).count() == 2
        assert db.query(Usuario).filter(Usuario.correo.like("b2.%@example.com")).count() == 0
        assert db.query(Restaurante).count() == 0
        assert db.query(Reserva).count() == 0
        assert db.query(Pedido).count() == 0


def test_destination_guard_rejects_production_like_targets():
    _validar_destino(SimpleNamespace(url=make_url("postgresql://user@postgres/menuopt_db")), "development")
    _validar_destino(SimpleNamespace(url=make_url("postgresql://user@remote/menuopt_seed_test")), "test")
    for url, env in (
        ("postgresql://user@remote/menuopt_db", "development"),
        ("postgresql://user@postgres/menuopt_db", "test"),
    ):
        try:
            _validar_destino(SimpleNamespace(url=make_url(url)), env)
        except RuntimeError:
            pass
        else:
            raise AssertionError(f"El destino {url} debió ser rechazado para APP_ENV={env}")
