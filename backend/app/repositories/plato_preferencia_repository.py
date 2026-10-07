# CASO DE USO: CU08 - Gestionar preferencias en platos
from typing import List
from sqlalchemy.orm import Session
from app.models.plato_preferencia import PlatoPreferencia
from app.models.preferencia import Preferencia


class PlatoPreferenciaRepository:
    """
    Repositorio para persistencia y consultas de la relación PlatoPreferencia.
    """

    @staticmethod
    def listar_preferencias_de_plato(db: Session, id_plato: int) -> List[Preferencia]:
        return (
            db.query(Preferencia)
            .join(PlatoPreferencia, PlatoPreferencia.id_preferencia == Preferencia.id_preferencia)
            .filter(PlatoPreferencia.id_plato == id_plato)
            .order_by(Preferencia.nombre.asc())
            .all()
        )

    @staticmethod
    def actualizar_preferencias_de_plato(
        db: Session,
        id_plato: int,
        ids_preferencias: List[int]
    ) -> List[Preferencia]:
        """
        Sincroniza transaccionalmente las preferencias de un plato.
        """
        existentes = (
            db.query(PlatoPreferencia)
            .filter(PlatoPreferencia.id_plato == id_plato)
            .all()
        )
        mapa_existentes = {pp.id_preferencia: pp for pp in existentes}
        ids_set = set(ids_preferencias)

        # Eliminar las que ya no están
        for id_pref, obj_pp in mapa_existentes.items():
            if id_pref not in ids_set:
                db.delete(obj_pp)

        # Insertar las nuevas
        for id_pref in ids_set:
            if id_pref not in mapa_existentes:
                db.add(PlatoPreferencia(
                    id_plato=id_plato,
                    id_preferencia=id_pref
                ))

        db.commit()
        return PlatoPreferenciaRepository.listar_preferencias_de_plato(db, id_plato)
