import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU17 - Crear plano 2D del restaurante
// CASO DE USO: CU18 - Gestionar mesas
// CASO DE USO: CU19 - Definir combinación de mesas
import { Component, OnInit, inject, signal, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { RestauranteService } from '../../../core/services/restaurante.service';
import { AreaRestauranteService } from '../../../core/services/area-restaurante.service';
import { MesaService } from '../../../core/services/mesa.service';
import { DistribucionMesasService } from '../../../core/services/distribucion-mesas.service';
import { MesaCombinacionService } from '../../../core/services/mesa-combinacion.service';

import { Restaurante } from '../../../core/models/restaurante.model';
import { AreaRestaurante, AreaRestauranteCrear, AreaRestauranteActualizar } from '../../../core/models/area-restaurante.model';
import { Mesa, FormaMesa, MesaCrear, MesaActualizar } from '../../../core/models/mesa.model';
import { MesaCombinacion, MesaCombinacionCrear } from '../../../core/models/mesa-combinacion.model';
import { GenerarDistribucionRequest } from '../../../core/models/distribucion.model';

@Component({
  selector: 'app-distribucion-editor',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule],
  templateUrl: './distribucion-editor.component.html',
  styleUrls: ['./distribucion-editor.component.css']
})
export class DistribucionEditorComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private restauranteService = inject(RestauranteService);
  private areaService = inject(AreaRestauranteService);
  private mesaService = inject(MesaService);
  private distribucionService = inject(DistribucionMesasService);
  private combinacionService = inject(MesaCombinacionService);

  @ViewChild('canvasContainer') canvasContainer!: ElementRef<HTMLDivElement>;

  // Estado reactivo principal
  restauranteId = signal<number>(0);
  restaurante = signal<Restaurante | null>(null);
  areas = signal<AreaRestaurante[]>([]);
  areaSeleccionada = signal<AreaRestaurante | null>(null);
  mesas = signal<Mesa[]>([]);
  combinaciones = signal<MesaCombinacion[]>([]);
  mesaSeleccionada = signal<Mesa | null>(null);

  // Estados de control
  subtabActiva = signal<'canvas' | 'mesas' | 'combinaciones'>('canvas');
  hayCambios = signal<boolean>(false);
  cargando = signal<boolean>(false);
  guardandoDistribucion = signal<boolean>(false);
  generandoDistribucion = signal<boolean>(false);
  mensaje = signal<string | null>(null);
  error = signal<string | null>(null);

  // Drag & drop interactivo
  mesaEnArrastre: Mesa | null = null;
  dragStartPointerX = 0;
  dragStartPointerY = 0;
  initialMesaX = 0;
  initialMesaY = 0;

  // Estado de modales
  modalAreaVisible = signal<boolean>(false);
  areaEditando = signal<AreaRestaurante | null>(null);
  formArea = {
    nombre: '',
    descripcion: '',
    ancho_mapa: 1000,
    alto_mapa: 600
  };

  modalMesaVisible = signal<boolean>(false);
  mesaEditando = signal<Mesa | null>(null);
  formMesa = {
    numero: '',
    nombre: '',
    capacidad: 4,
    forma: 'CUADRADA' as FormaMesa,
    rotacion: 0,
    es_fija: false,
    combinable: true
  };

  modalGenerarVisible = signal<boolean>(false);
  formGenerar = {
    total_mesas: 8,
    cap2: 2,
    cap4: 4,
    cap6: 2,
    limpiar_existentes: true
  };

  modalCombinacionVisible = signal<boolean>(false);
  formCombinacion: {
    id_mesa_origen: number | null;
    id_mesa_destino: number | null;
    descripcion: string;
  } = {
    id_mesa_origen: null,
    id_mesa_destino: null,
    descripcion: ''
  };
  capacidadCombinadaPreview = 0;

  modalConfirmarCambioAreaVisible = signal<boolean>(false);
  areaPendienteCambio: AreaRestaurante | null = null;

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.restauranteId.set(Number(idParam));
      this.cargarRestaurante();
      this.cargarAreas();
    }
  }

  mostrarMensaje(msg: string): void {
    this.mensaje.set(msg);
    setTimeout(() => this.mensaje.set(null), 4000);
  }

  mostrarError(err: string): void {
    this.error.set(err);
    setTimeout(() => this.error.set(null), 5000);
  }

  cargarRestaurante(): void {
    this.restauranteService.getRestaurante(this.restauranteId()).subscribe({
      next: (data) => this.restaurante.set(data),
      error: () => this.mostrarError('No se pudo cargar la información del restaurante.')
    });
  }

  cargarAreas(): void {
    this.cargando.set(true);
    this.areaService.listarAreasPorRestaurante(this.restauranteId(), false).subscribe({
      next: (lista) => {
        this.areas.set(lista);
        this.cargando.set(false);
        if (lista.length > 0 && !this.areaSeleccionada()) {
          this.seleccionarArea(lista[0]);
        }
      },
      error: () => {
        this.cargando.set(false);
        this.mostrarError('Error al listar las áreas del restaurante.');
      }
    });
  }

  contarMesasArea(idArea: number): number {
    const a = this.areas().find(item => item.id_area === idArea);
    return a?.total_mesas || 0;
  }

  seleccionarArea(area: AreaRestaurante): void {
    if (this.areaSeleccionada()?.id_area === area.id_area) {
      return;
    }
    if (this.hayCambios()) {
      this.areaPendienteCambio = area;
      this.modalConfirmarCambioAreaVisible.set(true);
      return;
    }
    this.aplicarCambioArea(area);
  }

  private aplicarCambioArea(area: AreaRestaurante): void {
    this.areaSeleccionada.set(area);
    this.mesaSeleccionada.set(null);
    this.hayCambios.set(false);
    this.cargarMesasArea(area.id_area);
    this.cargarCombinacionesArea(area.id_area);
  }

  cancelarCambioArea(): void {
    this.modalConfirmarCambioAreaVisible.set(false);
    this.areaPendienteCambio = null;
  }

  confirmarDescarteYCambiarArea(): void {
    this.modalConfirmarCambioAreaVisible.set(false);
    if (this.areaPendienteCambio) {
      this.aplicarCambioArea(this.areaPendienteCambio);
      this.areaPendienteCambio = null;
    }
  }

  guardarYCambiarArea(): void {
    this.guardarDistribucion(() => {
      this.modalConfirmarCambioAreaVisible.set(false);
      if (this.areaPendienteCambio) {
        this.aplicarCambioArea(this.areaPendienteCambio);
        this.areaPendienteCambio = null;
      }
    });
  }

  cargarMesasArea(idArea: number): void {
    this.mesaService.listarMesasPorArea(idArea, false).subscribe({
      next: (mesas) => {
        this.mesas.set(mesas);
        this.hayCambios.set(false);
      },
      error: () => this.mostrarError('Error al cargar las mesas del área seleccionada.')
    });
  }

  cargarCombinacionesArea(idArea: number): void {
    this.combinacionService.listarCombinacionesPorArea(idArea, false).subscribe({
      next: (combs) => this.combinaciones.set(combs),
      error: () => this.mostrarError('Error al cargar las combinaciones de mesas.')
    });
  }

  cambiarSubtab(subtab: 'canvas' | 'mesas' | 'combinaciones'): void {
    this.subtabActiva.set(subtab);
  }

  // --- DRAG AND DROP INTERACTIVO CON COORDENADAS NORMALIZADAS [0.0, 1.0] ---

  onTablePointerDown(event: PointerEvent, mesa: Mesa): void {
    if (mesa.es_fija) {
      this.seleccionarMesa(mesa);
      return;
    }
    this.seleccionarMesa(mesa);
    this.mesaEnArrastre = mesa;
    this.dragStartPointerX = event.clientX;
    this.dragStartPointerY = event.clientY;
    this.initialMesaX = Number(mesa.posicion_x);
    this.initialMesaY = Number(mesa.posicion_y);

    const target = event.currentTarget as HTMLElement;
    if (target.setPointerCapture) {
      target.setPointerCapture(event.pointerId);
    }
  }

  onPointerMove(event: PointerEvent): void {
    if (!this.mesaEnArrastre || !this.canvasContainer) {
      return;
    }
    const rect = this.canvasContainer.nativeElement.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      return;
    }

    const deltaX = (event.clientX - this.dragStartPointerX) / rect.width;
    const deltaY = (event.clientY - this.dragStartPointerY) / rect.height;

    // Acotar posiciones para que las mesas no salgan del lienzo
    let newX = Math.max(0.04, Math.min(0.94, this.initialMesaX + deltaX));
    let newY = Math.max(0.04, Math.min(0.94, this.initialMesaY + deltaY));

    // Redondear a 4 decimales
    newX = Math.round(newX * 10000) / 10000;
    newY = Math.round(newY * 10000) / 10000;

    this.mesaEnArrastre.posicion_x = newX;
    this.mesaEnArrastre.posicion_y = newY;
    this.hayCambios.set(true);
  }

  onPointerUp(event: PointerEvent): void {
    if (this.mesaEnArrastre) {
      const target = event.currentTarget as HTMLElement;
      if (target.releasePointerCapture && target.hasPointerCapture(event.pointerId)) {
        target.releasePointerCapture(event.pointerId);
      }
      this.mesaEnArrastre = null;
    }
  }

  seleccionarMesa(mesa: Mesa): void {
    this.mesaSeleccionada.set(mesa);
  }

  rotarMesa90(mesa: Mesa): void {
    mesa.rotacion = (mesa.rotacion + 90) % 360;
    this.hayCambios.set(true);
  }

  toggleFija(mesa: Mesa): void {
    this.mesaService.actualizarMesa(mesa.id_mesa, { es_fija: !mesa.es_fija }).subscribe({
      next: (actualizada) => {
        mesa.es_fija = actualizada.es_fija;
        this.mostrarMensaje(`Mesa ${mesa.numero} ahora es ${mesa.es_fija ? 'fija' : 'movible'}.`);
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al actualizar estado fijo de la mesa.')
    });
  }

  toggleCombinable(mesa: Mesa): void {
    this.mesaService.actualizarMesa(mesa.id_mesa, { combinable: !mesa.combinable }).subscribe({
      next: (actualizada) => {
        mesa.combinable = actualizada.combinable;
        this.mostrarMensaje(`Mesa ${mesa.numero} ahora es ${mesa.combinable ? 'combinable' : 'individual'}.`);
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al actualizar combinabilidad.')
    });
  }

  // --- CU17: GUARDAR, GENERAR Y RESTABLECER DISTRIBUCIÓN ---

  guardarDistribucion(onSuccess?: () => void): void {
    const area = this.areaSeleccionada();
    if (!area) return;

    this.guardandoDistribucion.set(true);
    const posiciones = this.mesas().map(m => ({
      id_mesa: m.id_mesa,
      posicion_x: m.posicion_x,
      posicion_y: m.posicion_y,
      rotacion: m.rotacion
    }));

    this.distribucionService.guardarDistribucion(area.id_area, posiciones).subscribe({
      next: (res) => {
        this.guardandoDistribucion.set(false);
        this.hayCambios.set(false);
        this.mostrarMensaje(res.mensaje || 'Distribución guardada exitosamente.');
        if (onSuccess) onSuccess();
      },
      error: (err) => {
        this.guardandoDistribucion.set(false);
        this.mostrarError(err.error?.detail || 'Error al guardar la distribución del plano.');
      }
    });
  }

  restablecerDistribucion(): void {
    const area = this.areaSeleccionada();
    if (!area) return;

    if (!confirm('¿Desea restablecer la distribución de mesas a una cuadrícula uniforme determinística?')) {
      return;
    }

    this.distribucionService.restablecerDistribucion(area.id_area).subscribe({
      next: (res) => {
        this.mesas.set(res.mesas);
        this.hayCambios.set(false);
        this.mostrarMensaje(res.mensaje || 'Distribución restablecida en cuadrícula óptima.');
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al restablecer distribución.')
    });
  }

  // --- MODAL ÁREA ---

  abrirModalNuevaArea(): void {
    this.areaEditando.set(null);
    this.formArea = {
      nombre: '',
      descripcion: '',
      ancho_mapa: 1000,
      alto_mapa: 600
    };
    this.modalAreaVisible.set(true);
  }

  abrirModalEditarArea(area: AreaRestaurante): void {
    this.areaEditando.set(area);
    this.formArea = {
      nombre: area.nombre,
      descripcion: area.descripcion || '',
      ancho_mapa: area.ancho_mapa,
      alto_mapa: area.alto_mapa
    };
    this.modalAreaVisible.set(true);
  }

  cerrarModalArea(): void {
    this.modalAreaVisible.set(false);
    this.areaEditando.set(null);
  }

  guardarArea(): void {
    if (!this.formArea.nombre.trim()) {
      this.mostrarError('El nombre del área es obligatorio.');
      return;
    }

    if (this.areaEditando()) {
      const area = this.areaEditando()!;
      const datos: AreaRestauranteActualizar = {
        nombre: this.formArea.nombre,
        descripcion: this.formArea.descripcion,
        ancho_mapa: this.formArea.ancho_mapa,
        alto_mapa: this.formArea.alto_mapa
      };
      this.areaService.actualizarArea(area.id_area, datos).subscribe({
        next: (act) => {
          this.mostrarMensaje(`Área '${act.nombre}' actualizada con éxito.`);
          this.cerrarModalArea();
          this.cargarAreas();
        },
        error: (err) => this.mostrarError(err.error?.detail || 'Error al actualizar el área.')
      });
    } else {
      const datos: AreaRestauranteCrear = {
        nombre: this.formArea.nombre,
        descripcion: this.formArea.descripcion,
        ancho_mapa: this.formArea.ancho_mapa,
        alto_mapa: this.formArea.alto_mapa,
        orden: this.areas().length + 1
      };
      this.areaService.crearArea(this.restauranteId(), datos).subscribe({
        next: (nueva) => {
          this.mostrarMensaje(`Área '${nueva.nombre}' creada con éxito.`);
          this.cerrarModalArea();
          this.areaService.listarAreasPorRestaurante(this.restauranteId(), false).subscribe(lista => {
            this.areas.set(lista);
            this.seleccionarArea(nueva);
          });
        },
        error: (err) => this.mostrarError(err.error?.detail || 'Error al crear el área.')
      });
    }
  }

  // --- MODAL MESA (CU18) ---

  abrirModalNuevaMesa(): void {
    this.mesaEditando.set(null);
    const sugeridoNum = 'M' + (this.mesas().length + 1);
    this.formMesa = {
      numero: sugeridoNum,
      nombre: '',
      capacidad: 4,
      forma: 'CUADRADA',
      rotacion: 0,
      es_fija: false,
      combinable: true
    };
    this.modalMesaVisible.set(true);
  }

  abrirModalEditarMesa(mesa: Mesa): void {
    this.mesaEditando.set(mesa);
    this.formMesa = {
      numero: mesa.numero,
      nombre: mesa.nombre || '',
      capacidad: mesa.capacidad,
      forma: mesa.forma,
      rotacion: mesa.rotacion,
      es_fija: mesa.es_fija,
      combinable: mesa.combinable
    };
    this.modalMesaVisible.set(true);
  }

  cerrarModalMesa(): void {
    this.modalMesaVisible.set(false);
    this.mesaEditando.set(null);
  }

  guardarMesa(): void {
    const area = this.areaSeleccionada();
    if (!area) return;

    if (!this.formMesa.numero.trim()) {
      this.mostrarError('El número o código de mesa es obligatorio.');
      return;
    }

    if (this.mesaEditando()) {
      const m = this.mesaEditando()!;
      const datos: MesaActualizar = {
        numero: this.formMesa.numero,
        nombre: this.formMesa.nombre,
        capacidad: this.formMesa.capacidad,
        forma: this.formMesa.forma,
        rotacion: this.formMesa.rotacion,
        es_fija: this.formMesa.es_fija,
        combinable: this.formMesa.combinable
      };
      this.mesaService.actualizarMesa(m.id_mesa, datos).subscribe({
        next: (act) => {
          this.mostrarMensaje(`Mesa '${act.numero}' actualizada correctamente.`);
          this.cerrarModalMesa();
          this.cargarMesasArea(area.id_area);
        },
        error: (err) => this.mostrarError(err.error?.detail || 'Error al actualizar la mesa.')
      });
    } else {
      const datos: MesaCrear = {
        numero: this.formMesa.numero,
        nombre: this.formMesa.nombre,
        capacidad: this.formMesa.capacidad,
        forma: this.formMesa.forma,
        rotacion: this.formMesa.rotacion,
        es_fija: this.formMesa.es_fija,
        combinable: this.formMesa.combinable
      };
      this.mesaService.crearMesa(area.id_area, datos).subscribe({
        next: (nueva) => {
          this.mostrarMensaje(`Mesa '${nueva.numero}' agregada correctamente.`);
          this.cerrarModalMesa();
          this.cargarMesasArea(area.id_area);
        },
        error: (err) => this.mostrarError(err.error?.detail || 'Error al crear la mesa.')
      });
    }
  }

  desactivarMesa(mesa: Mesa): void {
    if (!confirm(`¿Está seguro de eliminar o desactivar la mesa '${mesa.numero}'?`)) {
      return;
    }
    this.mesaService.desactivarMesa(mesa.id_mesa).subscribe({
      next: () => {
        this.mostrarMensaje(`Mesa '${mesa.numero}' eliminada.`);
        if (this.mesaSeleccionada()?.id_mesa === mesa.id_mesa) {
          this.mesaSeleccionada.set(null);
        }
        if (this.areaSeleccionada()) {
          this.cargarMesasArea(this.areaSeleccionada()!.id_area);
        }
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al eliminar mesa.')
    });
  }

  // --- MODAL GENERAR DISTRIBUCIÓN AUTOMÁTICA ---

  abrirModalGenerar(): void {
    this.modalGenerarVisible.set(true);
  }

  cerrarModalGenerar(): void {
    this.modalGenerarVisible.set(false);
  }

  ejecutarGeneracion(): void {
    const area = this.areaSeleccionada();
    if (!area) return;

    this.generandoDistribucion.set(true);

    const distCap: { [k: string]: number } = {};
    if (this.formGenerar.cap2 > 0) distCap['2'] = Number(this.formGenerar.cap2);
    if (this.formGenerar.cap4 > 0) distCap['4'] = Number(this.formGenerar.cap4);
    if (this.formGenerar.cap6 > 0) distCap['6'] = Number(this.formGenerar.cap6);

    const req: GenerarDistribucionRequest = {
      total_mesas: Number(this.formGenerar.total_mesas),
      distribucion_capacidades: Object.keys(distCap).length > 0 ? distCap : undefined,
      limpiar_existentes: this.formGenerar.limpiar_existentes
    };

    this.distribucionService.generarDistribucion(area.id_area, req).subscribe({
      next: (res) => {
        this.generandoDistribucion.set(false);
        this.cerrarModalGenerar();
        this.mesas.set(res.mesas);
        this.hayCambios.set(false);
        this.mostrarMensaje(res.mensaje || 'Distribución automática generada con éxito.');
      },
      error: (err) => {
        this.generandoDistribucion.set(false);
        this.mostrarError(err.error?.detail || 'Error al generar la distribución automática.');
      }
    });
  }

  // --- MODAL COMBINACIÓN (CU19) ---

  abrirModalNuevaCombinacion(): void {
    this.formCombinacion = {
      id_mesa_origen: null,
      id_mesa_destino: null,
      descripcion: ''
    };
    this.capacidadCombinadaPreview = 0;
    this.modalCombinacionVisible.set(true);
  }

  cerrarModalCombinacion(): void {
    this.modalCombinacionVisible.set(false);
  }

  getMesasCombinables(): Mesa[] {
    return this.mesas().filter(m => m.activo && m.combinable && !m.es_fija);
  }

  calcularCapacidadCombinada(): void {
    const m1 = this.mesas().find(m => m.id_mesa === this.formCombinacion.id_mesa_origen);
    const m2 = this.mesas().find(m => m.id_mesa === this.formCombinacion.id_mesa_destino);
    if (m1 && m2 && m1.id_mesa !== m2.id_mesa) {
      this.capacidadCombinadaPreview = m1.capacidad + m2.capacidad;
    } else {
      this.capacidadCombinadaPreview = 0;
    }
  }

  guardarCombinacion(): void {
    const { id_mesa_origen, id_mesa_destino, descripcion } = this.formCombinacion;
    if (!id_mesa_origen || !id_mesa_destino) {
      this.mostrarError('Debe seleccionar dos mesas diferentes para combinar.');
      return;
    }
    if (id_mesa_origen === id_mesa_destino) {
      this.mostrarError('No puede combinar una mesa consigo misma.');
      return;
    }

    const payload: MesaCombinacionCrear = {
      id_mesa_origen,
      id_mesa_destino,
      descripcion: descripcion || null
    };

    this.combinacionService.crearCombinacion(payload).subscribe({
      next: (comb) => {
        this.mostrarMensaje(`Combinación creada exitosamente (Capacidad: ${comb.capacidad_total || this.capacidadCombinadaPreview} comensales).`);
        this.cerrarModalCombinacion();
        if (this.areaSeleccionada()) {
          this.cargarCombinacionesArea(this.areaSeleccionada()!.id_area);
        }
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al crear la combinación de mesas.')
    });
  }

  desactivarCombinacion(c: MesaCombinacion): void {
    if (!confirm('¿Desea desactivar esta combinación de mesas?')) {
      return;
    }
    this.combinacionService.desactivarCombinacion(c.id_mesa_combinacion).subscribe({
      next: () => {
        this.mostrarMensaje('Combinación desactivada con éxito.');
        if (this.areaSeleccionada()) {
          this.cargarCombinacionesArea(this.areaSeleccionada()!.id_area);
        }
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al desactivar combinación.')
    });
  }
}
