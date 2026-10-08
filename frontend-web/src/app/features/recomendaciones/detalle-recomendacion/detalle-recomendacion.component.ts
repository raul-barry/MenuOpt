import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU13 - Detalle de Recomendación
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { RecomendacionService } from '../../../core/services/recomendacion.service';
import { Recomendacion } from '../../../core/models/recomendacion.model';

@Component({
  selector: 'app-detalle-recomendacion',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterLink],
  template: `
    <div class="detalle-rec-container">
      <div *ngIf="recomendacion() as rec" style="margin-bottom: 1rem;">
        <a [routerLink]="['/planificaciones', rec.id_planificacion, 'recomendaciones']" class="back-link">
          &larr; Volver a las recomendaciones
        </a>
      </div>

      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Cargando detalle de la recomendación...</p>
      </div>

      <div *ngIf="!cargando() && recomendacion() as rec">
        <div class="card header-card">
          <div class="header-main">
            <div>
              <span 
                class="badge" 
                [ngClass]="rec.tipo_recomendacion === 'RESTAURANTE' ? 'badge-restaurante' : 'badge-preparacion'"
              >
                {{ rec.tipo_recomendacion === 'RESTAURANTE' ? 'RESTAURANTE' : 'PREPARACIÓN PROPIA' }}
              </span>
              <h2 style="margin-top: 0.5rem;">{{ rec.nombre }}</h2>
              <p *ngIf="rec.descripcion" style="color: var(--text-muted);">{{ rec.descripcion }}</p>
            </div>
            <div class="score-box">
              <span class="score-val">{{ rec.puntuacion | number:'1.0-0' }}</span>
              <span class="score-lbl">Puntos / 100</span>
            </div>
          </div>

          <!-- Métricas -->
          <div class="grid-3" style="margin-top: 1.5rem;">
            <div class="metric-box">
              <span class="metric-lbl">Costo Total</span>
              <div class="metric-val primary">Bs {{ rec.costo_total | number:'1.2-2' }}</div>
            </div>
            <div class="metric-box">
              <span class="metric-lbl">Costo por Persona</span>
              <div class="metric-val">Bs {{ rec.costo_por_persona | number:'1.2-2' }}</div>
            </div>
            <div class="metric-box">
              <span class="metric-lbl">Fecha de Cálculo</span>
              <div class="metric-val" style="font-size: 1.1rem; color: var(--text-main);">
                {{ rec.fecha_generacion | date:'shortDate' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Detalle Restaurante -->
        <div *ngIf="rec.tipo_recomendacion === 'RESTAURANTE'" class="card">
          <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
            <div>
              <h3>Detalle de Platos a Consumir</h3>
              <span class="badge badge-secondary" *ngIf="rec.nombre_restaurante">{{ rec.nombre_restaurante }}</span>
            </div>
            <a
              *ngIf="rec.id_restaurante"
              [routerLink]="['/restaurantes', rec.id_restaurante, 'reservar']"
              [queryParams]="{ id_planificacion: rec.id_planificacion }"
              class="btn btn-primary btn-sm"
              title="Reservar mesa para esta recomendación gastronómica (CU20, CU21)"
            >
              <span><app-icon name="calendar" class="app-icon-inline"></app-icon></span> Reservar Mesa
            </a>
          </div>

          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Plato</th>
                  <th>Rendimiento</th>
                  <th>Cantidad</th>
                  <th>Precio Unitario</th>
                  <th style="text-align: right;">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let p of rec.platos">
                  <td><strong>{{ p.nombre_plato }}</strong></td>
                  <td>{{ p.personas_cubiertas }} personas</td>
                  <td>{{ p.cantidad }} unidad(es)</td>
                  <td>Bs {{ p.precio_unitario | number:'1.2-2' }}</td>
                  <td style="text-align: right;"><strong>Bs {{ p.subtotal | number:'1.2-2' }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Detalle Preparación Propia -->
        <div *ngIf="rec.tipo_recomendacion === 'PREPARACION_PROPIA'" class="card">
          <div class="card-header">
            <h3>Detalle de Preparación Casera</h3>
          </div>
          <p style="color: var(--text-muted); margin-bottom: 1.5rem;">
            Esta alternativa fue elaborada calculando las cantidades de ingredientes y consultando los mejores precios disponibles en mercados y supermercados registrados.
          </p>

          <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <a [routerLink]="['/recomendaciones', rec.id_recomendacion, 'preparacion']" class="btn btn-primary">
              <app-icon name="salad" class="app-icon-inline"></app-icon> Consultar Ingredientes Escalados (CU15)
            </a>
            <a [routerLink]="['/recomendaciones', rec.id_recomendacion, 'lugares-compra']" class="btn btn-outline">
              <app-icon name="store" class="app-icon-inline"></app-icon> Consultar Lugares de Compra (CU16)
            </a>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .detalle-rec-container {
      max-width: 950px;
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
      align-items: flex-start;
      gap: 1rem;
    }
    .badge-restaurante {
      background-color: #e2e8f0;
      color: #1d3557;
    }
    .badge-preparacion {
      background-color: #d1fae5;
      color: #065f46;
    }
    .score-box {
      text-align: center;
      background-color: #f8fafc;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 0.5rem 1rem;
      flex-shrink: 0;
    }
    .score-val {
      font-size: 2rem;
      font-weight: 700;
      color: var(--secondary);
      display: block;
      line-height: 1;
    }
    .score-lbl {
      font-size: 0.7rem;
      color: var(--text-muted);
    }
    .metric-box {
      text-align: center;
      background-color: #f8fafc;
      padding: 1rem;
      border-radius: var(--radius);
      border: 1px solid var(--border);
    }
    .metric-lbl {
      display: block;
      font-size: 0.7rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 0.25rem;
    }
    .metric-val {
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--secondary);
    }
    .metric-val.primary {
      color: var(--primary);
    }
  `]
})
export class DetalleRecomendacionComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private recomendacionService = inject(RecomendacionService);

  idRecomendacion!: number;
  recomendacion = signal<Recomendacion | null>(null);
  cargando = signal<boolean>(true);
  mensajeError = signal<string | null>(null);

  ngOnInit(): void {
    this.idRecomendacion = Number(this.route.snapshot.paramMap.get('id'));
    if (this.idRecomendacion) {
      this.cargarRecomendacion();
    }
  }

  cargarRecomendacion(): void {
    this.cargando.set(true);
    this.recomendacionService.obtenerRecomendacion(this.idRecomendacion).subscribe({
      next: (rec) => {
        this.recomendacion.set(rec);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al cargar recomendación:', err);
        this.mensajeError.set('No se pudo cargar el detalle de la recomendación.');
        this.cargando.set(false);
      }
    });
  }
}
