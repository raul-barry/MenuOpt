// CASO DE USO: CU12 - Definir preferencias
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Preferencia,
  UsuarioPreferencias,
  UsuarioPreferenciasUpdate
} from '../models/preferencia.model';

@Injectable({
  providedIn: 'root'
})
export class PreferenciaService {
  private http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  // Catálogo completo de preferencias activas
  listarPreferencias(): Observable<Preferencia[]> {
    return this.http.get<Preferencia[]>(`${this.apiUrl}/preferencias`);
  }

  // Preferencias actuales del usuario autenticado
  obtenerPreferenciasUsuario(): Observable<UsuarioPreferencias> {
    return this.http.get<UsuarioPreferencias>(`${this.apiUrl}/usuarios/preferencias`);
  }

  // Guardar preferencias del usuario autenticado
  guardarPreferenciasUsuario(idsPreferencias: number[]): Observable<UsuarioPreferencias> {
    const payload: UsuarioPreferenciasUpdate = { preferencias: idsPreferencias };
    return this.http.put<UsuarioPreferencias>(`${this.apiUrl}/usuarios/preferencias`, payload);
  }
}
