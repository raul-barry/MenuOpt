# CASO DE USO: CU14 - Comparar alternativas (RESTAURANTE vs PREPARACION_PROPIA)
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.recomendacion import RecomendacionPlatoItemSchema


class AlternativaComparacionSchema(BaseModel):
    id_recomendacion: int
    tipo_recomendacion: str  # RESTAURANTE o PREPARACION_PROPIA
    nombre: str
    costo_total: Decimal
    costo_por_persona: Decimal
    ahorro_respecto_presupuesto: Decimal
    porcentaje_presupuesto_utilizado: Decimal
    puntuacion: Decimal
    distancia_estimada: Optional[Decimal] = None
    resumen: str

    # Detalles para alternativa de RESTAURANTE
    id_restaurante: Optional[int] = None
    nombre_restaurante: Optional[str] = None
    platos: List[RecomendacionPlatoItemSchema] = []

    # Detalles para alternativa de PREPARACION_PROPIA
    id_preparacion_propia: Optional[int] = None
    nombre_preparacion: Optional[str] = None
    ingredientes_resumen: List[str] = []
    lugares_compra_resumen: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class ComparacionPlanificacionRespuestaSchema(BaseModel):
    id_planificacion: int
    presupuesto: Decimal
    cantidad_personas: int
    tipo_comida: str
    total_alternativas: int
    alternativas: List[AlternativaComparacionSchema]
    mejor_opcion_costo: Optional[AlternativaComparacionSchema] = None
    mejor_opcion_puntuacion: Optional[AlternativaComparacionSchema] = None

    model_config = ConfigDict(from_attributes=True)
