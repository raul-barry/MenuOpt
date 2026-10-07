// CASO DE USO: CU20, CU21, CU22 - Servicio Angular de Reservas y Disponibilidad
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  ConsultaDisponibilidad,
  DisponibilidadRespuesta,
  ReservaCrear,
  ReservaRespuesta,
  ReservaEstadoActualizar
} from '../models/reserva.model';

@Injectable({
  providedIn: 'root'
})
export class ReservaService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  // CU20: Consultar disponibilidad de mesas
  consultarDisponibilidad(
    idRestaurante: number,
    consulta: ConsultaDisponibilidad
  ): Observable<DisponibilidadRespuesta> {
    const params = new HttpParams()
      .set('id_area', consulta.id_area.toString())
      .set('fecha', consulta.fecha)
      .set('hora_inicio', consulta.hora_inicio)
      .set('hora_fin', consulta.hora_fin)
      .set('cantidad_personas', consulta.cantidad_personas.toString());

    return this.http.get<DisponibilidadRespuesta>(
      `${this.baseUrl}/restaurantes/${idRestaurante}/mesas-disponibles`,
      { params }
    );
  }

  // CU21: Confirmar reserva
  crearReserva(datos: ReservaCrear): Observable<ReservaRespuesta> {
    return this.http.post<ReservaRespuesta>(`${this.baseUrl}/reservas`, datos);
  }

  // CU21: Consultar mis reservas (Cliente)
  listarMisReservas(): Observable<ReservaRespuesta[]> {
    return this.http.get<ReservaRespuesta[]>(`${this.baseUrl}/reservas/mis-reservas`);
  }

  // CU21 & CU22: Obtener detalle de una reserva
  obtenerReserva(idReserva: number): Observable<ReservaRespuesta> {
    return this.http.get<ReservaRespuesta>(`${this.baseUrl}/reservas/${idReserva}`);
  }

  // CU21: Cancelar reserva como cliente
  cancelarReserva(idReserva: number): Observable<ReservaRespuesta> {
    return this.http.patch<ReservaRespuesta>(`${this.baseUrl}/reservas/${idReserva}/cancelar`, {});
  }

  // CU22: Consultar reservas del restaurante
  listarReservasRestaurante(
    idRestaurante: number,
    filtros?: { fecha?: string; estado?: string; id_area?: number }
  ): Observable<ReservaRespuesta[]> {
    let params = new HttpParams();
    if (filtros?.fecha) {
      params = params.set('fecha', filtros.fecha);
    }
    if (filtros?.estado) {
      params = params.set('estado', filtros.estado);
    }
    if (filtros?.id_area) {
      params = params.set('id_area', filtros.id_area.toString());
    }

    return this.http.get<ReservaRespuesta[]>(
      `${this.baseUrl}/restaurantes/${idRestaurante}/reservas`,
      { params }
    );
  }

  // CU22: Actualizar estado de reserva (Restaurante / Admin)
  actualizarEstado(idReserva: number, nuevoEstado: string): Observable<ReservaRespuesta> {
    const payload: ReservaEstadoActualizar = { estado: nuevoEstado as any };
    return this.http.patch<ReservaRespuesta>(`${this.baseUrl}/reservas/${idReserva}/estado`, payload);
  }
}
