export interface Ingrediente {
  id_ingrediente: number;
  nombre: string;
  unidad_medida: string;
  precio_estimado?: number | null;
  descripcion?: string;
  estado: string;
}

export interface CrearIngredienteRequest {
  nombre: string;
  unidad_medida: string;
  precio_estimado?: number | null;
  descripcion?: string;
  estado?: string;
}

export interface ActualizarIngredienteRequest {
  nombre?: string;
  unidad_medida?: string;
  precio_estimado?: number | null;
  descripcion?: string;
  estado?: string;
}

export interface PlatoIngredienteDetalle {
  id_plato_ingrediente: number;
  id_ingrediente: number;
  nombre_ingrediente: string;
  cantidad: number;
  unidad_medida: string;
  precio_estimado?: number | null;
}

export interface AsociarIngredientePlatoRequest {
  id_ingrediente: number;
  cantidad: number;
  unidad_medida: string;
}

export interface ActualizarIngredientePlatoRequest {
  cantidad: number;
  unidad_medida: string;
}
