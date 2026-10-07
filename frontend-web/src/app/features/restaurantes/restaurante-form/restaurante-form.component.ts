import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { RestauranteService } from '../../../core/services/restaurante.service';
import { RegistrarRestauranteRequest, ActualizarRestauranteRequest } from '../../../core/models/restaurante.model';

@Component({
  selector: 'app-restaurante-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;">
            {{ isEditMode() ? 'Editar Restaurante' : 'Registrar Nuevo Restaurante' }}
          </h2>
          <p style="margin: 0.25rem 0 0 0; color: var(--text-muted); font-size: 0.875rem;">
            {{ isEditMode() ? 'Actualice la información y ubicación del establecimiento.' : 'Complete los datos requeridos para registrar su establecimiento gastronómico.' }}
          </p>
        </div>
        <a routerLink="/restaurantes" class="btn btn-secondary">Volver</a>
      </div>

      <div class="card-body">
        <div *ngIf="errorMessage()" class="alert alert-danger">
          {{ errorMessage() }}
        </div>
        <div *ngIf="successMessage()" class="alert alert-success">
          {{ successMessage() }}
        </div>

        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <h4 style="margin-top: 0; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; color: var(--primary-color);">
            Información General
          </h4>

          <div class="form-row">
            <div class="form-group col-8">
              <label class="form-label" for="nombre">Nombre Comercial *</label>
              <input
                id="nombre"
                type="text"
                class="form-control"
                formControlName="nombre"
                placeholder="Ej. Sabor Boliviano"
              />
              <div *ngIf="form.get('nombre')?.touched && form.get('nombre')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                El nombre es obligatorio (mínimo 2 caracteres).
              </div>
            </div>

            <div class="form-group col-4">
              <label class="form-label" for="nit">NIT / Identificación Tributaria</label>
              <input
                id="nit"
                type="text"
                class="form-control"
                formControlName="nit"
                placeholder="Ej. 1020304050"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="descripcion">Descripción del Concepto</label>
            <textarea
              id="descripcion"
              class="form-control"
              rows="3"
              formControlName="descripcion"
              placeholder="Describa el tipo de comida, especialidad, ambiente, etc."
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label class="form-label" for="telefono">Teléfono / Celular</label>
              <input
                id="telefono"
                type="text"
                class="form-control"
                formControlName="telefono"
                placeholder="Ej. +591 71234567"
              />
            </div>
            <div class="form-group col-6">
              <label class="form-label" for="correo">Correo Electrónico Institucional</label>
              <input
                id="correo"
                type="email"
                class="form-control"
                formControlName="correo"
                placeholder="contacto@restaurante.com"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group col-6">
              <label class="form-label" for="horario_apertura">Horario Apertura</label>
              <input
                id="horario_apertura"
                type="time"
                step="1"
                class="form-control"
                formControlName="horario_apertura"
              />
            </div>
            <div class="form-group col-6">
              <label class="form-label" for="horario_cierre">Horario Cierre</label>
              <input
                id="horario_cierre"
                type="time"
                step="1"
                class="form-control"
                formControlName="horario_cierre"
              />
            </div>
          </div>

          <h4 style="margin-top: 1.5rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; color: var(--primary-color);">
            Ubicación Física
          </h4>

          <div formGroupName="ubicacion">
            <div class="form-row">
              <div class="form-group col-8">
                <label class="form-label" for="direccion">Dirección *</label>
                <input
                  id="direccion"
                  type="text"
                  class="form-control"
                  formControlName="direccion"
                  placeholder="Ej. Av. Ballivián #456 entre Calles 12 y 13"
                />
                <div *ngIf="form.get('ubicacion.direccion')?.touched && form.get('ubicacion.direccion')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  La dirección es requerida (mínimo 3 caracteres).
                </div>
              </div>

              <div class="form-group col-4">
                <label class="form-label" for="zona">Zona / Barrio</label>
                <input
                  id="zona"
                  type="text"
                  class="form-control"
                  formControlName="zona"
                  placeholder="Ej. Calacoto"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group col-6">
                <label class="form-label" for="ciudad">Ciudad *</label>
                <input
                  id="ciudad"
                  type="text"
                  class="form-control"
                  formControlName="ciudad"
                  placeholder="Ej. La Paz, Santa Cruz, Cochabamba"
                />
                <div *ngIf="form.get('ubicacion.ciudad')?.touched && form.get('ubicacion.ciudad')?.invalid" class="text-danger" style="font-size: 0.8rem; margin-top: 0.25rem;">
                  La ciudad es requerida.
                </div>
              </div>

              <div class="form-group col-6">
                <label class="form-label" for="referencia">Punto de Referencia</label>
                <input
                  id="referencia"
                  type="text"
                  class="form-control"
                  formControlName="referencia"
                  placeholder="Ej. Frente al supermercado, media cuadra antes de la plaza"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group col-6">
                <label class="form-label" for="latitud">Latitud Geográfica</label>
                <input
                  id="latitud"
                  type="number"
                  step="0.000001"
                  class="form-control"
                  formControlName="latitud"
                  placeholder="-16.500000"
                />
              </div>
              <div class="form-group col-6">
                <label class="form-label" for="longitud">Longitud Geográfica</label>
                <input
                  id="longitud"
                  type="number"
                  step="0.000001"
                  class="form-control"
                  formControlName="longitud"
                  placeholder="-68.150000"
                />
              </div>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem;">
            <a routerLink="/restaurantes" class="btn btn-secondary">Cancelar</a>
            <button type="submit" class="btn btn-primary" [disabled]="form.invalid || loading()">
              <span *ngIf="loading()" class="spinner" style="width: 14px; height: 14px; margin-right: 0.5rem;"></span>
              {{ isEditMode() ? 'Actualizar Restaurante' : 'Guardar y Registrar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .form-row {
      display: flex;
      flex-wrap: wrap;
      margin: 0 -0.5rem;
    }
    .col-4 { flex: 0 0 33.333%; padding: 0 0.5rem; }
    .col-6 { flex: 0 0 50%; padding: 0 0.5rem; }
    .col-8 { flex: 0 0 66.666%; padding: 0 0.5rem; }
    @media (max-width: 768px) {
      .col-4, .col-6, .col-8 { flex: 0 0 100%; }
    }
  `]
})
export class RestauranteFormComponent implements OnInit {
  private fb = inject(FormBuilder);
  private restauranteService = inject(RestauranteService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  isEditMode = signal<boolean>(false);
  restauranteId = signal<number | null>(null);
  loading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  form: FormGroup = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(150)]],
    descripcion: [''],
    nit: [''],
    telefono: [''],
    correo: ['', [Validators.email]],
    horario_apertura: [''],
    horario_cierre: [''],
    ubicacion: this.fb.group({
      direccion: ['', [Validators.required, Validators.minLength(3)]],
      zona: [''],
      ciudad: ['', [Validators.required, Validators.minLength(2)]],
      latitud: [null],
      longitud: [null],
      referencia: ['']
    })
  });

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.isEditMode.set(true);
      this.restauranteId.set(+idParam);
      this.cargarDatosRestaurante(+idParam);
    }
  }

  // =========================================================================
  // CASO DE USO: CU06 - GESTIONAR RESTAURANTE (CARGAR DATOS PARA EDICIÓN)
  // =========================================================================
  private cargarDatosRestaurante(id: number): void {
    this.loading.set(true);
    this.restauranteService.getRestaurante(id).subscribe({
      next: (resto) => {
        this.loading.set(false);
        this.form.patchValue({
          nombre: resto.nombre,
          descripcion: resto.descripcion || '',
          nit: resto.nit || '',
          telefono: resto.telefono || '',
          correo: resto.correo || '',
          horario_apertura: resto.horario_apertura ? resto.horario_apertura.substring(0, 5) : '',
          horario_cierre: resto.horario_cierre ? resto.horario_cierre.substring(0, 5) : '',
          ubicacion: {
            direccion: resto.ubicacion?.direccion || '',
            zona: resto.ubicacion?.zona || '',
            ciudad: resto.ubicacion?.ciudad || '',
            latitud: resto.ubicacion?.latitud || null,
            longitud: resto.ubicacion?.longitud || null,
            referencia: resto.ubicacion?.referencia || ''
          }
        });
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(err.error?.detail || 'No se pudo cargar la información del restaurante.');
      }
    });
  }

  // =========================================================================
  // CASO DE USO: CU05 / CU06 - GUARDAR O ACTUALIZAR RESTAURANTE
  // =========================================================================
  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    const val = this.form.value;

    const payloadUbicacion: any = {
      direccion: val.ubicacion.direccion,
      ciudad: val.ubicacion.ciudad,
      zona: val.ubicacion.zona || null,
      latitud: val.ubicacion.latitud !== null && val.ubicacion.latitud !== '' ? Number(val.ubicacion.latitud) : null,
      longitud: val.ubicacion.longitud !== null && val.ubicacion.longitud !== '' ? Number(val.ubicacion.longitud) : null,
      referencia: val.ubicacion.referencia || null
    };

    if (this.isEditMode()) {
      // =========================================================================
      // CASO DE USO: CU06 - GESTIONAR RESTAURANTE (ACTUALIZAR)
      // =========================================================================
      const updateData: ActualizarRestauranteRequest = {
        nombre: val.nombre,
        descripcion: val.descripcion || null,
        nit: val.nit || null,
        telefono: val.telefono || null,
        correo: val.correo || null,
        horario_apertura: val.horario_apertura ? `${val.horario_apertura}:00`.substring(0, 8) : null,
        horario_cierre: val.horario_cierre ? `${val.horario_cierre}:00`.substring(0, 8) : null,
        ubicacion: payloadUbicacion
      };

      this.restauranteService.updateRestaurante(this.restauranteId()!, updateData).subscribe({
        next: () => {
          this.loading.set(false);
          this.successMessage.set('Restaurante actualizado exitosamente.');
          setTimeout(() => this.router.navigate(['/restaurantes']), 1200);
        },
        error: (err) => {
          this.loading.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al actualizar el restaurante.');
        }
      });
    } else {
      // =========================================================================
      // CASO DE USO: CU05 - REGISTRAR RESTAURANTE
      // =========================================================================
      const createData: RegistrarRestauranteRequest = {
        nombre: val.nombre,
        descripcion: val.descripcion || undefined,
        nit: val.nit || undefined,
        telefono: val.telefono || undefined,
        correo: val.correo || undefined,
        horario_apertura: val.horario_apertura ? `${val.horario_apertura}:00`.substring(0, 8) : undefined,
        horario_cierre: val.horario_cierre ? `${val.horario_cierre}:00`.substring(0, 8) : undefined,
        ubicacion: payloadUbicacion
      };

      this.restauranteService.crearRestaurante(createData).subscribe({
        next: () => {
          this.loading.set(false);
          this.successMessage.set('Restaurante registrado exitosamente.');
          setTimeout(() => this.router.navigate(['/restaurantes']), 1200);
        },
        error: (err) => {
          this.loading.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al registrar el restaurante.');
        }
      });
    }
  }
}
