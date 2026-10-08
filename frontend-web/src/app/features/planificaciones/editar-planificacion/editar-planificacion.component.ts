import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU11 - Modificar planificación gastronómica
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { PlanificacionService } from '../../../core/services/planificacion.service';
import { PreferenciaService } from '../../../core/services/preferencia.service';
import { Preferencia } from '../../../core/models/preferencia.model';
import { TIPOS_COMIDA, PlanificacionActualizar } from '../../../core/models/planificacion.model';

@Component({
  selector: 'app-editar-planificacion',
  standalone: true,
  imports: [AppIconComponent, CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div class="form-container">
      <div class="header-section">
        <a [routerLink]="['/planificaciones', idPlanificacion]" class="back-link">&larr; Volver al detalle</a>
        <h2 style="margin-top: 0.5rem;">Editar Planificación #{{ idPlanificacion }}</h2>
        <p style="color: var(--text-muted);">
          Actualiza los parámetros presupuestarios, comensales o preferencias asociadas.
        </p>
      </div>

      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <!-- Estado de carga -->
      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Cargando datos de la planificación...</p>
      </div>

      <div *ngIf="!cargando()" class="card">
        <form [formGroup]="editForm" (ngSubmit)="onSubmit()">
          <!-- Presupuesto y Cantidad de Personas -->
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label" for="presupuesto">Presupuesto Disponible (Bs) *</label>
              <div class="input-group">
                <span class="input-addon">Bs</span>
                <input 
                  id="presupuesto" 
                  type="number" 
                  step="0.50" 
                  min="1" 
                  class="form-control" 
                  formControlName="presupuesto"
                  [class.is-invalid]="f['presupuesto'].touched && f['presupuesto'].invalid"
                />
              </div>
              <div *ngIf="f['presupuesto'].touched && f['presupuesto'].invalid" class="invalid-feedback">
                Presupuesto mayor a 0 Bs requerido.
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="cantidad_personas">Cantidad de Comensales *</label>
              <input 
                id="cantidad_personas" 
                type="number" 
                step="1" 
                min="1" 
                class="form-control" 
                formControlName="cantidad_personas"
                [class.is-invalid]="f['cantidad_personas'].touched && f['cantidad_personas'].invalid"
              />
              <div *ngIf="f['cantidad_personas'].touched && f['cantidad_personas'].invalid" class="invalid-feedback">
                Mínimo 1 comensal requerido.
              </div>
            </div>
          </div>

          <!-- Tipo de Comida y Ubicación de Referencia -->
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label" for="tipo_comida">Tipo de Comida *</label>
              <select 
                id="tipo_comida" 
                class="form-control" 
                formControlName="tipo_comida"
                [class.is-invalid]="f['tipo_comida'].touched && f['tipo_comida'].invalid"
              >
                <option *ngFor="let tipo of tiposComida" [value]="tipo.valor">
                  {{ tipo.etiqueta }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="ubicacion_referencia">Ubicación de Referencia *</label>
              <input 
                id="ubicacion_referencia" 
                type="text" 
                class="form-control" 
                formControlName="ubicacion_referencia"
                [class.is-invalid]="f['ubicacion_referencia'].touched && f['ubicacion_referencia'].invalid"
              />
            </div>
          </div>

          <!-- Preferencias específicas -->
          <div class="form-group" style="margin-top: 1.5rem;">
            <label class="form-label">Preferencias Gastronómicas para este evento</label>
            <div class="pref-chips-container">
              <div 
                *ngFor="let pref of catalogoPreferencias()" 
                class="pref-chip" 
                [class.active]="preferenciasSeleccionadas().has(pref.id_preferencia)"
                (click)="togglePreferencia(pref.id_preferencia)"
              >
                <span *ngIf="preferenciasSeleccionadas().has(pref.id_preferencia)"><app-icon name="check" class="app-icon-inline"></app-icon> </span>
                {{ pref.nombre }}
              </div>
            </div>
          </div>

          <!-- Botones de Acción -->
          <div class="form-actions" style="margin-top: 2rem; display: flex; justify-content: flex-end; gap: 1rem;">
            <a [routerLink]="['/planificaciones', idPlanificacion]" class="btn btn-outline">Cancelar</a>
            <button 
              type="submit" 
              class="btn btn-primary" 
              [disabled]="editForm.invalid || guardando()"
            >
              <span *ngIf="guardando()">Guardando Cambios...</span>
              <span *ngIf="!guardando()">Guardar Cambios</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .form-container {
      max-width: 850px;
      margin: 0 auto;
    }
    .back-link {
      color: var(--text-muted);
      font-size: 0.875rem;
    }
    .input-group {
      display: flex;
    }
    .input-addon {
      display: inline-flex;
      align-items: center;
      padding: 0.5rem 0.75rem;
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--text-muted);
      background-color: #f1f5f9;
      border: 1px solid var(--border);
      border-right: none;
      border-top-left-radius: var(--radius);
      border-bottom-left-radius: var(--radius);
    }
    .input-group .form-control {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }
    .pref-chips-container {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 0.5rem;
    }
    .pref-chip {
      padding: 0.4rem 0.85rem;
      font-size: 0.825rem;
      border: 1px solid var(--border);
      border-radius: 9999px;
      background-color: var(--surface);
      cursor: pointer;
      user-select: none;
      transition: all 0.2s ease;
    }
    .pref-chip:hover {
      border-color: var(--accent);
      background-color: #f8fafc;
    }
    .pref-chip.active {
      background-color: var(--primary);
      border-color: var(--primary);
      color: white;
      font-weight: 600;
    }
  `]
})
export class EditarPlanificacionComponent implements OnInit {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private planificacionService = inject(PlanificacionService);
  private preferenciaService = inject(PreferenciaService);

  idPlanificacion!: number;
  tiposComida = TIPOS_COMIDA;
  catalogoPreferencias = signal<Preferencia[]>([]);
  preferenciasSeleccionadas = signal<Set<number>>(new Set());

  cargando = signal<boolean>(true);
  guardando = signal<boolean>(false);
  mensajeError = signal<string | null>(null);

  editForm: FormGroup = this.fb.group({
    presupuesto: [null, [Validators.required, Validators.min(0.01)]],
    cantidad_personas: [null, [Validators.required, Validators.min(1)]],
    tipo_comida: ['', [Validators.required]],
    ubicacion_referencia: ['', [Validators.required, Validators.minLength(2)]]
  });

  get f() {
    return this.editForm.controls;
  }

  ngOnInit(): void {
    this.idPlanificacion = Number(this.route.snapshot.paramMap.get('id'));
    if (this.idPlanificacion) {
      this.cargarDatos();
    }
  }

  cargarDatos(): void {
    this.cargando.set(true);
    // Cargar catálogo de preferencias y luego la planificación
    this.preferenciaService.listarPreferencias().subscribe({
      next: (catalogo) => {
        this.catalogoPreferencias.set(catalogo.filter(p => p.activo));
        this.planificacionService.obtenerPlanificacion(this.idPlanificacion).subscribe({
          next: (plan) => {
            if (plan.estado === 'CANCELADA') {
              this.mensajeError.set('No se puede editar una planificación en estado CANCELADA.');
              this.cargando.set(false);
              return;
            }

            this.editForm.patchValue({
              presupuesto: Number(plan.presupuesto),
              cantidad_personas: plan.cantidad_personas,
              tipo_comida: plan.tipo_comida,
              ubicacion_referencia: plan.ubicacion_referencia
            });

            const setIds = new Set<number>((plan.preferencias || []).map(p => p.id_preferencia));
            this.preferenciasSeleccionadas.set(setIds);
            this.cargando.set(false);
          },
          error: (err) => {
            console.error('Error al cargar planificación para edición:', err);
            this.mensajeError.set(err.error?.detail || 'No se pudo cargar la planificación.');
            this.cargando.set(false);
          }
        });
      },
      error: () => {
        this.mensajeError.set('Error al cargar preferencias.');
        this.cargando.set(false);
      }
    });
  }

  togglePreferencia(id: number): void {
    const actual = new Set(this.preferenciasSeleccionadas());
    if (actual.has(id)) {
      actual.delete(id);
    } else {
      actual.add(id);
    }
    this.preferenciasSeleccionadas.set(actual);
  }

  onSubmit(): void {
    if (this.editForm.invalid) {
      this.editForm.markAllAsTouched();
      return;
    }

    this.guardando.set(true);
    this.mensajeError.set(null);

    const values = this.editForm.value;
    const datos: PlanificacionActualizar = {
      presupuesto: Number(values.presupuesto),
      cantidad_personas: Math.floor(Number(values.cantidad_personas)),
      tipo_comida: values.tipo_comida,
      ubicacion_referencia: values.ubicacion_referencia.trim(),
      preferencias: Array.from(this.preferenciasSeleccionadas())
    };

    this.planificacionService.actualizarPlanificacion(this.idPlanificacion, datos).subscribe({
      next: (actualizada) => {
        this.guardando.set(false);
        this.router.navigate(['/planificaciones', actualizada.id_planificacion]);
      },
      error: (err) => {
        console.error('Error al actualizar planificación:', err);
        this.guardando.set(false);
        this.mensajeError.set(err.error?.detail || 'No se pudo actualizar la planificación.');
      }
    });
  }
}
