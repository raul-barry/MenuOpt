# CASO DE USO: CU15 - Biblioteca de Recetas
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class RecetaIngredienteCrearSchema(BaseModel):
    id_ingrediente: Optional[int] = None
    nombre_ingrediente: str = Field(..., min_length=2, max_length=100)
    cantidad: Decimal = Field(..., gt=0)
    unidad_medida: str = Field(..., min_length=1, max_length=50)


class RecetaIngredienteRespuestaSchema(BaseModel):
    id_receta_ingrediente: int
    id_receta: int
    id_ingrediente: Optional[int] = None
    nombre_ingrediente: str
    cantidad: Decimal
    unidad_medida: str
    precio_referencial: Optional[Decimal] = None
    costo_subtotal: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class RecetaCrearSchema(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=255)
    instrucciones: Optional[str] = None
    tipo_comida: str = Field(default="ALMUERZO", max_length=50)
    porciones: int = Field(default=2, ge=1, le=50)
    tiempo_minutos: int = Field(default=30, ge=1, le=600)
    dificultad: str = Field(default="FACIL", max_length=50)
    origen: Optional[str] = Field(default="Tradicional Cruceña", max_length=100)
    imagen_url: Optional[str] = None
    ingredientes: List[RecetaIngredienteCrearSchema] = Field(default_factory=list)


class RecetaRespuestaSchema(BaseModel):
    id_receta: int
    nombre: str
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    tipo_comida: str
    porciones: int
    tiempo_minutos: int
    dificultad: str
    origen: Optional[str] = None
    imagen_url: Optional[str] = None
    fecha_creacion: datetime
    id_usuario_creador: Optional[int] = None
    nombre_creador: Optional[str] = None
    ingredientes: List[RecetaIngredienteRespuestaSchema] = []
    total_ingredientes: int = 0
    costo_estimado_insumos: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class RecetaConsultaIASchema(BaseModel):
    mensaje: str = Field(..., min_length=3, description="Mensaje del usuario con ingredientes o preguntas")
    comensales: Optional[int] = Field(None, ge=1, le=50, description="Cantidad deseada de comensales")


class RecetaIngredienteFaltanteSchema(BaseModel):
    nombre: str
    cantidad_requerida: Decimal
    unidad_medida: str
    tienda_sugerida: Optional[str] = None
    precio_referencial: Optional[Decimal] = None


class RecetaTiendaRecomendadaSchema(BaseModel):
    nombre_tienda: str
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    insumos_disponibles: List[str] = []
    costo_estimado: Optional[Decimal] = None


class RecetaConsultaIARespuestaSchema(BaseModel):
    mensaje_usuario: str
    respuesta_ia: str
    porciones_sugeridas: int
    platos_sugeridos: List[RecetaRespuestaSchema] = []
    ingredientes_faltantes: List[RecetaIngredienteFaltanteSchema] = []
    tiendas_recomendadas: List[RecetaTiendaRecomendadaSchema] = []

