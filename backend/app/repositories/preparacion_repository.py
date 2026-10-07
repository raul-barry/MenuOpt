# CASO DE USO: CU15 - Consultar ingredientes para preparación propia
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.models.preparacion_propia import PreparacionPropia
from app.models.preparacion_ingrediente import PreparacionIngrediente
from app.models.lugar_compra import LugarCompra


class PreparacionRepository:
    """
    Repositorio para persistencia y consultas de preparaciones gastronómicas propias.
    """

    @staticmethod
    def buscar_por_recomendacion(
        db: Session,
        id_recomendacion: int
    ) -> Optional[PreparacionPropia]:
        """
        Recupera la preparación propia asociada a una recomendación específica,
        cargando sus ingredientes, nombres y establecimientos de compra asociados.
        """
        return (
            db.query(PreparacionPropia)
            .options(
                joinedload(PreparacionPropia.ingredientes).joinedload(PreparacionIngrediente.ingrediente),
                joinedload(PreparacionPropia.ingredientes).joinedload(PreparacionIngrediente.lugar_compra).joinedload(LugarCompra.ubicacion),
                joinedload(PreparacionPropia.recomendacion)
            )
            .filter(PreparacionPropia.id_recomendacion == id_recomendacion)
            .first()
        )

    @staticmethod
    def buscar_por_id(
        db: Session,
        id_preparacion_propia: int
    ) -> Optional[PreparacionPropia]:
        return (
            db.query(PreparacionPropia)
            .options(
                joinedload(PreparacionPropia.ingredientes).joinedload(PreparacionIngrediente.ingrediente),
                joinedload(PreparacionPropia.ingredientes).joinedload(PreparacionIngrediente.lugar_compra).joinedload(LugarCompra.ubicacion),
                joinedload(PreparacionPropia.recomendacion)
            )
            .filter(PreparacionPropia.id_preparacion_propia == id_preparacion_propia)
            .first()
        )

    @staticmethod
    def guardar_preparacion(
        db: Session,
        preparacion: PreparacionPropia
    ) -> PreparacionPropia:
        db.add(preparacion)
        db.commit()
        db.refresh(preparacion)
        return preparacion
