// CASO DE USO: CU19 - Definir combinación de mesas
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { MesaCombinacion, MesaCombinacionCrear } from '../models/mesa-combinacion.model';

@Injectable({
  providedIn: 'root'
})
export class MesaCombinacionService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  listarCombinacionesPorArea(idArea: number, soloActivas: boolean = false): Observable<MesaCombinacion[]> {
    const params = new HttpParams().set('solo_activas', soloActivas.toString());
    return this.http.get<MesaCombinacion[]>(`${this.baseUrl}/areas/${idArea}/combinaciones`, { params });
  }

  crearCombinacion(datos: MesaCombinacionCrear, idArea?: number): Observable<MesaCombinacion> {
    if (idArea) {
      return this.http.post<MesaCombinacion>(`${this.baseUrl}/areas/${idArea}/combinaciones`, datos);
    }
    return this.http.post<MesaCombinacion>(`${this.baseUrl}/combinaciones`, datos);
  }

  desactivarCombinacion(idCombinacion: number): Observable<MesaCombinacion> {
    return this.http.delete<MesaCombinacion>(`${this.baseUrl}/combinaciones/${idCombinacion}`);
  }
}
