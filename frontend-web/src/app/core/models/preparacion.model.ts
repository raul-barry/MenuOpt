// CASO DE USO: CU15 - Consultar ingredientes para preparación propia
export interface PreparacionIngredienteItem {
  id_preparacion_ingrediente: number;
  id_ingrediente: number;
  nombre_ingrediente?: string;
  cantidad: number | string;
  unidad_medida: string;
  precio_unitario_usado?: number | string | null;
  costo_estimado: number | string;
  id_lugar_compra?: number | null;
  nombre_lugar_compra?: string | null;
}

export interface PreparacionPropia {
  id_preparacion_propia: number;
  id_recomendacion: number;
  nombre: string;
  descripcion?: string | null;
  cantidad_personas: number;
  costo_estimado: number | string;
  costo_por_persona: number | string;
  ingredientes: PreparacionIngredienteItem[];
}
