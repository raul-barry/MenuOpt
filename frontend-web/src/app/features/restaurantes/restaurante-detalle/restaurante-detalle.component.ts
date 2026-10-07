import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { RestauranteService } from '../../../core/services/restaurante.service';
import { Restaurante } from '../../../core/models/restaurante.model';

@Component({
  selector: 'app-restaurante-detalle',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <h2 style="margin: 0; font-size: 1.35rem;">Detalle del Restaurante</h2>
        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
          <a *ngIf="restaurante()" [routerLink]="['/restaurantes', restaurante()!.id_restaurante, 'platos']" class="btn btn-primary">
            Ver Carta de Platos
          </a>
          <a *ngIf="restaurante()" [routerLink]="['/restaurantes', restaurante()!.id_restaurante, 'distribucion']" class="btn btn-secondary">
            Plano 2D y Mesas
          </a>
          <a routerLink="/restaurantes" class="btn btn-outline">Volver</a>
        </div>
      </div>

      <div class="card-body">
        <div *ngIf="loading()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando información del restaurante...</p>
        </div>

        <div *ngIf="errorMessage()" class="alert alert-danger">
          {{ errorMessage() }}
        </div>

        <div *ngIf="!loading() && restaurante() as r">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
            <div>
              <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; color: var(--primary-color);">{{ r.nombre }}</h3>
              <p style="margin: 0; color: var(--text-muted);">{{ r.descripcion || 'Sin descripción registrada' }}</p>
            </div>
            <span class="badge" [ngClass]="r.estado === 'ACTIVO' ? 'badge-success' : 'badge-danger'" style="font-size: 0.85rem; padding: 0.35rem 0.75rem;">
              {{ r.estado }}
            </span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem; margin-bottom: 2rem;">
            <div style="background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem;">
              <h4 style="margin: 0 0 0.75rem 0; font-size: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">Contacto</h4>
              <p style="margin: 0 0 0.4rem 0;"><strong>NIT:</strong> {{ r.nit || 'No especificado' }}</p>
              <p style="margin: 0 0 0.4rem 0;"><strong>Teléfono:</strong> {{ r.telefono || 'No especificado' }}</p>
              <p style="margin: 0;"><strong>Correo:</strong> {{ r.correo || 'No especificado' }}</p>
            </div>

            <div style="background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem;">
              <h4 style="margin: 0 0 0.75rem 0; font-size: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">Horario de Atención</h4>
              <p style="margin: 0 0 0.4rem 0;"><strong>Apertura:</strong> {{ r.horario_apertura ? r.horario_apertura.substring(0, 5) : 'No configurado' }}</p>
              <p style="margin: 0;"><strong>Cierre:</strong> {{ r.horario_cierre ? r.horario_cierre.substring(0, 5) : 'No configurado' }}</p>
            </div>

            <div style="background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; grid-column: 1 / -1;">
              <h4 style="margin: 0 0 0.75rem 0; font-size: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">Ubicación</h4>
              <p style="margin: 0 0 0.4rem 0;"><strong>Dirección:</strong> {{ r.ubicacion?.direccion }}</p>
              <p style="margin: 0 0 0.4rem 0;"><strong>Zona / Barrio:</strong> {{ r.ubicacion?.zona || 'No especificada' }}</p>
              <p style="margin: 0 0 0.4rem 0;"><strong>Ciudad:</strong> {{ r.ubicacion?.ciudad }}</p>
              <p *ngIf="r.ubicacion?.referencia" style="margin: 0 0 0.4rem 0;"><strong>Referencia:</strong> {{ r.ubicacion?.referencia }}</p>
              <p *ngIf="r.ubicacion?.latitud && r.ubicacion?.longitud" style="margin: 0; color: var(--text-muted); font-size: 0.85rem;">
                Coordenadas: Lat {{ r.ubicacion?.latitud }}, Long {{ r.ubicacion?.longitud }}
              </p>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
            <a [routerLink]="['/restaurantes', r.id_restaurante, 'editar']" class="btn btn-warning">Editar Datos</a>
            <a [routerLink]="['/restaurantes', r.id_restaurante, 'platos']" class="btn btn-primary">Gestionar Menú</a>
          </div>
        </div>
      </div>
    </div>
  `
})
export class RestauranteDetalleComponent implements OnInit {
  private restauranteService = inject(RestauranteService);
  private route = inject(ActivatedRoute);

  restaurante = signal<Restaurante | null>(null);
  loading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.cargarDetalle(+id);
    }
  }

  // =========================================================================
  // CASO DE USO: CU06 - GESTIONAR RESTAURANTE (CONSULTAR DETALLE)
  // =========================================================================
  cargarDetalle(id: number): void {
    this.loading.set(true);
    this.restauranteService.getRestaurante(id).subscribe({
      next: (res) => {
        this.loading.set(false);
        this.restaurante.set(res);
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al cargar los datos del restaurante.');
      }
    });
  }
}
