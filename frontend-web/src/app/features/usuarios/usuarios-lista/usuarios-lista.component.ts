import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UsuarioService } from '../../../core/services/usuario.service';
import { Usuario, UsuariosPaginados } from '../../../core/models/usuario.model';

// =========================================================================
// CASO DE USO: CU04 - GESTIONAR USUARIOS (Solo ADMINISTRADOR)
// Vista para listar usuarios paginados, consultar detalles y activar/desactivar.
// =========================================================================
@Component({
  selector: 'app-usuarios-lista',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div>
      <div class="card-header" style="border: none; padding: 0;">
        <div>
          <h2>Gestión de Usuarios</h2>
          <p style="color: var(--text-muted);">Administra las cuentas de usuario y controla su estado en el sistema.</p>
        </div>
      </div>

      <div *ngIf="mensaje()" class="alert alert-success">{{ mensaje() }}</div>
      <div *ngIf="error()" class="alert alert-danger">{{ error() }}</div>

      <!-- Filtros -->
      <div class="card" style="padding: 1rem; margin-bottom: 1rem;">
        <div class="grid-3" style="align-items: flex-end;">
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label">Buscar por nombre o correo</label>
            <input type="text" class="form-control" [(ngModel)]="filtroBusqueda" (keyup.enter)="aplicarFiltros()" placeholder="Escribe y presiona Enter..." />
          </div>
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label">Filtrar por Rol</label>
            <select class="form-control" [(ngModel)]="filtroRol" (change)="aplicarFiltros()">
              <option value="">Todos los roles</option>
              <option value="CLIENTE">CLIENTE</option>
              <option value="RESTAURANTE">RESTAURANTE</option>
              <option value="ADMINISTRADOR">ADMINISTRADOR</option>
            </select>
          </div>
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label">Filtrar por Estado</label>
            <select class="form-control" [(ngModel)]="filtroEstado" (change)="aplicarFiltros()">
              <option value="">Todos los estados</option>
              <option value="ACTIVO">ACTIVO</option>
              <option value="INACTIVO">INACTIVO</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Tabla de Usuarios -->
      <div class="card" style="padding: 0;">
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre Completo</th>
                <th>Correo</th>
                <th>Teléfono</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Registro</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let u of datos()?.usuarios">
                <td>#{{ u.id_usuario }}</td>
                <td style="font-weight: 500;">{{ u.nombres }} {{ u.apellidos }}</td>
                <td>{{ u.correo }}</td>
                <td>{{ u.telefono || '—' }}</td>
                <td>
                  <span class="badge" [ngClass]="getRoleBadge(u.rol?.nombre)">{{ u.rol?.nombre }}</span>
                </td>
                <td>
                  <span class="badge" [ngClass]="u.estado === 'ACTIVO' ? 'badge-success' : 'badge-danger'">{{ u.estado }}</span>
                </td>
                <td style="font-size: 0.8rem; color: var(--text-muted);">{{ u.fecha_registro | date:'short' }}</td>
                <td>
                  <div class="d-flex gap-2">
                    <button class="btn btn-outline btn-sm" (click)="verDetalle(u)">Detalles</button>
                    <button
                      class="btn btn-sm"
                      [ngClass]="u.estado === 'ACTIVO' ? 'btn-danger' : 'btn-primary'"
                      (click)="toggleEstado(u)"
                    >
                      {{ u.estado === 'ACTIVO' ? 'Desactivar' : 'Activar' }}
                    </button>
                  </div>
                </td>
              </tr>
              <tr *ngIf="datos()?.usuarios?.length === 0">
                <td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                  No se encontraron usuarios con los filtros aplicados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Paginador -->
        <div class="card-header" style="border: none; border-top: 1px solid var(--border); margin: 0; padding: 1rem;">
          <span style="font-size: 0.875rem; color: var(--text-muted);">
            Página {{ paginaActual }} de {{ datos()?.total_paginas || 1 }} (Total: {{ datos()?.total || 0 }})
          </span>
          <div class="d-flex gap-2">
            <button class="btn btn-outline btn-sm" [disabled]="paginaActual <= 1" (click)="cambiarPagina(paginaActual - 1)">Anterior</button>
            <button class="btn btn-outline btn-sm" [disabled]="paginaActual >= (datos()?.total_paginas || 1)" (click)="cambiarPagina(paginaActual + 1)">Siguiente</button>
          </div>
        </div>
      </div>

      <!-- Modal de Detalle de Usuario -->
      <div *ngIf="usuarioSeleccionado()" class="modal-backdrop" (click)="cerrarModal()">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <div class="card-header">
            <h3>Detalle de Usuario</h3>
            <button class="btn btn-outline btn-sm" (click)="cerrarModal()">✕</button>
          </div>
          <div *ngIf="usuarioSeleccionado() as u" class="grid-2" style="gap: 1rem;">
            <div>
              <span class="label-meta">ID</span>
              <p>#{{ u.id_usuario }}</p>
            </div>
            <div>
              <span class="label-meta">Estado</span>
              <p><span class="badge" [ngClass]="u.estado === 'ACTIVO' ? 'badge-success' : 'badge-danger'">{{ u.estado }}</span></p>
            </div>
            <div>
              <span class="label-meta">Nombres</span>
              <p>{{ u.nombres }}</p>
            </div>
            <div>
              <span class="label-meta">Apellidos</span>
              <p>{{ u.apellidos }}</p>
            </div>
            <div>
              <span class="label-meta">Correo</span>
              <p>{{ u.correo }}</p>
            </div>
            <div>
              <span class="label-meta">Teléfono</span>
              <p>{{ u.telefono || 'No registrado' }}</p>
            </div>
            <div>
              <span class="label-meta">Rol</span>
              <p>{{ u.rol?.nombre }} - {{ u.rol?.descripcion }}</p>
            </div>
            <div>
              <span class="label-meta">Fecha de Registro</span>
              <p>{{ u.fecha_registro | date:'medium' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .label-meta {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
    }
    .modal-backdrop {
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.5);
      display: flex; align-items: center; justify-content: center;
      z-index: 1000;
    }
    .modal-content {
      background: var(--surface);
      border-radius: var(--radius);
      padding: 1.5rem;
      max-width: 500px;
      width: 90%;
      box-shadow: var(--shadow-lg);
    }
  `]
})
export class UsuariosListaComponent implements OnInit {
  private usuarioService = inject(UsuarioService);

  datos = signal<UsuariosPaginados | null>(null);
  usuarioSeleccionado = signal<Usuario | null>(null);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  filtroBusqueda = '';
  filtroRol = '';
  filtroEstado = '';
  paginaActual = 1;

  ngOnInit(): void {
    this.cargarUsuarios();
  }

  // --- LÓGICA CU04: Listar usuarios paginados mediante GET /usuarios ---
  cargarUsuarios(): void {
    this.usuarioService.getUsuarios(
      this.paginaActual,
      10,
      this.filtroEstado || undefined,
      this.filtroRol || undefined,
      this.filtroBusqueda || undefined
    ).subscribe({
      next: (res) => this.datos.set(res),
      error: () => this.error.set('Error al cargar la lista de usuarios.')
    });
  }

  aplicarFiltros(): void {
    this.paginaActual = 1;
    this.cargarUsuarios();
  }

  cambiarPagina(pag: number): void {
    this.paginaActual = pag;
    this.cargarUsuarios();
  }

  // --- LÓGICA CU04: Consultar Detalle con GET /usuarios/{id} ---
  verDetalle(usuario: Usuario): void {
    this.usuarioService.getUsuarioById(usuario.id_usuario).subscribe({
      next: (u) => this.usuarioSeleccionado.set(u),
      error: () => this.error.set('No se pudo cargar el detalle del usuario.')
    });
  }

  cerrarModal(): void {
    this.usuarioSeleccionado.set(null);
  }

  // --- LÓGICA CU04: Cambiar Estado Lógico mediante PATCH /usuarios/{id}/estado ---
  toggleEstado(usuario: Usuario): void {
    const nuevoEstado = usuario.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    const accion = nuevoEstado === 'ACTIVO' ? 'activar' : 'desactivar';

    if (!confirm(`¿Está seguro de que desea ${accion} al usuario ${usuario.nombres} ${usuario.apellidos}?`)) {
      return;
    }

    this.usuarioService.cambiarEstado(usuario.id_usuario, nuevoEstado).subscribe({
      next: (u) => {
        this.mensaje.set(`Usuario ${u.nombres} ${u.apellidos} ${nuevoEstado === 'ACTIVO' ? 'activado' : 'desactivado'} con éxito.`);
        this.cargarUsuarios();
        setTimeout(() => this.mensaje.set(null), 3000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'No se pudo cambiar el estado del usuario.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }

  getRoleBadge(role?: string): string {
    switch (role) {
      case 'ADMINISTRADOR': return 'badge-danger';
      case 'RESTAURANTE': return 'badge-warning';
      default: return 'badge-secondary';
    }
  }
}
