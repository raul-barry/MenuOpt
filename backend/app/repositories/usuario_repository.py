from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.usuario import Usuario
from app.models.rol import Rol


class UsuarioRepository:
    """
    Repositorio para gestionar el acceso a datos y persistencia de usuarios y roles.
    No incluye lógica de negocio ni respuestas HTTP.
    """

    @staticmethod
    def buscar_por_correo(db: Session, correo: str) -> Optional[Usuario]:
        """
        Busca un usuario por su correo electrónico cargando la relación de rol.
        """
        return (
            db.query(Usuario)
            .options(joinedload(Usuario.rol))
            .filter(func.lower(Usuario.correo) == func.lower(correo))
            .first()
        )

    @staticmethod
    def buscar_por_id(db: Session, id_usuario: int) -> Optional[Usuario]:
        """
        Busca un usuario por su clave primaria cargando la relación de rol.
        """
        return (
            db.query(Usuario)
            .options(joinedload(Usuario.rol))
            .filter(Usuario.id_usuario == id_usuario)
            .first()
        )

    @staticmethod
    def buscar_rol_por_nombre(db: Session, nombre_rol: str) -> Optional[Rol]:
        """
        Busca un rol por su nombre único.
        """
        return db.query(Rol).filter(Rol.nombre == nombre_rol).first()

    @staticmethod
    def crear_usuario(db: Session, usuario: Usuario) -> Usuario:
        """
        Persiste una nueva entidad Usuario en la base de datos.
        """
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def actualizar_usuario(db: Session, usuario: Usuario) -> Usuario:
        """
        Confirma y actualiza los cambios de una entidad Usuario.
        """
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def listar_usuarios(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        estado: Optional[str] = None,
        rol: Optional[str] = None,
        busqueda: Optional[str] = None
    ) -> Tuple[int, List[Usuario]]:
        """
        Lista usuarios de forma paginada aplicando filtros opcionales de estado, rol y búsqueda.
        Retorna una tupla (total_registros, lista_usuarios).
        """
        query = db.query(Usuario).join(Usuario.rol).options(joinedload(Usuario.rol))

        if estado:
            query = query.filter(Usuario.estado == estado.upper())

        if rol:
            query = query.filter(Rol.nombre == rol.upper())

        if busqueda:
            termino = f"%{busqueda.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(Usuario.nombres).like(termino),
                    func.lower(Usuario.apellidos).like(termino),
                    func.lower(Usuario.correo).like(termino)
                )
            )

        total = query.count()
        usuarios = query.order_by(Usuario.id_usuario.asc()).offset(skip).limit(limit).all()

        return total, usuarios
