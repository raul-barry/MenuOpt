// CASO DE USO: CU17 - Crear plano 2D del restaurante (Distribución de mesas)
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  GenerarDistribucionRequest,
  GuardarDistribucionRequest,
  DistribucionRespuesta
} from '../models/distribucion.model';
import { MesaPosicionActualizar } from '../models/mesa.model';

@Injectable({
  providedIn: 'root'
})
export class DistribucionMesasService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  generarDistribucion(idArea: number, datos: GenerarDistribucionRequest): Observable<DistribucionRespuesta> {
    return this.http.post<DistribucionRespuesta>(`${this.baseUrl}/areas/${idArea}/distribucion/generar`, datos);
  }

  guardarDistribucion(idArea: number, posiciones: MesaPosicionActualizar[]): Observable<DistribucionRespuesta> {
    const payload: GuardarDistribucionRequest = { posiciones };
    return this.http.put<DistribucionRespuesta>(`${this.baseUrl}/areas/${idArea}/distribucion`, payload);
  }

  restablecerDistribucion(idArea: number): Observable<DistribucionRespuesta> {
    return this.http.post<DistribucionRespuesta>(`${this.baseUrl}/areas/${idArea}/distribucion/restablecer`, {});
  }
}
