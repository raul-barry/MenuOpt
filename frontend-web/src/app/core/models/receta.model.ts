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

export interface RecetaConsultaIA {
  mensaje: string;
  comensales?: number | null;
}

export interface RecetaIngredienteFaltante {
  nombre: string;
  cantidad_requerida: number;
  unidad_medida: string;
  tienda_sugerida?: string | null;
  precio_referencial?: number | null;
}

export interface RecetaTiendaRecomendada {
  nombre_tienda: string;
  tipo?: string | null;
  insumos_disponibles: string[];
  costo_estimado?: number | null;
}

export interface RecetaConsultaIARespuesta {
  mensaje_usuario: string;
  respuesta_ia: string;
  porciones_sugeridas: number;
  platos_sugeridos: Receta[];
  ingredientes_faltantes: RecetaIngredienteFaltante[];
  tiendas_recomendadas: RecetaTiendaRecomendada[];
}
