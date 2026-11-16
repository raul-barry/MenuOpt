// CASO DE USO: CU15 - Biblioteca de Recetas
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Receta, RecetaCrear } from '../models/receta.model';

@Injectable({
  providedIn: 'root'
})
export class RecetaService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/recetas`;

  listarRecetas(tipoComida?: string, busqueda?: string): Observable<Receta[]> {
    let params = new HttpParams();
    if (tipoComida && tipoComida !== 'TODAS') {
      params = params.set('tipo_comida', tipoComida);
    }
    if (busqueda && busqueda.trim()) {
      params = params.set('busqueda', busqueda.trim());
    }
    return this.http.get<Receta[]>(this.apiUrl, { params });
  }

  obtenerReceta(idReceta: number): Observable<Receta> {
    return this.http.get<Receta>(`${this.apiUrl}/${idReceta}`);
  }

  crearReceta(receta: RecetaCrear): Observable<Receta> {
    return this.http.post<Receta>(this.apiUrl, receta);
  }

  eliminarReceta(idReceta: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(`${this.apiUrl}/${idReceta}`);
  }
}
