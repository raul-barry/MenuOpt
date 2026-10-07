// CASO DE USO: CU11 - Registrar planificación gastronómica
import { Preferencia } from './preferencia.model';

export type TipoComida = 'DESAYUNO' | 'ALMUERZO' | 'CENA' | 'MERIENDA' | 'OTRO';
export type EstadoPlanificacion = 'ACTIVA' | 'CANCELADA' | 'BORRADOR';

export const TIPOS_COMIDA: { valor: TipoComida; etiqueta: string }[] = [
  { valor: 'DESAYUNO', etiqueta: 'Desayuno' },
  { valor: 'ALMUERZO', etiqueta: 'Almuerzo' },
  { valor: 'CENA', etiqueta: 'Cena' },
  { valor: 'MERIENDA', etiqueta: 'Merienda' },
  { valor: 'OTRO', etiqueta: 'Otro' }
];

export interface Planificacion {
  id_planificacion: number;
  presupuesto: number | string;
  cantidad_personas: number;
  tipo_comida: string;
  ubicacion_referencia: string;
  fecha_planificacion: string;
  estado: string;
  id_usuario: number;
  preferencias: Preferencia[];
}

export interface PlanificacionCrear {
  presupuesto: number;
  cantidad_personas: number;
  tipo_comida: string;
  ubicacion_referencia: string;
  preferencias?: number[];
}

export interface PlanificacionActualizar {
  presupuesto?: number;
  cantidad_personas?: number;
  tipo_comida?: string;
  ubicacion_referencia?: string;
  preferencias?: number[];
}

export interface PlanificacionesPaginadas {
  total: number;
  pagina: number;
  limite: number;
  total_paginas: number;
  planificaciones: Planificacion[];
}
