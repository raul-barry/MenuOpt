// CASO DE USO: CU26 - Modelos TypeScript para Asistencia con IA

export interface ContextoPrevio {
  presupuesto?: number | null;
  cantidad_personas?: number | null;
  tipo_comida?: string | null;
  ubicacion_referencia?: string | null;
  preferencias_detectadas?: string[];
}

export interface SolicitudInterpretar {
  mensaje: string;
  contexto_previo?: ContextoPrevio | null;
}

export interface PreferenciaCoincidencia {
  nombre_detectado: string;
  id_preferencia?: number | null;
  registrada: boolean;
}

export interface SolicitudInterpretada {
  presupuesto?: number | null;
  cantidad_personas?: number | null;
  tipo_comida?: string | null;
  ubicacion_referencia?: string | null;
  preferencias_detectadas: string[];
  preferencias_validadas: PreferenciaCoincidencia[];
  datos_faltantes: string[];
  mensaje_asistente: string;
  listo_para_crear: boolean;
}

export interface SolicitudExplicarRecomendacion {
  id_recomendacion: number;
}

export interface SolicitudExplicarComparacion {
  id_planificacion: number;
}

export interface ExplicacionRespuesta {
  id_referencia: number;
  tipo: 'RECOMENDACION' | 'COMPARACION';
  explicacion: string;
  detalles_clave: string[];
}

export interface MensajeChat {
  emisor: 'usuario' | 'asistente';
  texto: string;
  fecha: Date;
  interpretacion?: SolicitudInterpretada | null;
}
