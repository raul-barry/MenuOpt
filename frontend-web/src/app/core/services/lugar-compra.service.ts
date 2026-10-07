// CASO DE USO: CU16 - Consultar lugares de compra
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LugaresCompraRecomendacion } from '../models/lugar-compra.model';

@Injectable({
  providedIn: 'root'
})
export class LugarCompraService {
  private http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  obtenerLugaresCompraRecomendacion(idRecomendacion: number): Observable<LugaresCompraRecomendacion> {
    return this.http.get<LugaresCompraRecomendacion>(
      `${this.apiUrl}/recomendaciones/${idRecomendacion}/lugares-compra`
    );
  }
}
