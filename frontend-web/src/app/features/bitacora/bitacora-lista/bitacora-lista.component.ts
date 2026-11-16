import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
import { BitacoraService } from '../../../core/services/bitacora.service';
import { BitacoraListadoPaginado, BitacoraRegistro } from '../../../core/models/bitacora.model';

// =========================================================================
// CASO DE USO: CU25 - CONSULTAR BITÁCORA DEL SISTEMA (Solo ADMINISTRADOR)
// Vista para auditoría de eventos de dominio con filtros, búsqueda y paginación.
// =========================================================================
@Component({
  selector: 'app-bitacora-lista',
  standalone: true,
  imports: [AppIconComponent, CommonModule, FormsModule],
  template: `
    <div>
      <div class="card-header" style="border: none; padding: 0; margin-bottom: 1.5rem;">
        <div>
          <h2><app-icon name="shield" class="app-icon-inline"></app-icon> Bitácora y Auditoría del Sistema</h2>
          <p style="color: var(--text-muted);">
            Registro auditable de eventos de dominio: inicios de sesión, cambios de estado, transacciones y seguridad.
          </p>
        </div>
      </div>

      <div *ngIf="error()" class="alert alert-danger">{{ error() }}</div>

      <!-- Filtros de Auditoría -->
      <div class="card" style="padding: 1.25rem; margin-bottom: 1.5rem; background: #f8fafc; border: 1px solid var(--border);">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; align-items: flex-end;">
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 600;">Buscar en descripción o acción</label>
            <input
              type="text"
              class="form-control"
              [(ngModel)]="filtroBusqueda"
              (keyup.enter)="aplicarFiltros()"
              placeholder="Ej. login, cancelación, reserva..."
            />
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 600;">Módulo</label>
            <select class="form-control" [(ngModel)]="filtroModulo" (change)="aplicarFiltros()">
              <option value="">Todos los módulos</option>
              <option value="AUTENTICACION">AUTENTICACIÓN</option>
              <option value="RESERVAS">RESERVAS</option>
              <option value="PEDIDOS">PEDIDOS</option>
              <option value="USUARIOS">USUARIOS</option>
              <option value="RESTAURANTES">RESTAURANTES</option>
            </select>
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 600;">Desde (Fecha)</label>
            <input type="date" class="form-control" [(ngModel)]="filtroFechaDesde" (change)="aplicarFiltros()" />
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 600;">Hasta (Fecha)</label>
            <input type="date" class="form-control" [(ngModel)]="filtroFechaHasta" (change)="aplicarFiltros()" />
          </div>

          <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-primary" (click)="aplicarFiltros()" style="flex: 1;">
              <app-icon name="search" class="app-icon-inline"></app-icon> Filtrar
            </button>
            <button class="btn btn-outline" (click)="limpiarFiltros()" title="Restablecer">
              Limpiar
            </button>
          </div>
        </div>
      </div>

      <!-- Resumen estadístico simple -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <span style="font-size: 0.9rem; color: var(--text-muted);">
          Total de registros encontrados: <strong>{{ datos()?.total || 0 }}</strong>
        </span>
        <span *ngIf="cargando()" style="font-size: 0.9rem; color: var(--primary);">
          Cargando eventos...
        </span>
      </div>

      <!-- Tabla de Bitácora -->
      <div class="card" style="padding: 0; overflow: hidden;">
        <div class="table-responsive">
          <table class="table" style="margin-bottom: 0;">
            <thead>
              <tr>
                <th style="width: 70px;">ID</th>
                <th style="width: 170px;">Fecha y Hora</th>
                <th style="width: 130px;">Módulo</th>
                <th style="width: 180px;">Acción</th>
                <th>Descripción del Evento</th>
                <th style="width: 200px;">Usuario Causante</th>
                <th style="width: 90px; text-align: center;">Detalle</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let reg of datos()?.items">
                <td><small style="color: var(--text-muted);">#{{ reg.id_bitacora }}</small></td>
                <td style="font-size: 0.85rem; white-space: nowrap;">
                  {{ formatearFecha(reg.fecha_hora) }}
                </td>
                <td>
                  <span class="badge" [ngClass]="getModuloBadge(reg.modulo)">
                    {{ reg.modulo }}
                  </span>
                </td>
                <td>
                  <code style="font-size: 0.8rem; font-weight: 600;">{{ reg.accion }}</code>
                </td>
                <td style="font-size: 0.9rem;">
                  {{ reg.descripcion }}
                </td>
                <td style="font-size: 0.85rem;">
                  <ng-container *ngIf="reg.correo_usuario; else anonimo">
                    <div style="font-weight: 500;">{{ reg.nombre_usuario || 'Usuario' }}</div>
                    <small style="color: var(--text-muted);">{{ reg.correo_usuario }}</small>
                  </ng-container>
                  <ng-template #anonimo>
                    <span style="color: var(--text-muted); font-style: italic;">Sistema / Anónimo</span>
                  </ng-template>
                </td>
                <td style="text-align: center;">
                  <button
                    *ngIf="reg.detalles"
                    class="btn btn-sm btn-outline"
                    (click)="abrirModal(reg)"
                    style="padding: 0.2rem 0.5rem; font-size: 0.75rem;"
                    title="Ver metadatos JSON"
                  >
                    JSON
                  </button>
                  <span *ngIf="!reg.detalles" style="color: var(--text-muted);">&mdash;</span>
                </td>
              </tr>

              <tr *ngIf="!cargando() && (!datos()?.items || datos()?.items?.length === 0)">
                <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                  <app-icon name="info" style="font-size: 2rem; display: block; margin-bottom: 0.5rem;"></app-icon>
                  No se encontraron registros de auditoría para los filtros seleccionados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Paginación -->
        <div
          *ngIf="datos() && datos()!.total_paginas > 1"
          style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1.25rem; border-top: 1px solid var(--border); background: #fafafa;"
        >
          <span style="font-size: 0.85rem; color: var(--text-muted);">
            Página {{ datos()?.pagina }} de {{ datos()?.total_paginas }}
          </span>
          <div style="display: flex; gap: 0.5rem;">
            <button
              class="btn btn-sm btn-outline"
              [disabled]="datos()?.pagina === 1"
              (click)="cambiarPagina((datos()?.pagina || 1) - 1)"
            >
              &larr; Anterior
            </button>
            <button
              class="btn btn-sm btn-outline"
              [disabled]="datos()?.pagina === datos()?.total_paginas"
              (click)="cambiarPagina((datos()?.pagina || 1) + 1)"
            >
              Siguiente &rarr;
            </button>
          </div>
        </div>
      </div>

      <!-- Modal de Detalle JSON -->
      <div
        *ngIf="modalActivo()"
        style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1050; padding: 1rem;"
      >
        <div class="card" style="width: 100%; max-width: 550px; max-height: 85vh; overflow-y: auto; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">
            <h3 style="margin: 0; font-size: 1.15rem;">
              Metadatos del Evento #{{ registroSeleccionado()?.id_bitacora }}
            </h3>
            <button class="btn btn-sm btn-outline" (click)="cerrarModal()" style="padding: 0.2rem 0.5rem;">&times;</button>
          </div>

          <div style="margin-bottom: 1rem;">
            <p style="margin: 0 0 0.25rem; font-size: 0.85rem; color: var(--text-muted);">Acción: <strong>{{ registroSeleccionado()?.accion }}</strong></p>
            <p style="margin: 0 0 0.5rem; font-size: 0.85rem; color: var(--text-muted);">Descripción: {{ registroSeleccionado()?.descripcion }}</p>
            <pre style="background: #1e293b; color: #f8fafc; padding: 1rem; border-radius: var(--radius); font-size: 0.8rem; overflow-x: auto;">{{ registroSeleccionado()?.detalles | json }}</pre>
          </div>

          <div style="text-align: right;">
            <button class="btn btn-secondary btn-sm" (click)="cerrarModal()">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class BitacoraListaComponent implements OnInit {
  private bitacoraService = inject(BitacoraService);

  cargando = signal<boolean>(false);
  error = signal<string | null>(null);
  datos = signal<BitacoraListadoPaginado | null>(null);

  filtroBusqueda = '';
  filtroModulo = '';
  filtroFechaDesde = '';
  filtroFechaHasta = '';
  paginaActual = 1;
  limite = 20;

  modalActivo = signal<boolean>(false);
  registroSeleccionado = signal<BitacoraRegistro | null>(null);

  ngOnInit(): void {
    this.cargarBitacora();
  }

  cargarBitacora(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.bitacoraService.getBitacora(
      this.paginaActual,
      this.limite,
      this.filtroModulo,
      undefined,
      this.filtroFechaDesde,
      this.filtroFechaHasta,
      this.filtroBusqueda
    ).subscribe({
      next: (resp) => {
        this.datos.set(resp);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err?.error?.detail || 'Error al consultar la bitácora del sistema.');
        this.cargando.set(false);
      }
    });
  }

  aplicarFiltros(): void {
    this.paginaActual = 1;
    this.cargarBitacora();
  }

  limpiarFiltros(): void {
    this.filtroBusqueda = '';
    this.filtroModulo = '';
    this.filtroFechaDesde = '';
    this.filtroFechaHasta = '';
    this.paginaActual = 1;
    this.cargarBitacora();
  }

  cambiarPagina(nuevaPagina: number): void {
    this.paginaActual = nuevaPagina;
    this.cargarBitacora();
  }

  abrirModal(reg: BitacoraRegistro): void {
    this.registroSeleccionado.set(reg);
    this.modalActivo.set(true);
  }

  cerrarModal(): void {
    this.modalActivo.set(false);
    this.registroSeleccionado.set(null);
  }

  formatearFecha(isoStr: string): string {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return isoStr;
    }
  }

  getModuloBadge(modulo: string): string {
    switch (modulo?.toUpperCase()) {
      case 'AUTENTICACION':
        return 'badge-primary';
      case 'RESERVAS':
        return 'badge-success';
      case 'PEDIDOS':
        return 'badge-warning';
      case 'USUARIOS':
        return 'badge-secondary';
      default:
        return 'badge-info';
    }
  }
}
