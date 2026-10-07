// CASO DE USO: CU13 - Generar recomendación & CU14 - Comparar alternativas
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Recomendacion } from '../models/recomendacion.model';
import { ComparacionPlanificacion } from '../models/comparacion.model';

@Injectable({
  providedIn: 'root'
})
export class RecomendacionService {
  private http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  generarRecomendaciones(idPlanificacion: number): Observable<Recomendacion[]> {
    return this.http.post<Recomendacion[]>(
      `${this.apiUrl}/planificaciones/${idPlanificacion}/recomendaciones/generar`,
      {}
    );
  }

  listarRecomendaciones(idPlanificacion: number, tipo?: string): Observable<Recomendacion[]> {
    let params = new HttpParams();
    if (tipo) {
      params = params.set('tipo', tipo);
    }
    return this.http.get<Recomendacion[]>(
      `${this.apiUrl}/planificaciones/${idPlanificacion}/recomendaciones`,
      { params }
    );
  }

  obtenerRecomendacion(idRecomendacion: number): Observable<Recomendacion> {
    return this.http.get<Recomendacion>(`${this.apiUrl}/recomendaciones/${idRecomendacion}`);
  }

  compararAlternativas(idPlanificacion: number): Observable<ComparacionPlanificacion> {
    return this.http.get<ComparacionPlanificacion>(
      `${this.apiUrl}/planificaciones/${idPlanificacion}/comparacion`
    );
  }
}
