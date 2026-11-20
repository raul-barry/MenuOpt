"""Biblioteca de 40 recetas demostrativas con ingredientes del catálogo."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.seed_demo_util import ejecutar_comando
from app.models.ingrediente import Ingrediente
from app.models.receta import Receta, RecetaIngrediente


def _r(nombre, tipo, origen, minutos, dificultad, descripcion, pasos, ingredientes):
    return {
        "nombre": f"DEMO | {nombre}", "tipo": tipo, "origen": origen,
        "minutos": minutos, "dificultad": dificultad, "descripcion": descripcion,
        "pasos": pasos, "ingredientes": ingredientes,
    }


# ingrediente: cantidad por porción, unidad del catálogo. Los nombres se
# resuelven en la base; no se usan IDs fijos.
RECETAS = [
    _r("Majadito de charque", "ALMUERZO", "Bolivia · Santa Cruz", 55, "MEDIA", "Arroz majado con charque, plátano frito y huevo.", "Desalar y desmenuzar el charque. Sofreír cebolla y tomate, añadir arroz y caldo; cocinar hasta que quede húmedo y suave. Servir con plátano y huevo fritos.", [("Charque", "0.12", "kg"), ("Arroz grano largo", "0.14", "kg"), ("Plátano de cocinar", "0.15", "kg"), ("Huevo", "0.08", "docena"), ("Tomate", "0.05", "kg"), ("Cebolla", "0.04", "kg"), ("Aceite vegetal", "0.02", "litro")]),
    _r("Majadito de pollo", "ALMUERZO", "Bolivia · Santa Cruz", 50, "MEDIA", "Arroz dorado con pollo desmenuzado, plátano y huevo.", "Dorar el pollo y reservar. Sofreír cebolla, incorporar arroz y caldo, luego el pollo; cocinar hasta que el arroz esté tierno. Acompañar con plátano y huevo fritos.", [("Pechuga de pollo", "0.18", "kg"), ("Arroz grano largo", "0.14", "kg"), ("Plátano de cocinar", "0.15", "kg"), ("Huevo", "0.08", "docena"), ("Cebolla", "0.04", "kg"), ("Tomate", "0.04", "kg")]),
    _r("Silpancho cochabambino", "ALMUERZO", "Bolivia · Cochabamba", 50, "MEDIA", "Carne apanada sobre arroz y papa, con huevo y sarza fresca.", "Aplanar y sazonar la carne, pasar por pan rallado y dorar. Servir sobre arroz y papa cocida; completar con huevo frito, tomate y cebolla picados.", [("Carne de res para guiso", "0.18", "kg"), ("Pan rallado", "0.05", "kg"), ("Huevo", "0.16", "docena"), ("Arroz grano largo", "0.12", "kg"), ("Papa", "0.20", "kg"), ("Tomate", "0.05", "kg"), ("Cebolla", "0.04", "kg")]),
    _r("Pique macho", "CENA", "Bolivia · Cochabamba", 45, "MEDIA", "Fuente para compartir con res, salchicha, papas, tomate, cebolla y locoto.", "Freír las papas hasta dorar. Saltear la carne en trozos y calentar la salchicha. Montar en una fuente y cubrir con tomate, cebolla y locoto en rodajas.", [("Carne de res para guiso", "0.22", "kg"), ("Salchicha", "0.10", "kg"), ("Papa", "0.30", "kg"), ("Tomate", "0.08", "kg"), ("Cebolla", "0.05", "kg"), ("Locoto", "0.02", "kg"), ("Aceite vegetal", "0.03", "litro")]),
    _r("Sopa de maní", "ALMUERZO", "Bolivia · Valles", 70, "MEDIA", "Sopa espesa de maní con res, papa, fideo y verduras.", "Tostar y moler el maní. Cocer la carne con cebolla y zanahoria; agregar maní, papa y fideo. Hervir suavemente hasta espesar y servir con perejil.", [("Carne de res para guiso", "0.12", "kg"), ("Maní", "0.04", "kg"), ("Papa", "0.12", "kg"), ("Fideo", "0.04", "kg"), ("Zanahoria", "0.04", "kg"), ("Cebolla", "0.03", "kg"), ("Perejil", "0.10", "atado")]),
    _r("Picante de pollo", "ALMUERZO", "Bolivia · Altiplano", 65, "MEDIA", "Pollo guisado en ají amarillo con papa, chuño y arroz.", "Hidratar y licuar el ají; sofreírlo con cebolla. Añadir pollo y caldo, cocer hasta ablandar y servir con papa, chuño y arroz.", [("Pechuga de pollo", "0.25", "kg"), ("Ají amarillo", "0.04", "kg"), ("Papa", "0.18", "kg"), ("Chuño", "0.08", "kg"), ("Arroz grano largo", "0.10", "kg"), ("Cebolla", "0.05", "kg")]),
    _r("Picante de lengua", "ALMUERZO", "Bolivia · Altiplano", 120, "DIFICIL", "Lengua de res cocida lentamente en salsa de ají colorado.", "Cocer la lengua hasta que esté tierna, pelar y cortar. Preparar una salsa de cebolla y ají colorado; terminar la lengua en la salsa y servir con papa y tunta.", [("Lengua de res", "0.22", "kg"), ("Ají colorado", "0.04", "kg"), ("Papa", "0.18", "kg"), ("Tunta", "0.08", "kg"), ("Cebolla", "0.05", "kg"), ("Ajo", "0.01", "kg")]),
    _r("Sajta de pollo", "ALMUERZO", "Bolivia · La Paz", 75, "MEDIA", "Pollo en salsa de maní y ají con papa y chuño.", "Cocer el pollo con cebolla. Preparar una salsa licuada de maní y ají amarillo; incorporar el pollo y cocinar a fuego bajo. Servir con papa y chuño cocidos.", [("Pechuga de pollo", "0.24", "kg"), ("Maní", "0.04", "kg"), ("Ají amarillo", "0.03", "kg"), ("Papa", "0.18", "kg"), ("Chuño", "0.08", "kg"), ("Cebolla", "0.04", "kg")]),
    _r("Charquekan", "ALMUERZO", "Bolivia · Oruro", 55, "MEDIA", "Charque crocante con mote, papa, huevo y queso.", "Hervir y deshilachar el charque; dorarlo en sartén. Cocer el mote y las papas, freír el huevo y servir con queso criollo.", [("Charque", "0.14", "kg"), ("Maíz mote", "0.14", "kg"), ("Papa", "0.20", "kg"), ("Huevo", "0.08", "docena"), ("Queso criollo", "0.05", "kg")]),
    _r("Plato paceño", "ALMUERZO", "Bolivia · La Paz", 40, "FACIL", "Choclo, papa, haba y queso criollo con llajua.", "Cocer por separado el choclo, las habas y las papas. Dorar el queso en plancha y servir todo caliente con llajua de tomate y locoto.", [("Choclo", "1", "unidad"), ("Papa", "0.22", "kg"), ("Haba", "0.08", "kg"), ("Queso criollo", "0.08", "kg"), ("Tomate", "0.04", "kg"), ("Locoto", "0.01", "kg")]),
    _r("Saice tarijeño", "ALMUERZO", "Bolivia · Tarija", 60, "MEDIA", "Guiso de carne molida con papa, arveja y ají colorado.", "Sofreír cebolla, tomate y ají. Añadir la carne molida, luego papa y arveja; cocinar tapado hasta que todo esté tierno. Acompañar con arroz.", [("Carne molida de res", "0.16", "kg"), ("Papa", "0.16", "kg"), ("Arveja", "0.05", "kg"), ("Ají colorado", "0.02", "kg"), ("Tomate", "0.05", "kg"), ("Cebolla", "0.04", "kg"), ("Arroz grano largo", "0.10", "kg")]),
    _r("Chicharrón de cerdo", "ALMUERZO", "Bolivia · Cochabamba", 95, "DIFICIL", "Cerdo dorado con mote y papa, terminado con hierbas y limón.", "Cocer el cerdo con agua, sal y comino hasta que se evapore el líquido; dejar que se dore en su grasa. Servir con mote, papa y limón.", [("Carne de cerdo", "0.25", "kg"), ("Maíz mote", "0.12", "kg"), ("Papa", "0.18", "kg"), ("Limón", "0.03", "kg"), ("Comino", "0.002", "kg")]),
    _r("Locro de gallina", "ALMUERZO", "Bolivia · Santa Cruz", 80, "MEDIA", "Caldo de gallina con arroz, yuca, plátano y verduras.", "Cocer la gallina con cebolla y ajo hasta ablandar. Añadir arroz y verduras; incorporar yuca y plátano al final para que conserven su forma.", [("Pollo entero", "0.30", "unidad"), ("Arroz grano largo", "0.08", "kg"), ("Yuca", "0.12", "kg"), ("Plátano de cocinar", "0.08", "kg"), ("Cebolla", "0.04", "kg"), ("Zanahoria", "0.04", "kg"), ("Ajo", "0.01", "kg")]),
    _r("Pacumutu", "ALMUERZO", "Bolivia · Santa Cruz", 40, "FACIL", "Brochetas de res con pimiento y cebolla, asadas a la parrilla.", "Cortar la carne y las verduras en cubos, sazonar y ensartar alternando. Asar girando las brochetas hasta el punto deseado; acompañar con yuca.", [("Carne de res para guiso", "0.22", "kg"), ("Pimiento morrón", "0.06", "kg"), ("Cebolla", "0.05", "kg"), ("Yuca", "0.18", "kg")]),
    _r("Keperí al horno", "ALMUERZO", "Bolivia · Santa Cruz", 150, "DIFICIL", "Carne de res marinada y cocida lentamente hasta quedar suave.", "Marinar la carne con ajo, limón, comino y sal. Hornear tapada a temperatura media hasta ablandar; destapar al final para dorar y servir con arroz.", [("Costilla de res", "0.28", "kg"), ("Ajo", "0.01", "kg"), ("Limón", "0.03", "kg"), ("Comino", "0.002", "kg"), ("Arroz grano largo", "0.10", "kg")]),
    _r("Sonso de yuca", "MERIENDA", "Bolivia · Oriente", 45, "FACIL", "Yuca majada con queso criollo, asada hasta dorar.", "Cocer la yuca y retirarle las fibras. Majar con mantequilla y queso, formar porciones y asarlas en brochetas o sartén hasta dorar.", [("Yuca", "0.24", "kg"), ("Queso criollo", "0.08", "kg"), ("Mantequilla", "0.02", "kg"), ("Leche", "0.02", "litro")]),
    _r("Hamburguesa clásica casera", "CENA", "Internacional", 30, "FACIL", "Medallón de res con queso, vegetales y papas doradas.", "Formar y sellar el medallón. Fundir el queso sobre la carne, armar en el pan con tomate y lechuga; servir con papas.", [("Carne molida de res", "0.16", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Queso mozzarella", "0.03", "kg"), ("Tomate", "0.04", "kg"), ("Lechuga", "0.10", "unidad"), ("Papa", "0.18", "kg")]),
    _r("Hamburguesa con tocino", "CENA", "Internacional", 35, "FACIL", "Hamburguesa doble con tocino crocante, queso y cebolla.", "Dorar el tocino y cocinar los medallones a la plancha. Fundir el queso y montar en el pan con cebolla salteada.", [("Carne molida de res", "0.22", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Tocino", "0.05", "kg"), ("Queso mozzarella", "0.04", "kg"), ("Cebolla", "0.04", "kg")]),
    _r("Hamburguesa vegetariana de lentejas", "CENA", "Internacional · Vegetariana", 40, "MEDIA", "Medallón de lentejas con vegetales y salsa de mostaza.", "Cocer las lentejas y aplastarlas con huevo y pan rallado. Formar medallones, dorar por ambos lados y servir en pan con vegetales.", [("Lenteja", "0.12", "kg"), ("Huevo", "0.04", "docena"), ("Pan rallado", "0.03", "kg"), ("Pan de hamburguesa", "1", "unidad"), ("Tomate", "0.04", "kg"), ("Lechuga", "0.10", "unidad"), ("Mostaza", "0.01", "kg")]),
    _r("Pizza margarita", "CENA", "Italia", 45, "MEDIA", "Pizza de tomate, mozzarella, albahaca y orégano.", "Extender la masa, cubrir con salsa de tomate y mozzarella. Hornear a temperatura alta hasta dorar; terminar con albahaca y orégano.", [("Harina de trigo", "0.18", "kg"), ("Salsa de tomate", "0.08", "kg"), ("Queso mozzarella", "0.12", "kg"), ("Albahaca", "0.05", "atado"), ("Orégano seco", "0.002", "kg")]),
    _r("Pizza de pepperoni", "CENA", "Italia · Estados Unidos", 45, "MEDIA", "Pizza horneada con mozzarella, pepperoni y orégano.", "Estirar la masa y añadir salsa y queso. Distribuir pepperoni, hornear hasta que la base esté crujiente y el queso burbujee.", [("Harina de trigo", "0.18", "kg"), ("Salsa de tomate", "0.08", "kg"), ("Queso mozzarella", "0.12", "kg"), ("Pepperoni", "0.06", "kg"), ("Orégano seco", "0.002", "kg")]),
    _r("Pizza vegetariana", "CENA", "Internacional · Vegetariana", 45, "MEDIA", "Pizza con berenjena, champiñones, pimiento y mozzarella.", "Asar ligeramente la berenjena y saltear los champiñones. Cubrir la masa con salsa, vegetales y queso; hornear hasta dorar.", [("Harina de trigo", "0.18", "kg"), ("Salsa de tomate", "0.08", "kg"), ("Queso mozzarella", "0.10", "kg"), ("Berenjena", "0.05", "kg"), ("Champiñón", "0.05", "kg"), ("Pimiento morrón", "0.04", "kg")]),
    _r("Lasaña a la boloñesa", "ALMUERZO", "Italia", 75, "MEDIA", "Capas de pasta, salsa de carne, tomate y queso gratinado.", "Preparar la salsa con carne molida, tomate y cebolla. Alternar salsa y láminas de pasta en una fuente, cubrir con queso y hornear hasta gratinar.", [("Tallarín para lasaña", "0.12", "kg"), ("Carne molida de res", "0.14", "kg"), ("Tomate", "0.10", "kg"), ("Cebolla", "0.04", "kg"), ("Queso mozzarella", "0.08", "kg"), ("Leche", "0.05", "litro")]),
    _r("Espagueti a la boloñesa", "ALMUERZO", "Italia", 40, "FACIL", "Pasta con salsa casera de carne, tomate y hierbas.", "Cocer la pasta al dente. Sofreír cebolla, añadir carne y tomate; cocinar la salsa y mezclar con la pasta.", [("Fideo", "0.12", "kg"), ("Carne molida de res", "0.12", "kg"), ("Tomate", "0.12", "kg"), ("Cebolla", "0.04", "kg"), ("Ajo", "0.01", "kg"), ("Orégano seco", "0.002", "kg")]),
    _r("Pasta al pesto", "ALMUERZO", "Italia", 30, "FACIL", "Pasta mezclada con pesto de albahaca, ajo y queso.", "Cocer la pasta. Procesar albahaca, ajo, aceite y queso hasta formar una salsa; mezclar con la pasta caliente y servir.", [("Fideo", "0.12", "kg"), ("Albahaca", "0.10", "atado"), ("Ajo", "0.005", "kg"), ("Aceite vegetal", "0.02", "litro"), ("Queso parmesano", "0.03", "kg")]),
    _r("Tacos de res", "CENA", "México", 35, "FACIL", "Tortillas rellenas de res salteada, cebolla y tomate.", "Saltear la carne en tiras a fuego alto. Calentar las tortillas y rellenar con carne, tomate, cebolla y unas gotas de limón.", [("Carne de res para guiso", "0.14", "kg"), ("Tortilla de trigo", "2", "unidad"), ("Tomate", "0.05", "kg"), ("Cebolla", "0.04", "kg"), ("Limón", "0.02", "kg")]),
    _r("Quesadillas de pollo", "CENA", "México", 30, "FACIL", "Tortillas doradas con pollo salteado y queso fundido.", "Cocinar el pollo con cebolla y pimiento. Rellenar las tortillas con pollo y queso, doblar y dorar por ambos lados.", [("Pechuga de pollo", "0.12", "kg"), ("Tortilla de trigo", "2", "unidad"), ("Queso mozzarella", "0.07", "kg"), ("Cebolla", "0.03", "kg"), ("Pimiento morrón", "0.03", "kg")]),
    _r("Burrito de frijoles y arroz", "ALMUERZO", "México", 35, "FACIL", "Tortilla grande rellena de frijol, arroz, tomate y queso.", "Cocer el arroz y calentar los frijoles. Colocar ambos sobre la tortilla con tomate y queso; doblar los extremos y enrollar.", [("Tortilla de trigo", "1", "unidad"), ("Frijol negro", "0.10", "kg"), ("Arroz grano largo", "0.08", "kg"), ("Tomate", "0.05", "kg"), ("Queso criollo", "0.04", "kg")]),
    _r("Arroz salteado con pollo", "ALMUERZO", "Asia · Adaptación casera", 35, "FACIL", "Arroz salteado con pollo, huevo, cebolla y salsa de soya.", "Saltear el pollo y reservar. Cocinar el huevo revuelto, añadir arroz cocido, cebolla y soya; reincorporar el pollo y saltear a fuego alto.", [("Arroz grano largo", "0.14", "kg"), ("Pechuga de pollo", "0.12", "kg"), ("Huevo", "0.08", "docena"), ("Cebolla", "0.03", "kg"), ("Salsa de soya", "0.02", "litro"), ("Zanahoria", "0.04", "kg")]),
    _r("Ensalada César con pollo", "ALMUERZO", "Estados Unidos", 25, "FACIL", "Lechuga fresca con pollo a la plancha, limón y aderezo cremoso.", "Sellar el pollo y cortarlo en tiras. Mezclar lechuga con aderezo de mayonesa y limón; añadir pollo y queso rallado.", [("Pechuga de pollo", "0.14", "kg"), ("Lechuga", "0.25", "unidad"), ("Mayonesa", "0.025", "kg"), ("Limón", "0.02", "kg"), ("Queso parmesano", "0.02", "kg")]),
    _r("Bowl de quinua y verduras", "ALMUERZO", "Bolivia · Vegetariana", 35, "FACIL", "Quinua con verduras salteadas, palta y aderezo de limón.", "Lavar y cocer la quinua. Saltear pimiento y champiñón; servir sobre la quinua con palta y aderezo de limón.", [("Quinua", "0.10", "kg"), ("Pimiento morrón", "0.05", "kg"), ("Champiñón", "0.05", "kg"), ("Palta", "0.05", "kg"), ("Limón", "0.02", "kg")]),
    _r("Sopa de lentejas", "ALMUERZO", "Internacional · Vegetariana", 55, "FACIL", "Lentejas guisadas con papa, zanahoria, tomate y comino.", "Sofreír cebolla, tomate y comino. Añadir lentejas, agua, papa y zanahoria; cocinar hasta que las lentejas estén tiernas.", [("Lenteja", "0.12", "kg"), ("Papa", "0.10", "kg"), ("Zanahoria", "0.05", "kg"), ("Tomate", "0.05", "kg"), ("Cebolla", "0.04", "kg"), ("Comino", "0.002", "kg")]),
    _r("Panqueques clásicos", "DESAYUNO", "Internacional", 25, "FACIL", "Panqueques suaves de leche y huevo, servidos con miel.", "Batir harina, leche, huevo y azúcar hasta integrar. Verter porciones en una sartén engrasada; voltear al formar burbujas y servir con miel.", [("Harina de trigo", "0.08", "kg"), ("Leche", "0.10", "litro"), ("Huevo", "0.08", "docena"), ("Azúcar", "0.02", "kg"), ("Mantequilla", "0.01", "kg"), ("Miel", "0.02", "kg")]),
    _r("Brownies de cacao", "POSTRE", "Estados Unidos", 45, "MEDIA", "Cuadrados húmedos de cacao, mantequilla, huevo y azúcar.", "Fundir mantequilla y mezclar con cacao y azúcar. Incorporar huevo y harina; hornear hasta que el centro quede ligeramente húmedo.", [("Cacao en polvo", "0.025", "kg"), ("Mantequilla", "0.04", "kg"), ("Azúcar", "0.06", "kg"), ("Huevo", "0.08", "docena"), ("Harina de trigo", "0.05", "kg")]),
    _r("Flan casero", "POSTRE", "Internacional", 60, "MEDIA", "Flan horneado de leche, huevo y caramelo.", "Preparar caramelo con azúcar y cubrir el molde. Batir leche y huevo sin espumar, verter y hornear a baño maría; enfriar antes de desmoldar.", [("Leche", "0.12", "litro"), ("Huevo", "0.12", "docena"), ("Azúcar", "0.04", "kg"), ("Canela", "0.001", "kg")]),
    _r("Tarta de manzana", "POSTRE", "Europa", 75, "MEDIA", "Manzanas con canela sobre una masa horneada.", "Formar una masa con harina, mantequilla y azúcar. Cubrir con manzana en láminas y canela; hornear hasta que la fruta esté suave y la masa dorada.", [("Manzana", "0.16", "kg"), ("Harina de trigo", "0.08", "kg"), ("Mantequilla", "0.04", "kg"), ("Azúcar", "0.04", "kg"), ("Canela", "0.002", "kg")]),
    _r("Licuado de banana y avena", "DESAYUNO", "Internacional", 10, "FACIL", "Bebida cremosa de banana, leche, avena y miel.", "Licuar la banana con leche, avena y miel hasta obtener una bebida homogénea. Servir fría.", [("Banana", "0.12", "kg"), ("Leche", "0.20", "litro"), ("Avena", "0.03", "kg"), ("Miel", "0.01", "kg")]),
    _r("Risotto de champiñones", "ALMUERZO", "Italia", 45, "MEDIA", "Arroz cremoso con champiñones, mantequilla y parmesano.", "Dorar los champiñones y reservar. Sofreír cebolla, añadir arroz y caldo poco a poco removiendo; terminar con mantequilla, champiñones y parmesano.", [("Arroz grano largo", "0.12", "kg"), ("Champiñón", "0.10", "kg"), ("Cebolla", "0.03", "kg"), ("Mantequilla", "0.02", "kg"), ("Queso parmesano", "0.03", "kg")]),
    _r("Tofu salteado con verduras", "ALMUERZO", "Asia · Vegetariana", 25, "FACIL", "Tofu dorado con pimiento, cebolla y salsa de soya.", "Dorar el tofu en cubos. Saltear pimiento y cebolla a fuego alto; añadir salsa de soya y devolver el tofu a la sartén.", [("Tofu", "0.15", "kg"), ("Pimiento morrón", "0.06", "kg"), ("Cebolla", "0.04", "kg"), ("Salsa de soya", "0.02", "litro"), ("Arroz grano largo", "0.08", "kg")]),
    _r("Sándwich de queso fundido", "MERIENDA", "Estados Unidos", 15, "FACIL", "Pan tostado con queso fundido y tomate a la plancha.", "Rellenar el pan con queso y tomate. Dorar en sartén con mantequilla a fuego bajo, presionando hasta fundir el queso.", [("Pan de hamburguesa", "1", "unidad"), ("Queso mozzarella", "0.06", "kg"), ("Tomate", "0.04", "kg"), ("Mantequilla", "0.01", "kg")]),
    _r("Pollo al limón al horno", "ALMUERZO", "Internacional", 60, "FACIL", "Pollo horneado con limón, ajo y papa rústica.", "Marinar el pollo con limón, ajo y sal. Colocar con papas en una fuente y hornear, girando una vez, hasta que esté bien cocido y dorado.", [("Pechuga de pollo", "0.22", "kg"), ("Limón", "0.03", "kg"), ("Ajo", "0.01", "kg"), ("Papa", "0.20", "kg"), ("Aceite vegetal", "0.02", "litro")]),
    _r("Tallarines con salsa de tomate", "ALMUERZO", "Italia", 30, "FACIL", "Pasta con salsa de tomate, ajo, cebolla y orégano.", "Cocer el fideo. Cocinar tomate, cebolla y ajo hasta formar una salsa espesa; sazonar con orégano y mezclar con la pasta.", [("Fideo", "0.12", "kg"), ("Tomate", "0.15", "kg"), ("Cebolla", "0.04", "kg"), ("Ajo", "0.01", "kg"), ("Orégano seco", "0.002", "kg"), ("Aceite vegetal", "0.01", "litro")]),
    _r("Ensalada de quinua y palta", "ALMUERZO", "Bolivia · Vegetariana", 25, "FACIL", "Quinua fría con palta, tomate, pepino y limón.", "Cocer la quinua y enfriarla. Cortar las verduras, mezclar con la quinua y aderezar con limón, aceite y sal.", [("Quinua", "0.09", "kg"), ("Palta", "0.06", "kg"), ("Tomate", "0.05", "kg"), ("Pepino", "0.05", "kg"), ("Limón", "0.02", "kg"), ("Aceite vegetal", "0.01", "litro")]),
    _r("Milanesa de pollo", "ALMUERZO", "Internacional", 35, "FACIL", "Pechuga apanada y dorada con papa y ensalada.", "Aplanar la pechuga, pasar por huevo y pan rallado; dorar por ambos lados. Servir con papa cocida y ensalada fresca.", [("Pechuga de pollo", "0.20", "kg"), ("Huevo", "0.08", "docena"), ("Pan rallado", "0.05", "kg"), ("Papa", "0.18", "kg"), ("Lechuga", "0.10", "unidad"), ("Tomate", "0.04", "kg")]),
    _r("Pollo a la plancha con ensalada", "ALMUERZO", "Internacional", 25, "FACIL", "Pechuga sellada con ensalada de lechuga, tomate y pepino.", "Sazonar y sellar la pechuga en plancha caliente hasta cocinarla por completo. Servir con ensalada fresca y aderezo de limón.", [("Pechuga de pollo", "0.20", "kg"), ("Lechuga", "0.15", "unidad"), ("Tomate", "0.05", "kg"), ("Pepino", "0.05", "kg"), ("Limón", "0.02", "kg")]),
    _r("Tortilla de papa", "DESAYUNO", "España", 40, "MEDIA", "Tortilla gruesa de papa, cebolla y huevo cuajada en sartén.", "Cocinar las papas y cebollas lentamente en aceite. Mezclar con huevo batido, devolver a la sartén y cuajar por ambos lados.", [("Papa", "0.20", "kg"), ("Cebolla", "0.04", "kg"), ("Huevo", "0.20", "docena"), ("Aceite vegetal", "0.02", "litro")]),
    _r("Crema de zapallo y zanahoria", "ALMUERZO", "Internacional · Vegetariana", 40, "FACIL", "Crema suave de verduras con leche y especias.", "Cocer las verduras con cebolla hasta que estén blandas. Licuar con parte del caldo y leche; calentar suavemente y ajustar la sazón.", [("Zanahoria", "0.10", "kg"), ("Papa", "0.10", "kg"), ("Cebolla", "0.04", "kg"), ("Leche", "0.08", "litro"), ("Mantequilla", "0.01", "kg")]),
    _r("Galletas de avena y banana", "MERIENDA", "Internacional", 25, "FACIL", "Galletas suaves de avena, banana y miel.", "Aplastar la banana y mezclar con avena, miel y canela. Formar galletas y hornear hasta que los bordes estén dorados.", [("Avena", "0.08", "kg"), ("Banana", "0.10", "kg"), ("Miel", "0.02", "kg"), ("Canela", "0.001", "kg")]),
    _r("Empanadas de queso al horno", "MERIENDA", "Bolivia", 50, "MEDIA", "Empanadas horneadas con masa suave y relleno de queso.", "Preparar una masa con harina, leche, mantequilla y huevo. Rellenar con queso, sellar los bordes y hornear hasta dorar.", [("Harina de trigo", "0.10", "kg"), ("Queso criollo", "0.06", "kg"), ("Leche", "0.03", "litro"), ("Mantequilla", "0.02", "kg"), ("Huevo", "0.04", "docena")]),
]


def sembrar(db: Session) -> dict[str, int]:
    ingredientes = {i.nombre: i for i in db.scalars(select(Ingrediente)).all()}
    necesarios = {nombre for receta in RECETAS for nombre, _, _ in receta["ingredientes"]}
    faltantes = necesarios - ingredientes.keys()
    if faltantes:
        raise RuntimeError("Ejecuta primero el seeder base; faltan ingredientes: " + ", ".join(sorted(faltantes)))

    creadas = vinculos_nuevos = 0
    for datos in RECETAS:
        receta = db.scalar(select(Receta).where(Receta.nombre == datos["nombre"]))
        if receta is None:
            receta = Receta(
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                instrucciones=datos["pasos"],
                tipo_comida=datos["tipo"],
                porciones=2,
                tiempo_minutos=datos["minutos"],
                dificultad=datos["dificultad"],
                origen=datos["origen"],
                imagen_url=None,
                id_usuario_creador=None,
            )
            db.add(receta)
            db.flush()
            creadas += 1

        for nombre_ingrediente, cantidad, unidad in datos["ingredientes"]:
            ingrediente = ingredientes[nombre_ingrediente]
            vinculo = db.scalar(select(RecetaIngrediente).where(
                RecetaIngrediente.id_receta == receta.id_receta,
                RecetaIngrediente.id_ingrediente == ingrediente.id_ingrediente,
            ))
            if vinculo is None:
                db.add(RecetaIngrediente(
                    id_receta=receta.id_receta,
                    id_ingrediente=ingrediente.id_ingrediente,
                    nombre_ingrediente=ingrediente.nombre,
                    cantidad=Decimal(cantidad),
                    unidad_medida=unidad,
                ))
                vinculos_nuevos += 1
    return {"recetas_nuevas": creadas, "ingredientes_vinculados_nuevos": vinculos_nuevos}


if __name__ == "__main__":
    ejecutar_comando("biblioteca de recetas", sembrar)
