import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU16 - Consultar lugares de compra agrupados
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { LugarCompraService } from '../../../core/services/lugar-compra.service';
import { LugaresCompraRecomendacion } from '../../../core/models/lugar-compra.model';

@Component({
  selector: 'app-lugares-compra',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterLink],
  template: `
    <div class="lugares-container">
      <div style="margin-bottom: 1rem;">
        <a [routerLink]="['/recomendaciones', idRecomendacion, 'preparacion']" class="back-link">
          &larr; Volver a la lista de ingredientes (CU15)
        </a>
      </div>

      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Organizando compras por establecimiento comercial...</p>
      </div>

      <div *ngIf="!cargando() && resumenCompras() as res">
        <!-- Header -->
        <div class="card header-card">
          <div class="header-main">
            <div>
              <span class="badge badge-success"><app-icon name="cart" class="app-icon-inline"></app-icon> LISTA DE COMPRAS AGRUPADA (CU16)</span>
              <h2 style="margin-top: 0.5rem;">{{ res.nombre_preparacion }}</h2>
              <p style="color: var(--text-muted); margin-top: 0.25rem;">
                Adquiere tus insumos optimizando costos según los comercios con mejores precios disponibles.
              </p>
            </div>
            <div class="header-metric">
              <span class="metric-title">Gasto Total Previsto</span>
              <span class="metric-value">Bs {{ res.costo_total_estimado | number:'1.2-2' }}</span>
              <span class="metric-sub">{{ res.total_lugares }} establecimiento(s)</span>
            </div>
          </div>
        </div>

        <!-- Tarjetas por Lugar de Compra -->
        <div *ngIf="res.lugares.length === 0" class="card" style="text-align: center; padding: 2rem;">
          <p style="color: var(--text-muted);">No hay establecimientos específicos vinculados a esta preparación.</p>
        </div>

        <div *ngFor="let lugar of res.lugares" class="card lugar-card">
          <div class="lugar-header">
            <div class="lugar-title-group">
              <span class="lugar-icono"><app-icon name="store" class="app-icon-inline"></app-icon></span>
              <div>
                <h3 class="lugar-nombre">{{ lugar.nombre_lugar }}</h3>
                <div class="lugar-tipo badge badge-secondary" *ngIf="lugar.tipo_lugar">
                  {{ lugar.tipo_lugar }}
                </div>
              </div>
            </div>

            <!-- Subtotal de este comercio -->
            <div class="lugar-subtotal">
              <span class="subtotal-label">Subtotal en este local:</span>
              <strong class="subtotal-val">Bs {{ lugar.subtotal_estimado | number:'1.2-2' }}</strong>
            </div>
          </div>

          <!-- Ubicación física del comercio -->
          <div class="lugar-info" *ngIf="lugar.direccion || lugar.zona || lugar.telefono">
            <span *ngIf="lugar.direccion"><app-icon name="pin" class="app-icon-inline"></app-icon> {{ lugar.direccion }}</span>
            <span *ngIf="lugar.zona">| Zona: {{ lugar.zona }}</span>
            <span *ngIf="lugar.ciudad">({{ lugar.ciudad }})</span>
            <span *ngIf="lugar.telefono">| <app-icon name="phone" class="app-icon-inline"></app-icon> {{ lugar.telefono }}</span>
          </div>

          <!-- Tabla de productos a adquirir en este comercio -->
          <div class="table-responsive" style="margin-top: 1rem;">
            <table class="table">
              <thead>
                <tr>
                  <th>Ingrediente a comprar</th>
                  <th>Cantidad a pedir</th>
                  <th>Precio Referencial</th>
                  <th style="text-align: right;">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let item of lugar.items">
                  <td><strong>{{ item.nombre_ingrediente }}</strong></td>
                  <td>{{ item.cantidad_requerida | number:'1.2-2' }} {{ item.unidad_medida }}</td>
                  <td>Bs {{ item.precio_referencia | number:'1.2-2' }} / {{ item.unidad_medida }}</td>
                  <td style="text-align: right;"><strong>Bs {{ item.subtotal | number:'1.2-2' }}</strong></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .lugares-container {
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
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .header-metric {
      text-align: right;
      background-color: #f8fafc;
      padding: 0.75rem 1.25rem;
      border-radius: var(--radius);
      border: 1px solid var(--border);
    }
    .metric-title {
      display: block;
      font-size: 0.7rem;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
    }
    .metric-value {
      display: block;
      font-size: 1.5rem;
      font-weight: 700;
      color: #059669;
    }
    .metric-sub {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .lugar-card {
      margin-bottom: 1.5rem;
      border-left: 4px solid var(--secondary);
    }
    .lugar-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.75rem;
    }
    .lugar-title-group {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .lugar-icono {
      font-size: 1.75rem;
    }
    .lugar-nombre {
      margin: 0;
      font-size: 1.2rem;
    }
    .lugar-tipo {
      font-size: 0.65rem;
    }
    .lugar-subtotal {
      text-align: right;
    }
    .subtotal-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-right: 0.5rem;
    }
    .subtotal-val {
      font-size: 1.25rem;
      color: #059669;
    }
    .lugar-info {
      font-size: 0.825rem;
      color: var(--text-muted);
      margin-top: 0.5rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
  `]
})
export class LugaresCompraComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private lugarCompraService = inject(LugarCompraService);

  idRecomendacion!: number;
  resumenCompras = signal<LugaresCompraRecomendacion | null>(null);
  cargando = signal<boolean>(true);
  mensajeError = signal<string | null>(null);

  ngOnInit(): void {
    this.idRecomendacion = Number(this.route.snapshot.paramMap.get('id'));
    if (this.idRecomendacion) {
      this.cargarLugares();
    }
  }

  cargarLugares(): void {
    this.cargando.set(true);
    this.lugarCompraService.obtenerLugaresCompraRecomendacion(this.idRecomendacion).subscribe({
      next: (res) => {
        this.resumenCompras.set(res);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('Error al cargar lugares de compra:', err);
        if (err.status === 403) {
          this.mensajeError.set('No tienes permiso para acceder a esta recomendación.');
        } else {
          this.mensajeError.set('No se pudieron consultar los lugares de compra para esta preparación.');
        }
        this.cargando.set(false);
      }
    });
  }
}
