# CASO DE USO: CU08 - Gestionar preferencias en platos
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.preferencia import PreferenciaRespuestaSchema


class ActualizarPreferenciasPlatoSchema(BaseModel):
    preferencias: Optional[List[int]] = Field(
        None,
        description="Lista de IDs de preferencias gastronómicas asociadas al plato"
    )
    preferencias_ids: Optional[List[int]] = Field(
        None,
        description="Alias de lista de IDs de preferencias gastronómicas asociadas al plato"
    )

    def obtener_ids(self) -> List[int]:
        if self.preferencias is not None:
            return self.preferencias
        if self.preferencias_ids is not None:
            return self.preferencias_ids
        return []


class PlatoPreferenciasRespuestaSchema(BaseModel):
    id_plato: int
    nombre_plato: str
    preferencias: List[PreferenciaRespuestaSchema]
