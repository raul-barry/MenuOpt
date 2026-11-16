// CASO DE USO: CU20, CU21, CU22 - Modelos de Reserva y Disponibilidad
import { EspacioPlano } from './area-restaurante.model';

export type EstadoDisponibilidadMesa = 'DISPONIBLE' | 'NO_DISPONIBLE' | 'NO_COMPATIBLE' | 'SELECCIONADA';
export type EstadoReserva = 'PENDIENTE' | 'CONFIRMADA' | 'CANCELADA' | 'FINALIZADA';

export interface MesaDisponibilidad {
  id_mesa: number;
  numero: string;
  nombre?: string | null;
  capacidad: number;
  forma: 'REDONDA' | 'CUADRADA' | 'RECTANGULAR';
  posicion_x: number;
  posicion_y: number;
  rotacion: number;
  ancho: number;
  alto: number;
  es_fija: boolean;
  combinable: boolean;
  estado_disponibilidad: EstadoDisponibilidadMesa;
  compatible_capacidad: boolean;
  seleccionable: boolean;
}

export interface CombinacionDisponible {
  id_combinacion: number;
  mesas: number[];
  numeros_mesas: string[];
  capacidad_total: number;
  disponible: boolean;
  seleccionable: boolean;
  descripcion?: string | null;
}

export interface ConsultaDisponibilidad {
  id_area: number;
  fecha: string;        // YYYY-MM-DD
  hora_inicio: string;  // HH:MM:SS o HH:MM
  hora_fin: string;     // HH:MM:SS o HH:MM
  cantidad_personas: number;
}

export interface DisponibilidadRespuesta {
  id_area: number;
  nombre_area: string;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  cantidad_personas: number;
  mesas: MesaDisponibilidad[];
  combinaciones: CombinacionDisponible[];
  elementos?: EspacioPlano[];
}

export interface MesaResumenReserva {
  id_mesa: number;
  numero: string;
  nombre?: string | null;
  capacidad: number;
}

export interface ReservaCrear {
  id_restaurante: number;
  id_area: number;
  fecha_reserva: string;
  hora_inicio: string;
  hora_fin: string;
  cantidad_personas: number;
  mesas: number[];
  id_planificacion?: number | null;
  observaciones?: string | null;
}

export interface ReservaRespuesta {
  id_reserva: number;
  id_restaurante: number;
  nombre_restaurante: string;
  id_area?: number | null;
  nombre_area?: string | null;
  fecha_reserva: string;
  hora_inicio: string;
  hora_fin: string;
  cantidad_personas: number;
  estado: EstadoReserva;
  observaciones?: string | null;
  id_usuario: number;
  nombre_cliente?: string | null;
  correo_cliente?: string | null;
  telefono_cliente?: string | null;
  id_planificacion?: number | null;
  mesas: MesaResumenReserva[];
  fecha_creacion: string;
}

export interface ReservaEstadoActualizar {
  estado: EstadoReserva;
}

// =========================================================================
// GESTIÓN DE INVITADOS DE LA RESERVA (Codex / Sprint Extensión CU21)
// =========================================================================
export interface ReservaInvitadoCrear {
  id_usuario?: number | null;
  nombre?: string | null;
  correo?: string | null;
}

export interface ReservaInvitadoRespuesta {
  id_invitado: number;
  id_reserva: number;
  id_usuario?: number | null;
  nombre: string;
  correo?: string | null;
  fecha_creacion: string;
}

