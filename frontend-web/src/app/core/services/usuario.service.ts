import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Usuario,
  ActualizarPerfilRequest,
  CambiarContrasenaRequest,
  UsuariosPaginados
} from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/usuarios`;

  // =========================================================================
  // CASO DE USO: CU03 - GESTIONAR PERFIL
  // =========================================================================
  getPerfil(): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/perfil`);
  }

  updatePerfil(datos: ActualizarPerfilRequest): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.apiUrl}/perfil`, datos);
  }

  cambiarContrasena(datos: CambiarContrasenaRequest): Observable<{ mensaje: string }> {
    return this.http.put<{ mensaje: string }>(`${this.apiUrl}/perfil/contrasena`, datos);
  }

  // =========================================================================
  // CASO DE USO: CU04 - GESTIONAR USUARIOS (Solo ADMINISTRADOR)
  // =========================================================================
  getUsuarios(
    pagina = 1,
    limite = 10,
    estado?: string,
    rol?: string,
    busqueda?: string
  ): Observable<UsuariosPaginados> {
    let params = new HttpParams()
      .set('pagina', pagina.toString())
      .set('limite', limite.toString());

    if (estado) params = params.set('estado', estado);
    if (rol) params = params.set('rol', rol);
    if (busqueda) params = params.set('busqueda', busqueda);

    return this.http.get<UsuariosPaginados>(this.apiUrl, { params });
  }

  getUsuarioById(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/${id}`);
  }

  cambiarEstado(id: number, estado: 'ACTIVO' | 'INACTIVO'): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.apiUrl}/${id}/estado`, { estado });
  }
}
