// CASO DE USO: CU13 - Generar recomendación
export type TipoRecomendacion = 'RESTAURANTE' | 'PREPARACION_PROPIA';

export interface RecomendacionPlatoItem {
  id_recomendacion_plato: number;
  id_plato: number;
  nombre_plato: string;
  personas_cubiertas: number;
  cantidad: number;
  precio_unitario: number | string;
  subtotal: number | string;
}

export interface Recomendacion {
  id_recomendacion: number;
  id_planificacion: number;
  tipo_recomendacion: TipoRecomendacion;
  nombre?: string;
  descripcion?: string;
  costo_total: number | string;
  costo_por_persona: number | string;
  puntuacion: number | string;
  distancia_estimada?: number | string | null;
  id_restaurante?: number | null;
  nombre_restaurante?: string | null;
  zona_restaurante?: string | null;
  direccion_restaurante?: string | null;
  id_preparacion_propia?: number | null;
  nombre_preparacion?: string | null;
  fecha_generacion: string;
  platos: RecomendacionPlatoItem[];
}
