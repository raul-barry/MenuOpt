// CASO DE USO: CU15 - Consultar ingredientes para preparación propia
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { PreparacionService } from '../../../core/services/preparacion.service';
import { PreparacionPropia } from '../../../core/models/preparacion.model';

@Component({
  selector: 'app-detalle-preparacion',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="preparacion-container">
      <div style="margin-bottom: 1rem;">
        <a [routerLink]="['/recomendaciones', idRecomendacion]" class="back-link">
          &larr; Volver al resumen de la recomendación
        </a>
      </div>

      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Calculando ingredientes escalados...</p>
      </div>

      <div *ngIf="!cargando() && preparacion() as prep">
        <!-- Header -->
        <div class="card header-card">
          <div class="header-main">
            <div>
              <span class="badge badge-success">🍳 PREPARACIÓN CASERA</span>
              <h2 style="margin-top: 0.5rem;">{{ prep.nombre }}</h2>
              <p *ngIf="prep.descripcion" style="color: var(--text-muted); margin-top: 0.25rem;">
                {{ prep.descripcion }}
              </p>
            </div>
            <a [routerLink]="['/recomendaciones', idRecomendacion, 'lugares-compra']" class="btn btn-outline">
              🏪 Ver Dónde Comprar (CU16) &rarr;
            </a>
          </div>

          <div class="grid-3" style="margin-top: 1.5rem;">
            <div class="metric-card">
              <span class="metric-lbl">Comensales Escalados</span>
              <div class="metric-val">{{ prep.cantidad_personas }} personas</div>
            </div>
            <div class="metric-card">
              <span class="metric-lbl">Costo Total Insumos</span>
              <div class="metric-val primary">Bs {{ prep.costo_estimado | number:'1.2-2' }}</div>
            </div>
            <div class="metric-card">
              <span class="metric-lbl">Costo por Persona</span>
              <div class="metric-val">Bs {{ prep.costo_por_persona | number:'1.2-2' }}</div>
            </div>
          </div>
        </div>

        <!-- Tabla de Ingredientes (CU15) -->
        <div class="card">
          <div class="card-header">
            <div>
              <h3>Lista de Ingredientes Necesarios (CU15)</h3>
              <p style="font-size: 0.85rem; color: var(--text-muted); margin: 0;">
                Cantidades proporcionales exactas calculadas según la receta base para {{ prep.cantidad_personas }} personas.
              </p>
            </div>
            <span class="badge badge-secondary">{{ prep.ingredientes.length }} insumos</span>
          </div>

          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Ingrediente</th>
                  <th>Cantidad Requerida</th>
                  <th>Unidad</th>
                  <th>Precio Unitario Usado</th>
                  <th>Costo Estimado</th>
                  <th>Lugar de Compra Sugerido</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let ing of prep.ingredientes; let i = index">
                  <td>{{ i + 1 }}</td>
                  <td><strong>{{ ing.nombre_ingrediente }}</strong></td>
                  <td>{{ ing.cantidad | number:'1.2-2' }}</td>
                  <td><span class="badge badge-secondary">{{ ing.unidad_medida }}</span></td>
                  <td>
                    <span *ngIf="ing.precio_unitario_usado !== null && ing.precio_unitario_usado !== undefined">
                      Bs {{ ing.precio_unitario_usado | number:'1.2-2' }}
                    </span>
                    <span *ngIf="ing.precio_unitario_usado === null || ing.precio_unitario_usado === undefined" style="color: var(--danger);">
                      No disponible
                    </span>
                  </td>
                  <td>
                    <strong>Bs {{ ing.costo_estimado | number:'1.2-2' }}</strong>
                  </td>
                  <td>
                    <span *ngIf="ing.nombre_lugar_compra">
                      📍 {{ ing.nombre_lugar_compra }}
                    </span>
                    <span *ngIf="!ing.nombre_lugar_compra" style="color: var(--text-muted);">
                      Lugar genérico
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="totales-footer">
            <span>Total Insumos Calculados:</span>
            <strong class="total-valor">Bs {{ prep.costo_estimado | number:'1.2-2' }}</strong>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .preparacion-container {
      max-width: 1050px;
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
    .metric-card {
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
      color: #059669;
    }
    .totales-footer {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 1rem;
      padding-top: 1rem;
      margin-top: 1rem;
      border-top: 2px solid var(--border);
      font-size: 1.1rem;
    }
    .total-valor {
      color: #059669;
      font-size: 1.35rem;
    }
  `]
})
export class DetallePreparacionComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private preparacionService = inject(PreparacionService);

  idRecomendacion!: number;
  preparacion = signal<PreparacionPropia | null>(null);
  cargando = signal<boolean>(true);
  mensajeError = signal<string | null>(null);

  ngOnInit(): void {
    this.idRecomendacion = Number(this.route.snapshot.paramMap.get('id'));
    if (this.idRecomendacion) {
      this.cargarPreparacion();
    }
  }

  cargarPreparacion(): void {
    this.cargando.set(true);
    this.preparacionService.obtenerDetallePreparacion(this.idRecomendacion).subscribe({
      next: (prep) => {
        this.preparacion.set(prep);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al cargar detalle de preparación:', err);
        if (err.status === 403) {
          this.mensajeError.set('No tienes permiso para acceder a los datos de esta preparación.');
        } else {
          this.mensajeError.set('No se pudieron consultar los ingredientes de esta preparación.');
        }
        this.cargando.set(false);
      }
    });
  }
}
