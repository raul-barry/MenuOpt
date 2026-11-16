export interface BitacoraRegistro {
  id_bitacora: number;
  id_usuario?: number | null;
  correo_usuario?: string | null;
  nombre_usuario?: string | null;
  accion: string;
  modulo: string;
  descripcion: string;
  direccion_ip?: string | null;
  detalles?: Record<string, any> | null;
  fecha_hora: string;
}

export interface BitacoraListadoPaginado {
  total: number;
  pagina: number;
  limite: number;
  total_paginas: number;
  items: BitacoraRegistro[];
}
