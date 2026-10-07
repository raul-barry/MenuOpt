// CASO DE USO: CU18 - Gestionar mesas
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Mesa, MesaCrear, MesaActualizar } from '../models/mesa.model';

@Injectable({
  providedIn: 'root'
})
export class MesaService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  listarMesasPorArea(idArea: number, soloActivas: boolean = true): Observable<Mesa[]> {
    const params = new HttpParams().set('solo_activas', soloActivas.toString());
    return this.http.get<Mesa[]>(`${this.baseUrl}/areas/${idArea}/mesas`, { params });
  }

  obtenerMesa(idMesa: number): Observable<Mesa> {
    return this.http.get<Mesa>(`${this.baseUrl}/mesas/${idMesa}`);
  }

  crearMesa(idArea: number, datos: MesaCrear): Observable<Mesa> {
    return this.http.post<Mesa>(`${this.baseUrl}/areas/${idArea}/mesas`, datos);
  }

  actualizarMesa(idMesa: number, datos: MesaActualizar): Observable<Mesa> {
    return this.http.put<Mesa>(`${this.baseUrl}/mesas/${idMesa}`, datos);
  }

  cambiarEstado(idMesa: number, activo: boolean): Observable<Mesa> {
    return this.http.patch<Mesa>(`${this.baseUrl}/mesas/${idMesa}/estado`, { activo });
  }

  desactivarMesa(idMesa: number): Observable<Mesa> {
    return this.http.delete<Mesa>(`${this.baseUrl}/mesas/${idMesa}`);
  }
}
