import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU14 - Comparar alternativas (RESTAURANTE vs PREPARACION_PROPIA)
import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { RecomendacionService } from '../../../core/services/recomendacion.service';
import { AsistenteIAService } from '../../../core/services/asistente-ia.service';
import { ComparacionPlanificacion, AlternativaComparacion } from '../../../core/models/comparacion.model';
import { ExplicacionRespuesta } from '../../../core/models/asistente-ia.model';

@Component({
  selector: 'app-comparacion',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterLink],
  template: `
    <div class="comparacion-container">
      <div style="margin-bottom: 1rem;">
        <a [routerLink]="['/planificaciones', idPlanificacion, 'recomendaciones']" class="back-link">
          &larr; Volver a las recomendaciones
        </a>
      </div>

      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Calculando matriz comparativa de alternativas...</p>
      </div>

      <div *ngIf="!cargando() && comparacion() as comp">
        <!-- Header de la Comparativa -->
        <div class="card header-card">
          <div class="header-main">
            <div>
              <span class="badge badge-secondary">ANÁLISIS COMPARATIVO (CU14)</span>
              <h2 style="margin-top: 0.5rem;">Comparación de Alternativas Gastronómicas</h2>
              <p style="color: var(--text-muted); margin-top: 0.25rem;">
                Evaluación para <strong>{{ comp.cantidad_personas }} comensales</strong> con presupuesto límite de <strong>Bs {{ comp.presupuesto | number:'1.2-2' }}</strong> ({{ comp.tipo_comida }}).
              </p>
            </div>
            <div style="display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;">
              <button
                class="btn btn-outline-info btn-sm"
                (click)="explicarComparacion()"
                title="Explicar comparativa objetiva mediante asistente IA (CU26)"
              >
                <app-icon name="bot" class="app-icon-inline"></app-icon> Explicar Comparación
              </button>
              <div class="header-summary-box">
                <span class="sum-count">{{ comp.total_alternativas }}</span>
                <span class="sum-lbl">Opciones Viables</span>
              </div>
            </div>
          </div>

          <!-- Resumen de Destacados: Menor Costo & Mejor Puntuación -->
          <div class="grid-2" style="margin-top: 1.5rem;" *ngIf="comp.mejor_opcion_costo || comp.mejor_opcion_puntuacion">
            <div class="highlight-card cost-card" *ngIf="comp.mejor_opcion_costo">
              <div class="hl-badge"><app-icon name="money" class="app-icon-inline"></app-icon> MENOR COSTO</div>
              <h4>{{ comp.mejor_opcion_costo.nombre }}</h4>
              <p class="hl-sub">
                {{ comp.mejor_opcion_costo.tipo_recomendacion }}
                <span *ngIf="comp.mejor_opcion_costo.zona_restaurante" style="margin-left: 0.35rem; color: #0284c7;">
                  📍 {{ comp.mejor_opcion_costo.zona_restaurante }}
                </span>
              </p>
              <div class="hl-row">
                <span>Costo: <strong>Bs {{ comp.mejor_opcion_costo.costo_total | number:'1.2-2' }}</strong></span>
                <span>Ahorro: <strong class="text-success">Bs {{ comp.mejor_opcion_costo.ahorro_respecto_presupuesto | number:'1.2-2' }}</strong></span>
              </div>
            </div>

            <div class="highlight-card score-card" *ngIf="comp.mejor_opcion_puntuacion">
              <div class="hl-badge score"><app-icon name="star" class="app-icon-inline"></app-icon> MEJOR PUNTUADA</div>
              <h4>{{ comp.mejor_opcion_puntuacion.nombre }}</h4>
              <p class="hl-sub">
                {{ comp.mejor_opcion_puntuacion.tipo_recomendacion }}
                <span *ngIf="comp.mejor_opcion_puntuacion.zona_restaurante" style="margin-left: 0.35rem; color: #0284c7;">
                  📍 {{ comp.mejor_opcion_puntuacion.zona_restaurante }}
                </span>
              </p>
              <div class="hl-row">
                <span>Afinidad: <strong>{{ comp.mejor_opcion_puntuacion.puntuacion | number:'1.0-0' }} / 100</strong></span>
                <span>Costo: <strong>Bs {{ comp.mejor_opcion_puntuacion.costo_total | number:'1.2-2' }}</strong></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Filtros Visuales -->
        <div class="filter-bar card">
          <div class="filter-group">
            <span class="filter-label">Filtrar por tipo:</span>
            <button 
              class="btn btn-sm" 
              [ngClass]="filtroTipo() === 'TODAS' ? 'btn-primary' : 'btn-outline'"
              (click)="filtroTipo.set('TODAS')"
            >
              Todas ({{ comp.alternativas.length }})
            </button>
            <button 
              class="btn btn-sm" 
              [ngClass]="filtroTipo() === 'RESTAURANTE' ? 'btn-primary' : 'btn-outline'"
              (click)="filtroTipo.set('RESTAURANTE')"
            >
              Solo Restaurantes
            </button>
            <button 
              class="btn btn-sm" 
              [ngClass]="filtroTipo() === 'PREPARACION_PROPIA' ? 'btn-primary' : 'btn-outline'"
              (click)="filtroTipo.set('PREPARACION_PROPIA')"
            >
              Solo Preparación Propia
            </button>
          </div>

          <div class="filter-group">
            <span class="filter-label">Ordenar por:</span>
            <select class="form-control form-control-sm" style="width: auto;" (change)="onCambiarOrden($event)">
              <option value="OFICIAL">Orden oficial (Recomendado)</option>
              <option value="COSTO_ASC">Menor costo total</option>
              <option value="SCORE_DESC">Mayor puntuación</option>
              <option value="AHORRO_DESC">Mayor ahorro</option>
            </select>
          </div>
        </div>

        <!-- Lista de Alternativas Comparadas -->
        <div class="alternativas-grid">
          <div 
            *ngFor="let alt of alternativasFiltradas()" 
            class="card alt-card"
            [class.alt-restaurante]="alt.tipo_recomendacion === 'RESTAURANTE'"
            [class.alt-preparacion]="alt.tipo_recomendacion === 'PREPARACION_PROPIA'"
          >
            <!-- Badge y Título -->
            <div class="alt-header">
              <div>
                <span 
                  class="badge" 
                  [ngClass]="alt.tipo_recomendacion === 'RESTAURANTE' ? 'badge-restaurante' : 'badge-preparacion'"
                >
                  {{ alt.tipo_recomendacion === 'RESTAURANTE' ? 'RESTAURANTE' : 'PREPARACIÓN PROPIA' }}
                </span>
                <span 
                  *ngIf="alt.zona_restaurante" 
                  class="badge" 
                  style="margin-left: 0.5rem; background: #e0f2fe; color: #0369a1; font-weight: 500;"
                >
                  📍 {{ alt.zona_restaurante }}
                </span>
                <span 
                  *ngIf="alt.puntuacion === comp.mejor_opcion_puntuacion?.puntuacion" 
                  class="badge badge-warning" 
                  style="margin-left: 0.5rem;"
                >
                  Recomendada por el sistema
                </span>
                <h3 class="alt-nombre">{{ alt.nombre }}</h3>
              </div>
              <div class="score-chip">
                <span class="score-val">{{ alt.puntuacion | number:'1.0-0' }}</span>
                <span class="score-lbl">pts</span>
              </div>
            </div>

            <!-- Resumen Cualitativo -->
            <p class="alt-resumen">{{ alt.resumen }}</p>

            <!-- Tabla de Costos y Ahorro -->
            <div class="metrics-table">
              <div class="metric-row">
                <span class="metric-lbl">Presupuesto inicial:</span>
                <span class="metric-val">Bs {{ comp.presupuesto | number:'1.2-2' }}</span>
              </div>
              <div class="metric-row">
                <span class="metric-lbl">Costo total de la opción:</span>
                <span class="metric-val" style="color: var(--secondary);">
                  Bs {{ alt.costo_total | number:'1.2-2' }}
                </span>
              </div>
              <div class="metric-row">
                <span class="metric-lbl">Costo por persona:</span>
                <span class="metric-val">
                  Bs {{ alt.costo_por_persona | number:'1.2-2' }}
                </span>
              </div>
              <div class="metric-row highlight">
                <span class="metric-lbl">Ahorro conseguido:</span>
                <span class="metric-val text-success">
                  Bs {{ alt.ahorro_respecto_presupuesto | number:'1.2-2' }}
                </span>
              </div>
            </div>

            <!-- Botones de Acción -->
            <div class="alt-actions">
              <a 
                [routerLink]="['/recomendaciones', alt.id_recomendacion]" 
                class="btn btn-outline btn-sm"
              >
                Ver Detalle General
              </a>

              <!-- Acciones exclusivas para PREPARACION_PROPIA (CU15 y CU16) -->
              <ng-container *ngIf="alt.tipo_recomendacion === 'PREPARACION_PROPIA'">
                <a 
                  [routerLink]="['/recomendaciones', alt.id_recomendacion, 'preparacion']" 
                  class="btn btn-primary btn-sm"
                >
                  <app-icon name="salad" class="app-icon-inline"></app-icon> Ingredientes (CU15)
                </a>
                <a 
                  [routerLink]="['/recomendaciones', alt.id_recomendacion, 'lugares-compra']" 
                  class="btn btn-outline btn-sm"
                >
                  <app-icon name="store" class="app-icon-inline"></app-icon> Lugares de Compra (CU16)
                </a>
              </ng-container>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal / Panel de Explicación de Comparación IA (CU26) -->
      <div *ngIf="modalExplicacion()" class="modal-overlay" (click)="cerrarModalExplicacion()">
        <div class="modal-card card" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3><app-icon name="bot" class="app-icon-inline"></app-icon> Explicación Comparativa (CU14 con Asistencia IA)</h3>
            <button class="btn-close" (click)="cerrarModalExplicacion()"><app-icon name="close" class="app-icon-inline"></app-icon></button>
          </div>
          <div class="modal-body">
            <div *ngIf="cargandoExplicacion()" style="text-align: center; padding: 2rem;">
              <p style="color: var(--text-muted);">El asistente está analizando la matriz comparativa...</p>
            </div>
            <div *ngIf="!cargandoExplicacion() && explicacionActual() as exp">
              <p style="font-size: 1rem; line-height: 1.5; color: #1e293b; background: #f8fafc; padding: 1rem; border-radius: 6px; border: 1px solid var(--border);">
                {{ exp.explicacion }}
              </p>
              <div style="margin-top: 1rem;" *ngIf="exp.detalles_clave.length > 0">
                <strong style="font-size: 0.85rem; color: var(--text-muted);">PUNTOS CLAVE DE LA COMPARATIVA:</strong>
                <ul style="margin: 0.25rem 0 0 1rem; font-size: 0.9rem;">
                  <li *ngFor="let det of exp.detalles_clave">{{ det }}</li>
                </ul>
              </div>
            </div>
          </div>
          <div class="modal-footer" style="display: flex; justify-content: flex-end; margin-top: 1rem;">
            <button class="btn btn-primary btn-sm" (click)="cerrarModalExplicacion()">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .comparacion-container {
      max-width: 1100px;
      margin: 0 auto;
    }
    .back-link {
      color: var(--text-muted);
      font-size: 0.875rem;
    }
    .header-card {
      margin-bottom: 1rem;
    }
    .header-main {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .header-summary-box {
      text-align: center;
      background-color: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.5rem 1.25rem;
    }
    .sum-count {
      font-size: 1.75rem;
      font-weight: 700;
      color: var(--secondary);
      display: block;
      line-height: 1;
    }
    .sum-lbl {
      font-size: 0.7rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 600;
    }
    .highlight-card {
      padding: 1rem;
      border-radius: var(--radius);
      border: 1px solid var(--border);
    }
    .cost-card {
      background-color: #ecfdf5;
      border-color: #a7f3d0;
    }
    .score-card {
      background-color: #eff6ff;
      border-color: #bfdbfe;
    }
    .hl-badge {
      font-size: 0.7rem;
      font-weight: 700;
      color: #065f46;
      margin-bottom: 0.25rem;
    }
    .hl-badge.score {
      color: #1e40af;
    }
    .highlight-card h4 {
      margin: 0;
      font-size: 1rem;
    }
    .hl-sub {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
    }
    .hl-row {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
    }
    .text-success {
      color: #059669;
    }
    .filter-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      padding: 0.75rem 1.25rem;
      margin-bottom: 1.5rem;
    }
    .filter-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .filter-label {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
    }
    .alternativas-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
    }
    .alt-card {
      display: flex;
      flex-direction: column;
      border-top: 4px solid var(--border);
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .alt-card:hover {
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
    }
    .alt-restaurante {
      border-top-color: #1d3557;
    }
    .alt-preparacion {
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
    .alt-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.5rem;
    }
    .alt-nombre {
      font-size: 1.1rem;
      margin-top: 0.35rem;
      line-height: 1.3;
    }
    .score-chip {
      background-color: #f1f5f9;
      border-radius: var(--radius);
      padding: 0.25rem 0.5rem;
      text-align: center;
    }
    .score-val {
      font-weight: 700;
      font-size: 1rem;
      color: var(--secondary);
    }
    .score-lbl {
      font-size: 0.65rem;
      color: var(--text-muted);
      margin-left: 2px;
    }
    .alt-resumen {
      font-size: 0.825rem;
      color: var(--text-muted);
      margin-bottom: 1rem;
    }
    .metrics-table {
      background-color: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.75rem;
      margin-top: auto;
      margin-bottom: 1rem;
      font-size: 0.825rem;
    }
    .metric-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.25rem;
    }
    .metric-row.highlight {
      border-top: 1px solid var(--border);
      padding-top: 0.25rem;
      margin-top: 0.25rem;
      font-weight: 600;
    }
    .alt-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(15, 23, 42, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      backdrop-filter: blur(2px);
    }
    .modal-card {
      background: white;
      border-radius: 8px;
      max-width: 650px;
      width: 90%;
      max-height: 85vh;
      overflow-y: auto;
      padding: 1.5rem;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.75rem;
      margin-bottom: 1rem;
    }
    .modal-header h3 {
      margin: 0;
      font-size: 1.15rem;
      color: var(--text-color);
    }
    .btn-close {
      background: none;
      border: none;
      font-size: 1.25rem;
      cursor: pointer;
      color: var(--text-muted);
    }
  `]
})
export class ComparacionComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private recomendacionService = inject(RecomendacionService);
  private asistenteService = inject(AsistenteIAService);

  idPlanificacion!: number;
  comparacion = signal<ComparacionPlanificacion | null>(null);
  cargando = signal<boolean>(true);
  mensajeError = signal<string | null>(null);

  // Estados Asistente IA (CU26)
  modalExplicacion = signal<boolean>(false);
  cargandoExplicacion = signal<boolean>(false);
  explicacionActual = signal<ExplicacionRespuesta | null>(null);

  filtroTipo = signal<'TODAS' | 'RESTAURANTE' | 'PREPARACION_PROPIA'>('TODAS');
  criterioOrden = signal<'OFICIAL' | 'COSTO_ASC' | 'SCORE_DESC' | 'AHORRO_DESC'>('OFICIAL');

  alternativasFiltradas = computed(() => {
    const comp = this.comparacion();
    if (!comp) return [];

    let list = [...comp.alternativas];

    // Filtro por tipo
    const tipo = this.filtroTipo();
    if (tipo !== 'TODAS') {
      list = list.filter(a => a.tipo_recomendacion === tipo);
    }

    // Ordenamiento en frontend
    const orden = this.criterioOrden();
    switch (orden) {
      case 'COSTO_ASC':
        list.sort((a, b) => Number(a.costo_total) - Number(b.costo_total));
        break;
      case 'SCORE_DESC':
        list.sort((a, b) => Number(b.puntuacion) - Number(a.puntuacion));
        break;
      case 'AHORRO_DESC':
        list.sort((a, b) => Number(b.ahorro_respecto_presupuesto) - Number(a.ahorro_respecto_presupuesto));
        break;
      case 'OFICIAL':
      default:
        // Mantener orden original del backend
        break;
    }

    return list;
  });

  ngOnInit(): void {
    this.idPlanificacion = Number(this.route.snapshot.paramMap.get('id'));
    if (this.idPlanificacion) {
      this.cargarComparacion();
    }
  }

  cargarComparacion(): void {
    this.cargando.set(true);
    this.recomendacionService.compararAlternativas(this.idPlanificacion).subscribe({
      next: (res) => {
        this.comparacion.set(res);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al cargar comparación:', err);
        if (err.status === 403) {
          this.mensajeError.set('No tienes permiso para acceder a esta comparativa.');
        } else {
          this.mensajeError.set('No se pudieron obtener las alternativas para comparación.');
        }
        this.cargando.set(false);
      }
    });
  }

  onCambiarOrden(event: Event): void {
    const valor = (event.target as HTMLSelectElement).value as any;
    this.criterioOrden.set(valor);
  }

  explicarComparacion(): void {
    this.modalExplicacion.set(true);
    this.cargandoExplicacion.set(true);
    this.explicacionActual.set(null);

    this.asistenteService.explicarComparacion(this.idPlanificacion).subscribe({
      next: (resp) => {
        this.explicacionActual.set(resp);
        this.cargandoExplicacion.set(false);
      },
      error: (err) => {
        console.error('Error al solicitar explicación de comparación con IA:', err);
        this.explicacionActual.set({
          id_referencia: this.idPlanificacion,
          tipo: 'COMPARACION',
          explicacion: 'No se pudo generar la explicación con IA en este momento. La matriz comparativa objetiva de costos y puntuaciones se mantiene visible en pantalla.',
          detalles_clave: []
        });
        this.cargandoExplicacion.set(false);
      }
    });
  }

  cerrarModalExplicacion(): void {
    this.modalExplicacion.set(false);
    this.explicacionActual.set(null);
  }
}
