export interface Rol {
  id_rol: number;
  nombre: string;
  descripcion?: string;
  activo: boolean;
}

export interface Usuario {
  id_usuario: number;
  nombres: string;
  apellidos: string;
  correo: string;
  telefono?: string;
  estado: string;
  fecha_registro: string;
  fecha_actualizacion: string;
  id_rol: number;
  rol?: Rol;
}

export interface LoginRequest {
  correo: string;
  contrasena: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}

export interface RegistroRequest {
  nombres: string;
  apellidos: string;
  correo: string;
  contrasena: string;
  telefono?: string;
}

export interface ActualizarPerfilRequest {
  nombres?: string;
  apellidos?: string;
  telefono?: string;
  correo?: string;
}

export interface CambiarContrasenaRequest {
  contrasena_actual: string;
  contrasena_nueva: string;
}

export interface UsuariosPaginados {
  total: number;
  pagina: number;
  limite: number;
  total_paginas: number;
  usuarios: Usuario[];
}
