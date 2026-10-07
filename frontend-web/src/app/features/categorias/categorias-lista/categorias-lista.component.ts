import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { CategoriaService } from '../../../core/services/categoria.service';
import { Categoria, CrearCategoriaRequest, ActualizarCategoriaRequest } from '../../../core/models/categoria.model';

@Component({
  selector: 'app-categorias-lista',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;">Gestión de Categorías</h2>
          <p style="margin: 0.25rem 0 0 0; color: var(--text-muted); font-size: 0.875rem;">
            Administración del catálogo global de categorías gastronómicas para clasificación de platos.
          </p>
        </div>
        <button class="btn btn-primary" (click)="abrirModalCrear()">
          + Nueva Categoría
        </button>
      </div>

      <div class="card-body">
        <div *ngIf="errorMessage()" class="alert alert-danger">
          {{ errorMessage() }}
        </div>
        <div *ngIf="successMessage()" class="alert alert-success">
          {{ successMessage() }}
        </div>

        <!-- Buscador -->
        <div style="margin-bottom: 1rem; max-width: 350px;">
          <input
            type="text"
            class="form-control"
            placeholder="Buscar por nombre..."
            [(ngModel)]="filtroTexto"
            (ngModelChange)="filtrarCategorias()"
          />
        </div>

        <div *ngIf="loading()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando categorías...</p>
        </div>

        <div *ngIf="!loading()" class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th style="width: 70px;">ID</th>
                <th>Nombre</th>
                <th>Descripción</th>
                <th style="width: 110px;">Estado</th>
                <th style="width: 180px; text-align: right;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let cat of categoriasFiltradas()">
                <td><strong>#{{ cat.id_categoria }}</strong></td>
                <td><span style="font-weight: 600;">{{ cat.nombre }}</span></td>
                <td>{{ cat.descripcion || 'Sin descripción' }}</td>
                <td>
                  <span class="badge" [ngClass]="cat.activo ? 'badge-success' : 'badge-danger'">
                    {{ cat.activo ? 'Activa' : 'Inactiva' }}
                  </span>
                </td>
                <td style="text-align: right;">
                  <button class="btn btn-sm btn-outline" style="margin-right: 0.5rem;" (click)="abrirModalEditar(cat)">
                    Editar
                  </button>
                  <button
                    class="btn btn-sm"
                    [ngClass]="cat.activo ? 'btn-danger' : 'btn-success'"
                    (click)="toggleEstado(cat)"
                  >
                    {{ cat.activo ? 'Desactivar' : 'Activar' }}
                  </button>
                </td>
              </tr>
              <tr *ngIf="categoriasFiltradas().length === 0">
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                  No se encontraron categorías registradas.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal Formulario Categoría -->
    <div *ngIf="mostrarModal()" class="modal-overlay">
      <div class="modal-container" style="max-width: 500px;">
        <div class="modal-header">
          <h3 style="margin: 0; font-size: 1.15rem;">
            {{ categoriaEditando() ? 'Editar Categoría' : 'Nueva Categoría' }}
          </h3>
          <button class="btn-close" (click)="cerrarModal()">&times;</button>
        </div>

        <form [formGroup]="form" (ngSubmit)="guardarCategoria()">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="nombreCat">Nombre de Categoría *</label>
              <input
                id="nombreCat"
                type="text"
                class="form-control"
                formControlName="nombre"
                placeholder="Ej. Platos Fuertes, Postres, Bebidas..."
              />
              <div *ngIf="form.get('nombre')?.touched && form.get('nombre')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                El nombre es obligatorio (mínimo 2 caracteres).
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="descCat">Descripción</label>
              <textarea
                id="descCat"
                class="form-control"
                rows="3"
                formControlName="descripcion"
                placeholder="Breve descripción de los platos pertenecientes..."
              ></textarea>
            </div>

            <div class="form-group" style="display: flex; align-items: center; gap: 0.5rem;">
              <input
                type="checkbox"
                id="activoCat"
                formControlName="activo"
                style="width: 18px; height: 18px; accent-color: var(--primary-color);"
              />
              <label for="activoCat" style="margin: 0; cursor: pointer; font-weight: 500;">
                Categoría activa para selección
              </label>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" (click)="cerrarModal()">Cancelar</button>
            <button type="submit" class="btn btn-primary" [disabled]="form.invalid || guardando()">
              <span *ngIf="guardando()" class="spinner" style="width: 14px; height: 14px; margin-right: 0.5rem;"></span>
              {{ categoriaEditando() ? 'Actualizar' : 'Crear Categoría' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 1rem;
    }
    .modal-container {
      background: var(--surface-color);
      border-radius: 8px;
      width: 100%;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .modal-header {
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-body {
      padding: 1.25rem;
    }
    .modal-footer {
      padding: 1rem 1.25rem;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: flex-end;
      gap: 0.5rem;
    }
    .btn-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: var(--text-muted);
    }
  `]
})
export class CategoriasListaComponent implements OnInit {
  private categoriaService = inject(CategoriaService);
  private fb = inject(FormBuilder);

  todasCategorias = signal<Categoria[]>([]);
  categoriasFiltradas = signal<Categoria[]>([]);
  loading = signal<boolean>(false);
  guardando = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  mostrarModal = signal<boolean>(false);
  categoriaEditando = signal<Categoria | null>(null);
  filtroTexto = '';

  form: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(100)]],
    descripcion: [''],
    activo: [true]
  });

  ngOnInit(): void {
    this.cargarCategorias();
  }

  // =========================================================================
  // CASO DE USO: CU07 - GESTIONAR CATEGORÍAS (LISTAR CATEGORÍAS)
  // =========================================================================
  cargarCategorias(): void {
    this.loading.set(true);
    this.categoriaService.getCategorias().subscribe({
      next: (res) => {
        this.loading.set(false);
        this.todasCategorias.set(res);
        this.filtrarCategorias();
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al cargar las categorías.');
      }
    });
  }

  filtrarCategorias(): void {
    const texto = this.filtroTexto.toLowerCase().trim();
    if (!texto) {
      this.categoriasFiltradas.set(this.todasCategorias());
    } else {
      this.categoriasFiltradas.set(
        this.todasCategorias().filter(c =>
          c.nombre.toLowerCase().includes(texto) ||
          (c.descripcion && c.descripcion.toLowerCase().includes(texto))
        )
      );
    }
  }

  abrirModalCrear(): void {
    this.categoriaEditando.set(null);
    this.form.reset({ nombre: '', descripcion: '', activo: true });
    this.errorMessage.set(null);
    this.mostrarModal.set(true);
  }

  abrirModalEditar(cat: Categoria): void {
    this.categoriaEditando.set(cat);
    this.form.patchValue({
      nombre: cat.nombre,
      descripcion: cat.descripcion || '',
      activo: cat.activo
    });
    this.errorMessage.set(null);
    this.mostrarModal.set(true);
  }

  cerrarModal(): void {
    this.mostrarModal.set(false);
    this.categoriaEditando.set(null);
  }

  // =========================================================================
  // CASO DE USO: CU07 - GESTIONAR CATEGORÍAS (CREAR O ACTUALIZAR CATEGORÍA)
  // =========================================================================
  guardarCategoria(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.guardando.set(true);
    const val = this.form.value;

    if (this.categoriaEditando()) {
      // Actualizar categoría
      const updateData: ActualizarCategoriaRequest = {
        nombre: val.nombre,
        descripcion: val.descripcion || undefined,
        activo: val.activo
      };

      this.categoriaService.updateCategoria(this.categoriaEditando()!.id_categoria, updateData).subscribe({
        next: () => {
          this.guardando.set(false);
          this.cerrarModal();
          this.successMessage.set('Categoría actualizada exitosamente.');
          this.cargarCategorias();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.guardando.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al actualizar categoría.');
        }
      });
    } else {
      // Crear nueva categoría
      const createData: CrearCategoriaRequest = {
        nombre: val.nombre,
        descripcion: val.descripcion || undefined,
        activo: val.activo
      };

      this.categoriaService.crearCategoria(createData).subscribe({
        next: () => {
          this.guardando.set(false);
          this.cerrarModal();
          this.successMessage.set('Categoría creada exitosamente.');
          this.cargarCategorias();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.guardando.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al crear categoría.');
        }
      });
    }
  }

  // =========================================================================
  // CASO DE USO: CU07 - GESTIONAR CATEGORÍAS (CAMBIAR ESTADO ACTIVO/INACTIVO)
  // =========================================================================
  toggleEstado(cat: Categoria): void {
    const nuevoEstado = !cat.activo;
    this.categoriaService.updateCategoria(cat.id_categoria, { activo: nuevoEstado }).subscribe({
      next: () => {
        this.successMessage.set(`Categoría "${cat.nombre}" ${nuevoEstado ? 'activada' : 'desactivada'} correctamente.`);
        this.cargarCategorias();
        setTimeout(() => this.successMessage.set(null), 3000);
      },
      error: (err) => {
        this.errorMessage.set(err.error?.detail || 'Error al cambiar estado de la categoría.');
      }
    });
  }
}
