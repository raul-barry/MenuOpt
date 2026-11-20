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
    "tortilla de papa": "https://images.unsplash.com/photo-1639669794539-952631b44515?w=1000&auto=format&fit=crop&q=80",
    "pollo a la plancha con ensalada": "https://eato.health/food-images/feast/act/mixed-green-salad-with-grilled-chicken-49716475-1.webp",
    "milanesa de pollo": "https://snapcalorie-webflow-website.s3.us-east-2.amazonaws.com/media/recipe_pics_v2/medium/chicken_milanese_with_baby_spring_greens.jpg",
    "licuado de banana y avena": "https://www.novachef.es/images/recetas/batido-platano-avena/batido-avena-platano.jpg",
    "tarta de manzana": "https://www.gzrecipes.com/content/uploads/sites/7/2025/12/voorbereiding-van-de-appeltaart-7-6947f66da93cf5-06145174.jpg",
    "flan casero": "https://images.unsplash.com/photo-1702728109878-c61a98d80491?w=1000&auto=format&fit=crop&q=80",
    "brownies de cacao": "https://images.unsplash.com/photo-1604761483402-1e07d167c09b?w=1000&auto=format&fit=crop&q=80",
    "panqueques clasicos": "https://www.recipetineats.com/tachyon/2017/06/Pancakes-featured.jpg?resize=900%2C1260&zoom=0.86",
    "sopa de lentejas": "https://img.handmadev.com/photos/2024/07/latin-style-lentil-soup.jpg",
    "bowl de quinua y verduras": "https://smartyskitchen.com/cdn-cgi/image/fit%3Dcontain%2Cwidth%3D768%2Cquality%3D80%2Cformat%3Dauto/assets/images/1770086976047-81rsh4t2.webp",
    "ensalada cesar con pollo": "https://eato.health/food-images/feast/act/applebee-s-grilled-chicken-salad-27050037-1.webp",
    "arroz salteado con pollo": "https://recetarius.com/wp-content/uploads/2020/08/arroz-chino.jpg",
    "burrito de frijoles y arroz": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=1000&auto=format&fit=crop&q=80",
    "quesadillas de pollo": "https://tasteofcook.com/assets/images/1743902319629-f3lnlb9v.webp",
    "tacos de res": "https://images.squarespace-cdn.com/content/v1/5c793cc2e4afe934bb26e0c1/1610314057615-ZZHHHRU34Q9SC3S13P1D/beeftacosmaryberry.jpg",
    "pasta al pesto": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=1000&auto=format&fit=crop&q=80",
    "espagueti a la bolonesa": "https://images.unsplash.com/photo-1551892374-ecf8754cf8b0?w=1000&auto=format&fit=crop&q=80",
    "lasana a la bolonesa": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=1000&auto=format&fit=crop&q=80",
    "hamburguesa vegetariana de lentejas": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=1000&auto=format&fit=crop&q=80",
    "hamburguesa con tocino": "https://images.unsplash.com/photo-1553979459-d2229ba7433a?w=1000&auto=format&fit=crop&q=80",
    "hamburguesa clasica casera": "https://images.unsplash.com/photo-1568901346375-23c9450c58bd?w=1000&auto=format&fit=crop&q=80",
    "sonso de yuca": "https://www.lostiempos.com/sites/default/files/media_imagen/2016/7/23/sonso_de_yuca.jpg",
    "chicharron de cerdo": "https://images.unsplash.com/photo-1544025162-d76694265947?w=1000&auto=format&fit=crop&q=80",
    "saice tarijeno": "https://www.lostiempos.com/sites/default/files/styles/noticia_detalle/public/media_imagen/2018/8/6/saice_2.jpg?itok=-zw6Cd4k",
    "plato paceno": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=1000&auto=format&fit=crop&q=80",
    "charquekan": "https://upload.wikimedia.org/wikipedia/commons/9/90/Charquekan_de_Oruro.jpg",
    "sajta de pollo": "https://easyhotel.com.bo/wp-content/uploads/2024/03/Sajta-de-Pollo-scaled.jpg",
    "locro de gallina": "https://pxcdn.reduno.com.bo/reduno/082019/1565710717667.jpg",
    "keperi al horno": "https://images.unsplash.com/photo-1544025162-d76694265947?w=1000&auto=format&fit=crop&q=80",
    "pacumutu": "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?w=1000&auto=format&fit=crop&q=80",
    "picante de lengua": "https://recetasbolivia.com/wp-content/uploads/Picante-de-Lengua-Boliviana.webp",
    "picante de pollo": "https://recetasbolivia.com/wp-content/uploads/picante-de-pollo.jpg",
    "sopa de mani": "https://upload.wikimedia.org/wikipedia/commons/9/91/Sopa_de_Man%C3%AD_de_Bolivia.jpg",
    "pique macho": "https://comabien.es/images/recetas/mundo/pique-macho-banner.jpg",
    "silpancho cochabambino": "https://upload.wikimedia.org/wikipedia/commons/b/b7/Silpancho_cochabambino.jpg",
    "majadito de pollo": "https://1.bp.blogspot.com/-BAH0o3wvM0M/V0YRdCq4J5I/AAAAAAAAzes/um98-vSHvpoR68sHGXQhJUeMTkSh-R_5gCLcB/s640/IMG_6411%2B%2528640x427%2529.jpg",
    "majadito de charque": "https://cdn.tasteatlas.com/images/dishrestaurants/4c92d274fb5a427380ec331a2b3e651f.jpg",
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
