# CASO DE USO: CU03, CU04, CU05 - Seeder Integral de Restaurantes, Categorías y Platos
import logging
from datetime import time
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.models.ubicacion import Ubicacion
from app.models.categoria import Categoria
from app.models.restaurante import Restaurante
from app.models.plato import Plato
from app.models.preferencia import Preferencia
from app.models.plato_preferencia import PlatoPreferencia

logger = logging.getLogger(__name__)


def ejecutar_seeder():
    db: Session = next(get_db())

    print("=================================================================")
    print(" INICIANDO SEEDER: RESTAURANTES, CATEGORÍAS Y PLATILLOS")
    print("=================================================================")

    # 1. Obtener usuario responsable para restaurantes
    usuario_resto = db.query(Usuario).filter(Usuario.correo == "restaurante@menuopt.com").first()
    if not usuario_resto:
        usuario_resto = db.query(Usuario).filter(Usuario.correo == "admin@menuopt.com").first()
    id_usuario = usuario_resto.id_usuario if usuario_resto else 1

    # =========================================================================
    # 2. CATEGORÍAS (Al menos 20 categorías gastronómicas)
    # =========================================================================
    categorias_data = [
        {"nombre": "Comida Típica Cruceña y Boliviana", "descripcion": "Majadito, keperí, sopa de maní, pacú y delicias de la tradición oriental."},
        {"nombre": "Carnes a la Parrilla y Churrasquerías", "descripcion": "Cortes premium a las brasas: bife de chorizo, picaña, costillas y cuadril."},
        {"nombre": "Pollos a la Brasa y Broaster", "descripcion": "Pollo crocante, a la leña y broaster con papas fritas y plátano frito."},
        {"nombre": "Pastas y Cocina Italiana", "descripcion": "Lasagnas caseras, fettuccine, spaghetti artesanales y ravioles rellenos."},
        {"nombre": "Hamburguesas y Sandwiches", "descripcion": "Hamburguesas gourmet, smashed burgers, lomitos y sándwiches especiales."},
        {"nombre": "Pizzas Artesanales", "descripcion": "Pizzas a la leña, masa madre, mozzarella, pepperoni y variedades de autor."},
        {"nombre": "Pescados y Mariscos de Río y Mar", "descripcion": "Surubí a la plancha, pacú frito, ceviches y mariscos seleccionados."},
        {"nombre": "Comida Asiática, Chifa y Sushi", "descripcion": "Arroz chaufa, tallarines salteados, rolls de sushi y cocina fusión oriental."},
        {"nombre": "Comida Rápida y Al Paso", "descripcion": "Salchipapas, brochetas, empanadas y bocados rápidos económicos."},
        {"nombre": "Almuerzos Ejecutivos y Menú Diario", "descripcion": "Menús completos y balanceados con sopa, plato de fondo, postre y refresco."},
        {"nombre": "Comida Saludable, Fitness y Ensaladas", "descripcion": "Bowls de quinoa, ensaladas completas, pechuga grillada y platos balanceados."},
        {"nombre": "Cafetería y Repostería", "descripcion": "Cafés de especialidad, cappuccinos, tortas, cheesecakes y repostería artesanal."},
        {"nombre": "Desayunos Tradicionales y Brunch", "descripcion": "Salteñas, cuñapés, empanadas de queso, masitas típicas y desayunos completos."},
        {"nombre": "Comida Mexicana y Taquería", "descripcion": "Tacos al pastor, quesadillas, burritos, nachos y salsas mexicanas."},
        {"nombre": "Sopas, Caldos y Tradición", "descripcion": "Sopa de maní, caldo de gallina criolla, chupe y sopas reconfortantes."},
        {"nombre": "Comida Vegetariana y Vegana", "descripcion": "Platos 100% vegetales, libres de carne, llenos de sabor y nutrición."},
        {"nombre": "Tablas, Picadas y Parrilleros", "descripcion": "Tablas mixtas para compartir con embutidos, quesos criollos y carnes."},
        {"nombre": "Postres, Helados y Dulces", "descripcion": "Copas de helado artesanal, postres tradicionales y crepes."},
        {"nombre": "Bebidas Típicas, Jugos y Refrescos", "descripcion": "Mocochinchi tradicional, chicha camba, jugos naturales y limonadas."},
        {"nombre": "Cenas Gourmet y Románticas", "descripcion": "Platos de autor, alta gastronomía para ocasiones especiales y parejas."},
        {"nombre": "Menú Infantil y Familiar", "descripcion": "Porciones ideales para niños y combos familiares para compartir."}
    ]

    mapa_categorias = {}
    for cat_item in categorias_data:
        cat_existente = db.query(Categoria).filter(Categoria.nombre == cat_item["nombre"]).first()
        if not cat_existente:
            cat_nueva = Categoria(
                nombre=cat_item["nombre"],
                descripcion=cat_item["descripcion"],
                activo=True
            )
            db.add(cat_nueva)
            db.flush()
            mapa_categorias[cat_item["nombre"]] = cat_nueva
            print(f"[OK] Creada categoría: {cat_nueva.nombre}")
        else:
            mapa_categorias[cat_item["nombre"]] = cat_existente

    # =========================================================================
    # 3. RESTAURANTES (20 Establecimientos representativos de Santa Cruz)
    # =========================================================================
    restaurantes_data = [
        {
            "nombre": "La Casa del Camba",
            "descripcion": "El restaurante de tradición cruceña más emblemático, famoso por su keperí, majadito y carnes al horno.",
            "nit": "1023456701",
            "telefono": "33445566",
            "correo": "reservas@lacasadelcamba.com",
            "apertura": time(11, 30),
            "cierre": time(23, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Equipetrol",
                "direccion": "Av. San Martín esq. Calle 8",
                "referencia": "A dos cuadras del Hotel Los Tajibos",
                "latitud": Decimal("-17.76540000"),
                "longitud": Decimal("-63.19500000")
            }
        },
        {
            "nombre": "Churrasquería El Arriero",
            "descripcion": "Especialistas en cortes argentinos y carnes a la leña de primera calidad en un ambiente acogedor.",
            "nit": "1023456702",
            "telefono": "33447788",
            "correo": "contacto@elarriero.com.bo",
            "apertura": time(12, 0),
            "cierre": time(23, 0),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Equipetrol",
                "direccion": "3er Anillo Interno esq. Canal Isuto",
                "referencia": "Frente al centro empresarial",
                "latitud": Decimal("-17.76800000"),
                "longitud": Decimal("-63.19200000")
            }
        },
        {
            "nombre": "Pizzería Michelangelo",
            "descripcion": "Pizzas al horno de piedra con receta tradicional italiana, masas crujientes y pastas frescas.",
            "nit": "1023456703",
            "telefono": "33321122",
            "correo": "pedidos@michelangelo.bo",
            "apertura": time(18, 0),
            "cierre": time(23, 59),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Centro",
                "direccion": "Calle 24 de Septiembre Nº 245",
                "referencia": "A media cuadra de la Plaza 24 de Septiembre",
                "latitud": Decimal("-17.78300000"),
                "longitud": Decimal("-63.18200000")
            }
        },
        {
            "nombre": "Pollos Chuy Central",
            "descripcion": "La cadena de pollos broaster más querida de Santa Cruz, con su característico adobo y papas fritas.",
            "nit": "1023456704",
            "telefono": "33345500",
            "correo": "atencion@polloschuy.com",
            "apertura": time(10, 30),
            "cierre": time(23, 0),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Centro",
                "direccion": "Calle Junín esq. Libertad",
                "referencia": "Frente al Correo Central",
                "latitud": Decimal("-17.78150000"),
                "longitud": Decimal("-63.18350000")
            }
        },
        {
            "nombre": "Pollos Solar Banzer",
            "descripcion": "Pollo a la brasa jugoso, combos económicos y familiares con arroz con queso cremoso y ensalada buffet.",
            "nit": "1023456705",
            "telefono": "33418899",
            "correo": "banzer@pollossolar.bo",
            "apertura": time(11, 0),
            "cierre": time(22, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Zona Norte",
                "direccion": "Av. Cristo Redentor (Banzer) entre 4to y 5to Anillo",
                "referencia": "Lado estación de servicio",
                "latitud": Decimal("-17.74900000"),
                "longitud": Decimal("-63.17800000")
            }
        },
        {
            "nombre": "Rincón Vallegrandino",
            "descripcion": "Auténtica comida criolla y valluna: asado de chancho, escabeche, sopa de maní y lomo montado tradicional.",
            "nit": "1023456706",
            "telefono": "33621144",
            "correo": "contacto@rinconvallegrandino.bo",
            "apertura": time(11, 0),
            "cierre": time(17, 0),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Villa 1ro de Mayo",
                "direccion": "Av. Principal esq. Calle 5",
                "referencia": "Cerca de la plaza de la Villa",
                "latitud": Decimal("-17.79500000"),
                "longitud": Decimal("-63.14500000")
            }
        },
        {
            "nombre": "Burger House Santa Cruz",
            "descripcion": "Hamburguesas artesanales de carne 100% novillo cruceño, salsas de la casa y pan brioche horneado diario.",
            "nit": "1023456707",
            "telefono": "33554433",
            "correo": "hola@burgerhousescz.bo",
            "apertura": time(18, 0),
            "cierre": time(23, 45),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Urbarí",
                "direccion": "Av. Piraí entre 2do y 3er Anillo",
                "referencia": "Diagonal al supermercado",
                "latitud": Decimal("-17.79200000"),
                "longitud": Decimal("-63.19900000")
            }
        },
        {
            "nombre": "Chifa Dragón de Oro",
            "descripcion": "Cocina chifa cantonesa tradicional: arroz chaufa, tallarín saltado, sopa wantán y pollo tipakay crujiente.",
            "nit": "1023456708",
            "telefono": "33423322",
            "correo": "info@dragondeoro.bo",
            "apertura": time(12, 0),
            "cierre": time(22, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Zona Norte",
                "direccion": "Av. Beni y 2do Anillo",
                "referencia": "Rotonda 2do anillo Beni",
                "latitud": Decimal("-17.76900000"),
                "longitud": Decimal("-63.17600000")
            }
        },
        {
            "nombre": "Sushi Train Equipetrol",
            "descripcion": "Sushi fresco en cinta giratoria, rolls acevichados, tempuras y cocina japonesa contemporánea.",
            "nit": "1023456709",
            "telefono": "33458877",
            "correo": "reservas@sushitrain.bo",
            "apertura": time(19, 0),
            "cierre": time(23, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Equipetrol",
                "direccion": "Calle Los Claveles Nº 120",
                "referencia": "Equipetrol Norte",
                "latitud": Decimal("-17.76300000"),
                "longitud": Decimal("-63.19700000")
            }
        },
        {
            "nombre": "Tacos Güey - Taquería Mexicana",
            "descripcion": "Auténticos tacos callejeros mexicanos: pastor con piña, suadero, birria y aguas frescas de horchata y jamaica.",
            "nit": "1023456710",
            "telefono": "33419900",
            "correo": "orale@tacosguey.bo",
            "apertura": time(18, 30),
            "cierre": time(23, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Equipetrol",
                "direccion": "Av. San Martín entre calles 7 y 8",
                "referencia": "Zona de bares y cafés de Equipetrol",
                "latitud": Decimal("-17.76600000"),
                "longitud": Decimal("-63.19450000")
            }
        },
        {
            "nombre": "El Huerto Saludable & Green Bar",
            "descripcion": "Menús saludables, opciones vegetarianas, sin gluten, ensaladas completas, bowls fit y smoothies détox.",
            "nit": "1023456711",
            "telefono": "33527711",
            "correo": "saludable@elhuertoscz.bo",
            "apertura": time(8, 0),
            "cierre": time(20, 0),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Urbarí",
                "direccion": "Av. Las Américas Nº 430",
                "referencia": "Pasando el parque El Arenal de Urbarí",
                "latitud": Decimal("-17.79400000"),
                "longitud": Decimal("-63.19800000")
            }
        },
        {
            "nombre": "Café Patrimonio Histórico",
            "descripcion": "Cafetería colonial en el corazón de Santa Cruz: café de Los Yungas, horneados típicos, cuñapés y empanadas.",
            "nit": "1023456712",
            "telefono": "33358899",
            "correo": "cafe@patrimonio.bo",
            "apertura": time(7, 30),
            "cierre": time(21, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Centro",
                "direccion": "Calle Bolívar frente a la Manzana Uno",
                "referencia": "Plaza Principal 24 de Septiembre",
                "latitud": Decimal("-17.78320000"),
                "longitud": Decimal("-63.18180000")
            }
        },
        {
            "nombre": "Salteñería Santa Cruz Tradición",
            "descripcion": "Las mejores salteñas caldosas de res, pollo y mixtas de la ciudad, horneadas frescas a toda hora de la mañana.",
            "nit": "1023456713",
            "telefono": "33342211",
            "correo": "pedidos@saltenasdeloriente.bo",
            "apertura": time(7, 0),
            "cierre": time(13, 0),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Centro",
                "direccion": "Calle Sucre entre René Moreno e Independencia",
                "referencia": "A una cuadra de la Catedral",
                "latitud": Decimal("-17.78450000"),
                "longitud": Decimal("-63.18250000")
            }
        },
        {
            "nombre": "Pescadería y Marisquería Don Pacífico",
            "descripcion": "Especialistas en surubí fresco de río, pacú frito crocante, cazuela de mariscos y ceviches mixtos.",
            "nit": "1023456714",
            "telefono": "33561199",
            "correo": "donpacifico@pescaderia.bo",
            "apertura": time(11, 0),
            "cierre": time(16, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Zona Sur",
                "direccion": "Av. Santos Dumont y 3er Anillo",
                "referencia": "Frente al mercado de flores",
                "latitud": Decimal("-17.81000000"),
                "longitud": Decimal("-63.18900000")
            }
        },
        {
            "nombre": "Trattoria Da Luigi",
            "descripcion": "Restaurante italiano íntimo y elegante con pastas rellenas a mano, risottos cremosos y fina carta de vinos.",
            "nit": "1023456715",
            "telefono": "33451122",
            "correo": "daluigi@trattoriascz.bo",
            "apertura": time(19, 30),
            "cierre": time(23, 45),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Sirari",
                "direccion": "Calle Los Tulipanes esq. Las Begonias",
                "referencia": "Barrio Sirari, zona residencial",
                "latitud": Decimal("-17.76100000"),
                "longitud": Decimal("-63.19600000")
            }
        },
        {
            "nombre": "Almuerzos Doña Gladys",
            "descripcion": "Almuerzos caseros abundantes y muy económicos para trabajadores y ejecutivos, con sopa y segundo del día.",
            "nit": "1023456716",
            "telefono": "33489911",
            "correo": "donagladys@almuerzos.bo",
            "apertura": time(11, 30),
            "cierre": time(15, 0),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Parque Industrial",
                "direccion": "Av. Virgen de Cotoca esq. Calle 3",
                "referencia": "Entrada al Parque Industrial PI-21",
                "latitud": Decimal("-17.77200000"),
                "longitud": Decimal("-63.14900000")
            }
        },
        {
            "nombre": "Dumbo Heladería y Restaurante",
            "descripcion": "Punto de encuentro familiar tradicional sobre Monseñor Rivero, con helados, sándwiches de lomo y menú infantil.",
            "nit": "1023456717",
            "telefono": "33367788",
            "correo": "contacto@dumbo.com.bo",
            "apertura": time(9, 0),
            "cierre": time(23, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Norte",
                "direccion": "Av. Monseñor Rivero Nº 350",
                "referencia": "Paseo Monseñor Rivero",
                "latitud": Decimal("-17.77500000"),
                "longitud": Decimal("-63.18100000")
            }
        },
        {
            "nombre": "Churrasquería Los Hierros",
            "descripcion": "Buffet de ensaladas y guarniciones con cortes a la espada estilo rodizio brasileño y parrilla libre.",
            "nit": "1023456718",
            "telefono": "33434455",
            "correo": "reservas@loshierros.bo",
            "apertura": time(12, 0),
            "cierre": time(23, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Zona Norte",
                "direccion": "Av. Banzer y 4to Anillo",
                "referencia": "Esquina estratégica 4to anillo norte",
                "latitud": Decimal("-17.75300000"),
                "longitud": Decimal("-63.17700000")
            }
        },
        {
            "nombre": "La Cabaña del Pescador",
            "descripcion": "Cabaña campestre al aire libre para disfrutar pacú a la brasa, chicharrón de surubí y yuca frita los fines de semana.",
            "nit": "1023456719",
            "telefono": "33578822",
            "correo": "pescador@cabanascz.bo",
            "apertura": time(11, 0),
            "cierre": time(18, 0),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Suroeste",
                "direccion": "Km 6 Doble Vía a La Guardia",
                "referencia": "Frente al módulo policial",
                "latitud": Decimal("-17.82500000"),
                "longitud": Decimal("-63.22000000")
            }
        },
        {
            "nombre": "Restaurante Vegetariano Vida Sana",
            "descripcion": "Cocina vegetariana y macrobiótica consciente, buffet variado por peso, milanesas de soja y postres sin azúcar.",
            "nit": "1023456720",
            "telefono": "33339944",
            "correo": "vidasana@saludable.bo",
            "apertura": time(11, 30),
            "cierre": time(15, 30),
            "ubicacion": {
                "ciudad": "Santa Cruz de la Sierra",
                "zona": "Centro",
                "direccion": "Calle Pari Nº 156",
                "referencia": "Entre Velasco y España",
                "latitud": Decimal("-17.78500000"),
                "longitud": Decimal("-63.18400000")
            }
        }
    ]

    mapa_restaurantes = {}
    for r_data in restaurantes_data:
        r_existente = db.query(Restaurante).filter(Restaurante.nombre == r_data["nombre"]).first()
        if not r_existente:
            ub_data = r_data["ubicacion"]
            nueva_ubicacion = Ubicacion(
                ciudad=ub_data["ciudad"],
                zona=ub_data["zona"],
                direccion=ub_data["direccion"],
                referencia=ub_data["referencia"],
                latitud=ub_data["latitud"],
                longitud=ub_data["longitud"]
            )
            db.add(nueva_ubicacion)
            db.flush()

            nuevo_resto = Restaurante(
                nombre=r_data["nombre"],
                descripcion=r_data["descripcion"],
                nit=r_data["nit"],
                telefono=r_data["telefono"],
                correo=r_data["correo"],
                horario_apertura=r_data["apertura"],
                horario_cierre=r_data["cierre"],
                estado="ACTIVO",
                id_usuario_responsable=id_usuario,
                id_ubicacion=nueva_ubicacion.id_ubicacion
            )
            db.add(nuevo_resto)
            db.flush()
            mapa_restaurantes[r_data["nombre"]] = nuevo_resto
            print(f"[OK] Creado restaurante: {nuevo_resto.nombre} en {ub_data['zona']}")
        else:
            mapa_restaurantes[r_data["nombre"]] = r_existente

    # =========================================================================
    # 4. PLATILLOS (Más de 40 platos con precios variados de Bs 9.50 a Bs 120.00)
    # =========================================================================
    # Preferencias en BD
    pref_veg = db.query(Preferencia).filter(Preferencia.nombre == "Vegetariano").first()
    pref_vegano = db.query(Preferencia).filter(Preferencia.nombre == "Vegano").first()
    pref_sg = db.query(Preferencia).filter(Preferencia.nombre == "Sin gluten").first()
    pref_sl = db.query(Preferencia).filter(Preferencia.nombre == "Sin lactosa").first()
    pref_picante = db.query(Preferencia).filter(Preferencia.nombre == "Picante").first()
    pref_sa = db.query(Preferencia).filter(Preferencia.nombre == "Sin azúcar").first()

    platos_data = [
        # La Casa del Camba
        {
            "restaurante": "La Casa del Camba",
            "categoria": "Comida Típica Cruceña y Boliviana",
            "nombre": "Majadito de Charque Típico",
            "descripcion": "Arroz tostado con charque de res cruceño, huevo frito criollo, plátano dulce frito y yuca harinosa.",
            "precio": Decimal("34.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        {
            "restaurante": "La Casa del Camba",
            "categoria": "Comida Típica Cruceña y Boliviana",
            "nombre": "Keperí al Horno Tradicional",
            "descripcion": "Corte de keperí suave y tierno al horno a leña, acompañado con arroz con queso cremoso y yuca frita.",
            "precio": Decimal("48.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "La Casa del Camba",
            "categoria": "Sopas, Caldos y Tradición",
            "nombre": "Sopa de Maní Cruceña",
            "descripcion": "Sopa cremosa tradicional de maní tostado con trozos de res seleccionada, papas fritas al hilo y perejil.",
            "precio": Decimal("22.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Churrasquería El Arriero
        {
            "restaurante": "Churrasquería El Arriero",
            "categoria": "Carnes a la Parrilla y Churrasquerías",
            "nombre": "Bife de Chorizo a las Brasas (400g)",
            "descripcion": "Jugoso corte argentino a las brasas con chimichurri casero, papas al horno y buffet de ensaladas.",
            "precio": Decimal("75.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        {
            "restaurante": "Churrasquería El Arriero",
            "categoria": "Carnes a la Parrilla y Churrasquerías",
            "nombre": "Picaña Especial al Carbón",
            "descripcion": "Tapa de cuadril con su capa justa de grasa crocante, servida en tabla con mandioca caliente.",
            "precio": Decimal("85.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        {
            "restaurante": "Churrasquería El Arriero",
            "categoria": "Tablas, Picadas y Parrilleros",
            "nombre": "Tabla Arriero Familiar para 4 Personas",
            "descripcion": "Chorizo parrillero, morcilla, costilla de cerdo, bife de tira, yuca y queso provolone gratinado.",
            "precio": Decimal("120.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 4,
            "preferencias": []
        },
        # Pizzería Michelangelo
        {
            "restaurante": "Pizzería Michelangelo",
            "categoria": "Pizzas Artesanales",
            "nombre": "Pizza Michelangelo Familiar",
            "descripcion": "Masa madre a la piedra, salsa de tomate natural, abundante mozzarella, jamón serrano y rúcula.",
            "precio": Decimal("68.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 3,
            "preferencias": []
        },
        {
            "restaurante": "Pizzería Michelangelo",
            "categoria": "Pastas y Cocina Italiana",
            "nombre": "Lasagna a la Boloñesa Gratinada",
            "descripcion": "Capas de pasta artesanal con ragú clásico de carne molida, bechamel y queso parmesano gratinado al horno.",
            "precio": Decimal("42.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Pizzería Michelangelo",
            "categoria": "Pastas y Cocina Italiana",
            "nombre": "Spaghetti al Pesto Genovés",
            "descripcion": "Pasta larga al dente con salsa de albahaca fresca, nueces, ajo, aceite de oliva y queso de granja.",
            "precio": Decimal("36.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg] if pref_veg else []
        },
        # Pollos Chuy Central
        {
            "restaurante": "Pollos Chuy Central",
            "categoria": "Pollos a la Brasa y Broaster",
            "nombre": "Cuarto de Pollo Broaster Chuy",
            "descripcion": "Presa grande de pollo crujiente y jugosa con papas fritas naturales, plátano frito y salsa de la casa.",
            "precio": Decimal("22.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Pollos Chuy Central",
            "categoria": "Pollos a la Brasa y Broaster",
            "nombre": "Combo Económico Chuy Pipocas",
            "descripcion": "Pipocas de pollo crocantes con porción de papas fritas y refresco de mocochinchi personal.",
            "precio": Decimal("18.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Pollos Chuy Central",
            "categoria": "Menú Infantil y Familiar",
            "nombre": "Combo Familiar Pollo Entero Chuy (8 Presas)",
            "descripcion": "Pollo entero broaster de 8 presas con 2 porciones de papas fritas familiares, plátanos y gaseosa 2L.",
            "precio": Decimal("82.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 4,
            "preferencias": []
        },
        # Pollos Solar Banzer
        {
            "restaurante": "Pollos Solar Banzer",
            "categoria": "Pollos a la Brasa y Broaster",
            "nombre": "Cuarto de Pollo a la Brasa con Arroz con Queso",
            "descripcion": "Pollo dorado a la leña con guarnición de arroz con queso cremoso y ensalada buffet libre.",
            "precio": Decimal("25.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        {
            "restaurante": "Pollos Solar Banzer",
            "categoria": "Menú Infantil y Familiar",
            "nombre": "Medio Pollo a la Brasa Dúo",
            "descripcion": "Medio pollo a la leña para 2 comensales con papas fritas y dos platos de arroz con queso.",
            "precio": Decimal("46.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 2,
            "preferencias": [pref_sg] if pref_sg else []
        },
        # Rincón Vallegrandino
        {
            "restaurante": "Rincón Vallegrandino",
            "categoria": "Comida Típica Cruceña y Boliviana",
            "nombre": "Asado Criollo de Chancho",
            "descripcion": "Costillas y lomo de cerdo doradas en pailón tradicional con mote de maíz, plátano cocido y llajwa.",
            "precio": Decimal("38.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_picante] if pref_picante else []
        },
        {
            "restaurante": "Rincón Vallegrandino",
            "categoria": "Comida Típica Cruceña y Boliviana",
            "nombre": "Silpancho Tradicional Vallegrandino",
            "descripcion": "Milanesa gigante de carne apanada sobre colchón de arroz y papas doradas, coronada con dos huevos fritos.",
            "precio": Decimal("28.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Burger House Santa Cruz
        {
            "restaurante": "Burger House Santa Cruz",
            "categoria": "Hamburguesas y Sandwiches",
            "nombre": "Hamburguesa Doble Bacon & Cheddar",
            "descripcion": "Doble medallón de res 180g, queso cheddar fundido, tocino ahumado crocante, cebolla caramelizada y papas.",
            "precio": Decimal("35.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Burger House Santa Cruz",
            "categoria": "Hamburguesas y Sandwiches",
            "nombre": "Hamburguesa Clásica Simple",
            "descripcion": "Medallón de carne de res fresca, lechuga hidropónica, tomate manzano, pepinillos y papas rústicas.",
            "precio": Decimal("24.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Chifa Dragón de Oro
        {
            "restaurante": "Chifa Dragón de Oro",
            "categoria": "Comida Asiática, Chifa y Sushi",
            "nombre": "Arroz Chaufa Especial Mixto",
            "descripcion": "Arroz salteado al wok a fuego vivo con trozos de pollo, carne de res, huevo revuelto y cebollín fresco.",
            "precio": Decimal("28.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Chifa Dragón de Oro",
            "categoria": "Comida Asiática, Chifa y Sushi",
            "nombre": "Tallarín Saltado de Carne y Verduras",
            "descripcion": "Tallarines de huevo salteados con lomo de res, cebolla morada, tomate y pimiento en salsa de soya china.",
            "precio": Decimal("32.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Sushi Train Equipetrol
        {
            "restaurante": "Sushi Train Equipetrol",
            "categoria": "Comida Asiática, Chifa y Sushi",
            "nombre": "Roll Acevichado de Salmón (10 piezas)",
            "descripcion": "Roll relleno de palta y langostino furai, cubierto con láminas de salmón y bañada en salsa acevichada.",
            "precio": Decimal("55.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Sushi Train Equipetrol",
            "categoria": "Comida Vegetariana y Vegana",
            "nombre": "Roll Veggie Palta y Pepino (10 piezas)",
            "descripcion": "Roll vegetal con palta Hass, pepino japonés, espárragos y semillas de sésamo tostado.",
            "precio": Decimal("38.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg, pref_vegano] if pref_veg and pref_vegano else []
        },
        # Tacos Güey
        {
            "restaurante": "Tacos Güey - Taquería Mexicana",
            "categoria": "Comida Mexicana y Taquería",
            "nombre": "Orden de Tacos al Pastor (3 unidades)",
            "descripcion": "Carne de cerdo adobada al trompo con piña asada, cebolla, cilantro y tortilla de maíz nixtamalizado.",
            "precio": Decimal("30.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg, pref_picante] if pref_sg and pref_picante else []
        },
        {
            "restaurante": "Tacos Güey - Taquería Mexicana",
            "categoria": "Comida Mexicana y Taquería",
            "nombre": "Quesadillas de Queso Oaxaca y Champiñones",
            "descripcion": "Dos quesadillas en tortilla de harina con queso fundido y champiñones salteados con pico de gallo.",
            "precio": Decimal("26.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg] if pref_veg else []
        },
        # El Huerto Saludable
        {
            "restaurante": "El Huerto Saludable & Green Bar",
            "categoria": "Comida Saludable, Fitness y Ensaladas",
            "nombre": "Bowl Fit Proteico de Quinoa y Pollo",
            "descripcion": "Base de quinoa real andina, pechuga de pollo a la plancha, palta, tomate cherry, choclo y vinagreta cítrica.",
            "precio": Decimal("34.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg, pref_sl] if pref_sg and pref_sl else []
        },
        {
            "restaurante": "El Huerto Saludable & Green Bar",
            "categoria": "Comida Saludable, Fitness y Ensaladas",
            "nombre": "Ensalada César Saludable",
            "descripcion": "Hojas de lechuga romana fresca, dados de pechuga grillada, croutons integrales y aderezo ligero de yogur.",
            "precio": Decimal("29.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Café Patrimonio Histórico
        {
            "restaurante": "Café Patrimonio Histórico",
            "categoria": "Cafetería y Repostería",
            "nombre": "Desayuno Típico Cruceño Completo",
            "descripcion": "2 cuñapés calientes horneados, 1 empanada de queso, café pasado de Los Yungas y jugo de naranja natural.",
            "precio": Decimal("22.00"),
            "tipo_comida": "DESAYUNO",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg] if pref_veg else []
        },
        {
            "restaurante": "Café Patrimonio Histórico",
            "categoria": "Cafetería y Repostería",
            "nombre": "Cappuccino Doble con Torta Tres Leches",
            "descripcion": "Café con espuma cremosa de leche entera acompañado de una porción generosa de torta tres leches artesanal.",
            "precio": Decimal("25.00"),
            "tipo_comida": "MERIENDA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Salteñería Santa Cruz Tradición
        {
            "restaurante": "Salteñería Santa Cruz Tradición",
            "categoria": "Desayunos Tradicionales y Brunch",
            "nombre": "Salteña de Carne Caldosa de Res",
            "descripcion": "Masa crocante dorada rellena de carne picada jugosa, papa, huevo duro, aceituna y suave picante tradicional.",
            "precio": Decimal("9.50"),
            "tipo_comida": "DESAYUNO",
            "personas_cubiertas": 1,
            "preferencias": [pref_picante] if pref_picante else []
        },
        {
            "restaurante": "Salteñería Santa Cruz Tradición",
            "categoria": "Desayunos Tradicionales y Brunch",
            "nombre": "Combo 2 Salteñas de Pollo con Refresco",
            "descripcion": "2 salteñas caldosas de pechuga de pollo desmenuzada acompañadas con un vaso de refresco de mocochinchi frío.",
            "precio": Decimal("22.00"),
            "tipo_comida": "DESAYUNO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Pescadería Don Pacífico
        {
            "restaurante": "Pescadería y Marisquería Don Pacífico",
            "categoria": "Pescados y Mariscos de Río y Mar",
            "nombre": "Pacú Frito de Río con Yuca y Arroz",
            "descripcion": "Corte de pacú fresco frito al punto dorado crujiente con arroz blanco graneado, yuca hervida y limón.",
            "precio": Decimal("52.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        {
            "restaurante": "Pescadería y Marisquería Don Pacífico",
            "categoria": "Pescados y Mariscos de Río y Mar",
            "nombre": "Surubí a la Plancha en Salsa de Alcaparras",
            "descripcion": "Filete de surubí tierno a la plancha bañado en salsa suave de mantequilla y alcaparras con puré de papas.",
            "precio": Decimal("60.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        # Trattoria Da Luigi
        {
            "restaurante": "Trattoria Da Luigi",
            "categoria": "Cenas Gourmet y Románticas",
            "nombre": "Fettuccine Frutti di Mare",
            "descripcion": "Pasta larga al dente con calamares, langostinos y mejillones salteados al vino blanco y pomodoro italiano.",
            "precio": Decimal("58.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Trattoria Da Luigi",
            "categoria": "Pastas y Cocina Italiana",
            "nombre": "Ravioles de Ricotta y Espinaca",
            "descripcion": "Ravioles artesanales rellenos de queso ricotta fresco y espinacas tiernas, cubiertos con salsa de cuatro quesos.",
            "precio": Decimal("44.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg] if pref_veg else []
        },
        # Almuerzos Doña Gladys
        {
            "restaurante": "Almuerzos Doña Gladys",
            "categoria": "Almuerzos Ejecutivos y Menú Diario",
            "nombre": "Almuerzo Ejecutivo Completo del Día",
            "descripcion": "Menú completo: Sopa de fideo casera + Segundo de Pollo al Horno con arroz y ensalada + Postre + Refresco.",
            "precio": Decimal("18.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        {
            "restaurante": "Almuerzos Doña Gladys",
            "categoria": "Almuerzos Ejecutivos y Menú Diario",
            "nombre": "Almuerzo Criollo Chuleta de Cerdo",
            "descripcion": "Sopa reconfortante de verduras + Chuleta de cerdo dorada a la plancha con puré de papas y arroz graneado.",
            "precio": Decimal("20.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Dumbo Heladería y Restaurante
        {
            "restaurante": "Dumbo Heladería y Restaurante",
            "categoria": "Postres, Helados y Dulces",
            "nombre": "Copa Helada Dumbo Especial (3 Sabores)",
            "descripcion": "Tres bolas de helado artesanal a elección con crema chantilly, fudge de chocolate, nueces picadas y barquillo.",
            "precio": Decimal("32.00"),
            "tipo_comida": "MERIENDA",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg] if pref_veg else []
        },
        {
            "restaurante": "Dumbo Heladería y Restaurante",
            "categoria": "Hamburguesas y Sandwiches",
            "nombre": "Sándwich de Lomo Completo Dumbo",
            "descripcion": "Fino filete de lomo de res en pan especial tostado con queso derretido, jamón, huevo frito, lechuga y papas.",
            "precio": Decimal("36.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Churrasquería Los Hierros
        {
            "restaurante": "Churrasquería Los Hierros",
            "categoria": "Carnes a la Parrilla y Churrasquerías",
            "nombre": "Corte de Cuadril Especial 350g",
            "descripcion": "Corazón de cuadril tierno a las brasas con guarnición de mandioca hervida y salsa tártara de la casa.",
            "precio": Decimal("58.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        {
            "restaurante": "Churrasquería Los Hierros",
            "categoria": "Carnes a la Parrilla y Churrasquerías",
            "nombre": "Costillar de Cerdo a la Miel de Caña",
            "descripcion": "Costillas de cerdo asadas lentamente con glaseado de miel de caña cruceña y batatas horneadas.",
            "precio": Decimal("62.00"),
            "tipo_comida": "CENA",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # La Cabaña del Pescador
        {
            "restaurante": "La Cabaña del Pescador",
            "categoria": "Pescados y Mariscos de Río y Mar",
            "nombre": "Pacú Campestre a las Brasas",
            "descripcion": "Medio pacú a la parrilla sobre brasas de leña, con arroz con queso chaqueño y ensalada criolla fresca.",
            "precio": Decimal("55.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_sg] if pref_sg else []
        },
        {
            "restaurante": "La Cabaña del Pescador",
            "categoria": "Comida Rápida y Al Paso",
            "nombre": "Chicharrón de Surubí Crocante",
            "descripcion": "Bocados de surubí rebozados y fritos crocantes con rodajas de limón, tártara casera y yuca frita.",
            "precio": Decimal("45.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": []
        },
        # Restaurante Vegetariano Vida Sana
        {
            "restaurante": "Restaurante Vegetariano Vida Sana",
            "categoria": "Comida Vegetariana y Vegana",
            "nombre": "Almuerzo Vegetariano Saludable del Día",
            "descripcion": "Sopa depurativa de verduras + Hamburguesa de lentejas y avena con arroz integral, ensalada variada y jugo natural.",
            "precio": Decimal("22.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg, pref_vegano, pref_sa] if pref_veg and pref_vegano and pref_sa else []
        },
        {
            "restaurante": "Restaurante Vegetariano Vida Sana",
            "categoria": "Comida Vegetariana y Vegana",
            "nombre": "Lasaña Vegana de Berenjenas y Champiñones",
            "descripcion": "Láminas de berenjena asada con espinacas, salsa bechamel de avena y nuez moscada sin derivados lácteos.",
            "precio": Decimal("28.00"),
            "tipo_comida": "ALMUERZO",
            "personas_cubiertas": 1,
            "preferencias": [pref_veg, pref_vegano, pref_sg, pref_sl] if pref_veg and pref_vegano and pref_sg and pref_sl else []
        }
    ]

    platos_creados = 0
    for p_item in platos_data:
        resto_obj = mapa_restaurantes.get(p_item["restaurante"])
        cat_obj = mapa_categorias.get(p_item["categoria"])

        if not resto_obj or not cat_obj:
            continue

        plato_existente = db.query(Plato).filter(
            Plato.nombre == p_item["nombre"],
            Plato.id_restaurante == resto_obj.id_restaurante
        ).first()

        if not plato_existente:
            nuevo_plato = Plato(
                nombre=p_item["nombre"],
                descripcion=p_item["descripcion"],
                precio=p_item["precio"],
                tipo_comida=p_item["tipo_comida"],
                personas_cubiertas=p_item["personas_cubiertas"],
                disponible=True,
                estado="ACTIVO",
                id_restaurante=resto_obj.id_restaurante,
                id_categoria=cat_obj.id_categoria
            )
            db.add(nuevo_plato)
            db.flush()

            # Enlazar preferencias
            for pref in p_item.get("preferencias", []):
                if pref:
                    db.add(PlatoPreferencia(
                        id_plato=nuevo_plato.id_plato,
                        id_preferencia=pref.id_preferencia
                    ))
            platos_creados += 1
            print(f"[OK] Creado plato: {nuevo_plato.nombre} (Bs {nuevo_plato.precio}) en {resto_obj.nombre}")

    db.commit()
    print("=================================================================")
    print(f" [ÉXITO] Seeder completado satisfactoriamente.")
    print(f" Categorías totales en BD: {db.query(Categoria).count()}")
    print(f" Restaurantes totales en BD: {db.query(Restaurante).count()}")
    print(f" Platos totales en BD: {db.query(Plato).count()}")
    print("=================================================================")
    db.close()


if __name__ == "__main__":
    ejecutar_seeder()
