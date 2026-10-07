// CASO DE USO: CU12 - Definir preferencias
export interface Preferencia {
  id_preferencia: number;
  nombre: string;
  descripcion?: string;
  categoria: string;
  activo: boolean;
}

export interface UsuarioPreferencias {
  id_usuario: number;
  preferencias: Preferencia[];
}

export interface UsuarioPreferenciasUpdate {
  preferencias: number[];
}
