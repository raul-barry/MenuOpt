// CASO DE USO: CU26 - Servicio Angular para Asistente IA
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  SolicitudInterpretar,
  SolicitudInterpretada,
  SolicitudExplicarRecomendacion,
  SolicitudExplicarComparacion,
  ExplicacionRespuesta
} from '../models/asistente-ia.model';

@Injectable({
  providedIn: 'root'
})
export class AsistenteIAService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  // CU26: Interpretar lenguaje natural
  interpretar(solicitud: SolicitudInterpretar): Observable<SolicitudInterpretada> {
    return this.http.post<SolicitudInterpretada>(`${this.baseUrl}/asistente/interpretar`, solicitud);
  }

  // CU26: Explicar recomendación
  explicarRecomendacion(idRecomendacion: number): Observable<ExplicacionRespuesta> {
    const payload: SolicitudExplicarRecomendacion = { id_recomendacion: idRecomendacion };
    return this.http.post<ExplicacionRespuesta>(`${this.baseUrl}/asistente/explicar-recomendacion`, payload);
  }

  // CU26: Explicar comparación
  explicarComparacion(idPlanificacion: number): Observable<ExplicacionRespuesta> {
    const payload: SolicitudExplicarComparacion = { id_planificacion: idPlanificacion };
    return this.http.post<ExplicacionRespuesta>(`${this.baseUrl}/asistente/explicar-comparacion`, payload);
  }
}
