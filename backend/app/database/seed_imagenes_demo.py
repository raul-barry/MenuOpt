"""URLs de imágenes gastronómicas reutilizadas por los seeders de demostración."""
import unicodedata
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.seed_demo_util import ejecutar_comando
from app.models.plato import Plato
from app.models.receta import Receta
from app.models.restaurante import Restaurante

_FOTOS_RECETAS = (
    "photo-1563379091339-03b21ab4a4f8",
    "photo-1603064752734-4c48eff53d05",
    "photo-1513104890138-7c749659a591",
    "photo-1621996346565-e3adc644d9fa",
    "photo-1568901346375-23c9450c58bd",
    "photo-1547592166-23ac45744acd",
    "photo-1598103442097-8b74394b95c6",
    "photo-1604908176997-125f25cc6f3d",
    "photo-1555939594-58d7cb561ad1",
    "photo-1528735602780-2552fd46c7af",
    "photo-1574894709920-11b28e7367e3",
    "photo-1544025162-d76694265947",
    "photo-1512058564366-18510be2db19",
    "photo-1532550907401-a500c9a57435",
    "photo-1584308666744-24d5c474f2ae",
    "photo-1608897013039-887f21d8c804",
)

_FOTOS_TIPO = {
    "PARRILLA": ("photo-1555939594-58d7cb561ad1", "photo-1544025162-d76694265947"),
    "POLLO": ("photo-1598103442097-8b74394b95c6", "photo-1532550907401-a500c9a57435"),
    "HAMBURGUESA": ("photo-1568901346375-23c9450c58bd", "photo-1513104890138-7c749659a591"),
    "TIPICA": ("photo-1512058564366-18510be2db19", "photo-1547592166-23ac45744acd"),
}

_FOTOS_POR_PLATO = {
    "majadito": "photo-1563379091339-03b21ab4a4f8",
    "silpancho": "photo-1603064752734-4c48eff53d05",
    "pizza": "photo-1513104890138-7c749659a591",
    "spaghetti": "photo-1621996346565-e3adc644d9fa",
    "tallarin": "photo-1621996346565-e3adc644d9fa",
    "hamburguesa": "photo-1568901346375-23c9450c58bd",
    "sopa": "photo-1547592166-23ac45744acd",
    "pollo": "photo-1598103442097-8b74394b95c6",
    "picante": "photo-1604908176997-125f25cc6f3d",
    "pique macho": "photo-1555939594-58d7cb561ad1",
    "sandwich": "photo-1528735602780-2552fd46c7af",
    "lasagna": "photo-1574894709920-11b28e7367e3",
    "keperi": "photo-1544025162-d76694265947",
    "chaufa": "photo-1512058564366-18510be2db19",
    "milanesa": "photo-1532550907401-a500c9a57435",
    "tortilla": "photo-1584308666744-24d5c474f2ae",
    "cunape": "photo-1608897013039-887f21d8c804",
}


def _url(photo_id: str) -> str:
    return f"https://images.unsplash.com/{photo_id}?w=1000&auto=format&fit=crop&q=80"


def imagen_receta(indice: int, nombre: str | None = None) -> str:
    normalizado = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode().lower()
    photo_id = next((foto for palabra, foto in _FOTOS_POR_PLATO.items() if palabra in normalizado), None)
    return _url(photo_id or _FOTOS_RECETAS[indice % len(_FOTOS_RECETAS)])


def imagen_por_tipo(tipo: str, indice: int = 0) -> str:
    fotos = _FOTOS_TIPO.get(tipo, _FOTOS_RECETAS[:2])
    return _url(fotos[indice % len(fotos)])


def sembrar(db: Session) -> dict[str, int]:
    restaurantes = db.scalars(
        select(Restaurante).where(Restaurante.nombre.like("DEMO | %")).order_by(Restaurante.id_restaurante)
    ).all()
    recetas = db.scalars(
        select(Receta).where(Receta.nombre.like("DEMO | %")).order_by(Receta.id_receta)
    ).all()
    asignadas_restaurantes = asignadas_platos = asignadas_recetas = 0

    for restaurante in restaurantes:
        tipo = "TIPICA"
        if restaurante.platos and restaurante.platos[0].categoria:
            nombre_categoria = restaurante.platos[0].categoria.nombre.lower()
            if "parrilla" in nombre_categoria:
                tipo = "PARRILLA"
            elif "pollo" in nombre_categoria:
                tipo = "POLLO"
            elif "hamburgues" in nombre_categoria:
                tipo = "HAMBURGUESA"

        if not restaurante.imagen_url:
            restaurante.imagen_url = imagen_por_tipo(tipo)
            asignadas_restaurantes += 1
        for indice, plato in enumerate(sorted(restaurante.platos, key=lambda item: item.id_plato)):
            if not plato.imagen_url:
                plato.imagen_url = imagen_por_tipo(tipo, indice)
                asignadas_platos += 1

    for indice, receta in enumerate(recetas):
        if not receta.imagen_url:
            receta.imagen_url = imagen_receta(indice, receta.nombre.removeprefix("DEMO | "))
            asignadas_recetas += 1

    return {
        "restaurantes_con_imagen": asignadas_restaurantes,
        "platos_con_imagen": asignadas_platos,
        "recetas_con_imagen": asignadas_recetas,
    }


if __name__ == "__main__":
    ejecutar_comando("imágenes de datos demostrativos", sembrar)
