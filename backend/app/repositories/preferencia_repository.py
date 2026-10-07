from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.preferencia import Preferencia
from app.models.usuario_preferencia import UsuarioPreferencia


class PreferenciaRepository:
    """
    Repositorio para persistencia y consultas de Preferencia y UsuarioPreferencia.
    """

    # =========================================================================
    # CASO DE USO: CU12 - DEFINIR PREFERENCIAS
    # =========================================================================

    @staticmethod
    def buscar_por_id(db: Session, id_preferencia: int) -> Optional[Preferencia]:
        return db.query(Preferencia).filter(Preferencia.id_preferencia == id_preferencia).first()

    @staticmethod
    def buscar_por_nombre(db: Session, nombre: str) -> Optional[Preferencia]:
        return (
            db.query(Preferencia)
            .filter(func.lower(Preferencia.nombre) == func.lower(nombre.strip()))
            .first()
        )

    @staticmethod
    def listar_activas(db: Session) -> List[Preferencia]:
        return (
            db.query(Preferencia)
            .filter(Preferencia.activo.is_(True))
            .order_by(Preferencia.id_preferencia.asc())
            .all()
        )

    @staticmethod
    def listar_todas(db: Session) -> List[Preferencia]:
        return db.query(Preferencia).order_by(Preferencia.id_preferencia.asc()).all()

    @staticmethod
    def crear(db: Session, preferencia: Preferencia) -> Preferencia:
        db.add(preferencia)
        db.commit()
        db.refresh(preferencia)
        return preferencia

    @staticmethod
    def actualizar(db: Session, preferencia: Preferencia) -> Preferencia:
        db.commit()
        db.refresh(preferencia)
        return preferencia

    @staticmethod
    def buscar_activas_por_ids(db: Session, ids: List[int]) -> List[Preferencia]:
        if not ids:
            return []
        return (
            db.query(Preferencia)
            .filter(Preferencia.id_preferencia.in_(ids), Preferencia.activo.is_(True))
            .all()
        )

    @staticmethod
    def obtener_preferencias_usuario(db: Session, id_usuario: int) -> List[Preferencia]:
        return (
            db.query(Preferencia)
            .join(UsuarioPreferencia, UsuarioPreferencia.id_preferencia == Preferencia.id_preferencia)
            .filter(UsuarioPreferencia.id_usuario == id_usuario)
            .order_by(Preferencia.id_preferencia.asc())
            .all()
        )

    @staticmethod
    def sincronizar_preferencias_usuario(
        db: Session,
        id_usuario: int,
        ids_preferencias: List[int]
    ) -> List[Preferencia]:
        # Eliminar las que ya no están
        existentes = (
            db.query(UsuarioPreferencia)
            .filter(UsuarioPreferencia.id_usuario == id_usuario)
            .all()
        )
        mapa_existentes = {up.id_preferencia: up for up in existentes}

        ids_set = set(ids_preferencias)

        for id_pref, obj_up in mapa_existentes.items():
            if id_pref not in ids_set:
                db.delete(obj_up)

        for id_pref in ids_set:
            if id_pref not in mapa_existentes:
                db.add(UsuarioPreferencia(id_usuario=id_usuario, id_preferencia=id_pref))

        db.commit()

        return PreferenciaRepository.obtener_preferencias_usuario(db, id_usuario)
