import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU21 & CU22 - Detalle de Reserva
import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ReservaService } from '../../../core/services/reserva.service';
import { AuthService } from '../../../core/services/auth.service';
import {
  ReservaRespuesta,
  ReservaInvitadoCrear,
  ReservaInvitadoRespuesta
} from '../../../core/models/reserva.model';

export interface InvitadoVisual {
  id_invitado?: number;
  nombre: string;
  correo?: string | null;
  id_usuario?: number | null;
  esTitular: boolean;
  tieneCuenta: boolean;
}

@Component({
  selector: 'app-detalle-reserva',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule],
  template: `
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;">Detalle de Reserva #{{ reservaId() }}</h2>
          <p style="margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.85rem;">
            Información registrada del comensal, establecimiento y mesa asignada.
          </p>
        </div>
        <button class="btn btn-outline btn-sm" (click)="volver()">
          &larr; Volver
        </button>
      </div>

      <div class="card-body">
        <div *ngIf="cargando()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando detalle de la reserva...</p>
        </div>

        <div *ngIf="mensaje()" class="alert alert-success" style="margin-bottom: 1rem;">
          {{ mensaje() }}
        </div>
        <div *ngIf="error()" class="alert alert-danger" style="margin-bottom: 1rem;">
          {{ error() }}
        </div>

        <div *ngIf="!cargando() && reserva() as r">
          <!-- Banner Superior de Estado -->
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: #f8fafc; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 1.5rem;">
            <div>
              <h3 style="margin: 0; color: var(--primary);">{{ r.nombre_restaurante }}</h3>
              <span style="font-size: 0.85rem; color: var(--text-muted);">Área: {{ r.nombre_area || 'Sin área asignada' }}</span>
            </div>
            <span
              class="badge"
              style="font-size: 0.9rem; padding: 0.4rem 0.8rem;"
              [class.badge-success]="r.estado === 'CONFIRMADA'"
              [class.badge-secondary]="r.estado === 'FINALIZADA'"
              [class.badge-danger]="r.estado === 'CANCELADA'"
              [class.badge-warning]="r.estado === 'PENDIENTE'"
            >
              {{ r.estado }}
            </span>
          </div>

          <!-- Cuadrícula de Datos -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
            <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem;">
              <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">HORARIO Y FECHA</h4>
              <p style="margin: 0 0 0.25rem 0; font-size: 1.1rem; font-weight: 600;"><app-icon name="calendar-days" class="app-icon-inline"></app-icon> {{ r.fecha_reserva }}</p>
              <p style="margin: 0; color: var(--text-muted);"><app-icon name="clock" class="app-icon-inline"></app-icon> {{ r.hora_inicio.substring(0, 5) }} &ndash; {{ r.hora_fin.substring(0, 5) }}</p>
            </div>

            <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem;">
              <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">COMENSALES</h4>
              <p style="margin: 0 0 0.25rem 0; font-size: 1.1rem; font-weight: 600;"><app-icon name="users" class="app-icon-inline"></app-icon> {{ r.cantidad_personas }} personas</p>
              <p style="margin: 0; color: var(--text-muted);">Titular: {{ r.nombre_cliente || 'Cliente #' + r.id_usuario }}</p>
            </div>

            <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem;">
              <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">MESA(S) ASIGNADA(S)</h4>
              <div style="margin-top: 0.25rem;">
                <span *ngFor="let m of r.mesas" class="badge" style="background: #e0f2fe; color: #0369a1; margin-right: 4px; font-size: 0.9rem; padding: 0.3rem 0.6rem;">
                  <app-icon name="table" class="app-icon-inline"></app-icon> Mesa {{ m.numero }} ({{ m.capacidad }}p)
                </span>
              </div>
            </div>
          </div>

          <!-- SECCIÓN: Invitados de la reserva -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem;">
              <div style="display: flex; align-items: center; gap: 0.6rem;">
                <h4 style="margin: 0; font-size: 1rem; font-weight: 700; color: #333333;">
                  <app-icon name="users" class="app-icon-inline" style="color: #FF6F00;"></app-icon>
                  Invitados de la reserva
                </h4>
                <span
                  class="badge"
                  style="font-size: 0.8rem; padding: 0.25rem 0.6rem;"
                  [style.background]="invitados().length <= r.cantidad_personas ? '#fff2e7' : '#fee2e2'"
                  [style.color]="invitados().length <= r.cantidad_personas ? '#FF6F00' : '#b91c1c'"
                  [style.border]="invitados().length <= r.cantidad_personas ? '1px solid #ffe3c8' : '1px solid #fecaca'"
                >
                  {{ invitados().length }} / {{ r.cantidad_personas }} comensales
                </span>
              </div>

              <button
                type="button"
                class="btn btn-outline btn-sm"
                (click)="toggleFormularioInvitado()"
                [disabled]="r.estado === 'CANCELADA' || r.estado === 'FINALIZADA' || invitados().length >= r.cantidad_personas"
                [title]="invitados().length >= r.cantidad_personas ? 'Capacidad máxima de la reserva alcanzada' : 'Registrar un comensal invitado'"
              >
                <app-icon [name]="mostrarFormularioInvitado() ? 'close' : 'plus'" class="app-icon-inline"></app-icon>
                {{ mostrarFormularioInvitado() ? 'Cerrar formulario' : 'Agregar invitado' }}
              </button>
            </div>

            <!-- Alerta informativa de dependencia técnica (Solo si el backend devuelve 404 al no estar integrado) -->
            <div
              *ngIf="endpointDisponible() === false"
              style="background: #fff7ed; border: 1px solid #fed7aa; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.82rem; color: #9a3412;"
            >
              <div style="display: flex; align-items: flex-start; gap: 0.5rem;">
                <app-icon name="info" class="app-icon-inline" style="color: #ea580c; flex-shrink: 0; margin-top: 2px;"></app-icon>
                <div>
                  <strong>Integración API backend pendiente:</strong>
                  Los endpoints de persistencia (<code>GET / POST / DELETE /reservas/&#123;id&#125;/invitados</code>) fueron implementados en la rama <code>codex-funcionalidades</code>.
                  El servicio Angular y los contratos TypeScript ya están integrados en esta vista. Tan pronto como los cambios del backend se incorporen al servidor activo, las operaciones responderán de forma inmediata.
                </div>
              </div>
            </div>

            <!-- Mensajes de éxito y error en gestión de invitados -->
            <div *ngIf="mensajeInvitados()" class="alert alert-success" style="font-size: 0.85rem; padding: 0.6rem 0.9rem; margin-bottom: 0.75rem;">
              {{ mensajeInvitados() }}
            </div>
            <div *ngIf="errorInvitados()" class="alert alert-danger" style="font-size: 0.85rem; padding: 0.6rem 0.9rem; margin-bottom: 0.75rem;">
              {{ errorInvitados() }}
            </div>

            <!-- Formulario para agregar invitado -->
            <div
              *ngIf="mostrarFormularioInvitado()"
              style="background: #fafaf9; border: 1px dashed var(--border); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                <span style="font-size: 0.85rem; font-weight: 600; color: #333333;">Registrar nuevo acompañante</span>
                <span *ngIf="endpointDisponible() === false" class="badge" style="background: #fff7ed; color: #c2410c; font-size: 0.72rem; border: 1px solid #fed7aa;">
                  <app-icon name="info" class="app-icon-inline" style="color: #c2410c;"></app-icon> Backend pendiente en ejecución
                </span>
              </div>

              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; margin-bottom: 0.75rem;">
                <div>
                  <label class="form-label" style="font-size: 0.78rem; margin-bottom: 0.25rem;">Nombre del invitado *</label>
                  <input
                    type="text"
                    class="form-control"
                    placeholder="Ej. Carlos Mendoza"
                    [(ngModel)]="nuevoInvitadoNombre"
                    [disabled]="guardandoInvitado()"
                  />
                </div>
                <div>
                  <label class="form-label" style="font-size: 0.78rem; margin-bottom: 0.25rem;">Correo electrónico (opcional)</label>
                  <input
                    type="email"
                    class="form-control"
                    placeholder="carlos@ejemplo.com"
                    [(ngModel)]="nuevoInvitadoCorreo"
                    [disabled]="guardandoInvitado()"
                  />
                </div>
                <div style="display: flex; align-items: flex-end; padding-bottom: 0.25rem;">
                  <label style="font-size: 0.82rem; display: flex; align-items: center; gap: 0.45rem; cursor: pointer; color: #333333; user-select: none;">
                    <input type="checkbox" [(ngModel)]="nuevoInvitadoVinculado" [disabled]="guardandoInvitado()" />
                    ¿Cuenta registrada en MenuOpt?
                  </label>
                </div>
              </div>

              <div *ngIf="nuevoInvitadoVinculado" style="margin-bottom: 0.75rem;">
                <label class="form-label" style="font-size: 0.78rem; margin-bottom: 0.25rem;">ID de usuario cliente (opcional)</label>
                <input
                  type="number"
                  class="form-control"
                  placeholder="Ej. 3"
                  [(ngModel)]="nuevoInvitadoIdUsuario"
                  [disabled]="guardandoInvitado()"
                  min="1"
                  style="max-width: 180px;"
                />
                <span style="font-size: 0.72rem; color: #737373;">Si se indica un ID, se vinculará a la cuenta de cliente registrada.</span>
              </div>

              <div *ngIf="endpointDisponible() === false" style="font-size: 0.75rem; color: #737373; margin-bottom: 0.85rem; line-height: 1.4;">
                <app-icon name="info" class="app-icon-inline" style="color: #FF6F00;"></app-icon>
                <strong>Nota:</strong> El backend de la rama actual responde 404 para este endpoint. El botón quedará habilitado en cuanto el backend incorpore los cambios de Codex.
              </div>

              <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
                <button type="button" class="btn btn-outline btn-sm" (click)="toggleFormularioInvitado()" [disabled]="guardandoInvitado()">
                  Cancelar
                </button>
                <button
                  type="button"
                  class="btn btn-primary btn-sm"
                  (click)="agregarInvitado()"
                  [disabled]="guardandoInvitado() || (!nuevoInvitadoNombre.trim() && !nuevoInvitadoIdUsuario) || endpointDisponible() === false"
                  [title]="endpointDisponible() === false ? 'Endpoints pendientes en backend (Codex)' : 'Registrar invitado en la reserva'"
                >
                  <app-icon *ngIf="!guardandoInvitado()" name="plus" class="app-icon-inline"></app-icon>
                  <app-icon *ngIf="guardandoInvitado()" name="loader" class="app-icon-inline app-spin"></app-icon>
                  {{ guardandoInvitado() ? 'Guardando...' : 'Guardar invitado' }}
                </button>
              </div>
            </div>

            <!-- Estado de carga de invitados -->
            <div *ngIf="cargandoInvitados()" style="text-align: center; padding: 1rem; color: var(--text-muted); font-size: 0.85rem;">
              <span class="spinner" style="width: 18px; height: 18px;"></span>
              <span style="margin-left: 0.5rem;">Cargando lista de invitados...</span>
            </div>

            <!-- Lista de invitados -->
            <div *ngIf="!cargandoInvitados()" style="display: flex; flex-direction: column; gap: 0.5rem;">
              <div
                *ngFor="let inv of invitados()"
                style="display: flex; justify-content: space-between; align-items: center; padding: 0.7rem 0.9rem; background: #ffffff; border: 1px solid #ededed; border-radius: 8px;"
              >
                <div style="display: flex; align-items: center; gap: 0.75rem; min-width: 0;">
                  <div
                    style="width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;"
                    [style.background]="inv.esTitular ? '#fff2e7' : '#f4f4f5'"
                    [style.color]="inv.esTitular ? '#FF6F00' : '#333333'"
                  >
                    <app-icon [name]="inv.esTitular ? 'star' : 'user-round'" [size]="16"></app-icon>
                  </div>

                  <div style="min-width: 0;">
                    <div style="display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap;">
                      <strong style="color: #333333; font-size: 0.9rem;">{{ inv.nombre }}</strong>
                      <span
                        *ngIf="inv.esTitular"
                        class="badge"
                        style="background: #fff2e7; color: #FF6F00; border: 1px solid #ffe3c8; font-size: 0.7rem; font-weight: 600;"
                      >
                        Titular de la reserva
                      </span>
                    </div>
                    <div style="font-size: 0.78rem; color: #737373; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.15rem;">
                      <span *ngIf="inv.correo">{{ inv.correo }}</span>
                      <span *ngIf="inv.correo">&bull;</span>
                      <span
                        *ngIf="inv.tieneCuenta"
                        style="color: #16845b; display: inline-flex; align-items: center; gap: 0.25rem; font-weight: 500;"
                      >
                        <app-icon name="check" [size]="12"></app-icon>
                        {{ inv.id_usuario ? 'Cuenta vinculada (ID: #' + inv.id_usuario + ')' : 'Cuenta vinculada' }}
                      </span>
                      <span
                        *ngIf="!inv.tieneCuenta"
                        style="color: #737373; display: inline-flex; align-items: center;"
                      >
                        Invitado sin cuenta
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <button
                    *ngIf="!inv.esTitular"
                    type="button"
                    class="btn btn-outline btn-sm"
                    style="padding: 0.25rem 0.55rem; color: #c83b36; border-color: #fecdd3;"
                    (click)="eliminarInvitado(inv)"
                    [disabled]="eliminandoInvitadoId() === inv.id_invitado || endpointDisponible() === false || r.estado === 'CANCELADA' || r.estado === 'FINALIZADA'"
                    [title]="endpointDisponible() === false ? 'Endpoints pendientes en backend (Codex)' : 'Eliminar invitado de la reserva'"
                  >
                    <app-icon *ngIf="eliminandoInvitadoId() !== inv.id_invitado" name="trash" [size]="14"></app-icon>
                    <app-icon *ngIf="eliminandoInvitadoId() === inv.id_invitado" name="loader" [size]="14" class="app-spin"></app-icon>
                  </button>
                  <span
                    *ngIf="inv.esTitular"
                    style="font-size: 0.75rem; color: #a1a1aa; padding: 0.25rem 0.5rem;"
                  >
                    No removible
                  </span>
                </div>
              </div>
            </div>

            <!-- Resumen y aviso de capacidad -->
            <p
              *ngIf="invitados().length < r.cantidad_personas"
              style="margin: 0.75rem 0 0; font-size: 0.8rem; color: var(--text-muted); text-align: left;"
            >
              Capacidad total de la reserva: {{ r.cantidad_personas }} personas. Quedan {{ r.cantidad_personas - invitados().length }} lugares por asignar.
            </p>
            <p
              *ngIf="invitados().length >= r.cantidad_personas"
              style="margin: 0.75rem 0 0; font-size: 0.8rem; color: #16845b; font-weight: 500; text-align: left;"
            >
              <app-icon name="check" class="app-icon-inline" style="color: #16845b;"></app-icon>
              Capacidad completa de la reserva alcanzada ({{ r.cantidad_personas }} de {{ r.cantidad_personas }} lugares asignados).
            </p>
          </div>

          <!-- Observaciones y Contacto -->
          <div style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">DETALLES ADICIONALES</h4>
            <p style="margin: 0 0 0.5rem 0;">
              <strong>Observaciones:</strong> {{ r.observaciones || 'Ninguna observación especificada.' }}
            </p>
            <p *ngIf="r.correo_cliente" style="margin: 0 0 0.25rem 0; font-size: 0.85rem; color: var(--text-muted);">
              <strong>Contacto:</strong> <app-icon name="mail" class="app-icon-inline"></app-icon> {{ r.correo_cliente }} <span *ngIf="r.telefono_cliente">| <app-icon name="phone" class="app-icon-inline"></app-icon> {{ r.telefono_cliente }}</span>
            </p>
            <p style="margin: 0; font-size: 0.8rem; color: var(--text-muted);">
              Registrada el: {{ r.fecha_creacion | date:'dd/MM/yyyy HH:mm' }}
            </p>
          </div>

          <!-- Acciones -->
          <div style="display: flex; justify-content: flex-end; gap: 0.5rem; flex-wrap: wrap;">
            <a
              *ngIf="r.estado === 'CONFIRMADA' || r.estado === 'PENDIENTE'"
              [routerLink]="['/restaurantes', r.id_restaurante, 'pedido']"
              [queryParams]="{ id_reserva: r.id_reserva }"
              class="btn btn-success"
            >
              <app-icon name="utensils" class="app-icon-inline"></app-icon> Ordenar platos para esta reserva
            </a>
            <button
              *ngIf="puedeCancelar(r)"
              class="btn btn-danger"
              (click)="cancelarReserva(r)"
            >
              Cancelar Reserva
            </button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class DetalleReservaComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private reservaService = inject(ReservaService);
  private authService = inject(AuthService);

  reservaId = signal<number>(0);
  reserva = signal<ReservaRespuesta | null>(null);
  cargando = signal<boolean>(false);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  // Gestión de invitados conectada a ReservaService
  invitadosRegistrados = signal<ReservaInvitadoRespuesta[]>([]);
  cargandoInvitados = signal<boolean>(false);
  guardandoInvitado = signal<boolean>(false);
  eliminandoInvitadoId = signal<number | null>(null);
  endpointDisponible = signal<boolean | null>(null);
  mensajeInvitados = signal<string | null>(null);
  errorInvitados = signal<string | null>(null);

  mostrarFormularioInvitado = signal<boolean>(false);
  nuevoInvitadoNombre = '';
  nuevoInvitadoCorreo = '';
  nuevoInvitadoIdUsuario: number | null = null;
  nuevoInvitadoVinculado = false;

  invitados = computed<InvitadoVisual[]>(() => {
    const r = this.reserva();
    if (!r) return [];
    const titular: InvitadoVisual = {
      nombre: r.nombre_cliente || `Cliente #${r.id_usuario}`,
      correo: r.correo_cliente,
      esTitular: true,
      tieneCuenta: true,
      id_usuario: r.id_usuario
    };
    const registrados: InvitadoVisual[] = this.invitadosRegistrados().map(inv => ({
      id_invitado: inv.id_invitado,
      nombre: inv.nombre,
      correo: inv.correo,
      id_usuario: inv.id_usuario,
      esTitular: false,
      tieneCuenta: !!inv.id_usuario
    }));
    return [titular, ...registrados];
  });

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.reservaId.set(Number(idParam));
      this.cargarDetalle();
    }
  }

  cargarDetalle(): void {
    this.cargando.set(true);
    this.reservaService.obtenerReserva(this.reservaId()).subscribe({
      next: (r) => {
        this.reserva.set(r);
        this.cargando.set(false);
        this.cargarInvitados();
      },
      error: (err) => {
        this.cargando.set(false);
        this.error.set(err.error?.detail || 'No se pudo cargar la información de la reserva.');
      }
    });
  }

  cargarInvitados(): void {
    this.cargandoInvitados.set(true);
    this.errorInvitados.set(null);
    this.reservaService.listarInvitados(this.reservaId()).subscribe({
      next: (lista) => {
        this.invitadosRegistrados.set(lista || []);
        this.cargandoInvitados.set(false);
        this.endpointDisponible.set(true);
      },
      error: (err) => {
        this.cargandoInvitados.set(false);
        if (err.status === 404) {
          // El backend activo aún no monta /reservas/:id/invitados (rama codex-funcionalidades)
          this.endpointDisponible.set(false);
        } else if (err.status === 403) {
          this.endpointDisponible.set(true);
          this.errorInvitados.set('No tiene permisos para ver los invitados de esta reserva.');
        } else {
          this.endpointDisponible.set(true);
          this.errorInvitados.set(err.error?.detail || 'No se pudieron cargar los invitados de la reserva.');
        }
      }
    });
  }

  toggleFormularioInvitado(): void {
    this.mostrarFormularioInvitado.update(v => !v);
    this.errorInvitados.set(null);
  }

  agregarInvitado(): void {
    if (this.guardandoInvitado()) return;

    if (this.endpointDisponible() === false) {
      this.errorInvitados.set('La API backend para persistir invitados aún no está disponible en este entorno (pendiente integrar cambios de Codex).');
      return;
    }

    const nombreLimpio = this.nuevoInvitadoNombre.trim();
    const correoLimpio = this.nuevoInvitadoCorreo.trim() || undefined;
    const idUsuarioVal = this.nuevoInvitadoVinculado && this.nuevoInvitadoIdUsuario ? Number(this.nuevoInvitadoIdUsuario) : undefined;

    if (!nombreLimpio && !idUsuarioVal) {
      this.errorInvitados.set('Debe ingresar el nombre del invitado o indicar su ID de usuario.');
      return;
    }

    const r = this.reserva();
    if (r && this.invitados().length >= r.cantidad_personas) {
      this.errorInvitados.set(`La reserva ya alcanzó la capacidad máxima permitida (${r.cantidad_personas} personas).`);
      return;
    }

    if (idUsuarioVal && r && idUsuarioVal === r.id_usuario) {
      this.errorInvitados.set('El titular ya forma parte de la reserva.');
      return;
    }

    // Comprobación de duplicados en lista actual
    if (nombreLimpio && this.invitadosRegistrados().some(i => i.nombre.trim().toLowerCase() === nombreLimpio.toLowerCase())) {
      this.errorInvitados.set(`Ya existe un invitado registrado con el nombre "${nombreLimpio}".`);
      return;
    }
    if (correoLimpio && this.invitadosRegistrados().some(i => i.correo && i.correo.toLowerCase() === correoLimpio.toLowerCase())) {
      this.errorInvitados.set(`Ya existe un invitado registrado con el correo "${correoLimpio}".`);
      return;
    }

    const payload: ReservaInvitadoCrear = {};
    if (idUsuarioVal) payload.id_usuario = idUsuarioVal;
    if (nombreLimpio) payload.nombre = nombreLimpio;
    if (correoLimpio) payload.correo = correoLimpio;

    this.guardandoInvitado.set(true);
    this.errorInvitados.set(null);
    this.mensajeInvitados.set(null);

    this.reservaService.agregarInvitado(this.reservaId(), payload).subscribe({
      next: (invitadoCreado) => {
        this.invitadosRegistrados.update(prev => [...prev, invitadoCreado]);
        this.nuevoInvitadoNombre = '';
        this.nuevoInvitadoCorreo = '';
        this.nuevoInvitadoIdUsuario = null;
        this.nuevoInvitadoVinculado = false;
        this.mostrarFormularioInvitado.set(false);
        this.guardandoInvitado.set(false);
        this.endpointDisponible.set(true);
        this.mensajeInvitados.set(`Invitado "${invitadoCreado.nombre}" agregado exitosamente.`);
        setTimeout(() => this.mensajeInvitados.set(null), 4000);
      },
      error: (err) => {
        this.guardandoInvitado.set(false);
        if (err.status === 400) {
          this.errorInvitados.set(err.error?.detail || 'Datos de invitado inválidos.');
        } else if (err.status === 403) {
          this.errorInvitados.set(err.error?.detail || 'No tiene permisos para agregar invitados a esta reserva.');
        } else if (err.status === 409) {
          this.errorInvitados.set(err.error?.detail || 'Conflicto: Capacidad máxima alcanzada o invitado duplicado.');
        } else if (err.status === 422) {
          const detail = err.error?.detail;
          const msg = Array.isArray(detail) ? detail.map((d: any) => d.msg).join(', ') : detail;
          this.errorInvitados.set(msg || 'Error de validación en los datos del invitado.');
        } else if (err.status === 404 && this.endpointDisponible() === false) {
          this.errorInvitados.set('El servicio backend aún no está disponible en esta rama (pendiente integrar cambios de Codex).');
        } else {
          this.errorInvitados.set(err.error?.detail || 'Error al agregar el invitado a la reserva.');
        }
      }
    });
  }

  eliminarInvitado(inv: InvitadoVisual): void {
    if (inv.esTitular || !inv.id_invitado) return;
    if (this.eliminandoInvitadoId() !== null) return;

    if (this.endpointDisponible() === false) {
      this.errorInvitados.set('La API backend para eliminar invitados aún no está disponible en este entorno (pendiente integrar cambios de Codex).');
      return;
    }

    if (!confirm(`¿Está seguro de eliminar a "${inv.nombre}" de la reserva?`)) {
      return;
    }

    const idInv = inv.id_invitado;
    this.eliminandoInvitadoId.set(idInv);
    this.errorInvitados.set(null);
    this.mensajeInvitados.set(null);

    this.reservaService.eliminarInvitado(this.reservaId(), idInv).subscribe({
      next: () => {
        this.invitadosRegistrados.update(prev => prev.filter(i => i.id_invitado !== idInv));
        this.eliminandoInvitadoId.set(null);
        this.endpointDisponible.set(true);
        this.mensajeInvitados.set(`Invitado "${inv.nombre}" eliminado exitosamente.`);
        setTimeout(() => this.mensajeInvitados.set(null), 4000);
      },
      error: (err) => {
        this.eliminandoInvitadoId.set(null);
        if (err.status === 403) {
          this.errorInvitados.set(err.error?.detail || 'No tiene permisos para eliminar invitados de esta reserva.');
        } else if (err.status === 404) {
          this.errorInvitados.set(err.error?.detail || 'El invitado no fue encontrado en esta reserva.');
        } else if (err.status === 409) {
          this.errorInvitados.set(err.error?.detail || 'No se puede eliminar un invitado con pedidos asociados a esta reserva.');
        } else {
          this.errorInvitados.set(err.error?.detail || 'Error al eliminar el invitado de la reserva.');
        }
      }
    });
  }

  puedeCancelar(r: ReservaRespuesta): boolean {
    const rol = this.authService.userRole();
    const userId = this.authService.currentUser()?.id_usuario;
    const esTitular = r.id_usuario === userId;
    return (esTitular || rol === 'ADMINISTRADOR') && (r.estado === 'CONFIRMADA' || r.estado === 'PENDIENTE');
  }

  cancelarReserva(r: ReservaRespuesta): void {
    if (!confirm(`¿Está seguro de cancelar la reserva #${r.id_reserva}?`)) {
      return;
    }

    this.reservaService.cancelarReserva(r.id_reserva).subscribe({
      next: (act) => {
        this.reserva.set(act);
        this.mensaje.set('Reserva cancelada exitosamente.');
        setTimeout(() => this.mensaje.set(null), 4000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al cancelar la reserva.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }

  volver(): void {
    const rol = this.authService.userRole();
    if (rol === 'RESTAURANTE') {
      const restoId = this.reserva()?.id_restaurante;
      if (restoId) {
        this.router.navigate(['/restaurantes', restoId, 'reservas']);
        return;
      }
    }
    this.router.navigate(['/mis-reservas']);
  }
}

