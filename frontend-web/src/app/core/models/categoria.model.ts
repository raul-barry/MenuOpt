export interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion?: string;
  activo: boolean;
}

export interface CrearCategoriaRequest {
  nombre: string;
  descripcion?: string;
  activo?: boolean;
}

export interface ActualizarCategoriaRequest {
  nombre?: string;
  descripcion?: string;
  activo?: boolean;
}
