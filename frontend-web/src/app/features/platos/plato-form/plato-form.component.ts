import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { PlatoService } from '../../../core/services/plato.service';
import { CategoriaService } from '../../../core/services/categoria.service';
import { IngredienteService } from '../../../core/services/ingrediente.service';
import { Categoria } from '../../../core/models/categoria.model';
import { Plato, CrearPlatoRequest, ActualizarPlatoRequest } from '../../../core/models/plato.model';
import { Ingrediente, PlatoIngredienteDetalle } from '../../../core/models/ingrediente.model';

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
                  step="0.5"
                  class="form-control"
                  formControlName="precio"
                  placeholder="0.00"
                />
                <div *ngIf="formPlato.get('precio')?.touched && formPlato.get('precio')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  Ingrese un precio válido.
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="descripcion">Descripción</label>
              <textarea
                id="descripcion"
                class="form-control"
                rows="3"
                formControlName="descripcion"
                placeholder="Breve reseña o ingredientes principales..."
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label" for="imagen_url">URL de imagen</label>
              <input id="imagen_url" type="url" class="form-control" formControlName="imagen_url" placeholder="https://..." />
              <img *ngIf="formPlato.get('imagen_url')?.value" [src]="formPlato.get('imagen_url')?.value" alt="Vista previa del plato" style="display:block;max-width:260px;max-height:150px;object-fit:cover;border-radius:0.5rem;margin-top:0.75rem" />
            </div>

            <div class="form-row">
              <div class="form-group col-4">
                <label class="form-label" for="id_categoria">Categoría *</label>
                <select id="id_categoria" class="form-control" formControlName="id_categoria">
                  <option [ngValue]="null" disabled>Seleccione una categoría</option>
                  <option *ngFor="let cat of categorias()" [value]="cat.id_categoria">
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
                  <option value="">Cualquiera / No especificado</option>
                  <option value="DESAYUNO">Desayuno</option>
                  <option value="ALMUERZO">Almuerzo</option>
                  <option value="CENA">Cena</option>
                  <option value="MERIENDA">Merienda / Postre</option>
                </select>
              </div>

              <div class="form-group col-4">
                <label class="form-label" for="personas_cubiertas">Comensales *</label>
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

            <div class="form-check" style="margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <input
                id="disponible"
                type="checkbox"
                formControlName="disponible"
                style="width: 18px; height: 18px; cursor: pointer;"
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

      <!-- Sección de Composición de Ingredientes / Receta (CU09) -->
      <div *ngIf="isEditMode()" class="card">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <h3 style="margin: 0; font-size: 1.15rem;">
              Composición de Ingredientes y Receta (CU09)
            </h3>
            <p style="margin: 0.25rem 0 0 0; color: var(--text-muted); font-size: 0.85rem;">
              Especifique los insumos requeridos para este plato con sus cantidades exactas.
            </p>
          </div>
          <button class="btn btn-sm btn-primary" (click)="abrirModalAsociar()">
            + Asignar Ingrediente
          </button>
        </div>

        <div class="card-body">
          <div *ngIf="mensajeIngrediente()" class="alert" [ngClass]="errorIngrediente() ? 'alert-danger' : 'alert-success'">
            {{ mensajeIngrediente() }}
          </div>

          <div *ngIf="cargandoIngredientes()" style="text-align: center; padding: 1.5rem;">
            <p style="color: var(--text-muted);">Cargando receta del plato...</p>
          </div>

          <div *ngIf="!cargandoIngredientes()" class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Ingrediente</th>
                  <th>Cantidad Requerida</th>
                  <th>Unidad de Medida</th>
                  <th style="width: 140px; text-align: right;">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let pi of ingredientesPlato()">
                  <td><strong>{{ pi.nombre_ingrediente || 'Ingrediente #' + pi.id_ingrediente }}</strong></td>
                  <td>{{ pi.cantidad }}</td>
                  <td><span class="badge badge-secondary">{{ pi.unidad_medida }}</span></td>
                  <td style="text-align: right;">
                    <button class="btn btn-sm btn-outline" style="margin-right: 0.35rem; padding: 0.2rem 0.5rem;" (click)="abrirModalEditarIngrediente(pi)">
                      Editar
                    </button>
                    <button class="btn btn-sm btn-outline" style="color: #ef4444; border-color: #ef4444; padding: 0.2rem 0.5rem;" (click)="quitarIngrediente(pi)">
                      Quitar
                    </button>
                  </td>
                </tr>
                <tr *ngIf="ingredientesPlato().length === 0">
                  <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">
                    Este plato aún no tiene ingredientes asociados en su receta.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para Asociar o Editar Ingrediente en el Plato (CU09) -->
    <div *ngIf="mostrarModalIngrediente()" style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1050; padding: 1rem;">
      <div class="card" style="width: 100%; max-width: 480px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">
          <h3 style="margin: 0; font-size: 1.15rem;">
            {{ ingredienteEditando() ? 'Editar Ingrediente en Receta' : 'Asociar Ingrediente a Receta' }}
          </h3>
          <button class="btn btn-sm btn-outline" (click)="cerrarModalIngrediente()" style="padding: 0.2rem 0.5rem;">&times;</button>
        </div>

        <form [formGroup]="formAsociar" (ngSubmit)="guardarIngredientePlato()">
          <div class="form-group" *ngIf="!ingredienteEditando()" style="margin-bottom: 1rem;">
            <label class="form-label">Ingrediente *</label>
            <select class="form-control" formControlName="id_ingrediente">
              <option [ngValue]="null" disabled>Seleccione un ingrediente</option>
              <option *ngFor="let ing of ingredientesCatalogo()" [value]="ing.id_ingrediente">
                {{ ing.nombre }} ({{ ing.unidad_medida }})
              </option>
            </select>
          </div>

          <div class="form-group" style="margin-bottom: 1rem;">
            <label class="form-label">Cantidad Requerida *</label>
            <input type="number" step="0.01" min="0.001" class="form-control" formControlName="cantidad" placeholder="Ej. 250, 1.5, etc." />
          </div>

          <div class="form-group" style="margin-bottom: 1.5rem;">
            <label class="form-label">Unidad de Medida *</label>
            <input type="text" class="form-control" formControlName="unidad_medida" placeholder="Ej. gramos, kg, ml, unidades" />
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
            <button type="button" class="btn btn-secondary btn-sm" (click)="cerrarModalIngrediente()">Cancelar</button>
            <button type="submit" class="btn btn-primary btn-sm" [disabled]="formAsociar.invalid || guardandoIngrediente()">
              {{ ingredienteEditando() ? 'Actualizar' : 'Agregar' }}
            </button>
          </div>
        </form>
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
  private ingredienteService = inject(IngredienteService);
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

  // CU09: Ingredientes y Receta
  ingredientesCatalogo = signal<Ingrediente[]>([]);
  ingredientesPlato = signal<PlatoIngredienteDetalle[]>([]);
  cargandoIngredientes = signal<boolean>(false);
  mostrarModalIngrediente = signal<boolean>(false);
  guardandoIngrediente = signal<boolean>(false);
  ingredienteEditando = signal<PlatoIngredienteDetalle | null>(null);
  mensajeIngrediente = signal<string | null>(null);
  errorIngrediente = signal<boolean>(false);

  formPlato: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
    descripcion: [''],
    imagen_url: [''],
    precio: [null, [Validators.required, Validators.min(0)]],
    tipo_comida: [''],
    personas_cubiertas: [1, [Validators.required, Validators.min(1)]],
    disponible: [true],
    id_categoria: [null, [Validators.required]]
  });

  formAsociar: FormGroup = this.fb.group({
    id_ingrediente: [null, [Validators.required]],
    cantidad: [null, [Validators.required, Validators.min(0.001)]],
    unidad_medida: ['', [Validators.required]]
  });

  ngOnInit(): void {
    this.cargarCategorias();
    this.cargarCatalogoIngredientes();

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
      this.cargarIngredientesPlato(+idRestoParam);
    }
  }

  cargarCategorias(): void {
    this.categoriaService.getCategorias().subscribe({
      next: (cats) => this.categorias.set(cats),
      error: () => {}
    });
  }

  cargarCatalogoIngredientes(): void {
    this.ingredienteService.getIngredientes().subscribe({
      next: (ings) => this.ingredientesCatalogo.set(ings),
      error: () => {}
    });
  }

  cargarPlato(idPlato: number): void {
    this.loading.set(true);
    this.platoService.getPlato(idPlato).subscribe({
      next: (plato) => {
        this.loading.set(false);
        this.restauranteId.set(plato.id_restaurante);
        this.formPlato.patchValue({
          nombre: plato.nombre,
          descripcion: plato.descripcion || '',
          imagen_url: plato.imagen_url || '',
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
  // CASO DE USO: CU09 - COMPOSICIÓN DE PLATOS E INGREDIENTES
  // =========================================================================
  cargarIngredientesPlato(idPlato: number): void {
    this.cargandoIngredientes.set(true);
    this.platoService.getIngredientesPlato(idPlato).subscribe({
      next: (res) => {
        this.cargandoIngredientes.set(false);
        this.ingredientesPlato.set(res);
      },
      error: () => {
        this.cargandoIngredientes.set(false);
      }
    });
  }

  abrirModalAsociar(): void {
    this.ingredienteEditando.set(null);
    this.formAsociar.reset({
      id_ingrediente: null,
      cantidad: null,
      unidad_medida: ''
    });
    this.mostrarModalIngrediente.set(true);
  }

  abrirModalEditarIngrediente(pi: PlatoIngredienteDetalle): void {
    this.ingredienteEditando.set(pi);
    this.formAsociar.patchValue({
      id_ingrediente: pi.id_ingrediente,
      cantidad: pi.cantidad,
      unidad_medida: pi.unidad_medida
    });
    this.mostrarModalIngrediente.set(true);
  }

  cerrarModalIngrediente(): void {
    this.mostrarModalIngrediente.set(false);
    this.ingredienteEditando.set(null);
  }

  guardarIngredientePlato(): void {
    if (this.formAsociar.invalid) {
      this.formAsociar.markAllAsTouched();
      return;
    }

    this.guardandoIngrediente.set(true);
    const val = this.formAsociar.value;

    if (this.ingredienteEditando()) {
      this.platoService.updateIngredientePlato(
        this.platoId()!,
        this.ingredienteEditando()!.id_ingrediente,
        {
          cantidad: Number(val.cantidad),
          unidad_medida: val.unidad_medida
        }
      ).subscribe({
        next: () => {
          this.guardandoIngrediente.set(false);
          this.cerrarModalIngrediente();
          this.errorIngrediente.set(false);
          this.mensajeIngrediente.set('Ingrediente actualizado en la receta.');
          this.cargarIngredientesPlato(this.platoId()!);
          setTimeout(() => this.mensajeIngrediente.set(null), 3000);
        },
        error: (err) => {
          this.guardandoIngrediente.set(false);
          this.errorIngrediente.set(true);
          this.mensajeIngrediente.set(err.error?.detail || 'Error al actualizar ingrediente.');
        }
      });
    } else {
      this.platoService.asociarIngrediente(
        this.platoId()!,
        {
          id_ingrediente: Number(val.id_ingrediente),
          cantidad: Number(val.cantidad),
          unidad_medida: val.unidad_medida
        }
      ).subscribe({
        next: () => {
          this.guardandoIngrediente.set(false);
          this.cerrarModalIngrediente();
          this.errorIngrediente.set(false);
          this.mensajeIngrediente.set('Ingrediente agregado a la receta correctamente.');
          this.cargarIngredientesPlato(this.platoId()!);
          setTimeout(() => this.mensajeIngrediente.set(null), 3000);
        },
        error: (err) => {
          this.guardandoIngrediente.set(false);
          this.errorIngrediente.set(true);
          this.mensajeIngrediente.set(err.error?.detail || 'Error al agregar ingrediente.');
        }
      });
    }
  }

  quitarIngrediente(pi: PlatoIngredienteDetalle): void {
    if (!confirm(`¿Desea quitar "${pi.nombre_ingrediente}" de la receta de este plato?`)) {
      return;
    }

    this.platoService.quitarIngrediente(this.platoId()!, pi.id_ingrediente).subscribe({
      next: () => {
        this.errorIngrediente.set(false);
        this.mensajeIngrediente.set('Ingrediente desvinculado de la receta.');
        this.cargarIngredientesPlato(this.platoId()!);
        setTimeout(() => this.mensajeIngrediente.set(null), 3000);
      },
      error: (err) => {
        this.errorIngrediente.set(true);
        this.mensajeIngrediente.set(err.error?.detail || 'Error al quitar ingrediente.');
      }
    });
  }

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
        imagen_url: val.imagen_url || null,
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
        imagen_url: val.imagen_url || undefined,
        precio: Number(val.precio),
        tipo_comida: val.tipo_comida || undefined,
        personas_cubiertas: Number(val.personas_cubiertas),
        disponible: val.disponible,
        id_categoria: Number(val.id_categoria)
      };

      this.platoService.crearPlato(this.restauranteId()!, createData).subscribe({
        next: () => {
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
