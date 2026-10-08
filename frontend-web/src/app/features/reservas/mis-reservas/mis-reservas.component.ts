import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU21 - Consultar y cancelar mis reservas (Cliente)
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ReservaService } from '../../../core/services/reserva.service';
import { ReservaRespuesta } from '../../../core/models/reserva.model';

@Component({
  selector: 'app-mis-reservas',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2 style="margin: 0; font-size: 1.4rem;"><app-icon name="calendar" class="app-icon-inline"></app-icon> Mis Reservas</h2>
          <p style="margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.875rem;">
            Supervise sus reservas gastronómicas activas, pasadas y canceladas.
          </p>
        </div>
        <a routerLink="/restaurantes" class="btn btn-primary btn-sm">
          <app-icon name="plus" class="app-icon-inline"></app-icon> Nueva Reserva
        </a>
      </div>

      <div class="card-body">
        <div *ngIf="mensaje()" class="alert alert-success" style="margin-bottom: 1rem;">
          {{ mensaje() }}
        </div>
        <div *ngIf="error()" class="alert alert-danger" style="margin-bottom: 1rem;">
          {{ error() }}
        </div>

        <!-- Filtro por Estado -->
        <div style="display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap;">
          <button
            class="btn btn-sm"
            [class.btn-primary]="filtroEstado() === 'TODAS'"
            [class.btn-outline]="filtroEstado() !== 'TODAS'"
            (click)="setFiltro('TODAS')"
          >
            Todas
          </button>
          <button
            class="btn btn-sm"
            [class.btn-primary]="filtroEstado() === 'CONFIRMADA'"
            [class.btn-outline]="filtroEstado() !== 'CONFIRMADA'"
            (click)="setFiltro('CONFIRMADA')"
          >
            Confirmadas
          </button>
          <button
            class="btn btn-sm"
            [class.btn-primary]="filtroEstado() === 'FINALIZADA'"
            [class.btn-outline]="filtroEstado() !== 'FINALIZADA'"
            (click)="setFiltro('FINALIZADA')"
          >
            Finalizadas
          </button>
          <button
            class="btn btn-sm"
            [class.btn-primary]="filtroEstado() === 'CANCELADA'"
            [class.btn-outline]="filtroEstado() !== 'CANCELADA'"
            (click)="setFiltro('CANCELADA')"
          >
            Canceladas
          </button>
        </div>

        <!-- Indicador de Carga -->
        <div *ngIf="cargando()" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          <app-icon name="loader" class="app-icon-inline"></app-icon> Cargando sus reservas...
        </div>

        <!-- Listado de Reservas -->
        <div *ngIf="!cargando() && getReservasFiltradas().length > 0" class="table-responsive">
          <table class="table" style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="border-bottom: 2px solid var(--border); text-align: left; font-size: 0.875rem;">
                <th style="padding: 0.75rem;"># ID</th>
                <th style="padding: 0.75rem;">Restaurante</th>
                <th style="padding: 0.75rem;">Área</th>
                <th style="padding: 0.75rem;">Mesa(s)</th>
                <th style="padding: 0.75rem;">Fecha y Horario</th>
                <th style="padding: 0.75rem;">Personas</th>
                <th style="padding: 0.75rem;">Estado</th>
                <th style="padding: 0.75rem; text-align: right;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let r of getReservasFiltradas()" style="border-bottom: 1px solid var(--border); font-size: 0.9rem;">
                <td style="padding: 0.75rem; font-weight: 600;">#{{ r.id_reserva }}</td>
                <td style="padding: 0.75rem;">
                  <strong>{{ r.nombre_restaurante }}</strong>
                  <span *ngIf="r.observaciones" style="display: block; font-size: 0.75rem; color: var(--text-muted);">
                    Nota: {{ r.observaciones }}
                  </span>
                </td>
                <td style="padding: 0.75rem;">{{ r.nombre_area || '-' }}</td>
                <td style="padding: 0.75rem;">
                  <span *ngFor="let m of r.mesas; let last = last" class="badge" style="background: #f1f5f9; border: 1px solid #cbd5e1; margin-right: 2px;">
                    {{ m.numero }} ({{ m.capacidad }}p)
                  </span>
                </td>
                <td style="padding: 0.75rem;">
                  <app-icon name="calendar" class="app-icon-inline"></app-icon> {{ r.fecha_reserva }}<br />
                  <small style="color: var(--text-muted);"><app-icon name="clock" class="app-icon-inline"></app-icon> {{ r.hora_inicio.substring(0, 5) }} - {{ r.hora_fin.substring(0, 5) }}</small>
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
                  <a [routerLink]="['/reservas', r.id_reserva]" class="btn btn-outline btn-xs" style="margin-right: 0.25rem;">
                    Detalle
                  </a>
                  <button
                    *ngIf="r.estado === 'CONFIRMADA' || r.estado === 'PENDIENTE'"
                    class="btn btn-danger btn-xs"
                    (click)="cancelarReserva(r)"
                    title="Cancelar esta reserva"
                  >
                    Cancelar
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Estado vacío -->
        <div *ngIf="!cargando() && getReservasFiltradas().length === 0" style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <div style="font-size: 3rem; margin-bottom: 0.5rem;"><app-icon name="calendar" class="app-icon-inline"></app-icon></div>
          <h4>No tiene reservas {{ filtroEstado() !== 'TODAS' ? 'con estado ' + filtroEstado() : 'registradas' }}</h4>
          <p style="font-size: 0.85rem; margin-bottom: 1rem;">
            Explore los restaurantes disponibles y reserve una mesa con anticipación.
          </p>
          <a routerLink="/restaurantes" class="btn btn-primary btn-sm">Explorar Restaurantes</a>
        </div>
      </div>
    </div>
  `
})
export class MisReservasComponent implements OnInit {
  private reservaService = inject(ReservaService);

  reservas = signal<ReservaRespuesta[]>([]);
  cargando = signal<boolean>(false);
  filtroEstado = signal<string>('TODAS');
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarReservas();
  }

  cargarReservas(): void {
    this.cargando.set(true);
    this.reservaService.listarMisReservas().subscribe({
      next: (lista) => {
        this.reservas.set(lista);
        this.cargando.set(false);
      },
      error: () => {
        this.cargando.set(false);
        this.error.set('No se pudieron cargar sus reservas.');
      }
    });
  }

  setFiltro(estado: string): void {
    this.filtroEstado.set(estado);
  }

  getReservasFiltradas(): ReservaRespuesta[] {
    const estado = this.filtroEstado();
    if (estado === 'TODAS') {
      return this.reservas();
    }
    return this.reservas().filter(r => r.estado === estado);
  }

  cancelarReserva(reserva: ReservaRespuesta): void {
    if (!confirm(`¿Está seguro de que desea cancelar la reserva #${reserva.id_reserva} en '${reserva.nombre_restaurante}'? Esta acción liberará la mesa para otros clientes.`)) {
      return;
    }

    this.reservaService.cancelarReserva(reserva.id_reserva).subscribe({
      next: () => {
        this.mensaje.set(`Reserva #${reserva.id_reserva} cancelada exitosamente.`);
        this.cargarReservas();
        setTimeout(() => this.mensaje.set(null), 4000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al cancelar la reserva.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }
}
