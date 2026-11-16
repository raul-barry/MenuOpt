import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU13 - Generar recomendación & Visualización de alternativas
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { RecomendacionService } from '../../../core/services/recomendacion.service';
import { PlanificacionService } from '../../../core/services/planificacion.service';
import { AsistenteIAService } from '../../../core/services/asistente-ia.service';
import { Recomendacion } from '../../../core/models/recomendacion.model';
import { Planificacion } from '../../../core/models/planificacion.model';
import { ExplicacionRespuesta } from '../../../core/models/asistente-ia.model';

@Component({
  selector: 'app-lista-recomendaciones',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterLink],
  template: `
    <div class="recomendaciones-container">
      <!-- Breadcrumb -->
      <div style="margin-bottom: 1rem;">
        <a [routerLink]="['/planificaciones', idPlanificacion]" class="back-link">&larr; Volver a la Planificación</a>
      </div>

      <!-- Header -->
      <div class="header-card card" *ngIf="planificacion() as plan">
        <div class="header-main">
          <div>
            <span class="plan-tag">Planificación #{{ plan.id_planificacion }}</span>
            <h2>Alternativas Gastronómicas Recomendadas (CU13)</h2>
            <p style="color: var(--text-muted); margin-top: 0.25rem;">
              Para {{ plan.cantidad_personas }} comensales con presupuesto de <strong>Bs {{ plan.presupuesto | number:'1.2-2' }}</strong> ({{ plan.tipo_comida }}).
            </p>
          </div>
          <div class="header-actions">
            <a [routerLink]="['/planificaciones', plan.id_planificacion, 'comparacion']" class="btn btn-primary">
              <app-icon name="settings" class="app-icon-inline"></app-icon> Comparar Alternativas (CU14)
            </a>
            <button 
              *ngIf="plan.estado === 'ACTIVA'" 
              class="btn btn-outline" 
              [disabled]="regenerando()" 
              (click)="regenerarRecomendaciones()"
            >
              <span *ngIf="regenerando()">Regenerando...</span>
              <span *ngIf="!regenerando()"><app-icon name="refresh" class="app-icon-inline"></app-icon> Regenerar</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Feedback visual -->
      <div *ngIf="mensajeExito()" class="alert alert-success">{{ mensajeExito() }}</div>
      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <!-- Estado de Carga -->
      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Consultando recomendaciones optimizadas...</p>
      </div>

      <!-- Sin resultados -->
      <div *ngIf="!cargando() && recomendaciones().length === 0" class="card empty-card">
        <div style="font-size: 3rem; margin-bottom: 1rem;"><app-icon name="search" class="app-icon-inline"></app-icon></div>
        <h3>No encontramos alternativas dentro del presupuesto</h3>
        <p style="color: var(--text-muted); max-width: 500px; margin-bottom: 1.5rem;">
          No se hallaron opciones comerciales o recetas caseras que cumplan estrictamente con tu presupuesto disponible de Bs {{ planificacion()?.presupuesto }} y tus preferencias.
        </p>
        <div style="display: flex; gap: 1rem;">
          <a [routerLink]="['/planificaciones', idPlanificacion, 'editar']" class="btn btn-primary">
            Aumentar presupuesto o editar
          </a>
          <a routerLink="/preferencias" class="btn btn-outline">
            Ajustar mis preferencias
          </a>
        </div>
      </div>

      <!-- Grid de Tarjetas de Recomendaciones -->
      <div *ngIf="!cargando() && recomendaciones().length > 0" class="cards-grid">
        <div 
          *ngFor="let rec of recomendaciones()" 
          class="card rec-card"
          [class.restaurante]="rec.tipo_recomendacion === 'RESTAURANTE'"
          [class.preparacion]="rec.tipo_recomendacion === 'PREPARACION_PROPIA'"
        >
          <!-- Encabezado de la Tarjeta -->
          <div class="rec-header">
            <div>
              <span 
                class="badge" 
                [ngClass]="rec.tipo_recomendacion === 'RESTAURANTE' ? 'badge-restaurante' : 'badge-preparacion'"
              >
                {{ rec.tipo_recomendacion === 'RESTAURANTE' ? ' RESTAURANTE' : ' PREPARACIÓN PROPIA' }}
              </span>
              <span 
                *ngIf="rec.zona_restaurante" 
                class="badge" 
                style="margin-left: 0.5rem; background: #e0f2fe; color: #0369a1; font-weight: 500;"
              >
                📍 {{ rec.zona_restaurante }}
              </span>
              <h3 class="rec-title">{{ rec.nombre }}</h3>
            </div>
            <div class="score-badge" title="Puntuación de afinidad calculada por el sistema">
              <span class="score-num">{{ rec.puntuacion | number:'1.0-0' }}</span>
              <span class="score-den">/100</span>
            </div>
          </div>

          <p *ngIf="rec.descripcion" class="rec-desc">{{ rec.descripcion }}</p>

          <!-- Desglose de Platos para Restaurante -->
          <div *ngIf="rec.tipo_recomendacion === 'RESTAURANTE' && rec.platos.length > 0" class="platos-summary">
            <div class="platos-summary-title">Menú sugerido:</div>
            <div *ngFor="let p of rec.platos" class="plato-item">
              <span>{{ p.cantidad }}x {{ p.nombre_plato }} ({{ p.personas_cubiertas }} pers/plato)</span>
              <strong>Bs {{ p.subtotal | number:'1.2-2' }}</strong>
            </div>
          </div>

          <!-- Métricas Financieras -->
          <div class="metrics-row">
            <div class="metric-box">
              <span class="metric-title">Costo Total</span>
              <span class="metric-value">Bs {{ rec.costo_total | number:'1.2-2' }}</span>
            </div>
            <div class="metric-box">
              <span class="metric-title">Costo / Persona</span>
              <span class="metric-value">Bs {{ rec.costo_por_persona | number:'1.2-2' }}</span>
            </div>
            <div class="metric-box highlight">
              <span class="metric-title">Ahorro Estimado</span>
              <span class="metric-value ahorro">
                Bs {{ calcularAhorro(rec) | number:'1.2-2' }}
              </span>
            </div>
          </div>

          <!-- Acciones de la Tarjeta -->
          <div class="card-footer-actions">
            <a 
              [routerLink]="['/recomendaciones', rec.id_recomendacion]" 
              class="btn btn-outline btn-sm"
            >
              Ver Detalle
            </a>

            <!-- Botón IA: ¿Por qué esta opción? (CU26) -->
            <button
              class="btn btn-outline btn-sm"
              style="border-color: #3b82f6; color: #2563eb;"
              (click)="explicarRecomendacion(rec)"
              title="Solicitar al asistente una explicación objetiva basada en datos reales"
            >
              <app-icon name="bot" class="app-icon-inline"></app-icon> ¿Por qué esta opción?
            </button>

            <!-- Acciones específicas para PREPARACION_PROPIA (CU15 y CU16) -->
            <ng-container *ngIf="rec.tipo_recomendacion === 'PREPARACION_PROPIA'">
              <a 
                [routerLink]="['/recomendaciones', rec.id_recomendacion, 'preparacion']" 
                class="btn btn-primary btn-sm"
              >
                <app-icon name="salad" class="app-icon-inline"></app-icon> Ver Ingredientes
              </a>
              <a 
                [routerLink]="['/recomendaciones', rec.id_recomendacion, 'lugares-compra']" 
                class="btn btn-outline btn-sm"
              >
                <app-icon name="store" class="app-icon-inline"></app-icon> Lugares de Compra (CU16)
              </a>
            </ng-container>
          </div>
        </div>
      </div>

      <!-- Modal / Panel de Explicación IA (CU26) -->
      <div *ngIf="modalExplicacion()" class="modal-overlay" (click)="cerrarModalExplicacion()">
        <div class="modal-card card" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3><app-icon name="bot" class="app-icon-inline"></app-icon> Explicación del Asistente MenuOpt</h3>
            <button class="btn-close" (click)="cerrarModalExplicacion()"><app-icon name="close" class="app-icon-inline"></app-icon></button>
          </div>
          <div class="modal-body">
            <div *ngIf="cargandoExplicacion()" style="text-align: center; padding: 2rem;">
              <p style="color: var(--text-muted);">Consultando al asistente...</p>
            </div>
            <div *ngIf="!cargandoExplicacion() && explicacionActual() as exp">
              <p style="font-size: 1rem; line-height: 1.5; color: #1e293b; background: #f8fafc; padding: 1rem; border-radius: 6px; border: 1px solid var(--border);">
                {{ exp.explicacion }}
              </p>
              <div style="margin-top: 1rem;" *ngIf="exp.detalles_clave.length > 0">
                <strong style="font-size: 0.85rem; color: var(--text-muted);">DATOS REALES VERIFICADOS:</strong>
                <ul style="margin: 0.25rem 0 0 1rem; font-size: 0.9rem;">
                  <li *ngFor="let det of exp.detalles_clave">{{ det }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="modal-footer" style="display: flex; justify-content: flex-end; margin-top: 1rem;">
            <button class="btn btn-primary btn-sm" (click)="cerrarModalExplicacion()">Entendido</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .recomendaciones-container {
      max-width: 1100px;
      margin: 0 auto;
    }
    .back-link {
      color: var(--text-muted);
      font-size: 0.875rem;
    }
    .header-card {
      margin-bottom: 1.5rem;
    }
    .header-main {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .header-actions {
      display: flex;
      gap: 0.75rem;
    }
    .plan-tag {
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--primary);
      text-transform: uppercase;
    }
    .empty-card {
      text-align: center;
      padding: 4rem 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
    }
    .rec-card {
      display: flex;
      flex-direction: column;
      border-top: 4px solid var(--border);
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .rec-card:hover {
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
    }
    .rec-card.restaurante {
      border-top-color: #1d3557;
    }
    .rec-card.preparacion {
      border-top-color: #10b981;
    }
    .badge-restaurante {
      background-color: #e2e8f0;
      color: #1d3557;
    }
    .badge-preparacion {
      background-color: #d1fae5;
      color: #065f46;
    }
    .rec-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.75rem;
    }
    .rec-title {
      font-size: 1.15rem;
      margin-top: 0.35rem;
      line-height: 1.3;
    }
    .score-badge {
      background-color: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.25rem 0.5rem;
      text-align: center;
    }
    .score-num {
      font-weight: 700;
      font-size: 1.1rem;
      color: var(--secondary);
    }
    .score-den {
      font-size: 0.7rem;
      color: var(--text-muted);
    }
    .rec-desc {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 1rem;
    }
    .platos-summary {
      background-color: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.75rem;
      margin-bottom: 1rem;
      font-size: 0.825rem;
    }
    .platos-summary-title {
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 0.35rem;
      font-size: 0.75rem;
      text-transform: uppercase;
    }
    .plato-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.25rem;
    }
    .metrics-row {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 0.5rem;
      background-color: #f1f5f9;
      padding: 0.75rem;
      border-radius: var(--radius);
      margin-top: auto;
      margin-bottom: 1rem;
      text-align: center;
    }
    .metric-title {
      display: block;
      font-size: 0.65rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
    }
    .metric-value {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-main);
    }
    .metric-value.ahorro {
      color: #059669;
    }
    .card-footer-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.45);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 1rem;
    }
    .modal-card {
      max-width: 550px;
      width: 100%;
      background: #ffffff;
      border-radius: 8px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
      padding: 1.5rem;
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }
    .modal-header h3 {
      margin: 0;
      font-size: 1.15rem;
    }
  `]
})
export class ListaRecomendacionesComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private recomendacionService = inject(RecomendacionService);
  private planificacionService = inject(PlanificacionService);
  private asistenteService = inject(AsistenteIAService);

  idPlanificacion!: number;
  planificacion = signal<Planificacion | null>(null);
  recomendaciones = signal<Recomendacion[]>([]);

  cargando = signal<boolean>(true);
  regenerando = signal<boolean>(false);
  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  // Modal de Explicación IA (CU26)
  modalExplicacion = signal<boolean>(false);
  cargandoExplicacion = signal<boolean>(false);
  explicacionActual = signal<ExplicacionRespuesta | null>(null);

  ngOnInit(): void {
    this.idPlanificacion = Number(this.route.snapshot.paramMap.get('id'));
    if (this.idPlanificacion) {
      this.cargarDatos();
    }
  }

  cargarDatos(): void {
    this.cargando.set(true);
    // Cargar datos de la planificación
    this.planificacionService.obtenerPlanificacion(this.idPlanificacion).subscribe({
      next: (plan) => {
        this.planificacion.set(plan);
        // Cargar recomendaciones
        this.recomendacionService.listarRecomendaciones(this.idPlanificacion).subscribe({
          next: (recs) => {
            this.recomendaciones.set(recs);
            this.cargando.set(false);
          },
          error: (err) => {
            console.error('Error al listar recomendaciones:', err);
            this.mensajeError.set('No se pudieron cargar las recomendaciones.');
            this.cargando.set(false);
          }
        });
      },
      error: (err) => {
        console.error('Error al obtener planificación:', err);
        this.mensajeError.set('No se encontró la planificación asociada.');
        this.cargando.set(false);
      }
    });
  }

  calcularAhorro(rec: Recomendacion): number {
    const pres = Number(this.planificacion()?.presupuesto) || 0;
    const costo = Number(rec.costo_total) || 0;
    return Math.max(0, pres - costo);
  }

  regenerarRecomendaciones(): void {
    const confirmar = confirm('¿Deseas recalcular las recomendaciones con los datos actuales?');
    if (!confirmar) return;

    this.regenerando.set(true);
    this.mensajeError.set(null);
    this.mensajeExito.set(null);

    this.recomendacionService.generarRecomendaciones(this.idPlanificacion).subscribe({
      next: (nuevas) => {
        this.recomendaciones.set(nuevas);
        this.regenerando.set(false);
        this.mensajeExito.set(`Recomendaciones actualizadas con éxito (${nuevas.length} alternativas generadas).`);
        setTimeout(() => this.mensajeExito.set(null), 3000);
      },
      error: (err) => {
        console.error('Error al regenerar recomendaciones:', err);
        this.regenerando.set(false);
        this.mensajeError.set(err.error?.detail || 'No se pudieron regenerar las recomendaciones.');
      }
    });
  }

  // --- Integración Asistente IA (CU26) ---
  explicarRecomendacion(rec: Recomendacion): void {
    this.modalExplicacion.set(true);
    this.cargandoExplicacion.set(true);
    this.explicacionActual.set(null);

    this.asistenteService.explicarRecomendacion(rec.id_recomendacion).subscribe({
      next: (exp) => {
        this.explicacionActual.set(exp);
        this.cargandoExplicacion.set(false);
      },
      error: (err) => {
        this.cargandoExplicacion.set(false);
        this.explicacionActual.set({
          id_referencia: rec.id_recomendacion,
          tipo: 'RECOMENDACION',
          explicacion: err.error?.detail || 'El asistente no pudo procesar la explicación en este momento.',
          detalles_clave: []
        });
      }
    });
  }

  cerrarModalExplicacion(): void {
    this.modalExplicacion.set(false);
    this.explicacionActual.set(null);
  }
}
