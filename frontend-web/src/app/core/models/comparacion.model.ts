// CASO DE USO: CU14 - Comparar alternativas (RESTAURANTE vs PREPARACION_PROPIA)
import { RecomendacionPlatoItem } from './recomendacion.model';

export interface AlternativaComparacion {
  id_recomendacion: number;
  tipo_recomendacion: 'RESTAURANTE' | 'PREPARACION_PROPIA';
  nombre: string;
  costo_total: number | string;
  costo_por_persona: number | string;
  ahorro_respecto_presupuesto: number | string;
  porcentaje_presupuesto_utilizado: number | string;
  puntuacion: number | string;
  distancia_estimada?: number | string | null;
  resumen: string;

  // Restaurante
  id_restaurante?: number | null;
  nombre_restaurante?: string | null;
  imagen_url_restaurante?: string | null;
  zona_restaurante?: string | null;
  direccion_restaurante?: string | null;
  platos: RecomendacionPlatoItem[];

  // Preparacion propia
  id_preparacion_propia?: number | null;
  nombre_preparacion?: string | null;
  ingredientes_resumen: string[];
  lugares_compra_resumen: string[];
}

export interface ComparacionPlanificacion {
  id_planificacion: number;
  presupuesto: number | string;
  cantidad_personas: number;
  tipo_comida: string;
  total_alternativas: number;
  alternativas: AlternativaComparacion[];
  mejor_opcion_costo?: AlternativaComparacion | null;
  mejor_opcion_puntuacion?: AlternativaComparacion | null;
}
