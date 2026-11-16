// CASO DE USO: CU09 - Gestionar proveedores & CU16 - Consultar lugares de compra

export interface UbicacionSimple {
  id_ubicacion?: number;
  direccion: string;
  zona?: string | null;
  ciudad: string;
  latitud?: number | null;
  longitud?: number | null;
  referencia?: string | null;
}

export interface LugarCompra {
  id_lugar_compra: number;
  nombre: string;
  tipo?: string | null;
  telefono?: string | null;
  estado: string;
  id_ubicacion?: number | null;
  id_usuario_responsable?: number | null;
  ubicacion?: UbicacionSimple | null;
}

export interface CrearLugarCompraRequest {
  nombre: string;
  tipo?: string;
  telefono?: string;
  id_ubicacion?: number;
  ubicacion?: UbicacionSimple;
  id_usuario_responsable?: number;
}

export interface ActualizarLugarCompraRequest {
  nombre?: string;
  tipo?: string;
  telefono?: string;
  id_ubicacion?: number;
  ubicacion?: UbicacionSimple;
  id_usuario_responsable?: number;
}

export interface IngredienteLugarCompra {
  id_ingrediente_lugar_compra?: number;
  id_ingrediente: number;
  id_lugar_compra: number;
  nombre_ingrediente?: string;
  precio: number;
  cantidad_referencia: number;
  unidad_medida: string;
  disponible: boolean;
  fecha_actualizacion?: string;
}

export interface AsociarIngredienteLugarCompraRequest {
  id_ingrediente?: number | null;
  nombre_ingrediente?: string | null;
  precio: number;
  cantidad_referencia: number;
  unidad_medida: string;
  disponible: boolean;
}

export interface ActualizarIngredienteLugarCompraRequest {
  precio?: number;
  cantidad_referencia?: number;
  unidad_medida?: string;
  disponible?: boolean;
}

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
