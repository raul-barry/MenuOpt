// CASO DE USO: CU17 - Crear plano 2D del restaurante (Áreas y Espacios)

export type TipoEspacioPlano =
  | 'CAJA'
  | 'ACCESO'
  | 'JUEGOS'
  | 'BANOS'
  | 'ESCALERA'
  | 'RETIRO'
  | 'BARRA'
  | 'COCINA'
  | 'ESPERA'
  | 'TERRAZA'
  | 'ESCENARIO'
  | 'PERSONALIZADO'
  | 'OTRO';

export interface EspacioPlano {
  id: string;
  tipo: TipoEspacioPlano;
  nombre: string;
  posicion_x: number;
  posicion_y: number;
  ancho?: number;
  alto?: number;
  rotacion?: number;
  icono?: string;
}

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
  elementos?: EspacioPlano[] | null;
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
