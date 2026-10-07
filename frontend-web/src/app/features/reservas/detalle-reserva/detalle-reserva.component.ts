// CASO DE USO: CU21 & CU22 - Detalle de Reserva
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { ReservaService } from '../../../core/services/reserva.service';
import { AuthService } from '../../../core/services/auth.service';
import { ReservaRespuesta } from '../../../core/models/reserva.model';

@Component({
  selector: 'app-detalle-reserva',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;">Detalle de Reserva #{{ reservaId() }}</h2>
          <p style="margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.85rem;">
            Información registrada del comensal, establecimiento y mesa asignada.
          </p>
        </div>
        <button class="btn btn-outline btn-sm" (click)="volver()">
          &larr; Volver
        </button>
      </div>

      <div class="card-body">
        <div *ngIf="cargando()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando detalle de la reserva...</p>
        </div>

        <div *ngIf="mensaje()" class="alert alert-success" style="margin-bottom: 1rem;">
          {{ mensaje() }}
        </div>
        <div *ngIf="error()" class="alert alert-danger" style="margin-bottom: 1rem;">
          {{ error() }}
        </div>

        <div *ngIf="!cargando() && reserva() as r">
          <!-- Banner Superior de Estado -->
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #f8fafc; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 1.5rem;">
            <div>
              <h3 style="margin: 0; color: var(--primary);">{{ r.nombre_restaurante }}</h3>
              <span style="font-size: 0.85rem; color: var(--text-muted);">Área: {{ r.nombre_area || 'Sin área asignada' }}</span>
            </div>
            <span
              class="badge"
              style="font-size: 0.9rem; padding: 0.4rem 0.8rem;"
              [class.badge-success]="r.estado === 'CONFIRMADA'"
              [class.badge-secondary]="r.estado === 'FINALIZADA'"
              [class.badge-danger]="r.estado === 'CANCELADA'"
              [class.badge-warning]="r.estado === 'PENDIENTE'"
            >
              {{ r.estado }}
            </span>
          </div>

          <!-- Cuadrícula de Datos -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
            <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem;">
              <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">HORARIO Y FECHA</h4>
              <p style="margin: 0 0 0.25rem 0; font-size: 1.1rem; font-weight: 600;">📅 {{ r.fecha_reserva }}</p>
              <p style="margin: 0; color: var(--text-muted);">⏰ {{ r.hora_inicio.substring(0, 5) }} &ndash; {{ r.hora_fin.substring(0, 5) }}</p>
            </div>

            <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem;">
              <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">COMENSALES</h4>
              <p style="margin: 0 0 0.25rem 0; font-size: 1.1rem; font-weight: 600;">👥 {{ r.cantidad_personas }} personas</p>
              <p style="margin: 0; color: var(--text-muted);">Titular: {{ r.nombre_cliente || 'Cliente #' + r.id_usuario }}</p>
            </div>

            <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem;">
              <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">MESA(S) ASIGNADA(S)</h4>
              <div style="margin-top: 0.25rem;">
                <span *ngFor="let m of r.mesas" class="badge" style="background: #e0f2fe; color: #0369a1; margin-right: 4px; font-size: 0.9rem; padding: 0.3rem 0.6rem;">
                  🪑 Mesa {{ m.numero }} ({{ m.capacidad }}p)
                </span>
              </div>
            </div>
          </div>

          <!-- Observaciones y Contacto -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">DETALLES ADICIONALES</h4>
            <p style="margin: 0 0 0.5rem 0;">
              <strong>Observaciones:</strong> {{ r.observaciones || 'Ninguna observación especificada.' }}
            </p>
            <p *ngIf="r.correo_cliente" style="margin: 0 0 0.25rem 0; font-size: 0.85rem; color: var(--text-muted);">
              <strong>Contacto:</strong> ✉️ {{ r.correo_cliente }} <span *ngIf="r.telefono_cliente">| 📞 {{ r.telefono_cliente }}</span>
            </p>
            <p style="margin: 0; font-size: 0.8rem; color: var(--text-muted);">
              Registrada el: {{ r.fecha_creacion | date:'dd/MM/yyyy HH:mm' }}
            </p>
          </div>

          <!-- Acciones -->
          <div style="display: flex; justify-content: flex-end; gap: 0.5rem; flex-wrap: wrap;">
            <a
              *ngIf="r.estado === 'CONFIRMADA' || r.estado === 'PENDIENTE'"
              [routerLink]="['/restaurantes', r.id_restaurante, 'pedido']"
              [queryParams]="{ id_reserva: r.id_reserva }"
              class="btn btn-success"
            >
              🍽️ Ordenar platos para esta reserva
            </a>
            <button
              *ngIf="puedeCancelar(r)"
              class="btn btn-danger"
              (click)="cancelarReserva(r)"
            >
              Cancelar Reserva
            </button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class DetalleReservaComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private reservaService = inject(ReservaService);
  private authService = inject(AuthService);

  reservaId = signal<number>(0);
  reserva = signal<ReservaRespuesta | null>(null);
  cargando = signal<boolean>(false);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.reservaId.set(Number(idParam));
      this.cargarDetalle();
    }
  }

  cargarDetalle(): void {
    this.cargando.set(true);
    this.reservaService.obtenerReserva(this.reservaId()).subscribe({
      next: (r) => {
        this.reserva.set(r);
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        this.error.set(err.error?.detail || 'No se pudo cargar la información de la reserva.');
      }
    });
  }

  puedeCancelar(r: ReservaRespuesta): boolean {
    const rol = this.authService.userRole();
    const userId = this.authService.currentUser()?.id_usuario;
    const esTitular = r.id_usuario === userId;
    return (esTitular || rol === 'ADMINISTRADOR') && (r.estado === 'CONFIRMADA' || r.estado === 'PENDIENTE');
  }

  cancelarReserva(r: ReservaRespuesta): void {
    if (!confirm(`¿Está seguro de cancelar la reserva #${r.id_reserva}?`)) {
      return;
    }

    this.reservaService.cancelarReserva(r.id_reserva).subscribe({
      next: (act) => {
        this.reserva.set(act);
        this.mensaje.set('Reserva cancelada exitosamente.');
        setTimeout(() => this.mensaje.set(null), 4000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al cancelar la reserva.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }

  volver(): void {
    const rol = this.authService.userRole();
    if (rol === 'RESTAURANTE') {
      const restoId = this.reserva()?.id_restaurante;
      if (restoId) {
        this.router.navigate(['/restaurantes', restoId, 'reservas']);
        return;
      }
    }
    this.router.navigate(['/mis-reservas']);
  }
}
