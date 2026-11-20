import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { PlatoService } from '../../../core/services/plato.service';
import { RestauranteService } from '../../../core/services/restaurante.service';
import { CategoriaService } from '../../../core/services/categoria.service';
import { AuthService } from '../../../core/services/auth.service';
import { Plato } from '../../../core/models/plato.model';
import { Restaurante } from '../../../core/models/restaurante.model';
import { Categoria } from '../../../core/models/categoria.model';

@Component({
  selector: 'app-platos-lista',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <a [routerLink]="['/restaurantes', restauranteId()]" class="btn btn-sm btn-outline" style="padding: 0.2rem 0.5rem;">&larr; Volver</a>
            <h2 style="margin: 0; font-size: 1.35rem;">
              Carta de Platos - {{ restaurante()?.nombre || 'Restaurante #' + restauranteId() }}
            </h2>
          </div>
          <p style="margin: 0.25rem 0 0 0; color: var(--text-muted); font-size: 0.875rem;">
            Gestione los platos ofrecidos, precios, porciones, estado y disponibilidad inmediata.
          </p>
        </div>

        <a [routerLink]="['/restaurantes', restauranteId(), 'platos', 'nuevo']" class="btn btn-primary">
          + Nuevo Plato
        </a>
      </div>

      <div class="card-body">
        <div *ngIf="errorMessage()" class="alert alert-danger">
          {{ errorMessage() }}
        </div>
        <div *ngIf="successMessage()" class="alert alert-success">
          {{ successMessage() }}
        </div>

        <!-- Filtros -->
        <div style="display: flex; gap: 0.75rem; margin-bottom: 1.25rem; flex-wrap: wrap;">
          <input
            type="text"
            class="form-control"
            style="max-width: 250px;"
            placeholder="Buscar por nombre..."
            [(ngModel)]="filtroTexto"
            (ngModelChange)="aplicarFiltrosLocales()"
          />

          <select class="form-control" style="max-width: 200px;" [(ngModel)]="filtroCategoria" (ngModelChange)="cargarPlatos()">
            <option [ngValue]="null">Todas las categorías</option>
            <option *ngFor="let cat of categorias()" [ngValue]="cat.id_categoria">
              {{ cat.nombre }}
            </option>
          </select>

          <select class="form-control" style="max-width: 180px;" [(ngModel)]="filtroTipoComida" (ngModelChange)="cargarPlatos()">
            <option value="">Cualquier tipo</option>
            <option value="Desayuno">Desayuno</option>
            <option value="Almuerzo">Almuerzo</option>
            <option value="Cena">Cena</option>
            <option value="Snack">Snack</option>
            <option value="Postre">Postre</option>
            <option value="Bebida">Bebida</option>
          </select>

          <select class="form-control" style="max-width: 170px;" [(ngModel)]="filtroDisponibilidad" (ngModelChange)="cargarPlatos()">
            <option [ngValue]="null">Disponibilidad</option>
            <option [ngValue]="true">Solo Disponibles</option>
            <option [ngValue]="false">No Disponibles</option>
          </select>
        </div>

        <div *ngIf="loading()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando platos...</p>
        </div>

        <div *ngIf="!loading()" class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th style="width: 60px;">ID</th>
                <th>Imagen</th>
                <th>Nombre del Plato</th>
                <th>Categoría</th>
                <th>Tipo</th>
                <th>Precio</th>
                <th style="text-align: center;">Porciones</th>
                <th style="text-align: center; width: 140px;">Disponibilidad (CU10)</th>
                <th style="text-align: center; width: 100px;">Estado</th>
                <th style="width: 220px; text-align: right;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let plato of platosFiltrados()">
                <td><strong>#{{ plato.id_plato }}</strong></td>
                <td><img *ngIf="plato.imagen_url" [src]="plato.imagen_url" [alt]="plato.nombre" style="width:64px;height:48px;object-fit:cover;border-radius:0.35rem" /></td>
                <td>
                  <div style="font-weight: 600;">{{ plato.nombre }}</div>
                  <small style="color: var(--text-muted);">{{ plato.descripcion || 'Sin descripción' }}</small>
                </td>
                <td>
                  <span class="badge" style="background-color: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-color);">
                    {{ plato.categoria?.nombre || 'Cat. #' + plato.id_categoria }}
                  </span>
                </td>
                <td>{{ plato.tipo_comida || 'N/A' }}</td>
                <td><strong style="color: var(--primary-color);">Bs {{ plato.precio }}</strong></td>
                <td style="text-align: center;">{{ plato.personas_cubiertas }} pers.</td>
                <td style="text-align: center;">
                  <!-- CASO DE USO: CU10 - GESTIONAR DISPONIBILIDAD -->
                  <button
                    class="btn btn-sm"
                    [ngClass]="plato.disponible ? 'btn-success' : 'btn-danger'"
                    style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 20px;"
                    (click)="toggleDisponibilidad(plato)"
                    title="Haga clic para alternar disponibilidad inmediata"
                  >
                    {{ plato.disponible ? 'Disponible' : 'Agotado' }}
                  </button>
                </td>
                <td style="text-align: center;">
                  <span class="badge" [ngClass]="plato.estado === 'ACTIVO' ? 'badge-success' : 'badge-danger'">
                    {{ plato.estado }}
                  </span>
                </td>
                <td style="text-align: right;">
                  <div style="display: flex; justify-content: flex-end; gap: 0.4rem;">
                    <a [routerLink]="['/platos', plato.id_plato, 'editar']" class="btn btn-sm btn-outline" title="Editar plato">
                      Editar
                    </a>
                    <!-- CASO DE USO: CU08 - CAMBIAR ESTADO -->
                    <button
                      class="btn btn-sm"
                      [ngClass]="plato.estado === 'ACTIVO' ? 'btn-danger' : 'btn-success'"
                      (click)="toggleEstado(plato)"
                      [title]="plato.estado === 'ACTIVO' ? 'Desactivar plato' : 'Activar plato'"
                    >
                      {{ plato.estado === 'ACTIVO' ? 'Inactivar' : 'Activar' }}
                    </button>
                  </div>
                </td>
              </tr>
              <tr *ngIf="platosFiltrados().length === 0">
                <td colspan="10" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                  No hay platos registrados con los criterios seleccionados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `
})
export class PlatosListaComponent implements OnInit {
  private platoService = inject(PlatoService);
  private restauranteService = inject(RestauranteService);
  private categoriaService = inject(CategoriaService);
  private authService = inject(AuthService);
  private route = inject(ActivatedRoute);

  restauranteId = signal<number>(0);
  restaurante = signal<Restaurante | null>(null);
  categorias = signal<Categoria[]>([]);
  todosPlatos = signal<Plato[]>([]);
  platosFiltrados = signal<Plato[]>([]);

  loading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  filtroTexto = '';
  filtroCategoria: number | null = null;
  filtroTipoComida = '';
  filtroDisponibilidad: boolean | null = null;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.restauranteId.set(+id);
      this.cargarRestaurante(+id);
      this.cargarCategorias();
      this.cargarPlatos();
    }
  }

  // =========================================================================
  // CASO DE USO: CU06 - GESTIONAR RESTAURANTE (INFO CABECERA)
  // =========================================================================
  cargarRestaurante(id: number): void {
    this.restauranteService.getRestaurante(id).subscribe({
      next: (resto) => this.restaurante.set(resto),
      error: () => {}
    });
  }

  // =========================================================================
  // CASO DE USO: CU07 - GESTIONAR CATEGORÍAS (CATÁLOGO PARA FILTRO)
  // =========================================================================
  cargarCategorias(): void {
    this.categoriaService.getCategorias().subscribe({
      next: (cats) => this.categorias.set(cats),
      error: () => {}
    });
  }

  // =========================================================================
  // CASO DE USO: CU08 - GESTIONAR PLATOS (LISTAR PLATOS DE RESTAURANTE)
  // =========================================================================
  cargarPlatos(): void {
    this.loading.set(true);
    this.errorMessage.set(null);

    this.platoService.getPlatosPorRestaurante(
      this.restauranteId(),
      this.filtroCategoria || undefined,
      this.filtroTipoComida || undefined,
      this.filtroDisponibilidad !== null ? this.filtroDisponibilidad : undefined
    ).subscribe({
      next: (platos) => {
        this.loading.set(false);
        this.todosPlatos.set(platos);
        this.aplicarFiltrosLocales();
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al cargar los platos del restaurante.');
      }
    });
  }

  aplicarFiltrosLocales(): void {
    const texto = this.filtroTexto.toLowerCase().trim();
    if (!texto) {
      this.platosFiltrados.set(this.todosPlatos());
    } else {
      this.platosFiltrados.set(
        this.todosPlatos().filter(p =>
          p.nombre.toLowerCase().includes(texto) ||
          (p.descripcion && p.descripcion.toLowerCase().includes(texto))
        )
      );
    }
  }

  // =========================================================================
  // CASO DE USO: CU10 - GESTIONAR DISPONIBILIDAD
  // =========================================================================
  toggleDisponibilidad(plato: Plato): void {
    const nuevoValor = !plato.disponible;
    this.platoService.cambiarDisponibilidad(plato.id_plato, nuevoValor).subscribe({
      next: (actualizado) => {
        plato.disponible = actualizado.disponible;
        this.successMessage.set(`Plato "${plato.nombre}" marcado como ${nuevoValor ? 'Disponible' : 'Agotado'}.`);
        setTimeout(() => this.successMessage.set(null), 3000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cambiar disponibilidad del plato.');
      }
    });
  }

  // =========================================================================
  // CASO DE USO: CU08 - GESTIONAR PLATOS (CAMBIAR ESTADO ACTIVO/INACTIVO)
  // =========================================================================
  toggleEstado(plato: Plato): void {
    const nuevoEstado = plato.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    this.platoService.cambiarEstado(plato.id_plato, nuevoEstado).subscribe({
      next: (actualizado) => {
        plato.estado = actualizado.estado;
        this.successMessage.set(`Plato "${plato.nombre}" cambiado a estado ${nuevoEstado}.`);
        setTimeout(() => this.successMessage.set(null), 3000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cambiar estado del plato.');
      }
    });
  }
}
