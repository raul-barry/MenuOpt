import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU11 - Registrar planificación gastronómica (Mis planificaciones)
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { PlanificacionService } from '../../../core/services/planificacion.service';
import { Planificacion } from '../../../core/models/planificacion.model';

@Component({
  selector: 'app-planificaciones-lista',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterLink],
  template: `
    <div class="lista-container">
      <div class="header-section">
        <div>
          <h2>Mis Planificaciones Gastronómicas</h2>
          <p style="color: var(--text-muted);">
            Consulta el historial de eventos gastronómicos, recomendaciones calculadas y comparativas.
          </p>
        </div>
        <a routerLink="/planificaciones/nueva" class="btn btn-primary">
          <span>+</span> Nueva Planificación
        </a>
      </div>

      <!-- Feedback visual -->
      <div *ngIf="mensajeExito()" class="alert alert-success">{{ mensajeExito() }}</div>
      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <!-- Estado de Carga -->
      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Cargando planificaciones...</p>
      </div>

      <!-- Estado Vacío -->
      <div *ngIf="!cargando() && planificaciones().length === 0" class="card empty-card">
        <div style="font-size: 3rem; margin-bottom: 1rem;"><app-icon name="utensils" class="app-icon-inline"></app-icon></div>
        <h3>Aún no tienes planificaciones registradas</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem; max-width: 450px;">
          Comienza ingresando tu presupuesto y cantidad de personas para recibir sugerencias optimizadas de restaurantes y cocina casera.
        </p>
        <a routerLink="/planificaciones/nueva" class="btn btn-primary">
          Crear mi primera planificación
        </a>
      </div>

      <!-- Tabla de Planificaciones -->
      <div *ngIf="!cargando() && planificaciones().length > 0" class="card">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Comensales</th>
                <th>Presupuesto</th>
                <th>Ubicación</th>
                <th>Estado</th>
                <th style="text-align: right;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let plan of planificaciones()">
                <td><strong>#{{ plan.id_planificacion }}</strong></td>
                <td>{{ plan.fecha_planificacion | date:'shortDate' }}</td>
                <td>
                  <span class="tipo-badge">{{ plan.tipo_comida }}</span>
                </td>
                <td>{{ plan.cantidad_personas }} pers.</td>
                <td><strong>Bs {{ plan.presupuesto | number:'1.2-2' }}</strong></td>
                <td>{{ plan.ubicacion_referencia }}</td>
                <td>
                  <span class="badge" [ngClass]="getEstadoBadgeClass(plan.estado)">
                    {{ plan.estado }}
                  </span>
                </td>
                <td style="text-align: right;">
                  <div class="action-buttons">
                    <a [routerLink]="['/planificaciones', plan.id_planificacion]" class="btn btn-outline btn-sm" title="Ver Detalle">
                      Ver
                    </a>
                    
                    <a 
                      *ngIf="plan.estado === 'ACTIVA'" 
                      [routerLink]="['/planificaciones', plan.id_planificacion, 'editar']" 
                      class="btn btn-outline btn-sm"
                      title="Editar"
                    >
                      Editar
                    </a>

                    <a 
                      [routerLink]="['/planificaciones', plan.id_planificacion, 'recomendaciones']" 
                      class="btn btn-primary btn-sm"
                      title="Recomendaciones"
                    >
                      Recomendaciones
                    </a>

                    <button 
                      *ngIf="plan.estado === 'ACTIVA'" 
                      class="btn btn-danger btn-sm"
                      (click)="confirmarCancelar(plan)"
                      title="Cancelar Planificación"
                    >
                      Cancelar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .lista-container {
      max-width: 1100px;
      margin: 0 auto;
    }
    .header-section {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }
    .empty-card {
      text-align: center;
      padding: 4rem 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .tipo-badge {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--secondary);
      background-color: #f1f5f9;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
    }
    .action-buttons {
      display: flex;
      gap: 0.35rem;
      justify-content: flex-end;
    }
  `]
})
export class PlanificacionesListaComponent implements OnInit {
  private planificacionService = inject(PlanificacionService);

  planificaciones = signal<Planificacion[]>([]);
  cargando = signal<boolean>(true);
  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarPlanificaciones();
  }

  cargarPlanificaciones(): void {
    this.cargando.set(true);
    this.planificacionService.listarMisPlanificaciones(1, 50).subscribe({
      next: (res) => {
        this.planificaciones.set(res.planificaciones || []);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al listar planificaciones:', err);
        this.mensajeError.set('No se pudieron cargar tus planificaciones.');
        this.cargando.set(false);
      }
    });
  }

  getEstadoBadgeClass(estado: string): string {
    switch (estado) {
      case 'ACTIVA': return 'badge-success';
      case 'CANCELADA': return 'badge-danger';
      default: return 'badge-secondary';
    }
  }

  confirmarCancelar(plan: Planificacion): void {
    const confirmar = confirm(`¿Estás seguro de que deseas cancelar la planificación #${plan.id_planificacion}?`);
    if (!confirmar) return;

    this.planificacionService.cancelarPlanificacion(plan.id_planificacion).subscribe({
      next: (actualizada) => {
        this.mensajeExito.set(`Planificación #${plan.id_planificacion} cancelada correctamente.`);
        setTimeout(() => this.mensajeExito.set(null), 3000);
        // Actualizar estado en la lista local sin recargar
        this.planificaciones.update(lista =>
          lista.map(p => p.id_planificacion === actualizada.id_planificacion ? actualizada : p)
        );
      },
      error: (err) => {
        console.error('Error al cancelar planificación:', err);
        this.mensajeError.set(err.error?.detail || 'No se pudo cancelar la planificación.');
      }
    });
  }
}
