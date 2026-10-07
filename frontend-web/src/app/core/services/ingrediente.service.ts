import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Ingrediente,
  CrearIngredienteRequest,
  ActualizarIngredienteRequest
} from '../models/ingrediente.model';

@Injectable({
  providedIn: 'root'
})
export class IngredienteService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/ingredientes`;

  // =========================================================================
  // CASO DE USO: CU09 - GESTIONAR INGREDIENTES
  // =========================================================================
  getIngredientes(estado?: string): Observable<Ingrediente[]> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);
    return this.http.get<Ingrediente[]>(this.apiUrl, { params });
  }

  getIngrediente(id: number): Observable<Ingrediente> {
    return this.http.get<Ingrediente>(`${this.apiUrl}/${id}`);
  }

  crearIngrediente(datos: CrearIngredienteRequest): Observable<Ingrediente> {
    return this.http.post<Ingrediente>(this.apiUrl, datos);
  }

  updateIngrediente(id: number, datos: ActualizarIngredienteRequest): Observable<Ingrediente> {
    return this.http.put<Ingrediente>(`${this.apiUrl}/${id}`, datos);
  }
}
