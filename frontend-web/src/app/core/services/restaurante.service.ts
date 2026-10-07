import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Restaurante,
  RegistrarRestauranteRequest,
  ActualizarRestauranteRequest
} from '../models/restaurante.model';

@Injectable({
  providedIn: 'root'
})
export class RestauranteService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/restaurantes`;

  // =========================================================================
  // CASO DE USO: CU05 - REGISTRAR RESTAURANTE
  // =========================================================================
  crearRestaurante(datos: RegistrarRestauranteRequest): Observable<Restaurante> {
    return this.http.post<Restaurante>(this.apiUrl, datos);
  }

  // =========================================================================
  // CASO DE USO: CU06 - GESTIONAR RESTAURANTE
  // =========================================================================
  getMisRestaurantes(): Observable<Restaurante[]> {
    return this.http.get<Restaurante[]>(`${this.apiUrl}/mis-restaurantes`);
  }

  getRestaurante(id: number): Observable<Restaurante> {
    return this.http.get<Restaurante>(`${this.apiUrl}/${id}`);
  }

  updateRestaurante(id: number, datos: ActualizarRestauranteRequest): Observable<Restaurante> {
    return this.http.put<Restaurante>(`${this.apiUrl}/${id}`, datos);
  }

  cambiarEstado(id: number, estado: 'ACTIVO' | 'INACTIVO'): Observable<Restaurante> {
    return this.http.patch<Restaurante>(`${this.apiUrl}/${id}/estado`, { estado });
  }
}
