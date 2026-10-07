// CASO DE USO: CU17 - Crear plano 2D del restaurante (Áreas)
export interface AreaRestaurante {
  id_area: number;
  id_restaurante: number;
  nombre: string;
  descripcion?: string | null;
  ancho_mapa: number;
  alto_mapa: number;
  orden: number;
  activo: boolean;
  fecha_creacion: string;
  fecha_actualizacion?: string | null;
  total_mesas?: number;
}

export interface AreaRestauranteCrear {
  nombre: string;
  descripcion?: string | null;
  ancho_mapa?: number;
  alto_mapa?: number;
  orden?: number;
}

export interface AreaRestauranteActualizar {
  nombre?: string;
  descripcion?: string | null;
  ancho_mapa?: number;
  alto_mapa?: number;
  orden?: number;
  activo?: boolean;
}

export interface CambiarEstadoArea {
  activo: boolean;
}
