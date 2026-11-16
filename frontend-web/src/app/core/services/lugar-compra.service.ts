// CASO DE USO: CU09 - Gestionar proveedores & CU16 - Consultar lugares de compra
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  LugarCompra,
  CrearLugarCompraRequest,
  ActualizarLugarCompraRequest,
  IngredienteLugarCompra,
  AsociarIngredienteLugarCompraRequest,
  ActualizarIngredienteLugarCompraRequest,
  LugaresCompraRecomendacion
} from '../models/lugar-compra.model';

@Injectable({
  providedIn: 'root'
})
export class LugarCompraService {
  private http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/lugares-compra`;
  private readonly apiUrl = environment.apiUrl;

  // =========================================================================
  // GESTIÓN DE PROVEEDORES Y TIENDAS (CU09)
  // =========================================================================

  getLugaresCompra(estado?: string, tipo?: string): Observable<LugarCompra[]> {
    let params = new HttpParams();
    if (estado) params = params.set('estado', estado);
    if (tipo) params = params.set('tipo', tipo);
    return this.http.get<LugarCompra[]>(this.baseUrl, { params });
  }

  getMisTiendas(): Observable<LugarCompra[]> {
    return this.http.get<LugarCompra[]>(`${this.baseUrl}/mis-tiendas`);
  }

  getLugarCompra(id: number): Observable<LugarCompra> {
    return this.http.get<LugarCompra>(`${this.baseUrl}/${id}`);
  }

  crearLugarCompra(datos: CrearLugarCompraRequest): Observable<LugarCompra> {
    return this.http.post<LugarCompra>(this.baseUrl, datos);
  }

  actualizarLugarCompra(id: number, datos: ActualizarLugarCompraRequest): Observable<LugarCompra> {
    return this.http.put<LugarCompra>(`${this.baseUrl}/${id}`, datos);
  }

  cambiarEstado(id: number, estado: 'ACTIVO' | 'INACTIVO'): Observable<LugarCompra> {
    return this.http.patch<LugarCompra>(`${this.baseUrl}/${id}/estado`, { estado });
  }

  // =========================================================================
  // GESTIÓN DE INGREDIENTES Y PRECIOS POR PROVEEDOR (CU09)
  // =========================================================================

  getIngredientesDeLugar(idLugar: number): Observable<IngredienteLugarCompra[]> {
    return this.http.get<IngredienteLugarCompra[]>(`${this.baseUrl}/${idLugar}/ingredientes`);
  }

  asociarIngrediente(idLugar: number, datos: AsociarIngredienteLugarCompraRequest): Observable<IngredienteLugarCompra> {
    return this.http.post<IngredienteLugarCompra>(`${this.baseUrl}/${idLugar}/ingredientes`, datos);
  }

  actualizarIngrediente(
    idLugar: number,
    idIngrediente: number,
    datos: ActualizarIngredienteLugarCompraRequest
  ): Observable<IngredienteLugarCompra> {
    return this.http.put<IngredienteLugarCompra>(
      `${this.baseUrl}/${idLugar}/ingredientes/${idIngrediente}`,
      datos
    );
  }

  eliminarIngrediente(idLugar: number, idIngrediente: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(
      `${this.baseUrl}/${idLugar}/ingredientes/${idIngrediente}`
    );
  }

  // =========================================================================
  // CONSULTA DE LUGARES DE COMPRA PARA RECOMENDACIÓN (CU16)
  // =========================================================================

  obtenerLugaresCompraRecomendacion(idRecomendacion: number): Observable<LugaresCompraRecomendacion> {
    return this.http.get<LugaresCompraRecomendacion>(
      `${this.apiUrl}/recomendaciones/${idRecomendacion}/lugares-compra`
    );
  }
}
