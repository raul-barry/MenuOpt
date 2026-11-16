import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { BitacoraListadoPaginado } from '../models/bitacora.model';

@Injectable({
  providedIn: 'root'
})
export class BitacoraService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/bitacora`;

  /**
   * CU25: Consultar bitácora del sistema
   */
  getBitacora(
    pagina = 1,
    limite = 20,
    modulo?: string,
    accion?: string,
    fechaDesde?: string,
    fechaHasta?: string,
    busqueda?: string
  ): Observable<BitacoraListadoPaginado> {
    let params = new HttpParams()
      .set('pagina', pagina.toString())
      .set('limite', limite.toString());

    if (modulo && modulo.trim()) {
      params = params.set('modulo', modulo.trim());
    }
    if (accion && accion.trim()) {
      params = params.set('accion', accion.trim());
    }
    if (fechaDesde && fechaDesde.trim()) {
      params = params.set('fecha_desde', fechaDesde.trim());
    }
    if (fechaHasta && fechaHasta.trim()) {
      params = params.set('fecha_hasta', fechaHasta.trim());
    }
    if (busqueda && busqueda.trim()) {
      params = params.set('busqueda', busqueda.trim());
    }

    return this.http.get<BitacoraListadoPaginado>(this.apiUrl, { params });
  }
}
