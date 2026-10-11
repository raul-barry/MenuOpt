import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { PlatoService } from '../../../core/services/plato.service';
import { CategoriaService } from '../../../core/services/categoria.service';
import { Categoria } from '../../../core/models/categoria.model';
import { Plato, CrearPlatoRequest, ActualizarPlatoRequest } from '../../../core/models/plato.model';

@Component({
  selector: 'app-plato-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule, RouterModule],
  template: `
    <div style="max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 1.5rem;">
      <!-- Tarjeta Formulario de Plato (CU08) -->
      <div class="card">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <h2 style="margin: 0; font-size: 1.35rem;">
              {{ isEditMode() ? 'Editar Plato #' + platoId() : 'Registrar Nuevo Plato' }}
            </h2>
            <p style="margin: 0.25rem 0 0 0; color: var(--text-muted); font-size: 0.875rem;">
              {{ isEditMode() ? 'Modifique la información comercial y características del plato.' : 'Ingrese los datos del nuevo plato para la carta de su establecimiento.' }}
            </p>
          </div>
          <button type="button" class="btn btn-secondary" (click)="volver()">Volver</button>
        </div>

        <div class="card-body">
          <div *ngIf="errorMessage()" class="alert alert-danger">
            {{ errorMessage() }}
          </div>
          <div *ngIf="successMessage()" class="alert alert-success">
            {{ successMessage() }}
          </div>

          <form [formGroup]="formPlato" (ngSubmit)="onSubmitPlato()">
            <div class="form-row">
              <div class="form-group col-8">
                <label class="form-label" for="nombre">Nombre del Plato *</label>
                <input
                  id="nombre"
                  type="text"
                  class="form-control"
                  formControlName="nombre"
                  placeholder="Ej. Silpancho Cochabambino, Pique Macho, etc."
                />
                <div *ngIf="formPlato.get('nombre')?.touched && formPlato.get('nombre')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  El nombre es obligatorio (mínimo 2 caracteres).
                </div>
              </div>

              <div class="form-group col-4">
                <label class="form-label" for="precio">Precio (Bs) *</label>
                <input
                  id="precio"
                  type="number"
                  step="0.50"
                  min="0"
                  class="form-control"
                  formControlName="precio"
                  placeholder="0.00"
                />
                <div *ngIf="formPlato.get('precio')?.touched && formPlato.get('precio')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  El precio es obligatorio y debe ser positivo.
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="descripcion">Descripción del Plato</label>
              <textarea
                id="descripcion"
                class="form-control"
                rows="2"
                formControlName="descripcion"
                placeholder="Breve reseña del plato, guarniciones incluidas, etc."
              ></textarea>
            </div>

            <div class="form-row">
              <div class="form-group col-4">
                <label class="form-label" for="categoria">Categoría *</label>
                <select id="categoria" class="form-control" formControlName="id_categoria">
                  <option [ngValue]="null" disabled>Seleccione categoría...</option>
                  <option *ngFor="let cat of categorias()" [ngValue]="cat.id_categoria">
                    {{ cat.nombre }}
                  </option>
                </select>
                <div *ngIf="formPlato.get('id_categoria')?.touched && formPlato.get('id_categoria')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  Seleccione una categoría.
                </div>
              </div>

              <div class="form-group col-4">
                <label class="form-label" for="tipo_comida">Tipo de Comida</label>
                <select id="tipo_comida" class="form-control" formControlName="tipo_comida">
                  <option value="">No especificado</option>
                  <option value="Desayuno">Desayuno</option>
                  <option value="Almuerzo">Almuerzo</option>
                  <option value="Cena">Cena</option>
                  <option value="Snack">Snack</option>
                  <option value="Postre">Postre</option>
                  <option value="Bebida">Bebida</option>
                </select>
              </div>

              <div class="form-group col-4">
                <label class="form-label" for="personas_cubiertas">Porciones / Personas *</label>
                <input
                  id="personas_cubiertas"
                  type="number"
                  min="1"
                  class="form-control"
                  formControlName="personas_cubiertas"
                />
                <div *ngIf="formPlato.get('personas_cubiertas')?.touched && formPlato.get('personas_cubiertas')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  Debe cubrir al menos 1 persona.
                </div>
              </div>
            </div>

            <div class="form-group" style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
              <input
                type="checkbox"
                id="disponible"
                formControlName="disponible"
                style="width: 18px; height: 18px; accent-color: var(--primary-color);"
              />
              <label for="disponible" style="margin: 0; cursor: pointer; font-weight: 500;">
                Plato disponible para pedidos de forma inmediata
              </label>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem;">
              <button type="button" class="btn btn-secondary" (click)="volver()">Cancelar</button>
              <button type="submit" class="btn btn-primary" [disabled]="formPlato.invalid || guardando()">
                <span *ngIf="guardando()" class="spinner" style="width: 14px; height: 14px; margin-right: 0.5rem;"></span>
                {{ isEditMode() ? 'Actualizar Información' : 'Crear Plato' }}
              </button>
            </div>
          </form>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .form-row { display: flex; flex-wrap: wrap; margin: 0 -0.5rem; }
    .col-4 { flex: 0 0 33.333%; padding: 0 0.5rem; }
    .col-8 { flex: 0 0 66.666%; padding: 0 0.5rem; }
    @media (max-width: 768px) {
      .col-4, .col-8 { flex: 0 0 100%; }
    }
  `]
})
export class PlatoFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private platoService = inject(PlatoService);
  private categoriaService = inject(CategoriaService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  isEditMode = signal<boolean>(false);
  platoId = signal<number | null>(null);
  restauranteId = signal<number | null>(null);

  categorias = signal<Categoria[]>([]);

  loading = signal<boolean>(false);
  guardando = signal<boolean>(false);

  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  formPlato: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
    descripcion: [''],
    precio: [null, [Validators.required, Validators.min(0)]],
    tipo_comida: [''],
    personas_cubiertas: [1, [Validators.required, Validators.min(1)]],
    disponible: [true],
    id_categoria: [null, [Validators.required]]
  });

  ngOnInit(): void {
    this.cargarCategorias();

    // Comprobar si estamos creando un plato para un restaurante
    const idRestoParam = this.route.snapshot.paramMap.get('id');
    const urlSegment = this.route.snapshot.url.map(s => s.path).join('/');

    if (urlSegment.includes('platos/nuevo') && idRestoParam) {
      this.isEditMode.set(false);
      this.restauranteId.set(+idRestoParam);
    } else if (idRestoParam && !urlSegment.includes('platos/nuevo')) {
      // Estamos en /platos/:id/editar
      this.isEditMode.set(true);
      this.platoId.set(+idRestoParam);
      this.cargarPlato(+idRestoParam);
    }
  }

  // =========================================================================
  // CASO DE USO: CU07 - GESTIONAR CATEGORÍAS (LISTA DE CATEGORÍAS PARA SELECT)
  // =========================================================================
  cargarCategorias(): void {
    this.categoriaService.getCategorias().subscribe({
      next: (cats) => this.categorias.set(cats),
      error: () => {}
    });
  }

  // =========================================================================
  // CASO DE USO: CU08 - GESTIONAR PLATOS (CARGAR PLATO PARA EDICIÓN)
  // =========================================================================
  cargarPlato(idPlato: number): void {
    this.loading.set(true);
    this.platoService.getPlato(idPlato).subscribe({
      next: (plato) => {
        this.loading.set(false);
        this.restauranteId.set(plato.id_restaurante);
        this.formPlato.patchValue({
          nombre: plato.nombre,
          descripcion: plato.descripcion || '',
          precio: plato.precio,
          tipo_comida: plato.tipo_comida || '',
          personas_cubiertas: plato.personas_cubiertas,
          disponible: plato.disponible,
          id_categoria: plato.id_categoria
        });
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al cargar la información del plato.');
      }
    });
  }

  // =========================================================================
  // CASO DE USO: CU08 - GESTIONAR PLATOS (CREAR O ACTUALIZAR PLATO)
  // =========================================================================
  onSubmitPlato(): void {
    if (this.formPlato.invalid) {
      this.formPlato.markAllAsTouched();
      return;
    }

    this.guardando.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    const val = this.formPlato.value;

    if (this.isEditMode()) {
      const updateData: ActualizarPlatoRequest = {
        nombre: val.nombre,
        descripcion: val.descripcion || undefined,
        precio: Number(val.precio),
        tipo_comida: val.tipo_comida || undefined,
        personas_cubiertas: Number(val.personas_cubiertas),
        disponible: val.disponible,
        id_categoria: Number(val.id_categoria)
      };

      this.platoService.updatePlato(this.platoId()!, updateData).subscribe({
        next: () => {
          this.guardando.set(false);
          this.successMessage.set('Plato actualizado exitosamente.');
          setTimeout(() => this.successMessage.set(null), 3000);
        },
        error: (err) => {
          this.guardando.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al actualizar el plato.');
        }
      });
    } else {
      const createData: CrearPlatoRequest = {
        nombre: val.nombre,
        descripcion: val.descripcion || undefined,
        precio: Number(val.precio),
        tipo_comida: val.tipo_comida || undefined,
        personas_cubiertas: Number(val.personas_cubiertas),
        disponible: val.disponible,
        id_categoria: Number(val.id_categoria)
      };

      this.platoService.crearPlato(this.restauranteId()!, createData).subscribe({
        next: (nuevo) => {
          this.guardando.set(false);
          this.successMessage.set('Plato creado exitosamente.');
          setTimeout(() => {
            if (this.restauranteId()) {
              this.router.navigate(['/restaurantes', this.restauranteId(), 'platos']);
            } else {
              this.router.navigate(['/restaurantes']);
            }
          }, 1000);
        },
        error: (err) => {
          this.guardando.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al crear el plato.');
        }
      });
    }
  }

  volver(): void {
    if (this.restauranteId()) {
      this.router.navigate(['/restaurantes', this.restauranteId(), 'platos']);
    } else {
      this.router.navigate(['/restaurantes']);
    }
  }
}
