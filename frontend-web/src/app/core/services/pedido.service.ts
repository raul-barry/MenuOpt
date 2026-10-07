// CASO DE USO: CU23, CU24 - Servicio Angular de Pedidos
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  PedidoCrear,
  PedidoRespuesta,
  PedidoEstadoActualizar
} from '../models/pedido.model';

@Injectable({
  providedIn: 'root'
})
export class PedidoService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  // CU23: Enviar pedido (Cliente)
  crearPedido(datos: PedidoCrear): Observable<PedidoRespuesta> {
    return this.http.post<PedidoRespuesta>(`${this.baseUrl}/pedidos`, datos);
  }

  // CU24: Consultar mis pedidos (Cliente)
  listarMisPedidos(): Observable<PedidoRespuesta[]> {
    return this.http.get<PedidoRespuesta[]>(`${this.baseUrl}/pedidos/mis-pedidos`);
  }

  // CU24: Obtener detalle completo de un pedido
  obtenerPedido(idPedido: number): Observable<PedidoRespuesta> {
    return this.http.get<PedidoRespuesta>(`${this.baseUrl}/pedidos/${idPedido}`);
  }

  // CU24: Cancelar pedido como cliente (sólo PENDIENTE)
  cancelarPedido(idPedido: number): Observable<PedidoRespuesta> {
    return this.http.patch<PedidoRespuesta>(`${this.baseUrl}/pedidos/${idPedido}/cancelar`, {});
  }

  // CU24: Listar pedidos recibidos por el restaurante
  listarPedidosRestaurante(
    idRestaurante: number,
    filtros?: { estado?: string; fecha?: string; id_reserva?: number }
  ): Observable<PedidoRespuesta[]> {
    let params = new HttpParams();
    if (filtros?.estado) {
      params = params.set('estado', filtros.estado);
    }
    if (filtros?.fecha) {
      params = params.set('fecha', filtros.fecha);
    }
    if (filtros?.id_reserva) {
      params = params.set('id_reserva', filtros.id_reserva.toString());
    }

    return this.http.get<PedidoRespuesta[]>(
      `${this.baseUrl}/restaurantes/${idRestaurante}/pedidos`,
      { params }
    );
  }

  // CU24: Actualizar estado de pedido por el restaurante
  actualizarEstado(idPedido: number, nuevoEstado: string): Observable<PedidoRespuesta> {
    const payload: PedidoEstadoActualizar = { estado: nuevoEstado as any };
    return this.http.patch<PedidoRespuesta>(`${this.baseUrl}/pedidos/${idPedido}/estado`, payload);
  }
}
