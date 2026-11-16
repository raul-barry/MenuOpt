# CASO DE USO: CU14, CU15, CU16 - Seeder de Recetas e Ingredientes para Platos
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database.conexion import get_db
from app.models.plato_ingrediente import PlatoIngrediente
from app.models.plato import Plato
from app.models.ingrediente import Ingrediente


def ejecutar_seeder():
    db: Session = next(get_db())

    recetas = [
        # (id_plato, [(id_ingrediente, cantidad, unidad_medida)])
        # CENA
        (9, [(17, Decimal("0.80"), "kg"), (15, Decimal("0.40"), "kg"), (10, Decimal("0.40"), "kg"), (9, Decimal("0.15"), "litro")]),  # Pizza Michelangelo
        (11, [(7, Decimal("0.40"), "kg"), (15, Decimal("0.20"), "kg"), (9, Decimal("0.15"), "litro"), (10, Decimal("0.30"), "kg")]),    # Spaghetti al Pesto
        (19, [(5, Decimal("0.30"), "kg"), (15, Decimal("0.15"), "kg"), (10, Decimal("0.15"), "kg"), (11, Decimal("0.15"), "kg")]),    # Hamburguesa Doble
        (20, [(5, Decimal("0.25"), "kg"), (15, Decimal("0.10"), "kg"), (10, Decimal("0.15"), "kg")]),                                  # Hamburguesa Simple
        (22, [(4, Decimal("0.40"), "kg"), (7, Decimal("0.40"), "kg"), (10, Decimal("0.30"), "kg"), (11, Decimal("0.20"), "kg"), (14, Decimal("0.15"), "kg")]), # Tallarín Saltado
        (25, [(4, Decimal("0.30"), "kg"), (11, Decimal("0.15"), "kg"), (10, Decimal("0.15"), "kg"), (9, Decimal("0.10"), "litro")]),   # Tacos al Pastor
        (26, [(17, Decimal("0.20"), "kg"), (15, Decimal("0.20"), "kg"), (9, Decimal("0.10"), "litro")]),                               # Quesadillas
        # ALMUERZO
        (3, [(4, Decimal("0.40"), "kg"), (1, Decimal("0.40"), "kg"), (8, Decimal("0.25"), "docena"), (11, Decimal("0.20"), "kg"), (10, Decimal("0.20"), "kg")]), # Majadito
        (10, [(5, Decimal("0.40"), "kg"), (7, Decimal("0.40"), "kg"), (15, Decimal("0.30"), "kg"), (10, Decimal("0.30"), "kg"), (16, Decimal("0.50"), "litro")]), # Lasagna
        (18, [(4, Decimal("0.25"), "kg"), (1, Decimal("0.20"), "kg"), (12, Decimal("0.25"), "kg"), (8, Decimal("0.10"), "docena"), (10, Decimal("0.15"), "kg")]), # Silpancho
        (21, [(1, Decimal("0.40"), "kg"), (2, Decimal("0.35"), "kg"), (8, Decimal("0.25"), "docena"), (11, Decimal("0.20"), "kg")]),  # Arroz Chaufa
        (2, [(2, Decimal("0.35"), "kg"), (17, Decimal("0.15"), "kg"), (12, Decimal("0.25"), "kg"), (9, Decimal("0.20"), "litro")]),   # Pollo Broaster
    ]

    total_agregados = 0
    for id_p, ings in recetas:
        plato = db.query(Plato).filter_by(id_plato=id_p).first()
        if not plato:
            continue
        for id_ing, cant, un in ings:
            existe = db.query(PlatoIngrediente).filter_by(id_plato=id_p, id_ingrediente=id_ing).first()
            if not existe:
                pi = PlatoIngrediente(id_plato=id_p, id_ingrediente=id_ing, cantidad=cant, unidad_medida=un)
                db.add(pi)
                total_agregados += 1

    db.commit()
    print(f"[OK] Seeder ejecutado: {total_agregados} relaciones de plato e ingredientes creadas.")


if __name__ == "__main__":
    ejecutar_seeder()
