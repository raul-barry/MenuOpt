// CASO DE USO: CU11 - Registrar planificación gastronómica
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Planificacion,
  PlanificacionCrear,
  PlanificacionActualizar,
  PlanificacionesPaginadas
} from '../models/planificacion.model';

@Injectable({
  providedIn: 'root'
})
export class PlanificacionService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/planificaciones`;

  crearPlanificacion(datos: PlanificacionCrear): Observable<Planificacion> {
    return this.http.post<Planificacion>(this.apiUrl, datos);
  }

  listarMisPlanificaciones(pagina: number = 1, limite: number = 20, estado?: string): Observable<PlanificacionesPaginadas> {
    let params = new HttpParams()
      .set('pagina', pagina.toString())
      .set('limite', limite.toString());

    if (estado) {
      params = params.set('estado', estado);
    }

    return this.http.get<PlanificacionesPaginadas>(`${this.apiUrl}/mis-planificaciones`, { params });
  }

  obtenerPlanificacion(idPlanificacion: number): Observable<Planificacion> {
    return this.http.get<Planificacion>(`${this.apiUrl}/${idPlanificacion}`);
  }

  actualizarPlanificacion(idPlanificacion: number, datos: PlanificacionActualizar): Observable<Planificacion> {
    return this.http.put<Planificacion>(`${this.apiUrl}/${idPlanificacion}`, datos);
  }

  cambiarEstado(idPlanificacion: number, estado: 'ACTIVA' | 'CANCELADA' | 'BORRADOR'): Observable<Planificacion> {
    return this.http.patch<Planificacion>(`${this.apiUrl}/${idPlanificacion}/estado`, { estado });
  }

  cancelarPlanificacion(idPlanificacion: number): Observable<Planificacion> {
    return this.cambiarEstado(idPlanificacion, 'CANCELADA');
  }
}
