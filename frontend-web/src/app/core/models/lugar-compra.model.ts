// CASO DE USO: CU16 - Consultar lugares de compra
export interface ItemCompraLugar {
  id_ingrediente: number;
  nombre_ingrediente: string;
  cantidad_requerida: number | string;
  unidad_medida: string;
  precio_referencia: number | string;
  subtotal: number | string;
}

export interface AgrupacionCompraLugarItem {
  id_lugar_compra?: number | null;
  nombre_lugar: string;
  tipo_lugar?: string | null;
  telefono?: string | null;
  direccion?: string | null;
  zona?: string | null;
  ciudad?: string | null;
  items: ItemCompraLugar[];
  subtotal_estimado: number | string;
}

export interface LugaresCompraRecomendacion {
  id_recomendacion: number;
  id_planificacion: number;
  nombre_preparacion: string;
  costo_total_estimado: number | string;
  cantidad_personas: number;
  total_lugares: number;
  lugares: AgrupacionCompraLugarItem[];
}
