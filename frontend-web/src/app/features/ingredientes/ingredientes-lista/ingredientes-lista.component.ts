import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { IngredienteService } from '../../../core/services/ingrediente.service';
import { AuthService } from '../../../core/services/auth.service';
import { Ingrediente, CrearIngredienteRequest, ActualizarIngredienteRequest } from '../../../core/models/ingrediente.model';

@Component({
  selector: 'app-ingredientes-lista',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  template: `
    <div class="card">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;">Catálogo General de Ingredientes</h2>
          <p style="margin: 0.25rem 0 0 0; color: var(--text-muted); font-size: 0.875rem;">
            Ingredientes e insumos disponibles para la composición de platos en la plataforma.
          </p>
        </div>
        <button *ngIf="puedeCrear()" class="btn btn-primary" (click)="abrirModalCrear()">
          + Nuevo Ingrediente
        </button>
      </div>

      <div class="card-body">
        <div *ngIf="errorMessage()" class="alert alert-danger">
          {{ errorMessage() }}
        </div>
        <div *ngIf="successMessage()" class="alert alert-success">
          {{ successMessage() }}
        </div>

        <!-- Barra de filtros -->
        <div style="display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
          <input
            type="text"
            class="form-control"
            style="max-width: 320px;"
            placeholder="Buscar por nombre o unidad..."
            [(ngModel)]="filtroTexto"
            (ngModelChange)="filtrarIngredientes()"
          />

          <select class="form-control" style="max-width: 200px;" [(ngModel)]="filtroEstado" (ngModelChange)="filtrarIngredientes()">
            <option value="">Todos los estados</option>
            <option value="ACTIVO">Solo Activos</option>
            <option value="INACTIVO">Solo Inactivos</option>
          </select>
        </div>

        <div *ngIf="loading()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando ingredientes...</p>
        </div>

        <div *ngIf="!loading()" class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th style="width: 70px;">ID</th>
                <th>Ingrediente</th>
                <th>Unidad de Medida</th>
                <th>Precio Estimado</th>
                <th>Descripción</th>
                <th style="width: 100px;">Estado</th>
                <th *ngIf="esAdmin()" style="width: 120px; text-align: right;">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let ing of ingredientesFiltrados()">
                <td><strong>#{{ ing.id_ingrediente }}</strong></td>
                <td><span style="font-weight: 600;">{{ ing.nombre }}</span></td>
                <td><span class="badge" style="background-color: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-color);">{{ ing.unidad_medida }}</span></td>
                <td>{{ ing.precio_estimado ? ('Bs ' + ing.precio_estimado) : 'N/D' }}</td>
                <td>{{ ing.descripcion || 'Sin descripción' }}</td>
                <td>
                  <span class="badge" [ngClass]="ing.estado === 'ACTIVO' ? 'badge-success' : 'badge-danger'">
                    {{ ing.estado }}
                  </span>
                </td>
                <td *ngIf="esAdmin()" style="text-align: right;">
                  <button class="btn btn-sm btn-outline" (click)="abrirModalEditar(ing)">
                    Editar
                  </button>
                </td>
              </tr>
              <tr *ngIf="ingredientesFiltrados().length === 0">
                <td [attr.colspan]="esAdmin() ? 7 : 6" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                  No se encontraron ingredientes con los filtros especificados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal Formulario Ingrediente -->
    <div *ngIf="mostrarModal()" class="modal-overlay">
      <div class="modal-container" style="max-width: 500px;">
        <div class="modal-header">
          <h3 style="margin: 0; font-size: 1.15rem;">
            {{ ingredienteEditando() ? 'Editar Ingrediente' : 'Nuevo Ingrediente' }}
          </h3>
          <button class="btn-close" (click)="cerrarModal()">&times;</button>
        </div>

        <form [formGroup]="form" (ngSubmit)="guardarIngrediente()">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="nombreIng">Nombre del Ingrediente *</label>
              <input
                id="nombreIng"
                type="text"
                class="form-control"
                formControlName="nombre"
                placeholder="Ej. Carne de res, Arroz, Tomate..."
              />
              <div *ngIf="form.get('nombre')?.touched && form.get('nombre')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                El nombre es obligatorio (mínimo 2 caracteres).
              </div>
            </div>

            <div class="form-row">
              <div class="form-group" style="flex: 1;">
                <label class="form-label" for="unidadIng">Unidad de Medida *</label>
                <input
                  id="unidadIng"
                  type="text"
                  class="form-control"
                  formControlName="unidad_medida"
                  placeholder="gramos, kg, ml, unidad..."
                />
                <div *ngIf="form.get('unidad_medida')?.touched && form.get('unidad_medida')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  La unidad de medida es requerida.
                </div>
              </div>

              <div class="form-group" style="flex: 1;">
                <label class="form-label" for="precioIng">Precio Estimado (Bs)</label>
                <input
                  id="precioIng"
                  type="number"
                  step="0.01"
                  min="0"
                  class="form-control"
                  formControlName="precio_estimado"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="descIng">Descripción</label>
              <textarea
                id="descIng"
                class="form-control"
                rows="2"
                formControlName="descripcion"
                placeholder="Detalle opcional..."
              ></textarea>
            </div>

            <div *ngIf="esAdmin() && ingredienteEditando()" class="form-group">
              <label class="form-label" for="estadoIng">Estado</label>
              <select id="estadoIng" class="form-control" formControlName="estado">
                <option value="ACTIVO">ACTIVO</option>
                <option value="INACTIVO">INACTIVO</option>
              </select>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" (click)="cerrarModal()">Cancelar</button>
            <button type="submit" class="btn btn-primary" [disabled]="form.invalid || guardando()">
              <span *ngIf="guardando()" class="spinner" style="width: 14px; height: 14px; margin-right: 0.5rem;"></span>
              {{ ingredienteEditando() ? 'Actualizar' : 'Guardar Ingrediente' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .form-row {
      display: flex;
      gap: 1rem;
    }
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: rgba(0, 0, 0, 0.5);
      display: flex; align-items: center; justify-content: center;
      z-index: 1000; padding: 1rem;
    }
    .modal-container {
      background: var(--surface-color);
      border-radius: 8px; width: 100%;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .modal-header {
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border-color);
      display: flex; justify-content: space-between; align-items: center;
    }
    .modal-body { padding: 1.25rem; }
    .modal-footer {
      padding: 1rem 1.25rem;
      border-top: 1px solid var(--border-color);
      display: flex; justify-content: flex-end; gap: 0.5rem;
    }
    .btn-close {
      background: none; border: none; font-size: 1.5rem;
      cursor: pointer; color: var(--text-muted);
    }
  `]
})
export class IngredientesListaComponent implements OnInit {
  private ingredienteService = inject(IngredienteService);
  private authService = inject(AuthService);
  private fb = inject(FormBuilder);

  todosIngredientes = signal<Ingrediente[]>([]);
  ingredientesFiltrados = signal<Ingrediente[]>([]);
  loading = signal<boolean>(false);
  guardando = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  mostrarModal = signal<boolean>(false);
  ingredienteEditando = signal<Ingrediente | null>(null);
  filtroTexto = '';
  filtroEstado = '';

  form: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(100)]],
    unidad_medida: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(50)]],
    precio_estimado: [null],
    descripcion: [''],
    estado: ['ACTIVO']
  });

  esAdmin(): boolean {
    return this.authService.userRole() === 'ADMINISTRADOR';
  }

  puedeCrear(): boolean {
    const rol = this.authService.userRole();
    return rol === 'ADMINISTRADOR' || rol === 'RESTAURANTE';
  }

  ngOnInit(): void {
    this.cargarIngredientes();
  }

  // =========================================================================
  // CASO DE USO: CU09 - GESTIONAR INGREDIENTES (LISTAR INGREDIENTES)
  // =========================================================================
  cargarIngredientes(): void {
    this.loading.set(true);
    this.ingredienteService.getIngredientes().subscribe({
      next: (res) => {
        this.loading.set(false);
        this.todosIngredientes.set(res);
        this.filtrarIngredientes();
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al cargar ingredientes.');
      }
    });
  }

  filtrarIngredientes(): void {
    const texto = this.filtroTexto.toLowerCase().trim();
    const estado = this.filtroEstado;

    let res = this.todosIngredientes();

    if (texto) {
      res = res.filter(i =>
        i.nombre.toLowerCase().includes(texto) ||
        i.unidad_medida.toLowerCase().includes(texto) ||
        (i.descripcion && i.descripcion.toLowerCase().includes(texto))
      );
    }

    if (estado) {
      res = res.filter(i => i.estado === estado);
    }

    this.ingredientesFiltrados.set(res);
  }

  abrirModalCrear(): void {
    this.ingredienteEditando.set(null);
    this.form.reset({
      nombre: '',
      unidad_medida: '',
      precio_estimado: null,
      descripcion: '',
      estado: 'ACTIVO'
    });
    this.errorMessage.set(null);
    this.mostrarModal.set(true);
  }

  abrirModalEditar(ing: Ingrediente): void {
    this.ingredienteEditando.set(ing);
    this.form.patchValue({
      nombre: ing.nombre,
      unidad_medida: ing.unidad_medida,
      precio_estimado: ing.precio_estimado || null,
      descripcion: ing.descripcion || '',
      estado: ing.estado
    });
    this.errorMessage.set(null);
    this.mostrarModal.set(true);
  }

  cerrarModal(): void {
    this.mostrarModal.set(false);
    this.ingredienteEditando.set(null);
  }

  // =========================================================================
  // CASO DE USO: CU09 - GESTIONAR INGREDIENTES (CREAR O MODIFICAR INGREDIENTE)
  // =========================================================================
  guardarIngrediente(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.guardando.set(true);
    const val = this.form.value;

    if (this.ingredienteEditando()) {
      // Modificar ingrediente (solo Admin)
      const updateData: ActualizarIngredienteRequest = {
        nombre: val.nombre,
        unidad_medida: val.unidad_medida,
        precio_estimado: val.precio_estimado !== null && val.precio_estimado !== '' ? Number(val.precio_estimado) : undefined,
        descripcion: val.descripcion || undefined,
        estado: val.estado || undefined
      };

      this.ingredienteService.updateIngrediente(this.ingredienteEditando()!.id_ingrediente, updateData).subscribe({
        next: () => {
          this.guardando.set(false);
          this.cerrarModal();
          this.successMessage.set('Ingrediente actualizado exitosamente.');
          this.cargarIngredientes();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.guardando.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al actualizar ingrediente.');
        }
      });
    } else {
      // Crear nuevo ingrediente
      const createData: CrearIngredienteRequest = {
        nombre: val.nombre,
        unidad_medida: val.unidad_medida,
        precio_estimado: val.precio_estimado !== null && val.precio_estimado !== '' ? Number(val.precio_estimado) : undefined,
        descripcion: val.descripcion || undefined,
        estado: val.estado || 'ACTIVO'
      };

      this.ingredienteService.crearIngrediente(createData).subscribe({
        next: () => {
          this.guardando.set(false);
          this.cerrarModal();
          this.successMessage.set('Ingrediente agregado al catálogo exitosamente.');
          this.cargarIngredientes();
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.guardando.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al registrar ingrediente.');
        }
      });
    }
  }
}
