// CASO DE USO: CU18 - Gestionar mesas
export type FormaMesa = 'REDONDA' | 'CUADRADA' | 'RECTANGULAR';

export interface Mesa {
  id_mesa: number;
  id_area: number;
  numero: string;
  nombre?: string | null;
  capacidad: number;
  forma: FormaMesa;
  posicion_x: number;
  posicion_y: number;
  rotacion: number;
  ancho: number;
  alto: number;
  es_fija: boolean;
  combinable: boolean;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string | null;
}

export interface MesaCrear {
  numero: string;
  nombre?: string | null;
  capacidad: number;
  forma?: FormaMesa;
  posicion_x?: number;
  posicion_y?: number;
  rotacion?: number;
  ancho?: number;
  alto?: number;
  es_fija?: boolean;
  combinable?: boolean;
}

export interface MesaActualizar {
  numero?: string;
  nombre?: string | null;
  capacidad?: number;
  forma?: FormaMesa;
  posicion_x?: number;
  posicion_y?: number;
  rotacion?: number;
  ancho?: number;
  alto?: number;
  es_fija?: boolean;
  combinable?: boolean;
  activo?: boolean;
}

export interface MesaPosicionActualizar {
  id_mesa: number;
  posicion_x: number;
  posicion_y: number;
  rotacion?: number;
}
