# CASO DE USO: CU16 - Consultar lugares de compra
from typing import Optional, List, Dict
from sqlalchemy.orm import Session, joinedload
from app.models.ingrediente_lugar_compra import IngredienteLugarCompra
from app.models.lugar_compra import LugarCompra
from app.models.ingrediente import Ingrediente


class IngredienteLugarCompraRepository:
    """
    Repositorio para persistencia y consultas de la relación IngredienteLugarCompra.
    """

    @staticmethod
    def buscar_relacion(
        db: Session,
        id_ingrediente: int,
        id_lugar_compra: int
    ) -> Optional[IngredienteLugarCompra]:
        return (
            db.query(IngredienteLugarCompra)
            .options(
                joinedload(IngredienteLugarCompra.ingrediente),
                joinedload(IngredienteLugarCompra.lugar_compra).joinedload(LugarCompra.ubicacion)
            )
            .filter(
                IngredienteLugarCompra.id_ingrediente == id_ingrediente,
                IngredienteLugarCompra.id_lugar_compra == id_lugar_compra
            )
            .first()
        )

    @staticmethod
    def asociar(
        db: Session,
        relacion: IngredienteLugarCompra
    ) -> IngredienteLugarCompra:
        db.add(relacion)
        db.commit()
        db.refresh(relacion)
        return relacion

    @staticmethod
    def actualizar(
        db: Session,
        relacion: IngredienteLugarCompra
    ) -> IngredienteLugarCompra:
        db.commit()
        db.refresh(relacion)
        return relacion

    @staticmethod
    def listar_ingredientes_de_lugar(
        db: Session,
        id_lugar_compra: int
    ) -> List[IngredienteLugarCompra]:
        return (
            db.query(IngredienteLugarCompra)
            .options(
                joinedload(IngredienteLugarCompra.ingrediente),
                joinedload(IngredienteLugarCompra.lugar_compra)
            )
            .filter(IngredienteLugarCompra.id_lugar_compra == id_lugar_compra)
            .all()
        )

    @staticmethod
    def listar_lugares_activos_para_ingrediente(
        db: Session,
        id_ingrediente: int
    ) -> List[IngredienteLugarCompra]:
        """
        Retorna los lugares activos donde se comercializa un ingrediente,
        ordenados por precio ascendente.
        """
        return (
            db.query(IngredienteLugarCompra)
            .join(LugarCompra, IngredienteLugarCompra.id_lugar_compra == LugarCompra.id_lugar_compra)
            .options(
                joinedload(IngredienteLugarCompra.lugar_compra).joinedload(LugarCompra.ubicacion),
                joinedload(IngredienteLugarCompra.ingrediente)
            )
            .filter(
                IngredienteLugarCompra.id_ingrediente == id_ingrediente,
                LugarCompra.estado == "ACTIVO"
            )
            .order_by(IngredienteLugarCompra.precio.asc())
            .all()
        )

    @staticmethod
    def buscar_mejores_precios(
        db: Session,
        ids_ingredientes: List[int]
    ) -> Dict[int, IngredienteLugarCompra]:
        """
        Consulta de alto rendimiento para evitar N+1:
        Retorna un diccionario {id_ingrediente: IngredienteLugarCompra} con la opción
        activa, disponible y de menor costo registrado para cada ingrediente solicitado.
        """
        if not ids_ingredientes:
            return {}

        relaciones = (
            db.query(IngredienteLugarCompra)
            .join(LugarCompra, IngredienteLugarCompra.id_lugar_compra == LugarCompra.id_lugar_compra)
            .options(
                joinedload(IngredienteLugarCompra.lugar_compra).joinedload(LugarCompra.ubicacion),
                joinedload(IngredienteLugarCompra.ingrediente)
            )
            .filter(
                IngredienteLugarCompra.id_ingrediente.in_(ids_ingredientes),
                IngredienteLugarCompra.disponible.is_(True),
                LugarCompra.estado == "ACTIVO"
            )
            .order_by(IngredienteLugarCompra.precio.asc())
            .all()
        )

        mejores: Dict[int, IngredienteLugarCompra] = {}
        for r in relaciones:
            if r.id_ingrediente not in mejores:
                mejores[r.id_ingrediente] = r

        return mejores
