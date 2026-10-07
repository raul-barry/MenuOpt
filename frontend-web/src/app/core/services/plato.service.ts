import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Plato, CrearPlatoRequest, ActualizarPlatoRequest } from '../models/plato.model';
import {
  PlatoIngredienteDetalle,
  AsociarIngredientePlatoRequest,
  ActualizarIngredientePlatoRequest
} from '../models/ingrediente.model';

@Injectable({
  providedIn: 'root'
})
export class PlatoService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  // =========================================================================
  // CASO DE USO: CU08 - GESTIONAR PLATOS
  // =========================================================================
  getPlatosPorRestaurante(
    idRestaurante: number,
    categoria?: number,
    tipoComida?: string,
    disponible?: boolean,
    estado?: string
  ): Observable<Plato[]> {
    let params = new HttpParams();
    if (categoria) params = params.set('categoria', categoria.toString());
    if (tipoComida) params = params.set('tipo_comida', tipoComida);
    if (disponible !== undefined && disponible !== null) params = params.set('disponible', disponible.toString());
    if (estado) params = params.set('estado', estado);

    return this.http.get<Plato[]>(`${this.baseUrl}/restaurantes/${idRestaurante}/platos`, { params });
  }

  getPlato(id: number): Observable<Plato> {
    return this.http.get<Plato>(`${this.baseUrl}/platos/${id}`);
  }

  crearPlato(idRestaurante: number, datos: CrearPlatoRequest): Observable<Plato> {
    return this.http.post<Plato>(`${this.baseUrl}/restaurantes/${idRestaurante}/platos`, datos);
  }

  updatePlato(id: number, datos: ActualizarPlatoRequest): Observable<Plato> {
    return this.http.put<Plato>(`${this.baseUrl}/platos/${id}`, datos);
  }

  cambiarEstado(id: number, estado: 'ACTIVO' | 'INACTIVO'): Observable<Plato> {
    return this.http.patch<Plato>(`${this.baseUrl}/platos/${id}/estado`, { estado });
  }

  // =========================================================================
  // CASO DE USO: CU10 - GESTIONAR DISPONIBILIDAD
  // =========================================================================
  cambiarDisponibilidad(id: number, disponible: boolean): Observable<Plato> {
    return this.http.patch<Plato>(`${this.baseUrl}/platos/${id}/disponibilidad`, { disponible });
  }

  // =========================================================================
  // CASO DE USO: CU09 - COMPOSICIÓN DE PLATOS E INGREDIENTES
  // =========================================================================
  getIngredientesPlato(idPlato: number): Observable<PlatoIngredienteDetalle[]> {
    return this.http.get<PlatoIngredienteDetalle[]>(`${this.baseUrl}/platos/${idPlato}/ingredientes`);
  }

  asociarIngrediente(idPlato: number, datos: AsociarIngredientePlatoRequest): Observable<PlatoIngredienteDetalle> {
    return this.http.post<PlatoIngredienteDetalle>(`${this.baseUrl}/platos/${idPlato}/ingredientes`, datos);
  }

  updateIngredientePlato(
    idPlato: number,
    idIngrediente: number,
    datos: ActualizarIngredientePlatoRequest
  ): Observable<PlatoIngredienteDetalle> {
    return this.http.put<PlatoIngredienteDetalle>(
      `${this.baseUrl}/platos/${idPlato}/ingredientes/${idIngrediente}`,
      datos
    );
  }

  quitarIngrediente(idPlato: number, idIngrediente: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(
      `${this.baseUrl}/platos/${idPlato}/ingredientes/${idIngrediente}`
    );
  }
}
