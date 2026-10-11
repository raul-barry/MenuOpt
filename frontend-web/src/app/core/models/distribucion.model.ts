// CASO DE USO: CU17 - Plano 2D y Distribución de mesas
import { Mesa, MesaPosicionActualizar } from './mesa.model';

export interface GenerarDistribucionRequest {
  total_mesas?: number | null;
  distribucion_capacidades?: { [key: string]: number } | null;
  limpiar_existentes?: boolean;
}

export interface GuardarDistribucionRequest {
  mesas?: MesaPosicionActualizar[];
  posiciones?: MesaPosicionActualizar[];
}

export interface DistribucionRespuesta {
  id_area: number;
  nombre_area: string;
  ancho_mapa: number;
  alto_mapa: number;
  total_mesas: number;
  mesas: Mesa[];
  mensaje: string;
}
