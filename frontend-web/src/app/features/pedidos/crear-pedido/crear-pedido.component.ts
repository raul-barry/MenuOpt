import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU23 - Enviar pedido
import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { RestauranteService } from '../../../core/services/restaurante.service';
import { PlatoService } from '../../../core/services/plato.service';
import { PedidoService } from '../../../core/services/pedido.service';
import { AuthService } from '../../../core/services/auth.service';

import { Restaurante } from '../../../core/models/restaurante.model';
import { Plato } from '../../../core/models/plato.model';
import { CartItem, PedidoCrear } from '../../../core/models/pedido.model';

@Component({
  selector: 'app-crear-pedido',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule],
  templateUrl: './crear-pedido.component.html',
  styleUrls: ['./crear-pedido.component.css']
})
export class CrearPedidoComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private restauranteService = inject(RestauranteService);
  private platoService = inject(PlatoService);
  private pedidoService = inject(PedidoService);
  public authService = inject(AuthService);

  restauranteId = signal<number>(0);
  restaurante = signal<Restaurante | null>(null);
  platos = signal<Plato[]>([]);
  cargando = signal<boolean>(false);
  enviando = signal<boolean>(false);
  error = signal<string | null>(null);
  mensaje = signal<string | null>(null);

  // Reserva opcional preasociada por query param
  idReservaParam: number | null = null;
  observaciones: string = '';

  // Carrito temporal SOLO en memoria
  carrito = signal<CartItem[]>([]);

  // Totales computados
  totalItems = computed(() => {
    return this.carrito().reduce((sum, item) => sum + item.cantidad, 0);
  });

  totalPrecio = computed(() => {
    const total = this.carrito().reduce((sum, item) => sum + item.subtotal, 0);
    return Math.round(total * 100) / 100;
  });

  // Filtro de categorías o búsqueda en frontend
  busquedaPlato: string = '';

  platosFiltrados = computed(() => {
    const list = this.platos().filter(p => p.estado === 'ACTIVO' && p.disponible);
    if (!this.busquedaPlato.trim()) return list;
    const term = this.busquedaPlato.toLowerCase();
    return list.filter(p =>
      p.nombre.toLowerCase().includes(term) ||
      (p.descripcion && p.descripcion.toLowerCase().includes(term))
    );
  });

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    const qReserva = this.route.snapshot.queryParamMap.get('id_reserva');
    if (qReserva) {
      this.idReservaParam = Number(qReserva);
    }

    if (idParam) {
      this.restauranteId.set(Number(idParam));
      this.cargarDatos();
    }
  }

  cargarDatos(): void {
    this.cargando.set(true);
    const id = this.restauranteId();

    this.restauranteService.getRestaurante(id).subscribe({
      next: (resto: Restaurante) => {
        this.restaurante.set(resto);
        this.cargarMenu(id);
      },
      error: (err: any) => {
        this.cargando.set(false);
        this.error.set(err.error?.detail || 'No se pudo cargar el restaurante.');
      }
    });
  }

  cargarMenu(idRestaurante: number): void {
    this.platoService.getPlatosPorRestaurante(idRestaurante).subscribe({
      next: (menu: Plato[]) => {
        this.platos.set(menu);
        this.cargando.set(false);
      },
      error: (err: any) => {
        this.cargando.set(false);
        this.error.set(err.error?.detail || 'Error al cargar los platos del restaurante.');
      }
    });
  }

  // --- Operaciones del Carrito en Memoria ---
  agregarAlCarrito(plato: Plato): void {
    const actual = [...this.carrito()];
    const index = actual.findIndex(i => i.id_plato === plato.id_plato);
    const precioNum = Number(plato.precio);

    if (index >= 0) {
      actual[index].cantidad += 1;
      actual[index].subtotal = Math.round(actual[index].cantidad * actual[index].precio * 100) / 100;
    } else {
      actual.push({
        id_plato: plato.id_plato,
        nombre: plato.nombre,
        precio: precioNum,
        cantidad: 1,
        subtotal: precioNum
      });
    }
    this.carrito.set(actual);
  }

  incrementar(idPlato: number): void {
    const actual = [...this.carrito()];
    const item = actual.find(i => i.id_plato === idPlato);
    if (item) {
      item.cantidad += 1;
      item.subtotal = Math.round(item.cantidad * item.precio * 100) / 100;
      this.carrito.set(actual);
    }
  }

  decrementar(idPlato: number): void {
    let actual = [...this.carrito()];
    const index = actual.findIndex(i => i.id_plato === idPlato);
    if (index >= 0) {
      if (actual[index].cantidad > 1) {
        actual[index].cantidad -= 1;
        actual[index].subtotal = Math.round(actual[index].cantidad * actual[index].precio * 100) / 100;
      } else {
        actual.splice(index, 1);
      }
      this.carrito.set(actual);
    }
  }

  eliminarDelCarrito(idPlato: number): void {
    const actual = this.carrito().filter(i => i.id_plato !== idPlato);
    this.carrito.set(actual);
  }

  limpiarCarrito(): void {
    this.carrito.set([]);
  }

  // --- Envío del Pedido a FastAPI (CU23) ---
  enviarPedido(): void {
    if (this.enviando()) return; // Prevenir doble clic

    const items = this.carrito();
    if (items.length === 0) {
      this.error.set('El carrito está vacío. Agrega al menos un plato.');
      return;
    }

    this.enviando.set(true);
    this.error.set(null);

    const payload: PedidoCrear = {
      id_restaurante: this.restauranteId(),
      detalles: items.map(i => ({
        id_plato: i.id_plato,
        cantidad: i.cantidad
      })),
      id_reserva: this.idReservaParam,
      observaciones: this.observaciones.trim() ? this.observaciones.trim() : null
    };

    this.pedidoService.crearPedido(payload).subscribe({
      next: (pedidoCreado) => {
        this.enviando.set(false);
        this.limpiarCarrito();
        this.router.navigate(['/pedidos', pedidoCreado.id_pedido]);
      },
      error: (err) => {
        this.enviando.set(false);
        this.error.set(err.error?.detail || 'Ocurrió un error al enviar el pedido. Verifica la disponibilidad.');
      }
    });
  }
}
