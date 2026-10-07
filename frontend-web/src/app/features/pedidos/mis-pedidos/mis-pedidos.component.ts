// CASO DE USO: CU24 - Mis Pedidos (Historial del Cliente)
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { PedidoService } from '../../../core/services/pedido.service';
import { PedidoRespuesta } from '../../../core/models/pedido.model';

@Component({
  selector: 'app-mis-pedidos',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="card" style="max-width: 960px; margin: 0 auto;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;">📦 Mis Pedidos Gastronómicos</h2>
          <p style="margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.85rem;">
            Historial de órdenes enviadas y seguimiento de su estado de preparación.
          </p>
        </div>
        <a [routerLink]="['/restaurantes']" class="btn btn-primary btn-sm">
          + Nuevo Pedido
        </a>
      </div>

      <div class="card-body">
        <div *ngIf="cargando()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando tu historial de pedidos...</p>
        </div>

        <div *ngIf="mensaje()" class="alert alert-success" style="margin-bottom: 1rem;">
          {{ mensaje() }}
        </div>
        <div *ngIf="error()" class="alert alert-danger" style="margin-bottom: 1rem;">
          {{ error() }}
        </div>

        <div *ngIf="!cargando() && pedidos().length === 0" style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
          <span style="font-size: 3rem; display: block; margin-bottom: 0.75rem;">🍽️</span>
          <h3 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; color: inherit;">Aún no has realizado pedidos</h3>
          <p style="margin: 0 0 1.25rem 0; font-size: 0.9rem;">Explora los restaurantes y realiza tu primera orden gastronómica.</p>
          <a [routerLink]="['/restaurantes']" class="btn btn-primary">Ver Restaurantes</a>
        </div>

        <div *ngIf="!cargando() && pedidos().length > 0" class="pedidos-lista">
          <div
            *ngFor="let p of pedidos()"
            class="pedido-item-card"
            style="border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1rem; background: var(--surface); display: flex; flex-direction: column; gap: 0.75rem;"
          >
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <h3 style="margin: 0; font-size: 1.1rem; color: var(--primary);">
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
                <p style="margin: 0.25rem 0 0; font-weight: 500;">
                  🍴 {{ p.nombre_restaurante }}
                </p>
                <p style="margin: 0.15rem 0 0; color: var(--text-muted); font-size: 0.85rem;">
                  📅 {{ p.fecha_pedido | date:'dd/MM/yyyy HH:mm' }}
                  <span *ngIf="p.id_reserva"> &bull; 🔗 Reserva #{{ p.id_reserva }}</span>
                </p>
              </div>

              <div style="text-align: right;">
                <span style="font-size: 0.8rem; color: var(--text-muted); display: block;">Total del pedido</span>
                <strong style="font-size: 1.25rem; color: var(--primary);">
                  {{ p.total | currency:'Bs. ':'symbol':'1.2-2' }}
                </strong>
              </div>
            </div>

            <!-- Resumen de items -->
            <div style="background: #f8fafc; border-radius: 6px; padding: 0.6rem 0.8rem; font-size: 0.85rem; color: var(--text-muted);">
              <strong>Platos ({{ p.detalles.length }}):</strong>
              <span *ngFor="let d of p.detalles; let last = last">
                {{ d.cantidad }}x {{ d.nombre_plato }}{{ last ? '' : ', ' }}
              </span>
            </div>

            <!-- Botones de Acción -->
            <div style="display: flex; justify-content: flex-end; gap: 0.5rem; align-items: center; border-top: 1px solid var(--border); padding-top: 0.75rem;">
              <button
                *ngIf="p.estado === 'PENDIENTE'"
                class="btn btn-outline-danger btn-sm"
                (click)="cancelarPedido(p)"
              >
                Cancelar Pedido
              </button>
              <a [routerLink]="['/pedidos', p.id_pedido]" class="btn btn-outline btn-sm">
                Ver Detalle &rarr;
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class MisPedidosComponent implements OnInit {
  private pedidoService = inject(PedidoService);

  pedidos = signal<PedidoRespuesta[]>([]);
  cargando = signal<boolean>(false);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarPedidos();
  }

  cargarPedidos(): void {
    this.cargando.set(true);
    this.pedidoService.listarMisPedidos().subscribe({
      next: (data) => {
        this.pedidos.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        this.error.set(err.error?.detail || 'Error al cargar el historial de pedidos.');
      }
    });
  }

  cancelarPedido(p: PedidoRespuesta): void {
    if (!confirm(`¿Estás seguro de cancelar tu Pedido #${p.id_pedido}?`)) {
      return;
    }

    this.pedidoService.cancelarPedido(p.id_pedido).subscribe({
      next: (act) => {
        const actualizados = this.pedidos().map(item =>
          item.id_pedido === act.id_pedido ? act : item
        );
        this.pedidos.set(actualizados);
        this.mensaje.set(`El Pedido #${act.id_pedido} ha sido cancelado.`);
        setTimeout(() => this.mensaje.set(null), 4000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'No se pudo cancelar el pedido.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }
}
