import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU11 - Detalle de planificación & CU13 - Generar recomendación
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { PlanificacionService } from '../../../core/services/planificacion.service';
import { RecomendacionService } from '../../../core/services/recomendacion.service';
import { Planificacion } from '../../../core/models/planificacion.model';

@Component({
  selector: 'app-detalle-planificacion',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterLink],
  template: `
    <div class="detalle-container">
      <!-- Breadcrumb / Volver -->
      <div style="margin-bottom: 1rem;">
        <a routerLink="/planificaciones" class="back-link">&larr; Volver a Mis Planificaciones</a>
      </div>

      <!-- Feedback visual -->
      <div *ngIf="mensajeExito()" class="alert alert-success">{{ mensajeExito() }}</div>
      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <!-- Estado de Carga -->
      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Cargando información de la planificación...</p>
      </div>

      <!-- Contenido Principal -->
      <div *ngIf="!cargando() && planificacion() as plan">
        <div class="header-card card">
          <div class="header-main">
            <div>
              <span class="plan-id">Planificación #{{ plan.id_planificacion }}</span>
              <h2>{{ plan.tipo_comida }} para {{ plan.cantidad_personas }} personas</h2>
              <p style="color: var(--text-muted); margin-top: 0.25rem;">
                Registrada el {{ plan.fecha_planificacion | date:'medium' }}
              </p>
            </div>
            <div>
              <span class="badge" [ngClass]="getEstadoBadgeClass(plan.estado)">
                {{ plan.estado }}
              </span>
            </div>
          </div>

          <!-- Acciones principales -->
          <div class="header-actions">
            <!-- Botón Generar Recomendaciones (CU13) -->
            <button 
              *ngIf="plan.estado === 'ACTIVA'" 
              class="btn btn-primary" 
              [disabled]="generando()" 
              (click)="onGenerarRecomendaciones()"
            >
              <span *ngIf="generando()"><app-icon name="zap" class="app-icon-inline"></app-icon> Calculando recomendaciones...</span>
              <span *ngIf="!generando()"><app-icon name="zap" class="app-icon-inline"></app-icon> Generar Recomendaciones</span>
            </button>

            <a [routerLink]="['/planificaciones', plan.id_planificacion, 'recomendaciones']" class="btn btn-outline">
              <app-icon name="list" class="app-icon-inline"></app-icon> Ver Recomendaciones
            </a>

            <a [routerLink]="['/planificaciones', plan.id_planificacion, 'comparacion']" class="btn btn-outline">
              <app-icon name="settings" class="app-icon-inline"></app-icon> Comparar Restaurantes (CU14)
            </a>

            <a 
              *ngIf="plan.estado === 'ACTIVA'" 
              [routerLink]="['/planificaciones', plan.id_planificacion, 'editar']" 
              class="btn btn-outline"
            >
              <app-icon name="edit" class="app-icon-inline"></app-icon> Editar
            </a>

            <button 
              *ngIf="plan.estado === 'ACTIVA'" 
              class="btn btn-danger btn-outline" 
              (click)="onCancelarPlanificacion()"
            >
              Cancelar
            </button>
          </div>
        </div>

        <!-- Métricas y Parámetros -->
        <div class="grid-3" style="margin-bottom: 1.5rem;">
          <div class="card metric-card">
            <span class="metric-label">Presupuesto Asignado</span>
            <div class="metric-val primary">Bs {{ plan.presupuesto | number:'1.2-2' }}</div>
            <span class="metric-sub">Límite económico total</span>
          </div>

          <div class="card metric-card">
            <span class="metric-label">Comensales</span>
            <div class="metric-val">{{ plan.cantidad_personas }}</div>
            <span class="metric-sub">Personas cubiertas</span>
          </div>

          <div class="card metric-card">
            <span class="metric-label">Presupuesto / Persona</span>
            <div class="metric-val">
              Bs {{ (obtenerPresupuestoPorPersona(plan)) | number:'1.2-2' }}
            </div>
            <span class="metric-sub">Promedio máximo por comensal</span>
          </div>
        </div>

        <!-- Parámetros de Ubicación y Preferencias -->
        <div class="grid-2">
          <div class="card">
            <div class="card-header">
              <h3>Ubicación de Referencia</h3>
            </div>
            <p style="font-size: 1.1rem; font-weight: 500;">
              <app-icon name="pin" class="app-icon-inline"></app-icon> {{ plan.ubicacion_referencia }}
            </p>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">
              Zona aproximada utilizada para estimar cercanía de restaurantes y mercados.
            </p>
          </div>

          <div class="card">
            <div class="card-header">
              <h3>Preferencias Asociadas</h3>
              <span class="badge badge-secondary">{{ plan.preferencias.length }}</span>
            </div>
            <div *ngIf="plan.preferencias.length === 0" style="color: var(--text-muted); font-size: 0.875rem;">
              Sin preferencias dietéticas específicas seleccionadas para este evento.
            </div>
            <div class="pref-tags" *ngIf="plan.preferencias.length > 0">
              <span *ngFor="let p of plan.preferencias" class="pref-tag">
                {{ p.nombre }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .detalle-container {
      max-width: 1050px;
      margin: 0 auto;
    }
    .back-link {
      color: var(--text-muted);
      font-size: 0.875rem;
    }
    .back-link:hover {
      color: var(--primary);
    }
    .header-card {
      padding: 1.75rem;
      margin-bottom: 1.5rem;
    }
    .header-main {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.25rem;
    }
    .plan-id {
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .header-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }
    .metric-card {
      text-align: center;
      padding: 1.25rem;
    }
    .metric-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
      display: block;
      margin-bottom: 0.25rem;
    }
    .metric-val {
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--secondary);
    }
    .metric-val.primary {
      color: var(--primary);
    }
    .metric-sub {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .pref-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .pref-tag {
      padding: 0.3rem 0.75rem;
      background-color: var(--primary-light);
      color: var(--primary);
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
    }
  `]
})
export class DetallePlanificacionComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private planificacionService = inject(PlanificacionService);
  private recomendacionService = inject(RecomendacionService);

  planificacion = signal<Planificacion | null>(null);
  cargando = signal<boolean>(true);
  generando = signal<boolean>(false);
  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.cargarPlanificacion(id);
    }
  }

  cargarPlanificacion(id: number): void {
    this.cargando.set(true);
    this.planificacionService.obtenerPlanificacion(id).subscribe({
      next: (plan) => {
        this.planificacion.set(plan);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al cargar detalle de planificación:', err);
        if (err.status === 403) {
          this.mensajeError.set('No tienes permiso para acceder a esta planificación.');
        } else if (err.status === 404) {
          this.mensajeError.set('La planificación solicitada no existe.');
        } else {
          this.mensajeError.set('Ocurrió un error al cargar la planificación.');
        }
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

  obtenerPresupuestoPorPersona(plan: Planificacion): number {
    const presupuesto = Number(plan.presupuesto) || 0;
    const personas = plan.cantidad_personas || 1;
    return presupuesto / personas;
  }

  onGenerarRecomendaciones(): void {
    const plan = this.planificacion();
    if (!plan) return;

    this.generando.set(true);
    this.mensajeError.set(null);
    this.mensajeExito.set(null);

    this.recomendacionService.generarRecomendaciones(plan.id_planificacion).subscribe({
      next: (recs) => {
        this.generando.set(false);
        this.mensajeExito.set(`¡Se generaron con éxito ${recs.length} alternativas optimizadas!`);
        // Redirigir a la vista de recomendaciones
        setTimeout(() => {
          this.router.navigate(['/planificaciones', plan.id_planificacion, 'recomendaciones']);
        }, 800);
      },
      error: (err) => {
        console.error('Error al generar recomendaciones:', err);
        this.generando.set(false);
        this.mensajeError.set(err.error?.detail || 'No se pudieron generar recomendaciones.');
      }
    });
  }

  onCancelarPlanificacion(): void {
    const plan = this.planificacion();
    if (!plan) return;

    const confirmar = confirm(`¿Seguro que deseas cancelar la planificación #${plan.id_planificacion}?`);
    if (!confirmar) return;

    this.planificacionService.cancelarPlanificacion(plan.id_planificacion).subscribe({
      next: (actualizada) => {
        this.planificacion.set(actualizada);
        this.mensajeExito.set('La planificación ha sido cancelada.');
        setTimeout(() => this.mensajeExito.set(null), 3000);
      },
      error: (err) => {
        console.error('Error al cancelar:', err);
        this.mensajeError.set(err.error?.detail || 'No se pudo cancelar la planificación.');
      }
    });
  }
}
