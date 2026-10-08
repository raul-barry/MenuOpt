import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU22 - Gestionar reservas de restaurante
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RestauranteService } from '../../../core/services/restaurante.service';
import { AreaRestauranteService } from '../../../core/services/area-restaurante.service';
import { ReservaService } from '../../../core/services/reserva.service';
import { Restaurante } from '../../../core/models/restaurante.model';
import { AreaRestaurante } from '../../../core/models/area-restaurante.model';
import { ReservaRespuesta } from '../../../core/models/reserva.model';

@Component({
  selector: 'app-gestion-reservas',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
            <a [routerLink]="['/restaurantes']" class="btn btn-sm btn-outline" style="padding: 0.2rem 0.5rem;">&larr; Restaurantes</a>
            <h2 style="margin: 0; font-size: 1.4rem;">
              <app-icon name="calendar" class="app-icon-inline"></app-icon> Gestión de Reservas &mdash; {{ restaurante()?.nombre || 'Restaurante #' + restauranteId() }}
            </h2>
          </div>
          <p style="margin: 0; color: var(--text-muted); font-size: 0.875rem;">
            Supervise la llegada de comensales, consulte mesas reservadas y actualice los estados operativos.
          </p>
        </div>

        <div style="display: flex; gap: 0.5rem;">
          <a [routerLink]="['/restaurantes', restauranteId(), 'distribucion']" class="btn btn-secondary btn-sm">
            <app-icon name="map" class="app-icon-inline"></app-icon> Ver Plano 2D
          </a>
        </div>
      </div>

      <div class="card-body">
        <div *ngIf="mensaje()" class="alert alert-success" style="margin-bottom: 1rem;">
          {{ mensaje() }}
        </div>
        <div *ngIf="error()" class="alert alert-danger" style="margin-bottom: 1rem;">
          {{ error() }}
        </div>

        <!-- Barra de Filtros -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; align-items: flex-end; background: #f8fafc; padding: 1rem; border-radius: var(--radius); border: 1px solid var(--border); margin-bottom: 1.5rem;">
          <div>
            <label class="form-label" style="display: block; font-weight: 500; font-size: 0.85rem; margin-bottom: 0.25rem;">Filtrar por Fecha</label>
            <input
              type="date"
              class="form-control"
              style="width: 100%; padding: 0.4rem; border: 1px solid var(--border); border-radius: var(--radius);"
              [(ngModel)]="filtroFecha"
              (ngModelChange)="cargarReservas()"
            />
          </div>

          <div>
            <label class="form-label" style="display: block; font-weight: 500; font-size: 0.85rem; margin-bottom: 0.25rem;">Filtrar por Estado</label>
            <select
              class="form-control"
              style="width: 100%; padding: 0.4rem; border: 1px solid var(--border); border-radius: var(--radius);"
              [(ngModel)]="filtroEstado"
              (ngModelChange)="cargarReservas()"
            >
              <option value="">Todos los estados</option>
              <option value="CONFIRMADA">Confirmadas</option>
              <option value="FINALIZADA">Finalizadas</option>
              <option value="CANCELADA">Canceladas</option>
              <option value="PENDIENTE">Pendientes</option>
            </select>
          </div>

          <div>
            <label class="form-label" style="display: block; font-weight: 500; font-size: 0.85rem; margin-bottom: 0.25rem;">Filtrar por Área</label>
            <select
              class="form-control"
              style="width: 100%; padding: 0.4rem; border: 1px solid var(--border); border-radius: var(--radius);"
              [(ngModel)]="filtroArea"
              (ngModelChange)="cargarReservas()"
            >
              <option [ngValue]="null">Todas las áreas</option>
              <option *ngFor="let a of areas()" [ngValue]="a.id_area">
                {{ a.nombre }}
              </option>
            </select>
          </div>

          <div>
            <button class="btn btn-outline btn-sm" style="width: 100%;" (click)="limpiarFiltros()">
              Limpiar Filtros
            </button>
          </div>
        </div>

        <!-- Indicador de Carga -->
        <div *ngIf="cargando()" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          <app-icon name="loader" class="app-icon-inline"></app-icon> Cargando reservas del restaurante...
        </div>

        <!-- Tabla de Reservas -->
        <div *ngIf="!cargando() && reservas().length > 0" class="table-responsive">
          <table class="table" style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 2px solid var(--border); text-align: left; font-size: 0.875rem;">
                <th style="padding: 0.75rem;"># ID</th>
                <th style="padding: 0.75rem;">Cliente</th>
                <th style="padding: 0.75rem;">Fecha y Horario</th>
                <th style="padding: 0.75rem;">Área</th>
                <th style="padding: 0.75rem;">Mesa(s)</th>
                <th style="padding: 0.75rem;">Personas</th>
                <th style="padding: 0.75rem;">Estado</th>
                <th style="padding: 0.75rem; text-align: right;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let r of reservas()" style="border-bottom: 1px solid var(--border); font-size: 0.9rem;">
                <td style="padding: 0.75rem; font-weight: 600;">#{{ r.id_reserva }}</td>
                <td style="padding: 0.75rem;">
                  <strong>{{ r.nombre_cliente || 'Cliente #' + r.id_usuario }}</strong>
                  <div style="font-size: 0.75rem; color: var(--text-muted);">
                    <span *ngIf="r.telefono_cliente"><app-icon name="phone" class="app-icon-inline"></app-icon> {{ r.telefono_cliente }} | </span>
                    <span><app-icon name="mail" class="app-icon-inline"></app-icon> {{ r.correo_cliente }}</span>
                  </div>
                  <div *ngIf="r.observaciones" style="font-size: 0.75rem; color: #b45309; margin-top: 2px;">
                    Nota: {{ r.observaciones }}
                  </div>
                </td>
                <td style="padding: 0.75rem;">
                  <app-icon name="calendar" class="app-icon-inline"></app-icon> {{ r.fecha_reserva }}<br />
                  <small style="color: var(--text-muted); font-weight: 600;"><app-icon name="clock" class="app-icon-inline"></app-icon> {{ r.hora_inicio.substring(0, 5) }} &ndash; {{ r.hora_fin.substring(0, 5) }}</small>
                </td>
                <td style="padding: 0.75rem;">{{ r.nombre_area || '-' }}</td>
                <td style="padding: 0.75rem;">
                  <span *ngFor="let m of r.mesas" class="badge" style="background: #e0f2fe; color: #0369a1; margin-right: 2px;">
                    Mesa {{ m.numero }} ({{ m.capacidad }}p)
                  </span>
                </td>
                <td style="padding: 0.75rem;"><app-icon name="users" class="app-icon-inline"></app-icon> {{ r.cantidad_personas }}</td>
                <td style="padding: 0.75rem;">
                  <span
                    class="badge"
                    [class.badge-success]="r.estado === 'CONFIRMADA'"
                    [class.badge-secondary]="r.estado === 'FINALIZADA'"
                    [class.badge-danger]="r.estado === 'CANCELADA'"
                    [class.badge-warning]="r.estado === 'PENDIENTE'"
                  >
                    {{ r.estado }}
                  </span>
                </td>
                <td style="padding: 0.75rem; text-align: right;">
                  <div style="display: flex; gap: 0.25rem; justify-content: flex-end;">
                    <a [routerLink]="['/reservas', r.id_reserva]" class="btn btn-outline btn-xs">
                      Detalle
                    </a>
                    <button
                      *ngIf="r.estado === 'CONFIRMADA'"
                      class="btn btn-primary btn-xs"
                      (click)="cambiarEstado(r, 'FINALIZADA')"
                      title="Marcar como atendida y completada"
                    >
                      <app-icon name="check" class="app-icon-inline"></app-icon> Finalizar
                    </button>
                    <button
                      *ngIf="r.estado === 'CONFIRMADA' || r.estado === 'PENDIENTE'"
                      class="btn btn-danger btn-xs"
                      (click)="cambiarEstado(r, 'CANCELADA')"
                      title="Cancelar reserva"
                    >
                      Cancelar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Estado vacío -->
        <div *ngIf="!cargando() && reservas().length === 0" style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <div style="font-size: 3rem; margin-bottom: 0.5rem;"><app-icon name="calendar" class="app-icon-inline"></app-icon></div>
          <h4>No se encontraron reservas con los filtros aplicados</h4>
          <p style="font-size: 0.85rem;">Pruebe cambiando las fechas o el estado seleccionado.</p>
        </div>
      </div>
    </div>
  `
})
export class GestionReservasComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private restauranteService = inject(RestauranteService);
  private areaService = inject(AreaRestauranteService);
  private reservaService = inject(ReservaService);

  restauranteId = signal<number>(0);
  restaurante = signal<Restaurante | null>(null);
  areas = signal<AreaRestaurante[]>([]);
  reservas = signal<ReservaRespuesta[]>([]);
  cargando = signal<boolean>(false);

  filtroFecha: string = '';
  filtroEstado: string = '';
  filtroArea: number | null = null;

  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.restauranteId.set(Number(idParam));
      this.cargarRestaurante();
      this.cargarAreas();
      this.cargarReservas();
    }
  }

  cargarRestaurante(): void {
    this.restauranteService.getRestaurante(this.restauranteId()).subscribe({
      next: (r) => this.restaurante.set(r)
    });
  }

  cargarAreas(): void {
    this.areaService.listarAreasPorRestaurante(this.restauranteId(), false).subscribe({
      next: (lista) => this.areas.set(lista)
    });
  }

  cargarReservas(): void {
    this.cargando.set(true);
    const filtros: any = {};
    if (this.filtroFecha) filtros.fecha = this.filtroFecha;
    if (this.filtroEstado) filtros.estado = this.filtroEstado;
    if (this.filtroArea) filtros.id_area = this.filtroArea;

    this.reservaService.listarReservasRestaurante(this.restauranteId(), filtros).subscribe({
      next: (lista) => {
        this.reservas.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.cargando.set(false);
        this.error.set('No se pudieron cargar las reservas del restaurante.');
      }
    });
  }

  limpiarFiltros(): void {
    this.filtroFecha = '';
    this.filtroEstado = '';
    this.filtroArea = null;
    this.cargarReservas();
  }

  cambiarEstado(reserva: ReservaRespuesta, nuevoEstado: string): void {
    const accion = nuevoEstado === 'FINALIZADA' ? 'marcar como finalizada/atendida' : 'cancelar';
    if (!confirm(`¿Confirma ${accion} la reserva #${reserva.id_reserva}?`)) {
      return;
    }

    this.reservaService.actualizarEstado(reserva.id_reserva, nuevoEstado).subscribe({
      next: (act) => {
        this.mensaje.set(`Reserva #${act.id_reserva} actualizada a ${act.estado}.`);
        this.cargarReservas();
        setTimeout(() => this.mensaje.set(null), 4000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al cambiar estado de la reserva.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }
}
