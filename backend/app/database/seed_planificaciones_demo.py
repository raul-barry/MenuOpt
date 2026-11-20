"""Planes demostrativos para las dos cuentas cliente ya existentes."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.seed_demo_util import ejecutar_comando
from app.models.planificacion import Planificacion
from app.models.planificacion_preferencia import PlanificacionPreferencia
from app.models.preferencia import Preferencia
from app.models.rol import Rol
from app.models.usuario import Usuario


CLIENTES = ("cliente1@menuopt.com", "cliente2@menuopt.com")
PLANES = [
    ("DEMO | Equipetrol, Santa Cruz", "ALMUERZO", "150.00", 2, None),
    ("DEMO | Sopocachi, La Paz", "CENA", "220.00", 4, None),
    ("DEMO | Cala Cala, Cochabamba vegetariano", "ALMUERZO", "120.00", 2, "Vegetariano"),
    ("DEMO | Centro, Santa Cruz", "CENA", "180.00", 2, None),
    ("DEMO | Calacoto, La Paz vegetariano", "ALMUERZO", "160.00", 2, "Vegetariano"),
    ("DEMO | Recoleta, Cochabamba", "CENA", "260.00", 4, None),
]


def sembrar(db: Session) -> dict[str, int]:
    clientes = {
        u.correo: u
        for u in db.scalars(select(Usuario).join(Usuario.rol).where(
            Usuario.correo.in_(CLIENTES), Usuario.estado == "ACTIVO", Rol.nombre == "CLIENTE"
        )).all()
    }
    faltan = set(CLIENTES) - clientes.keys()
    if faltan:
        raise RuntimeError("Faltan cuentas CLIENTE existentes: " + ", ".join(sorted(faltan)))

    veget = db.scalar(select(Preferencia).where(Preferencia.nombre == "Vegetariano"))
    if veget is None:
        veget = Preferencia(
            nombre="Vegetariano", tipo="DIETARIA",
            descripcion="No incluye carnes ni pescados; puede incluir lácteos y huevos.", activo=True,
        )
        db.add(veget)
        db.flush()

    creados = preferencias_nuevas = 0
    for index, (ubicacion, tipo, presupuesto, personas, preferencia) in enumerate(PLANES):
        cliente = clientes[CLIENTES[index // 3]]
        plan = db.scalar(select(Planificacion).where(
            Planificacion.id_usuario == cliente.id_usuario,
            Planificacion.ubicacion_referencia == ubicacion,
            Planificacion.tipo_comida == tipo,
        ))
        if plan is None:
            plan = Planificacion(
                presupuesto=Decimal(presupuesto),
                cantidad_personas=personas,
                tipo_comida=tipo,
                ubicacion_referencia=ubicacion,
                estado="ACTIVA",
                id_usuario=cliente.id_usuario,
            )
            db.add(plan)
            db.flush()
            creados += 1
        if preferencia:
            relacion = db.scalar(select(PlanificacionPreferencia).where(
                PlanificacionPreferencia.id_planificacion == plan.id_planificacion,
                PlanificacionPreferencia.id_preferencia == veget.id_preferencia,
            ))
            if relacion is None:
                db.add(PlanificacionPreferencia(
                    id_planificacion=plan.id_planificacion,
                    id_preferencia=veget.id_preferencia,
                ))
                preferencias_nuevas += 1

    return {"planes_nuevos": creados, "preferencias_de_plan_nuevas": preferencias_nuevas}


if __name__ == "__main__":
    ejecutar_comando("planes de cliente", sembrar)
