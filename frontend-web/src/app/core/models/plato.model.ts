import { Categoria } from './categoria.model';

export interface Plato {
  id_plato: number;
  nombre: string;
  descripcion?: string;
  precio: number;
  tipo_comida?: string;
  personas_cubiertas: number;
  disponible: boolean;
  estado: string;
  fecha_registro: string;
  fecha_actualizacion: string;
  id_restaurante: number;
  id_categoria: number;
  categoria?: Categoria;
}

export interface CrearPlatoRequest {
  nombre: string;
  descripcion?: string;
  precio: number;
  tipo_comida?: string;
  personas_cubiertas: number;
  disponible?: boolean;
  id_categoria: number;
}

export interface ActualizarPlatoRequest {
  nombre?: string;
  descripcion?: string;
  precio?: number;
  tipo_comida?: string;
  personas_cubiertas?: number;
  disponible?: boolean;
  id_categoria?: number;
}
