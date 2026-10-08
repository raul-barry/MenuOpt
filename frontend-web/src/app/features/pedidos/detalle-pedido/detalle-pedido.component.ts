import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU24 - Detalle de Pedido
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';

import { PedidoService } from '../../../core/services/pedido.service';
import { AuthService } from '../../../core/services/auth.service';
import { PedidoRespuesta } from '../../../core/models/pedido.model';

@Component({
  selector: 'app-detalle-pedido',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule],
  template: `
    <div class="card" style="max-width: 800px; margin: 0 auto;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h2 style="margin: 0; font-size: 1.35rem;">Detalle del Pedido #{{ pedidoId() }}</h2>
          <p style="margin: 0.25rem 0 0; color: var(--text-muted); font-size: 0.85rem;">
            Desglose de platos, precios unitarios registrados y estado de entrega.
          </p>
        </div>
        <button class="btn btn-outline btn-sm" (click)="volver()">
          &larr; Volver
        </button>
      </div>

      <div class="card-body">
        <div *ngIf="cargando()" style="text-align: center; padding: 2rem;">
          <span class="spinner"></span>
          <p style="margin-top: 0.5rem; color: var(--text-muted);">Cargando detalle del pedido...</p>
        </div>

        <div *ngIf="mensaje()" class="alert alert-success" style="margin-bottom: 1rem;">
          {{ mensaje() }}
        </div>
        <div *ngIf="error()" class="alert alert-danger" style="margin-bottom: 1rem;">
          {{ error() }}
        </div>

        <div *ngIf="!cargando() && pedido() as p">
          <!-- Banner Superior de Estado y Restaurante -->
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.25rem; background: #f8fafc; border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 1.5rem; flex-wrap: wrap; gap: 0.75rem;">
            <div>
              <h3 style="margin: 0; color: var(--primary);">{{ p.nombre_restaurante }}</h3>
              <p style="margin: 0.25rem 0 0; font-size: 0.85rem; color: var(--text-muted);">
                <app-icon name="calendar" class="app-icon-inline"></app-icon> Solicitado: {{ p.fecha_pedido | date:'dd/MM/yyyy HH:mm' }}
              </p>
              <p *ngIf="p.id_reserva" style="margin: 0.25rem 0 0; font-size: 0.85rem; color: #0284c7;">
                <app-icon name="link" class="app-icon-inline"></app-icon> Asociado a la Reserva #{{ p.id_reserva }}
              </p>
            </div>
            <div style="text-align: right;">
              <span
                class="badge"
                style="font-size: 0.95rem; padding: 0.4rem 0.8rem;"
                [class.badge-warning]="p.estado === 'PENDIENTE'"
                [class.badge-info]="p.estado === 'ACEPTADO' || p.estado === 'EN_PREPARACION'"
                [class.badge-success]="p.estado === 'LISTO' || p.estado === 'ENTREGADO'"
                [class.badge-danger]="p.estado === 'CANCELADO'"
              >
                {{ p.estado }}
              </span>
            </div>
          </div>

          <!-- Información del Cliente (si es restaurante/admin) -->
          <div *ngIf="p.nombre_cliente" style="background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: var(--text-muted);">CLIENTE COMENSAL</h4>
            <p style="margin: 0 0 0.25rem 0; font-weight: 600;"><app-icon name="user" class="app-icon-inline"></app-icon> {{ p.nombre_cliente }}</p>
            <p style="margin: 0; font-size: 0.85rem; color: var(--text-muted);">
              <app-icon name="mail" class="app-icon-inline"></app-icon> {{ p.correo_cliente }} <span *ngIf="p.telefono_cliente">| <app-icon name="phone" class="app-icon-inline"></app-icon> {{ p.telefono_cliente }}</span>
            </p>
          </div>

          <!-- Tabla de Desglose de Platos -->
          <div style="margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.75rem 0; font-size: 1rem;"><app-icon name="utensils" class="app-icon-inline"></app-icon> Platos Ordenados</h4>
            <div style="overflow-x: auto;">
              <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
                <thead>
                  <tr style="border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase;">
                    <th style="padding: 0.6rem 0.5rem;">Plato</th>
                    <th style="padding: 0.6rem 0.5rem; text-align: center;">Cant.</th>
                    <th style="padding: 0.6rem 0.5rem; text-align: right;">Precio Unit.</th>
                    <th style="padding: 0.6rem 0.5rem; text-align: right;">Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let d of p.detalles" style="border-bottom: 1px solid var(--border);">
                    <td style="padding: 0.75rem 0.5rem; font-weight: 500;">{{ d.nombre_plato }}</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: center;">{{ d.cantidad }}</td>
                    <td style="padding: 0.75rem 0.5rem; text-align: right; color: var(--text-muted);">
                      {{ d.precio_unitario | currency:'Bs. ':'symbol':'1.2-2' }}
                    </td>
                    <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 600;">
                      {{ d.subtotal | currency:'Bs. ':'symbol':'1.2-2' }}
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr style="border-top: 2px solid var(--border);">
                    <td colspan="3" style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 700; font-size: 1.05rem;">
                      Total Pedido:
                    </td>
                    <td style="padding: 0.75rem 0.5rem; text-align: right; font-weight: 700; font-size: 1.25rem; color: var(--primary);">
                      {{ p.total | currency:'Bs. ':'symbol':'1.2-2' }}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Observaciones -->
          <div *ngIf="p.observaciones" style="background: #fffbeb; border: 1px solid #fef3c7; border-radius: var(--radius); padding: 1rem; margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.25rem 0; font-size: 0.85rem; color: #b45309; text-transform: uppercase;">
              <app-icon name="receipt" class="app-icon-inline"></app-icon> Observaciones del comensal
            </h4>
            <p style="margin: 0; color: #78350f; font-size: 0.95rem;">{{ p.observaciones }}</p>
          </div>

          <!-- Acciones del Cliente (Cancelar si PENDIENTE) -->
          <div *ngIf="puedeCancelar(p)" style="display: flex; justify-content: flex-end; gap: 0.5rem;">
            <button class="btn btn-danger" (click)="cancelarPedido(p)">
              Cancelar Pedido
            </button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class DetallePedidoComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private pedidoService = inject(PedidoService);
  public authService = inject(AuthService);

  pedidoId = signal<number>(0);
  pedido = signal<PedidoRespuesta | null>(null);
  cargando = signal<boolean>(false);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.pedidoId.set(Number(idParam));
      this.cargarDetalle();
    }
  }

  cargarDetalle(): void {
    this.cargando.set(true);
    this.pedidoService.obtenerPedido(this.pedidoId()).subscribe({
      next: (p) => {
        this.pedido.set(p);
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        this.error.set(err.error?.detail || 'No se pudo cargar la información del pedido.');
      }
    });
  }

  puedeCancelar(p: PedidoRespuesta): boolean {
    const userId = this.authService.currentUser()?.id_usuario;
    const rol = this.authService.userRole();
    const esTitular = p.id_usuario === userId;
    return (esTitular || rol === 'ADMINISTRADOR') && p.estado === 'PENDIENTE';
  }

  cancelarPedido(p: PedidoRespuesta): void {
    if (!confirm(`¿Está seguro de cancelar el pedido #${p.id_pedido}?`)) {
      return;
    }

    this.pedidoService.cancelarPedido(p.id_pedido).subscribe({
      next: (act) => {
        this.pedido.set(act);
        this.mensaje.set('Pedido cancelado exitosamente.');
        setTimeout(() => this.mensaje.set(null), 4000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Error al cancelar el pedido.');
        setTimeout(() => this.error.set(null), 4000);
      }
    });
  }

  volver(): void {
    const rol = this.authService.userRole();
    if (rol === 'RESTAURANTE') {
      const rId = this.pedido()?.id_restaurante;
      if (rId) {
        this.router.navigate(['/restaurantes', rId, 'pedidos']);
        return;
      }
    }
    this.router.navigate(['/mis-pedidos']);
  }
}
