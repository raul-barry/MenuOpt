import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
import { LugarCompraService } from '../../../core/services/lugar-compra.service';
import { IngredienteService } from '../../../core/services/ingrediente.service';
import { AuthService } from '../../../core/services/auth.service';
import {
  LugarCompra,
  CrearLugarCompraRequest,
  ActualizarLugarCompraRequest,
  IngredienteLugarCompra
} from '../../../core/models/lugar-compra.model';
import { Ingrediente } from '../../../core/models/ingrediente.model';

// =========================================================================
// CASO DE USO: CU09 - GESTIONAR PROVEEDORES
// Actor: ADMINISTRADOR_TIENDA y ADMINISTRADOR
// Administración de comercios proveedores y actualización de precios de insumos
// =========================================================================
@Component({
  selector: 'app-proveedores-lista',
  standalone: true,
  imports: [AppIconComponent, CommonModule, FormsModule],
  template: `
    <div>
      <div class="card-header" style="border: none; padding: 0; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
        <div>
          <h2><app-icon name="store" class="app-icon-inline"></app-icon> Gestión de Proveedores & Tiendas (CU09)</h2>
          <p style="color: var(--text-muted); margin: 0.25rem 0 0 0;">
            Administre establecimientos comerciales proveedores y mantenga actualizados los precios de insumos para las recetas e Inteligencia Artificial.
          </p>
        </div>
        <button class="btn btn-primary" (click)="abrirModalCrear()">
          <app-icon name="plus" class="app-icon-inline"></app-icon> + Nuevo Proveedor / Tienda
        </button>
      </div>

      <div *ngIf="mensajeExito()" class="alert alert-success">{{ mensajeExito() }}</div>
      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <!-- Barra de Filtros -->
      <div class="card" style="padding: 1rem; margin-bottom: 1.5rem; background: #f8fafc; border: 1px solid var(--border);">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; align-items: flex-end;">
          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 600;">Buscar por nombre de tienda</label>
            <input
              type="text"
              class="form-control"
              [(ngModel)]="filtroNombre"
              (ngModelChange)="filtrarProveedores()"
              placeholder="Ej. Hipermaxi, Mercado Central..."
            />
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 600;">Tipo de Establecimiento</label>
            <select class="form-control" [(ngModel)]="filtroTipo" (change)="filtrarProveedores()">
              <option value="">Todos los tipos</option>
              <option value="SUPERMERCADO">SUPERMERCADO</option>
              <option value="MERCADO">MERCADO</option>
              <option value="TIENDA">TIENDA / ALMACÉN</option>
              <option value="DISTRIBUIDOR">DISTRIBUIDOR MAYORISTA</option>
            </select>
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label" style="font-size: 0.85rem; font-weight: 600;">Estado</label>
            <select class="form-control" [(ngModel)]="filtroEstado" (change)="filtrarProveedores()">
              <option value="">Todos</option>
              <option value="ACTIVO">ACTIVO</option>
              <option value="INACTIVO">INACTIVO</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Tarjetas de Proveedores / Tiendas -->
      <div *ngIf="cargando()" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
        <p>Cargando proveedores...</p>
      </div>

      <div *ngIf="!cargando() && proveedoresFiltrados().length === 0" class="card" style="text-align: center; padding: 3rem; color: var(--text-muted);">
        <app-icon name="store" style="font-size: 2.5rem; display: block; margin-bottom: 0.5rem;"></app-icon>
        <p style="margin: 0;">No se encontraron proveedores o tiendas registradas.</p>
      </div>

      <div *ngIf="!cargando() && proveedoresFiltrados().length > 0" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem;">
        <div *ngFor="let p of proveedoresFiltrados()" class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
              <span class="badge" [ngClass]="getTipoBadge(p.tipo)">{{ p.tipo || 'TIENDA' }}</span>
              <span class="badge" [ngClass]="p.estado === 'ACTIVO' ? 'badge-success' : 'badge-danger'">
                {{ p.estado }}
              </span>
            </div>

            <h3 style="margin: 0.25rem 0 0.5rem; font-size: 1.2rem;">{{ p.nombre }}</h3>

            <p style="margin: 0 0 0.25rem; font-size: 0.85rem; color: var(--text-muted);">
              <app-icon name="pin" class="app-icon-inline"></app-icon>
              {{ p.ubicacion?.ciudad || 'Ciudad no especificada' }} &bull; {{ p.ubicacion?.direccion || 'Sin dirección' }}
            </p>

            <p style="margin: 0 0 0.75rem; font-size: 0.85rem; color: var(--text-muted);" *ngIf="p.telefono">
              <app-icon name="phone" class="app-icon-inline"></app-icon> Tel: {{ p.telefono }}
            </p>
          </div>

          <div style="border-top: 1px solid var(--border); padding-top: 0.75rem; margin-top: 0.75rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <button class="btn btn-primary btn-sm" style="flex: 1;" (click)="abrirPreciosTienda(p)">
              <app-icon name="cart" class="app-icon-inline"></app-icon> Precios de Insumos
            </button>
            <button class="btn btn-outline btn-sm" (click)="abrirModalEditar(p)" title="Editar datos del proveedor">
              Editar
            </button>
            <button
              class="btn btn-outline btn-sm"
              [style.color]="p.estado === 'ACTIVO' ? '#ef4444' : '#10b981'"
              (click)="toggleEstadoProveedor(p)"
            >
              {{ p.estado === 'ACTIVO' ? 'Desactivar' : 'Activar' }}
            </button>
          </div>
        </div>
      </div>

      <!-- MODAL: Crear / Editar Proveedor -->
      <div *ngIf="modalProveedorAbierto()" style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1050; padding: 1rem;">
        <div class="card" style="width: 100%; max-width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">
            <h3 style="margin: 0; font-size: 1.15rem;">
              {{ proveedorEditando() ? 'Modificar Proveedor' : 'Registrar Nuevo Proveedor' }}
            </h3>
            <button class="btn btn-sm btn-outline" (click)="cerrarModalProveedor()" style="padding: 0.2rem 0.5rem;">&times;</button>
          </div>

          <form (ngSubmit)="guardarProveedor()">
            <div class="form-group" style="margin-bottom: 0.75rem;">
              <label class="form-label">Nombre del Comercio / Tienda *</label>
              <input type="text" class="form-control" [(ngModel)]="formLugar.nombre" name="nombre" required placeholder="Ej. Supermercado Fidalga" />
            </div>

            <div class="form-group" style="margin-bottom: 0.75rem;">
              <label class="form-label">Tipo de Establecimiento *</label>
              <select class="form-control" [(ngModel)]="formLugar.tipo" name="tipo">
                <option value="SUPERMERCADO">SUPERMERCADO</option>
                <option value="MERCADO">MERCADO</option>
                <option value="TIENDA">TIENDA / ABARROTES</option>
                <option value="DISTRIBUIDOR">DISTRIBUIDOR MAYORISTA</option>
              </select>
            </div>

            <div class="form-group" style="margin-bottom: 0.75rem;">
              <label class="form-label">Teléfono de Contacto</label>
              <input type="text" class="form-control" [(ngModel)]="formLugar.telefono" name="telefono" placeholder="Ej. 71234567 o 33445566" />
            </div>

            <div class="form-group" style="margin-bottom: 0.75rem;">
              <label class="form-label">Ciudad</label>
              <input type="text" class="form-control" [(ngModel)]="formLugar.ciudad" name="ciudad" placeholder="Ej. Cochabamba, Santa Cruz, La Paz" />
            </div>

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label class="form-label">Dirección / Zona</label>
              <input type="text" class="form-control" [(ngModel)]="formLugar.direccion" name="direccion" placeholder="Ej. Av. América y Pando" />
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
              <button type="button" class="btn btn-secondary btn-sm" (click)="cerrarModalProveedor()">Cancelar</button>
              <button type="submit" class="btn btn-primary btn-sm" [disabled]="!formLugar.nombre">
                {{ proveedorEditando() ? 'Guardar Cambios' : 'Crear Proveedor' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- MODAL / VISTA: Catálogo de Precios de Insumos del Proveedor -->
      <div *ngIf="modalPreciosAbierto()" style="position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1050; padding: 1rem;">
        <div class="card" style="width: 100%; max-width: 800px; max-height: 90vh; overflow-y: auto; box-shadow: 0 15px 35px rgba(0,0,0,0.3);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem;">
            <div>
              <h3 style="margin: 0; font-size: 1.25rem;">
                <app-icon name="cart" class="app-icon-inline"></app-icon> Catálogo de Precios &mdash; {{ tiendaSeleccionada()?.nombre }}
              </h3>
              <p style="margin: 0.25rem 0 0 0; font-size: 0.85rem; color: var(--text-muted);">
                Precios unitarios vigentes utilizados por el algoritmo de optimización e Inteligencia Artificial (CU09 & CU26).
              </p>
            </div>
            <button class="btn btn-sm btn-outline" (click)="cerrarPreciosTienda()" style="padding: 0.2rem 0.5rem;">&times;</button>
          </div>

          <div *ngIf="mensajePrecioExito()" class="alert alert-success">{{ mensajePrecioExito() }}</div>
          <div *ngIf="mensajePrecioError()" class="alert alert-danger">{{ mensajePrecioError() }}</div>

          <!-- Formulario rápido para asociar nuevo ingrediente y precio -->
          <div style="background: #f1f5f9; padding: 1rem; border-radius: var(--radius); margin-bottom: 1.5rem; border: 1px solid var(--border);">
            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.95rem; font-weight: 600;">
              {{ ingredienteEditando() ? 'Editar Precio de Insumo' : '+ Agregar Insumo con Precio Actualizado' }}
            </h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; align-items: flex-end;">
              <div *ngIf="!ingredienteEditando()" class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 0.8rem;">Nombre del Ingrediente / Insumo *</label>
                <input
                  type="text"
                  class="form-control"
                  [(ngModel)]="nuevoPrecio.nombre_ingrediente"
                  list="listaIngredientesSugeridos"
                  placeholder="Ej. Tomate, Arroz, Harina, Pollo..."
                />
                <datalist id="listaIngredientesSugeridos">
                  <option *ngFor="let ing of catalogoIngredientes()" [value]="ing.nombre"></option>
                </datalist>
              </div>

              <div *ngIf="ingredienteEditando()" class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 0.8rem;">Insumo en Edición</label>
                <input
                  type="text"
                  class="form-control"
                  [value]="ingredienteEditando()?.nombre_ingrediente"
                  disabled
                  style="background: #e2e8f0; font-weight: 600;"
                />
              </div>

              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 0.8rem;">Precio (Bs) *</label>
                <input type="number" step="0.1" class="form-control" [(ngModel)]="nuevoPrecio.precio" placeholder="Ej. 38.50" />
              </div>

              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 0.8rem;">Cant. Referencia *</label>
                <input type="number" step="0.1" class="form-control" [(ngModel)]="nuevoPrecio.cantidad_referencia" placeholder="1.0" />
              </div>

              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label" style="font-size: 0.8rem;">Unidad *</label>
                <input type="text" class="form-control" [(ngModel)]="nuevoPrecio.unidad_medida" placeholder="kg, litro, docena" />
              </div>

              <div style="display: flex; gap: 0.5rem;">
                <button class="btn btn-primary btn-sm" (click)="guardarPrecioIngrediente()" style="flex: 1;">
                  {{ ingredienteEditando() ? 'Guardar' : 'Agregar' }}
                </button>
                <button *ngIf="ingredienteEditando()" class="btn btn-outline btn-sm" (click)="cancelarEdicionPrecio()">
                  Cancelar
                </button>
              </div>
            </div>
          </div>

          <!-- Tabla de Insumos Registrados -->
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Insumo / Ingrediente</th>
                  <th>Precio Actualizado</th>
                  <th>Presentación</th>
                  <th>Disponibilidad</th>
                  <th>Última Actualización</th>
                  <th style="text-align: right;">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let item of preciosTienda()">
                  <td><strong>{{ item.nombre_ingrediente || 'Insumo #' + item.id_ingrediente }}</strong></td>
                  <td><span style="font-weight: 600; color: #10b981;">Bs. {{ item.precio | number:'1.2-2' }}</span></td>
                  <td>{{ item.cantidad_referencia }} {{ item.unidad_medida }}</td>
                  <td>
                    <span class="badge" [ngClass]="item.disponible ? 'badge-success' : 'badge-danger'">
                      {{ item.disponible ? 'DISPONIBLE' : 'AGOTADO' }}
                    </span>
                  </td>
                  <td style="font-size: 0.85rem; color: var(--text-muted);">
                    {{ formatearFecha(item.fecha_actualizacion) }}
                  </td>
                  <td style="text-align: right;">
                    <button class="btn btn-sm btn-outline" style="margin-right: 0.25rem; padding: 0.2rem 0.4rem;" (click)="prepararEdicionPrecio(item)">
                      Editar
                    </button>
                    <button class="btn btn-sm btn-outline" style="color: #ef4444; border-color: #ef4444; padding: 0.2rem 0.4rem;" (click)="quitarPrecio(item)">
                      Quitar
                    </button>
                  </td>
                </tr>

                <tr *ngIf="preciosTienda().length === 0">
                  <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                    Este proveedor aún no tiene insumos con precios asignados.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div style="text-align: right; margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 0.75rem;">
            <button class="btn btn-secondary btn-sm" (click)="cerrarPreciosTienda()">Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ProveedoresListaComponent implements OnInit {
  private lugarCompraService = inject(LugarCompraService);
  private ingredienteService = inject(IngredienteService);
  public authService = inject(AuthService);

  cargando = signal<boolean>(false);
  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  proveedores = signal<LugarCompra[]>([]);
  proveedoresFiltrados = signal<LugarCompra[]>([]);

  filtroNombre = '';
  filtroTipo = '';
  filtroEstado = '';

  // Modal Proveedor
  modalProveedorAbierto = signal<boolean>(false);
  proveedorEditando = signal<LugarCompra | null>(null);
  formLugar = {
    nombre: '',
    tipo: 'SUPERMERCADO',
    telefono: '',
    ciudad: 'Santa Cruz',
    direccion: ''
  };

  // Modal Precios
  modalPreciosAbierto = signal<boolean>(false);
  tiendaSeleccionada = signal<LugarCompra | null>(null);
  preciosTienda = signal<IngredienteLugarCompra[]>([]);
  catalogoIngredientes = signal<Ingrediente[]>([]);
  mensajePrecioExito = signal<string | null>(null);
  mensajePrecioError = signal<string | null>(null);
  ingredienteEditando = signal<IngredienteLugarCompra | null>(null);

  nuevoPrecio = {
    id_ingrediente: null as number | null,
    nombre_ingrediente: '',
    precio: null as number | null,
    cantidad_referencia: 1,
    unidad_medida: 'kg'
  };

  ngOnInit(): void {
    this.cargarProveedores();
    this.cargarCatalogoIngredientes();
  }

  cargarProveedores(): void {
    this.cargando.set(true);
    const rol = this.authService.userRole();

    // Si es Administrador de Tienda, consulta sus tiendas asignadas
    const consulta$ = rol === 'ADMINISTRADOR_TIENDA'
      ? this.lugarCompraService.getMisTiendas()
      : this.lugarCompraService.getLugaresCompra();

    consulta$.subscribe({
      next: (lugares) => {
        this.proveedores.set(lugares);
        this.filtrarProveedores();
        this.cargando.set(false);
      },
      error: (err) => {
        this.mensajeError.set(err?.error?.detail || 'Error al cargar proveedores.');
        this.cargando.set(false);
      }
    });
  }

  cargarCatalogoIngredientes(): void {
    this.ingredienteService.getIngredientes().subscribe({
      next: (ings) => this.catalogoIngredientes.set(ings),
      error: () => {}
    });
  }

  filtrarProveedores(): void {
    let list = this.proveedores();
    if (this.filtroNombre.trim()) {
      const term = this.filtroNombre.toLowerCase();
      list = list.filter(p => p.nombre.toLowerCase().includes(term));
    }
    if (this.filtroTipo) {
      list = list.filter(p => p.tipo?.toUpperCase() === this.filtroTipo.toUpperCase());
    }
    if (this.filtroEstado) {
      list = list.filter(p => p.estado?.toUpperCase() === this.filtroEstado.toUpperCase());
    }
    this.proveedoresFiltrados.set(list);
  }

  abrirModalCrear(): void {
    this.proveedorEditando.set(null);
    this.formLugar = {
      nombre: '',
      tipo: 'SUPERMERCADO',
      telefono: '',
      ciudad: 'Santa Cruz',
      direccion: ''
    };
    this.modalProveedorAbierto.set(true);
  }

  abrirModalEditar(p: LugarCompra): void {
    this.proveedorEditando.set(p);
    this.formLugar = {
      nombre: p.nombre,
      tipo: p.tipo || 'SUPERMERCADO',
      telefono: p.telefono || '',
      ciudad: p.ubicacion?.ciudad || 'Santa Cruz',
      direccion: p.ubicacion?.direccion || ''
    };
    this.modalProveedorAbierto.set(true);
  }

  cerrarModalProveedor(): void {
    this.modalProveedorAbierto.set(false);
    this.proveedorEditando.set(null);
  }

  guardarProveedor(): void {
    if (!this.formLugar.nombre.trim()) return;

    if (this.proveedorEditando()) {
      const id = this.proveedorEditando()!.id_lugar_compra;
      this.lugarCompraService.actualizarLugarCompra(id, {
        nombre: this.formLugar.nombre.trim(),
        tipo: this.formLugar.tipo,
        telefono: this.formLugar.telefono.trim() || undefined,
        ubicacion: {
          direccion: this.formLugar.direccion.trim(),
          ciudad: this.formLugar.ciudad.trim()
        }
      }).subscribe({
        next: () => {
          this.mensajeExito.set('Proveedor actualizado exitosamente.');
          this.cerrarModalProveedor();
          this.cargarProveedores();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        },
        error: (err) => {
          this.mensajeError.set(err?.error?.detail || 'Error al actualizar proveedor.');
        }
      });
    } else {
      this.lugarCompraService.crearLugarCompra({
        nombre: this.formLugar.nombre.trim(),
        tipo: this.formLugar.tipo,
        telefono: this.formLugar.telefono.trim() || undefined,
        ubicacion: {
          direccion: this.formLugar.direccion.trim(),
          ciudad: this.formLugar.ciudad.trim()
        }
      }).subscribe({
        next: () => {
          this.mensajeExito.set('Proveedor registrado exitosamente.');
          this.cerrarModalProveedor();
          this.cargarProveedores();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        },
        error: (err) => {
          this.mensajeError.set(err?.error?.detail || 'Error al crear proveedor.');
        }
      });
    }
  }

  toggleEstadoProveedor(p: LugarCompra): void {
    const nuevoEstado = p.estado === 'ACTIVO' ? 'INACTIVO' : 'ACTIVO';
    this.lugarCompraService.cambiarEstado(p.id_lugar_compra, nuevoEstado).subscribe({
      next: () => {
        this.cargarProveedores();
      },
      error: (err) => {
        this.mensajeError.set(err?.error?.detail || 'Error al cambiar estado.');
      }
    });
  }

  // Precios
  abrirPreciosTienda(p: LugarCompra): void {
    this.tiendaSeleccionada.set(p);
    this.cancelarEdicionPrecio();
    this.cargarPrecios(p.id_lugar_compra);
    this.modalPreciosAbierto.set(true);
  }

  cerrarPreciosTienda(): void {
    this.modalPreciosAbierto.set(false);
    this.tiendaSeleccionada.set(null);
    this.preciosTienda.set([]);
  }

  cargarPrecios(idLugar: number): void {
    this.lugarCompraService.getIngredientesDeLugar(idLugar).subscribe({
      next: (items) => this.preciosTienda.set(items),
      error: () => {}
    });
  }

  prepararEdicionPrecio(item: IngredienteLugarCompra): void {
    this.ingredienteEditando.set(item);
    this.nuevoPrecio = {
      id_ingrediente: item.id_ingrediente,
      nombre_ingrediente: item.nombre_ingrediente || '',
      precio: item.precio,
      cantidad_referencia: item.cantidad_referencia,
      unidad_medida: item.unidad_medida
    };
  }

  cancelarEdicionPrecio(): void {
    this.ingredienteEditando.set(null);
    this.nuevoPrecio = {
      id_ingrediente: null,
      nombre_ingrediente: '',
      precio: null,
      cantidad_referencia: 1,
      unidad_medida: 'kg'
    };
  }

  guardarPrecioIngrediente(): void {
    if (!this.tiendaSeleccionada()) return;
    const idLugar = this.tiendaSeleccionada()!.id_lugar_compra;

    if (this.ingredienteEditando()) {
      const idIng = this.ingredienteEditando()!.id_ingrediente;
      this.lugarCompraService.actualizarIngrediente(idLugar, idIng, {
        precio: Number(this.nuevoPrecio.precio),
        cantidad_referencia: Number(this.nuevoPrecio.cantidad_referencia),
        unidad_medida: this.nuevoPrecio.unidad_medida
      }).subscribe({
        next: () => {
          this.mensajePrecioExito.set('Precio actualizado correctamente.');
          this.cancelarEdicionPrecio();
          this.cargarPrecios(idLugar);
          setTimeout(() => this.mensajePrecioExito.set(null), 3000);
        },
        error: (err) => {
          this.mensajePrecioError.set(err?.error?.detail || 'Error al actualizar precio.');
        }
      });
    } else {
      if (!this.nuevoPrecio.nombre_ingrediente?.trim() || this.nuevoPrecio.precio === null || this.nuevoPrecio.precio === undefined) {
        this.mensajePrecioError.set('Debe ingresar el nombre del ingrediente y un precio válido.');
        return;
      }
      this.lugarCompraService.asociarIngrediente(idLugar, {
        nombre_ingrediente: this.nuevoPrecio.nombre_ingrediente.trim(),
        precio: Number(this.nuevoPrecio.precio),
        cantidad_referencia: Number(this.nuevoPrecio.cantidad_referencia || 1),
        unidad_medida: this.nuevoPrecio.unidad_medida?.trim() || 'kg',
        disponible: true
      }).subscribe({
        next: () => {
          this.mensajePrecioExito.set('Insumo y precio agregados exitosamente.');
          this.cancelarEdicionPrecio();
          this.cargarPrecios(idLugar);
          this.cargarCatalogoIngredientes();
          setTimeout(() => this.mensajePrecioExito.set(null), 3000);
        },
        error: (err) => {
          this.mensajePrecioError.set(err?.error?.detail || 'Error al asociar ingrediente.');
        }
      });
    }
  }

  quitarPrecio(item: IngredienteLugarCompra): void {
    if (!confirm(`¿Desea retirar "${item.nombre_ingrediente || 'Insumo'}" del catálogo de este comercio?`)) return;
    const idLugar = this.tiendaSeleccionada()!.id_lugar_compra;
    this.lugarCompraService.eliminarIngrediente(idLugar, item.id_ingrediente).subscribe({
      next: () => {
        this.cargarPrecios(idLugar);
      },
      error: (err) => {
        this.mensajePrecioError.set(err?.error?.detail || 'Error al quitar ingrediente.');
      }
    });
  }

  formatearFecha(isoStr?: string): string {
    if (!isoStr) return '—';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch {
      return isoStr;
    }
  }

  getTipoBadge(tipo?: string | null): string {
    switch (tipo?.toUpperCase()) {
      case 'SUPERMERCADO': return 'badge-primary';
      case 'MERCADO': return 'badge-success';
      case 'DISTRIBUIDOR': return 'badge-warning';
      default: return 'badge-secondary';
    }
  }
}
