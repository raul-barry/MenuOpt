from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.restaurante import Restaurante
from app.models.ubicacion import Ubicacion


class RestauranteRepository:
    """
    Repositorio para persistencia y consultas de Restaurante y Ubicacion.
    """

    @staticmethod
    def crear_con_ubicacion(db: Session, restaurante: Restaurante, ubicacion: Ubicacion) -> Restaurante:
        """
        Crea de forma transaccional y atómica la ubicación y el restaurante asociado.
        """
        db.add(ubicacion)
        db.flush()  # Asigna id_ubicacion sin hacer commit
        restaurante.id_ubicacion = ubicacion.id_ubicacion
        db.add(restaurante)
        db.flush()

        # Automatización CU17: Autogenerar área inicial "Salón Principal"
        from app.models.area_restaurante import AreaRestaurante
        area_inicial = AreaRestaurante(
            id_restaurante=restaurante.id_restaurante,
            nombre="Salón Principal",
            descripcion="Área física principal del establecimiento",
            ancho_mapa=1200,
            alto_mapa=700,
            orden=1,
            activo=True
        )
        db.add(area_inicial)

        db.commit()
        db.refresh(restaurante)
        return restaurante

    @staticmethod
    def buscar_por_id(db: Session, id_restaurante: int) -> Optional[Restaurante]:
        """
        Busca un restaurante por su ID cargando anticipadamente su ubicación.
        """
        return (
            db.query(Restaurante)
            .options(joinedload(Restaurante.ubicacion), joinedload(Restaurante.usuario_responsable))
            .filter(Restaurante.id_restaurante == id_restaurante)
            .first()
        )

    @staticmethod
    def buscar_por_nit(db: Session, nit: str) -> Optional[Restaurante]:
        """
        Busca si ya existe un restaurante con el NIT proporcionado.
        """
        return db.query(Restaurante).filter(Restaurante.nit == nit).first()

    @staticmethod
    def listar_por_usuario(db: Session, id_usuario_responsable: int) -> List[Restaurante]:
        """
        Retorna la lista de restaurantes pertenecientes al usuario responsable.
        """
        return (
            db.query(Restaurante)
            .options(joinedload(Restaurante.ubicacion))
            .filter(Restaurante.id_usuario_responsable == id_usuario_responsable)
            .order_by(Restaurante.id_restaurante.asc())
            .all()
        )

    @staticmethod
    def listar_todos(db: Session) -> List[Restaurante]:
        """
        Retorna todos los restaurantes del sistema (para supervisión de administradores).
        """
        return (
            db.query(Restaurante)
            .options(joinedload(Restaurante.ubicacion))
            .order_by(Restaurante.id_restaurante.asc())
            .all()
        )

    @staticmethod
    def actualizar(db: Session, restaurante: Restaurante) -> Restaurante:
        """
        Confirma y actualiza las modificaciones de un restaurante y/o su ubicación.
        """
        db.commit()
        db.refresh(restaurante)
        return restaurante
