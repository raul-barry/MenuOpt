import { AppIconComponent } from '../../shared/app-icon/app-icon.component';
// CASO DE USO: CU12 - Definir preferencias
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PreferenciaService } from '../../core/services/preferencia.service';
import { Preferencia } from '../../core/models/preferencia.model';

@Component({
  selector: 'app-preferencias',
  standalone: true,
  imports: [AppIconComponent, CommonModule],
  template: `
    <div class="preferencias-container">
      <div class="header-section">
        <h2>Mis Preferencias Gastronómicas (CU12)</h2>
        <p style="color: var(--text-muted);">
          Selecciona tus dietas, restricciones y gustos culinarios habituales. Estas preferencias se utilizarán para recomendarte los mejores menús y recetas.
        </p>
      </div>

      <!-- Feedback visual -->
      <div *ngIf="mensajeExito()" class="alert alert-success">{{ mensajeExito() }}</div>
      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <!-- Estado de carga -->
      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Cargando catálogo de preferencias...</p>
      </div>

      <!-- Contenido Principal -->
      <div *ngIf="!cargando()" class="card">
        <div class="card-header">
          <div>
            <h3>Catálogo de Preferencias Disponibles</h3>
            <span style="font-size: 0.8rem; color: var(--text-muted);">
              {{ seleccionadas().size }} seleccionada(s)
            </span>
          </div>
          <button 
            class="btn btn-primary" 
            [disabled]="guardando()" 
            (click)="guardarPreferencias()"
          >
            <span *ngIf="guardando()">Guardando...</span>
            <span *ngIf="!guardando()"><app-icon name="save" class="app-icon-inline"></app-icon> Guardar Preferencias</span>
          </button>
        </div>

        <div *ngIf="preferencias().length === 0" style="text-align: center; padding: 2rem; color: var(--text-muted);">
          No hay preferencias registradas en el sistema actualmente.
        </div>

        <!-- Chips / Tarjetas interactivas de preferencias -->
        <div class="preferencias-grid">
          <div 
            *ngFor="let pref of preferencias()" 
            class="pref-card" 
            [class.selected]="seleccionadas().has(pref.id_preferencia)"
            (click)="togglePreferencia(pref.id_preferencia)"
          >
            <div class="pref-checkbox">
              <span *ngIf="seleccionadas().has(pref.id_preferencia)"><app-icon name="check" class="app-icon-inline"></app-icon></span>
            </div>
            <div class="pref-info">
              <div class="pref-nombre">{{ pref.nombre }}</div>
              <div class="pref-categoria badge badge-secondary">{{ pref.categoria }}</div>
              <p *ngIf="pref.descripcion" class="pref-desc">{{ pref.descripcion }}</p>
            </div>
          </div>
        </div>

        <div class="card-footer" style="margin-top: 1.5rem; display: flex; justify-content: flex-end;">
          <button 
            class="btn btn-primary" 
            [disabled]="guardando()" 
            (click)="guardarPreferencias()"
          >
            <span *ngIf="guardando()">Guardando...</span>
            <span *ngIf="!guardando()"><app-icon name="save" class="app-icon-inline"></app-icon> Guardar Preferencias</span>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .preferencias-container {
      max-width: 900px;
      margin: 0 auto;
    }
    .header-section {
      margin-bottom: 1.5rem;
    }
    .preferencias-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: 1rem;
      margin-top: 1rem;
    }
    .pref-card {
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      padding: 1rem;
      border: 2px solid var(--border);
      border-radius: var(--radius);
      cursor: pointer;
      background-color: var(--surface);
      transition: all 0.2s ease;
      user-select: none;
    }
    .pref-card:hover {
      border-color: var(--accent);
      background-color: #f8fafc;
    }
    .pref-card.selected {
      border-color: var(--primary);
      background-color: var(--primary-light);
    }
    .pref-checkbox {
      width: 22px;
      height: 22px;
      border-radius: 4px;
      border: 2px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      font-weight: bold;
      color: white;
      background-color: white;
      flex-shrink: 0;
      margin-top: 2px;
      transition: all 0.2s ease;
    }
    .pref-card.selected .pref-checkbox {
      background-color: var(--primary);
      border-color: var(--primary);
    }
    .pref-info {
      flex: 1;
    }
    .pref-nombre {
      font-weight: 600;
      font-size: 0.95rem;
      color: var(--text-main);
      margin-bottom: 0.25rem;
    }
    .pref-categoria {
      font-size: 0.65rem;
      margin-bottom: 0.5rem;
    }
    .pref-desc {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin: 0;
      line-height: 1.3;
    }
  `]
})
export class PreferenciasComponent implements OnInit {
  private preferenciaService = inject(PreferenciaService);

  preferencias = signal<Preferencia[]>([]);
  seleccionadas = signal<Set<number>>(new Set());

  cargando = signal<boolean>(true);
  guardando = signal<boolean>(false);
  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarDatos();
  }

  cargarDatos(): void {
    this.cargando.set(true);
    this.mensajeError.set(null);

    // Cargar catálogo de preferencias
    this.preferenciaService.listarPreferencias().subscribe({
      next: (catalogo) => {
        this.preferencias.set(catalogo.filter(p => p.activo));
        // Cargar preferencias del usuario
        this.preferenciaService.obtenerPreferenciasUsuario().subscribe({
          next: (userPref) => {
            const setIds = new Set<number>((userPref.preferencias || []).map(p => p.id_preferencia));
            this.seleccionadas.set(setIds);
            this.cargando.set(false);
          },
          error: (err) => {
            console.error('Error al cargar preferencias del usuario:', err);
            this.cargando.set(false);
          }
        });
      },
      error: (err) => {
        console.error('Error al cargar catálogo de preferencias:', err);
        this.mensajeError.set('No se pudo cargar el catálogo de preferencias.');
        this.cargando.set(false);
      }
    });
  }

  togglePreferencia(id: number): void {
    const actual = new Set(this.seleccionadas());
    if (actual.has(id)) {
      actual.delete(id);
    } else {
      actual.add(id);
    }
    this.seleccionadas.set(actual);
  }

  guardarPreferencias(): void {
    this.guardando.set(true);
    this.mensajeExito.set(null);
    this.mensajeError.set(null);

    const ids = Array.from(this.seleccionadas());
    this.preferenciaService.guardarPreferenciasUsuario(ids).subscribe({
      next: () => {
        this.guardando.set(false);
        this.mensajeExito.set('¡Tus preferencias gastronómicas fueron actualizadas con éxito!');
        setTimeout(() => this.mensajeExito.set(null), 4000);
      },
      error: (err) => {
        console.error('Error al guardar preferencias:', err);
        this.guardando.set(false);
        this.mensajeError.set(err.error?.detail || 'Ocurrió un error al guardar tus preferencias.');
      }
    });
  }
}
