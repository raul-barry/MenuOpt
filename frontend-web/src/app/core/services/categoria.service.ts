import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Categoria,
  CrearCategoriaRequest,
  ActualizarCategoriaRequest
} from '../models/categoria.model';

@Injectable({
  providedIn: 'root'
})
export class CategoriaService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/categorias`;

  // =========================================================================
  // CASO DE USO: CU07 - GESTIONAR CATEGORÍAS
  // =========================================================================
  getCategorias(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(this.apiUrl);
  }

  crearCategoria(datos: CrearCategoriaRequest): Observable<Categoria> {
    return this.http.post<Categoria>(this.apiUrl, datos);
  }

  updateCategoria(id: number, datos: ActualizarCategoriaRequest): Observable<Categoria> {
    return this.http.put<Categoria>(`${this.apiUrl}/${id}`, datos);
  }
}
