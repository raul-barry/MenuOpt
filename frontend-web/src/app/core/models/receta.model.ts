// CASO DE USO: CU15 - Biblioteca de Recetas
export interface RecetaIngrediente {
  id_receta_ingrediente?: number;
  id_receta?: number;
  id_ingrediente?: number | null;
  nombre_ingrediente: string;
  cantidad: number;
  unidad_medida: string;
  precio_referencial?: number | null;
  costo_subtotal?: number | null;
}

export interface Receta {
  id_receta: number;
  nombre: string;
  descripcion?: string | null;
  instrucciones?: string | null;
  tipo_comida: string;
  porciones: number;
  tiempo_minutos: number;
  dificultad: string;
  origen?: string | null;
  imagen_url?: string | null;
  fecha_creacion: string;
  id_usuario_creador?: number | null;
  nombre_creador?: string | null;
  ingredientes: RecetaIngrediente[];
  total_ingredientes: number;
  costo_estimado_insumos?: number | null;
}

export interface RecetaCrear {
  nombre: string;
  descripcion?: string | null;
  instrucciones?: string | null;
  tipo_comida: string;
  porciones: number;
  tiempo_minutos: number;
  dificultad: string;
  origen?: string | null;
  imagen_url?: string | null;
  ingredientes: {
    id_ingrediente?: number | null;
    nombre_ingrediente: string;
    cantidad: number;
    unidad_medida: string;
  }[];
}
