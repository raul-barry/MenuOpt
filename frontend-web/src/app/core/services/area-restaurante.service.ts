// CASO DE USO: CU17 - Crear plano 2D del restaurante (Gestión de Áreas)
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  AreaRestaurante,
  AreaRestauranteCrear,
  AreaRestauranteActualizar,
  CambiarEstadoArea
} from '../models/area-restaurante.model';

@Injectable({
  providedIn: 'root'
})
export class AreaRestauranteService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  listarAreasPorRestaurante(idRestaurante: number, soloActivas: boolean = true): Observable<AreaRestaurante[]> {
    const params = new HttpParams().set('solo_activas', soloActivas.toString());
    return this.http.get<AreaRestaurante[]>(`${this.baseUrl}/restaurantes/${idRestaurante}/areas`, { params });
  }

  obtenerArea(idArea: number): Observable<AreaRestaurante> {
    return this.http.get<AreaRestaurante>(`${this.baseUrl}/areas/${idArea}`);
  }

  crearArea(idRestaurante: number, datos: AreaRestauranteCrear): Observable<AreaRestaurante> {
    return this.http.post<AreaRestaurante>(`${this.baseUrl}/restaurantes/${idRestaurante}/areas`, datos);
  }

  actualizarArea(idArea: number, datos: AreaRestauranteActualizar): Observable<AreaRestaurante> {
    return this.http.put<AreaRestaurante>(`${this.baseUrl}/areas/${idArea}`, datos);
  }

  cambiarEstado(idArea: number, activo: boolean): Observable<AreaRestaurante> {
    const payload: CambiarEstadoArea = { activo };
    return this.http.patch<AreaRestaurante>(`${this.baseUrl}/areas/${idArea}/estado`, payload);
  }

  desactivarArea(idArea: number): Observable<AreaRestaurante> {
    return this.http.delete<AreaRestaurante>(`${this.baseUrl}/areas/${idArea}`);
  }
}
