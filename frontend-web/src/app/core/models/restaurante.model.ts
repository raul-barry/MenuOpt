export interface Ubicacion {
  id_ubicacion?: number;
  direccion: string;
  zona?: string;
  ciudad: string;
  latitud?: number | null;
  longitud?: number | null;
  referencia?: string;
}

export interface Restaurante {
  id_restaurante: number;
  nombre: string;
  descripcion?: string;
  nit?: string;
  telefono?: string;
  correo?: string;
  horario_apertura?: string;
  horario_cierre?: string;
  estado: string;
  fecha_registro: string;
  fecha_actualizacion: string;
  id_usuario_responsable: number;
  id_ubicacion: number;
  ubicacion?: Ubicacion;
}

export interface RegistrarRestauranteRequest {
  nombre: string;
  descripcion?: string;
  nit?: string;
  telefono?: string;
  correo?: string;
  horario_apertura?: string;
  horario_cierre?: string;
  ubicacion: Ubicacion;
}

export interface ActualizarRestauranteRequest {
  nombre?: string | null;
  descripcion?: string | null;
  nit?: string | null;
  telefono?: string | null;
  correo?: string | null;
  horario_apertura?: string | null;
  horario_cierre?: string | null;
  ubicacion?: Partial<Ubicacion> | null;
}
