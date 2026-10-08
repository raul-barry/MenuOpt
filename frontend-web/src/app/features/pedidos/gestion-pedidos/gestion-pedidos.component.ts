import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU24 - Gestionar pedidos del restaurante
import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { PedidoService } from '../../../core/services/pedido.service';
import { RestauranteService } from '../../../core/services/restaurante.service';
import { PedidoRespuesta, EstadoPedido } from '../../../core/models/pedido.model';
import { Restaurante } from '../../../core/models/restaurante.model';

@Component({
  selector: 'app-gestion-pedidos',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule],
  template: `
    <div class="card" style="max-width: 1100px; margin: 0 auto;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;"><app-icon name="chef" class="app-icon-inline"></app-icon> Gestión de Pedidos - {{ restaurante()?.nombre || 'Restaurante' }}</h2>
          <p style="margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.85rem;">
            Control de comanda, avance de preparación y despacho de órdenes.
          </p>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <a [routerLink]="['/restaurantes', restauranteId(), 'reservas']" class="btn btn-outline btn-sm">
            <app-icon name="calendar" class="app-icon-inline"></app-icon> Ver Reservas
          </a>
          <button class="btn btn-outline btn-sm" (click)="cargarPedidos()">
            <app-icon name="refresh" class="app-icon-inline"></app-icon> Actualizar
          </button>
        </div>
      </div>

      <div class="card-body">
        <!-- Filtros de Consulta -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; background: #f8fafc; border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; margin-bottom: 1.5rem;">
          <div>
            <label class="form-label" style="font-size: 0.8rem;">Filtrar por Estado</label>
            <select class="form-control" [(ngModel)]="filtroEstado" (change)="cargarPedidos()">
              <option value="">Todos los estados</option>
              <option value="PENDIENTE">PENDIENTE</option>
              <option value="ACEPTADO">ACEPTADO</option>
              <option value="EN_PREPARACION">EN PREPARACIÓN</option>
              <option value="LISTO">LISTO</option>
              <option value="ENTREGADO">ENTREGADO</option>
              <option value="CANCELADO">CANCELADO</option>
            </select>
          </div>

          <div>
            <label class="form-label" style="font-size: 0.8rem;">Filtrar por Fecha</label>
            <input type="date" class="form-control" [(ngModel)]="filtroFecha" (change)="cargarPedidos()" />
          </div>

          <div style="display: flex; align-items: flex-end;">
            <button class="btn btn-outline btn-sm" (click)="limpiarFiltros()" style="width: 100%;">
              Limpiar Filtros
            </button>
          </div>
        </div>

        <div *ngIf="cargando()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando pedidos del establecimiento...</p>
        </div>

        <div *ngIf="mensaje()" class="alert alert-success" style="margin-bottom: 1rem;">
          {{ mensaje() }}
        </div>
        <div *ngIf="error()" class="alert alert-danger" style="margin-bottom: 1rem;">
          {{ error() }}
        </div>

        <div *ngIf="!cargando() && pedidos().length === 0" style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <span style="font-size: 3rem; display: block; margin-bottom: 0.75rem;"><app-icon name="list" class="app-icon-inline"></app-icon></span>
          <h3 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; color: inherit;">No hay pedidos registrados</h3>
          <p style="margin: 0; font-size: 0.9rem;">No se encontraron pedidos con los filtros seleccionados.</p>
        </div>

        <!-- Tabla / Lista de Comandas -->
        <div *ngIf="!cargando() && pedidos().length > 0" style="display: flex; flex-direction: column; gap: 1rem;">
          <div
            *ngFor="let p of pedidos()"
            style="border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; background: var(--surface); display: flex; flex-direction: column; gap: 0.75rem;"
          >
            <!-- Cabecera de Comanda -->
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <h3 style="margin: 0; font-size: 1.15rem; color: var(--primary);">
                    Pedido #{{ p.id_pedido }}
                  </h3>
                  <span
                    class="badge"
                    [class.badge-warning]="p.estado === 'PENDIENTE'"
                    [class.badge-info]="p.estado === 'ACEPTADO' || p.estado === 'EN_PREPARACION'"
                    [class.badge-success]="p.estado === 'LISTO' || p.estado === 'ENTREGADO'"
                    [class.badge-danger]="p.estado === 'CANCELADO'"
                  >
                    {{ p.estado }}
                  </span>
                </div>
                <p style="margin: 0.25rem 0 0; font-size: 0.9rem;">
                  <app-icon name="user" class="app-icon-inline"></app-icon> <strong>{{ p.nombre_cliente || 'Cliente #' + p.id_usuario }}</strong>
                  <span *ngIf="p.telefono_cliente"> &bull; <app-icon name="phone" class="app-icon-inline"></app-icon> {{ p.telefono_cliente }}</span>
                </p>
                <p style="margin: 0.15rem 0 0; color: var(--text-muted); font-size: 0.85rem;">
                  <app-icon name="clock" class="app-icon-inline"></app-icon> Solicitado: {{ p.fecha_pedido | date:'dd/MM/yyyy HH:mm' }}
                  <span *ngIf="p.id_reserva" style="color: #0284c7; font-weight: 500;"> &bull; <app-icon name="link" class="app-icon-inline"></app-icon> Vinculado a Reserva #{{ p.id_reserva }}</span>
                </p>
              </div>

              <div style="text-align: right;">
                <span style="font-size: 0.8rem; color: var(--text-muted); display: block;">Total Facturado</span>
                <strong style="font-size: 1.25rem; color: var(--primary);">
                  {{ p.total | currency:'Bs. ':'symbol':'1.2-2' }}
                </strong>
              </div>
            </div>

            <!-- Desglose de Platos -->
            <div style="background: #f8fafc; border-radius: 6px; padding: 0.75rem 1rem;">
              <h4 style="margin: 0 0 0.4rem 0; font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase;">
                Platos de la orden:
              </h4>
              <ul style="margin: 0; padding-left: 1.25rem; font-size: 0.9rem;">
                <li *ngFor="let det of p.detalles">
                  <strong>{{ det.cantidad }}x</strong> {{ det.nombre_plato }}
                  <span style="color: var(--text-muted);">({{ det.subtotal | currency:'Bs. ':'symbol':'1.2-2' }})</span>
                </li>
              </ul>
              <p *ngIf="p.observaciones" style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #b45309;">
                <app-icon name="alert" class="app-icon-inline"></app-icon> <strong>Nota:</strong> {{ p.observaciones }}
              </p>
            </div>

            <!-- Transiciones de Estado de Cocina / Comanda -->
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); padding-top: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
              <a [routerLink]="['/pedidos', p.id_pedido]" class="btn btn-outline btn-sm">
                Ver Ficha Completa &rarr;
              </a>

              <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                <!-- PENDIENTE -> ACEPTADO o CANCELADO -->
                <ng-container *ngIf="p.estado === 'PENDIENTE'">
                  <button class="btn btn-success btn-sm" (click)="actualizarEstado(p, 'ACEPTADO')">
                    <app-icon name="check" class="app-icon-inline"></app-icon> Aceptar Pedido
                  </button>
                  <button class="btn btn-danger btn-sm" (click)="actualizarEstado(p, 'CANCELADO')">
                    <app-icon name="close" class="app-icon-inline"></app-icon> Rechazar / Cancelar
                  </button>
                </ng-container>

                <!-- ACEPTADO -> EN_PREPARACION o CANCELADO -->
                <ng-container *ngIf="p.estado === 'ACEPTADO'">
                  <button class="btn btn-primary btn-sm" (click)="actualizarEstado(p, 'EN_PREPARACION')">
                    <app-icon name="chef" class="app-icon-inline"></app-icon> Iniciar Preparación
                  </button>
                  <button class="btn btn-outline-danger btn-sm" (click)="actualizarEstado(p, 'CANCELADO')">
                    <app-icon name="close" class="app-icon-inline"></app-icon> Cancelar
                  </button>
                </ng-container>

                <!-- EN_PREPARACION -> LISTO -->
                <ng-container *ngIf="p.estado === 'EN_PREPARACION'">
                  <button class="btn btn-success btn-sm" (click)="actualizarEstado(p, 'LISTO')">
                    <app-icon name="info" class="app-icon-inline"></app-icon> Marcar como Listo
                  </button>
                </ng-container>

                <!-- LISTO -> ENTREGADO -->
                <ng-container *ngIf="p.estado === 'LISTO'">
                  <button class="btn btn-success btn-sm" (click)="actualizarEstado(p, 'ENTREGADO')">
                    <app-icon name="package" class="app-icon-inline"></app-icon> Marcar como Entregado
                  </button>
                </ng-container>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class GestionPedidosComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private pedidoService = inject(PedidoService);
  private restauranteService = inject(RestauranteService);

  restauranteId = signal<number>(0);
  restaurante = signal<Restaurante | null>(null);
  pedidos = signal<PedidoRespuesta[]>([]);
  cargando = signal<boolean>(false);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  // Filtros
  filtroEstado: string = '';
  filtroFecha: string = '';

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.restauranteId.set(Number(idParam));
      this.cargarRestaurante();
      this.cargarPedidos();
    }
  }

  cargarRestaurante(): void {
    this.restauranteService.getRestaurante(this.restauranteId()).subscribe({
      next: (resto: Restaurante) => this.restaurante.set(resto),
      error: () => {}
    });
  }

  cargarPedidos(): void {
    this.cargando.set(true);
    const filtros: { estado?: string; fecha?: string } = {};
    if (this.filtroEstado) filtros.estado = this.filtroEstado;
    if (this.filtroFecha) filtros.fecha = this.filtroFecha;

    this.pedidoService.listarPedidosRestaurante(this.restauranteId(), filtros).subscribe({
      next: (data) => {
        this.pedidos.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        this.error.set(err.error?.detail || 'Error al cargar los pedidos del restaurante.');
      }
    });
  }

  limpiarFiltros(): void {
    this.filtroEstado = '';
    this.filtroFecha = '';
    this.cargarPedidos();
  }

  actualizarEstado(p: PedidoRespuesta, nuevoEstado: EstadoPedido): void {
    if (nuevoEstado === 'CANCELADO' && !confirm(`¿Está seguro de cancelar el pedido #${p.id_pedido}?`)) {
      return;
    }

    this.pedidoService.actualizarEstado(p.id_pedido, nuevoEstado).subscribe({
      next: (act) => {
        const actualizados = this.pedidos().map(item =>
          item.id_pedido === act.id_pedido ? act : item
        );
        this.pedidos.set(actualizados);
        this.mensaje.set(`Estado del Pedido #${act.id_pedido} actualizado a ${act.estado}.`);
        setTimeout(() => this.mensaje.set(null), 3500);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'No se pudo actualizar el estado del pedido.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }
}
