// CASO DE USO: CU15 - Consultar ingredientes para preparación propia
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PreparacionPropia } from '../models/preparacion.model';

@Injectable({
  providedIn: 'root'
})
export class PreparacionService {
  private http = inject(HttpClient);
  private readonly apiUrl = environment.apiUrl;

  obtenerDetallePreparacion(idRecomendacion: number): Observable<PreparacionPropia> {
    return this.http.get<PreparacionPropia>(
      `${this.apiUrl}/recomendaciones/${idRecomendacion}/preparacion`
    );
  }
}
