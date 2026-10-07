from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Clase base declarativa para todos los modelos ORM de SQLAlchemy en MenuOpt.
    Nota: Las tablas son creadas y gestionadas exclusivamente mediante migraciones con Alembic.
    No utilizar Base.metadata.create_all().
    """
    pass
