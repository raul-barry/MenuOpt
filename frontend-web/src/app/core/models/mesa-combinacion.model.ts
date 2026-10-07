// CASO DE USO: CU19 - Definir combinación de mesas
export interface MesaCombinacion {
  id_mesa_combinacion: number;
  id_mesa_origen: number;
  id_mesa_destino: number;
  permitida: boolean;
  descripcion?: string | null;
  activo: boolean;
  fecha_creacion: string;
  numero_mesa_origen?: string | null;
  numero_mesa_destino?: string | null;
  capacidad_total?: number | null;
}

export interface MesaCombinacionCrear {
  id_mesa_origen: number;
  id_mesa_destino: number;
  permitida?: boolean;
  descripcion?: string | null;
}
