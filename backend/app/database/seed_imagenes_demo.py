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

# Fotos verificadas para las recetas que aparecían con una imagen equivocada.
# Las URLs apuntan directamente al archivo publicado por cada fuente culinaria.
_FOTOS_URL_POR_PLATO = {
    "empanadas de queso": "https://img-global.cpcdn.com/recipes/1096bf5d37dde0cd/400x400cq80/photo.jpg",
    "galletas de avena y banana": "https://images.getrecipekit.com/v1619707297_Breakfast_Cookies_with_Bananas_and_Oatmeal_ovutvj.jpg?aspect_ratio=4%3A3&quality=90",
    "crema de zapallo y zanahoria": "https://assets.heartfoundation.org.nz/images/all-shared-sections/blogs/pumpkin-carrot-soup.webp?mtime=1669000867",
    "ensalada de quinua y palta": "https://www.hola.com/horizon/original_aspect_ratio/bf3f8d1f5b90-ensaladaquinoaguac.jpg",
    "tallarines con salsa de tomate": "https://d3s8tbcesxr4jm.cloudfront.net/recipe-images/v0/fusilli-pasta-with-fresh-tomato-sauce_large.jpg",
    "tofu salteado con verduras": "https://snapcalorie-webflow-website.s3.us-east-2.amazonaws.com/media/recipe_pics_v2/medium/stir-fried_tofu_with_vegetables.jpg",
    "risotto de champinones": "https://www.kabi.es/sites/default/files/2022-05/risotto-de-champinones.jpg",
}


def _url(photo_id: str) -> str:
    return f"https://images.unsplash.com/{photo_id}?w=1000&auto=format&fit=crop&q=80"


def imagen_receta(indice: int, nombre: str | None = None) -> str:
    normalizado = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode().lower()
    url = next((foto for palabra, foto in _FOTOS_URL_POR_PLATO.items() if palabra in normalizado), None)
    if url:
        return url
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
    asignadas_restaurantes = asignadas_platos = asignadas_recetas = recetas_corregidas = 0

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
        imagen_correcta = imagen_receta(indice, receta.nombre.removeprefix("DEMO | "))
        nombre_normalizado = unicodedata.normalize("NFKD", receta.nombre).encode("ascii", "ignore").decode().lower()
        necesita_correccion = any(palabra in nombre_normalizado for palabra in _FOTOS_URL_POR_PLATO)
        if necesita_correccion and receta.imagen_url != imagen_correcta:
            receta.imagen_url = imagen_correcta
            recetas_corregidas += 1
        elif not receta.imagen_url:
            receta.imagen_url = imagen_correcta
            asignadas_recetas += 1

    return {
        "restaurantes_con_imagen": asignadas_restaurantes,
        "platos_con_imagen": asignadas_platos,
        "recetas_con_imagen": asignadas_recetas,
        "recetas_corregidas": recetas_corregidas,
    }


if __name__ == "__main__":
    ejecutar_comando("imágenes de datos demostrativos", sembrar)
