// CASO DE USO: CU11 - Registrar planificación gastronómica
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { PlanificacionService } from '../../../core/services/planificacion.service';
import { PreferenciaService } from '../../../core/services/preferencia.service';
import { Preferencia } from '../../../core/models/preferencia.model';
import { TIPOS_COMIDA, PlanificacionCrear } from '../../../core/models/planificacion.model';

@Component({
  selector: 'app-nueva-planificacion',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div class="form-container">
      <div class="header-section">
        <h2>Registrar Planificación Gastronómica (CU11)</h2>
        <p style="color: var(--text-muted);">
          Indica los parámetros de tu comida o evento. El optimizador calculará opciones de restaurantes y de preparación casera adaptadas a tu presupuesto.
        </p>
      </div>

      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <div class="card">
        <form [formGroup]="planForm" (ngSubmit)="onSubmit()">
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
                  placeholder="Ej. 300.00"
                  formControlName="presupuesto"
                  [class.is-invalid]="f['presupuesto'].touched && f['presupuesto'].invalid"
                />
              </div>
              <div *ngIf="f['presupuesto'].touched && f['presupuesto'].invalid" class="invalid-feedback">
                <span *ngIf="f['presupuesto'].errors?.['required']">El presupuesto es obligatorio.</span>
                <span *ngIf="f['presupuesto'].errors?.['min']">El presupuesto debe ser mayor a 0 Bs.</span>
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
                placeholder="Ej. 20"
                formControlName="cantidad_personas"
                [class.is-invalid]="f['cantidad_personas'].touched && f['cantidad_personas'].invalid"
              />
              <div *ngIf="f['cantidad_personas'].touched && f['cantidad_personas'].invalid" class="invalid-feedback">
                <span *ngIf="f['cantidad_personas'].errors?.['required']">La cantidad de personas es obligatoria.</span>
                <span *ngIf="f['cantidad_personas'].errors?.['min']">Debe ser al menos 1 comensal.</span>
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
                <option value="">-- Selecciona el tipo de comida --</option>
                <option *ngFor="let tipo of tiposComida" [value]="tipo.valor">
                  {{ tipo.etiqueta }}
                </option>
              </select>
              <div *ngIf="f['tipo_comida'].touched && f['tipo_comida'].invalid" class="invalid-feedback">
                Selecciona un tipo de comida válido.
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="ubicacion_referencia">Ubicación de Referencia *</label>
              <input 
                id="ubicacion_referencia" 
                type="text" 
                class="form-control" 
                placeholder="Ej. Equipetrol, Centro, Zona Norte"
                formControlName="ubicacion_referencia"
                [class.is-invalid]="f['ubicacion_referencia'].touched && f['ubicacion_referencia'].invalid"
              />
              <div *ngIf="f['ubicacion_referencia'].touched && f['ubicacion_referencia'].invalid" class="invalid-feedback">
                <span *ngIf="f['ubicacion_referencia'].errors?.['required']">La ubicación de referencia es obligatoria.</span>
                <span *ngIf="f['ubicacion_referencia'].errors?.['minlength']">Mínimo 2 caracteres.</span>
              </div>
            </div>
          </div>

          <!-- Preferencias específicas para esta planificación -->
          <div class="form-group" style="margin-top: 1.5rem;">
            <label class="form-label">Preferencias Gastronómicas para este evento (Opcional)</label>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">
              Selecciona los requerimientos alimentarios para este grupo de comensales. Modificar esto no alterará las preferencias guardadas en tu perfil general.
            </p>

            <div *ngIf="cargandoPreferencias()" style="font-size: 0.85rem; color: var(--text-muted);">
              Cargando catálogo de preferencias...
            </div>

            <div *ngIf="!cargandoPreferencias()" class="pref-chips-container">
              <div 
                *ngFor="let pref of catalogoPreferencias()" 
                class="pref-chip" 
                [class.active]="preferenciasSeleccionadas().has(pref.id_preferencia)"
                (click)="togglePreferencia(pref.id_preferencia)"
              >
                <span *ngIf="preferenciasSeleccionadas().has(pref.id_preferencia)">✓ </span>
                {{ pref.nombre }}
              </div>
            </div>
          </div>

          <!-- Botones de Acción -->
          <div class="form-actions" style="margin-top: 2rem; display: flex; justify-content: flex-end; gap: 1rem;">
            <a routerLink="/planificaciones" class="btn btn-outline">Cancelar</a>
            <button 
              type="submit" 
              class="btn btn-primary" 
              [disabled]="planForm.invalid || guardando()"
            >
              <span *ngIf="guardando()">Guardando Planificación...</span>
              <span *ngIf="!guardando()">Guardar Planificación</span>
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
    .header-section {
      margin-bottom: 1.5rem;
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
export class NuevaPlanificacionComponent implements OnInit {
  private fb = inject(FormBuilder);
  private router = inject(Router);
  private planificacionService = inject(PlanificacionService);
  private preferenciaService = inject(PreferenciaService);

  tiposComida = TIPOS_COMIDA;
  catalogoPreferencias = signal<Preferencia[]>([]);
  preferenciasSeleccionadas = signal<Set<number>>(new Set());

  cargandoPreferencias = signal<boolean>(true);
  guardando = signal<boolean>(false);
  mensajeError = signal<string | null>(null);

  planForm: FormGroup = this.fb.group({
    presupuesto: [null, [Validators.required, Validators.min(0.01)]],
    cantidad_personas: [null, [Validators.required, Validators.min(1)]],
    tipo_comida: ['', [Validators.required]],
    ubicacion_referencia: ['', [Validators.required, Validators.minLength(2)]]
  });

  get f() {
    return this.planForm.controls;
  }

  ngOnInit(): void {
    this.cargarPreferenciasIniciales();
  }

  cargarPreferenciasIniciales(): void {
    this.preferenciaService.listarPreferencias().subscribe({
      next: (catalogo) => {
        this.catalogoPreferencias.set(catalogo.filter(p => p.activo));
        // Intentar pre-seleccionar con las del usuario
        this.preferenciaService.obtenerPreferenciasUsuario().subscribe({
          next: (userPref) => {
            const setIds = new Set<number>((userPref.preferencias || []).map(p => p.id_preferencia));
            this.preferenciasSeleccionadas.set(setIds);
            this.cargandoPreferencias.set(false);
          },
          error: () => {
            this.cargandoPreferencias.set(false);
          }
        });
      },
      error: () => {
        this.cargandoPreferencias.set(false);
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
    if (this.planForm.invalid) {
      this.planForm.markAllAsTouched();
      return;
    }

    this.guardando.set(true);
    this.mensajeError.set(null);

    const formValues = this.planForm.value;
    const datos: PlanificacionCrear = {
      presupuesto: Number(formValues.presupuesto),
      cantidad_personas: Math.floor(Number(formValues.cantidad_personas)),
      tipo_comida: formValues.tipo_comida,
      ubicacion_referencia: formValues.ubicacion_referencia.trim(),
      preferencias: Array.from(this.preferenciasSeleccionadas())
    };

    this.planificacionService.crearPlanificacion(datos).subscribe({
      next: (creada) => {
        this.guardando.set(false);
        // Redirigir al detalle de la planificación creada
        this.router.navigate(['/planificaciones', creada.id_planificacion]);
      },
      error: (err) => {
        console.error('Error al crear planificación:', err);
        this.guardando.set(false);
        this.mensajeError.set(err.error?.detail || 'No se pudo crear la planificación.');
      }
    });
  }
}
