import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { RestauranteService } from '../../../core/services/restaurante.service';
import { AuthService } from '../../../core/services/auth.service';
import { Restaurante } from '../../../core/models/restaurante.model';

// =========================================================================
// CASO DE USO: CU06 - GESTIONAR RESTAURANTE
// Vista para listar restaurantes del usuario autenticado y controlar su estado.
// =========================================================================
@Component({
  selector: 'app-restaurantes-lista',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterLink],
  template: `
    <div>
      <div class="card-header" style="border: none; padding: 0; margin-bottom: 1.5rem;">
        <div>
          <h2>{{ esAdmin() ? 'Todos los Restaurantes' : 'Mis Restaurantes' }}</h2>
          <p style="color: var(--text-muted);">
            {{ esAdmin() ? 'Supervisa los restaurantes registrados en la plataforma.' : 'Administra la información comercial y la carta de tus establecimientos.' }}
          </p>
        </div>
        <a routerLink="/restaurantes/nuevo" class="btn btn-primary">
          <span><app-icon name="plus" class="app-icon-inline"></app-icon></span> Registrar Restaurante
        </a>
      </div>

      <div *ngIf="mensaje()" class="alert alert-success">{{ mensaje() }}</div>
      <div *ngIf="error()" class="alert alert-danger">{{ error() }}</div>

      <!-- Grid de Restaurantes -->
      <div class="grid-2" *ngIf="restaurantes()?.length">
        <div class="card" *ngFor="let r of restaurantes()">
          <div class="card-header">
            <div>
              <h3>{{ r.nombre }}</h3>
              <span style="font-size: 0.8rem; color: var(--text-muted);">NIT: {{ r.nit || 'Sin NIT' }}</span>
            </div>
            <span class="badge" [ngClass]="r.estado === 'ACTIVO' ? 'badge-success' : 'badge-danger'">{{ r.estado }}</span>
          </div>

          <p style="color: var(--text-main); margin-bottom: 1rem; font-size: 0.9rem;">
            {{ r.descripcion || 'Sin descripción disponible.' }}
          </p>

          <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.25rem;">
            <p><app-icon name="pin" class="app-icon-inline"></app-icon> <strong>Ubicación:</strong> {{ r.ubicacion?.direccion }}, {{ r.ubicacion?.ciudad }} (Zona {{ r.ubicacion?.zona || 'Central' }})</p>
            <p><app-icon name="phone" class="app-icon-inline"></app-icon> <strong>Contacto:</strong> {{ r.telefono || 'No registrado' }} | <app-icon name="mail" class="app-icon-inline"></app-icon> {{ r.correo || 'No registrado' }}</p>
            <p><app-icon name="clock" class="app-icon-inline"></app-icon> <strong>Horario:</strong> {{ r.horario_apertura || '08:00' }} - {{ r.horario_cierre || '22:00' }}</p>
          </div>

          <div class="d-flex justify-between" style="border-top: 1px solid var(--border); padding-top: 1rem; flex-wrap: wrap; gap: 0.5rem;">
            <div class="d-flex gap-2" style="flex-wrap: wrap;">
              <a [routerLink]="['/restaurantes', r.id_restaurante, 'reservar']" class="btn btn-primary btn-sm" title="Reservar mesa en este restaurante (CU20, CU21)">
                <span><app-icon name="calendar" class="app-icon-inline"></app-icon></span> Reservar
              </a>
              <a [routerLink]="['/restaurantes', r.id_restaurante, 'pedido']" class="btn btn-success btn-sm" title="Enviar pedido gastronómico (CU23)">
                <span><app-icon name="cart" class="app-icon-inline"></app-icon></span> Pedir
              </a>
              <a [routerLink]="['/restaurantes', r.id_restaurante, 'platos']" class="btn btn-outline btn-sm">
                <span><app-icon name="list" class="app-icon-inline"></app-icon></span> Carta
              </a>
              <a [routerLink]="['/restaurantes', r.id_restaurante, 'distribucion']" class="btn btn-secondary btn-sm" title="Plano 2D y distribución de mesas (CU17, CU18, CU19)">
                <span><app-icon name="map" class="app-icon-inline"></app-icon></span> Plano 2D
              </a>
              <a [routerLink]="['/restaurantes', r.id_restaurante, 'reservas']" class="btn btn-outline btn-sm" title="Gestionar reservas recibidas (CU22)">
                <span><app-icon name="list" class="app-icon-inline"></app-icon></span> Reservas
              </a>
              <a [routerLink]="['/restaurantes', r.id_restaurante, 'pedidos']" class="btn btn-outline btn-sm" title="Gestionar pedidos y comandas (CU24)">
                <span><app-icon name="chef" class="app-icon-inline"></app-icon></span> Comandas
              </a>
            </div>
            <div class="d-flex gap-2">
              <a [routerLink]="['/restaurantes', r.id_restaurante, 'editar']" class="btn btn-outline btn-sm">Editar</a>
              <button
                class="btn btn-sm"
                [ngClass]="r.estado === 'ACTIVO' ? 'btn-danger' : 'btn-secondary'"
                (click)="toggleEstado(r)"
              >
                {{ r.estado === 'ACTIVO' ? 'Desactivar' : 'Activar' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Estado vacío -->
      <div class="card" *ngIf="restaurantes()?.length === 0" style="text-align: center; padding: 3rem;">
        <span style="font-size: 3rem; display: block; margin-bottom: 1rem;"><app-icon name="store" class="app-icon-inline"></app-icon></span>
        <h3>No tienes restaurantes registrados</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Comienza registrando tu primer establecimiento gastronómico.</p>
        <a routerLink="/restaurantes/nuevo" class="btn btn-primary">Registrar Ahora</a>
      </div>
    </div>
  `
})
export class RestaurantesListaComponent implements OnInit {
  private restauranteService = inject(RestauranteService);
  private authService = inject(AuthService);

  restaurantes = signal<Restaurante[] | null>(null);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  esAdmin = () => this.authService.userRole() === 'ADMINISTRADOR';

  ngOnInit(): void {
    this.cargarRestaurantes();
  }

  // --- LÓGICA CU06: Consultar Mis Restaurantes mediante GET /restaurantes/mis-restaurantes ---
  cargarRestaurantes(): void {
    this.restauranteService.getMisRestaurantes().subscribe({
      next: (data) => this.restaurantes.set(data),
      error: () => this.error.set('No se pudieron cargar los restaurantes.')
    });
  }

  // --- LÓGICA CU06: Cambiar Estado Lógico mediante PATCH /restaurantes/{id}/estado ---
  toggleEstado(restaurante: Restaurante): void {
    const nuevoEstado = restaurante.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    const accion = nuevoEstado === 'ACTIVO' ? 'activar' : 'desactivar';

    if (!confirm(`¿Está seguro de que desea ${accion} el restaurante '${restaurante.nombre}'?`)) {
      return;
    }

    this.restauranteService.cambiarEstado(restaurante.id_restaurante, nuevoEstado).subscribe({
      next: (actualizado) => {
        this.mensaje.set(`Restaurante '${actualizado.nombre}' ${nuevoEstado === 'ACTIVO' ? 'activado' : 'desactivado'} con éxito.`);
        this.cargarRestaurantes();
        setTimeout(() => this.mensaje.set(null), 3000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al cambiar el estado del restaurante.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }
}
