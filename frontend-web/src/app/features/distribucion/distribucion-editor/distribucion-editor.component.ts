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
import { AreaRestaurante, AreaRestauranteCrear, AreaRestauranteActualizar, EspacioPlano, TipoEspacioPlano } from '../../../core/models/area-restaurante.model';
import { Mesa, FormaMesa, MesaCrear, MesaActualizar } from '../../../core/models/mesa.model';
import { MesaCombinacion, MesaCombinacionCrear } from '../../../core/models/mesa-combinacion.model';
import { GenerarDistribucionRequest } from '../../../core/models/distribucion.model';

import { MesaSvgComponent, DisposicionMesa } from '../../../shared/mesa-svg/mesa-svg.component';
import { EspacioSvgComponent } from '../../../shared/espacio-svg/espacio-svg.component';

export interface ModeloMesaPreset {
  id: string;
  nombre: string;
  forma: FormaMesa;
  capacidad: number;
  disposicion: DisposicionMesa;
  categoria: 'REDONDA' | 'CUADRADA' | 'RECTANGULAR';
}

export interface ModeloEspacioPreset {
  id: string;
  tipo: TipoEspacioPlano;
  nombre: string;
  subtitulo: string;
  ancho: number;
  alto: number;
  categoria: 'ACCESOS' | 'SERVICIOS' | 'ATENCION' | 'ENTRETENIMIENTO' | 'PERSONALIZADO';
}

@Component({
  selector: 'app-distribucion-editor',
  standalone: true,
  imports: [AppIconComponent, MesaSvgComponent, EspacioSvgComponent, CommonModule, RouterModule, FormsModule],
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

  // Catálogo de modelos predeterminados según diseño arquitectónico
  readonly MODELOS_CATALOGO: ModeloMesaPreset[] = [
    // 1. Redondas
    { id: 'r1', nombre: 'Redonda 1 silla', forma: 'REDONDA', capacidad: 1, disposicion: 'redonda', categoria: 'REDONDA' },
    { id: 'r2', nombre: 'Redonda 2 sillas', forma: 'REDONDA', capacidad: 2, disposicion: 'redonda', categoria: 'REDONDA' },
    { id: 'r3', nombre: 'Redonda 3 sillas', forma: 'REDONDA', capacidad: 3, disposicion: 'redonda', categoria: 'REDONDA' },
    { id: 'r4', nombre: 'Redonda 4 sillas', forma: 'REDONDA', capacidad: 4, disposicion: 'redonda', categoria: 'REDONDA' },
    { id: 'r5', nombre: 'Redonda 5 sillas', forma: 'REDONDA', capacidad: 5, disposicion: 'redonda', categoria: 'REDONDA' },

    // 2. Cuadradas
    { id: 'c2', nombre: 'Cuadrada 2 sillas', forma: 'CUADRADA', capacidad: 2, disposicion: 'cuadrada-2', categoria: 'CUADRADA' },
    { id: 'c4', nombre: 'Cuadrada 4 sillas', forma: 'CUADRADA', capacidad: 4, disposicion: 'cuadrada-4', categoria: 'CUADRADA' },
    { id: 'c8', nombre: 'Cuadrada grande 8 sillas', forma: 'CUADRADA', capacidad: 8, disposicion: 'cuadrada-8', categoria: 'CUADRADA' },

    // 3. Rectangulares
    { id: 'rec4', nombre: 'Rectangular 4 sillas', forma: 'RECTANGULAR', capacidad: 4, disposicion: 'rect-4', categoria: 'RECTANGULAR' },
    { id: 'rec6_cab', nombre: 'Rectangular 6 sillas (cabeceras)', forma: 'RECTANGULAR', capacidad: 6, disposicion: 'rect-6-cabecera', categoria: 'RECTANGULAR' },
    { id: 'rec6_long', nombre: 'Rectangular 6 sillas (alargada)', forma: 'RECTANGULAR', capacidad: 6, disposicion: 'rect-6-largo', categoria: 'RECTANGULAR' },
    { id: 'rec8_cab', nombre: 'Rectangular 8 sillas (cabeceras)', forma: 'RECTANGULAR', capacidad: 8, disposicion: 'rect-8-cabecera', categoria: 'RECTANGULAR' },
    { id: 'rec8_long', nombre: 'Rectangular 8 sillas (alargada)', forma: 'RECTANGULAR', capacidad: 8, disposicion: 'rect-8-largo', categoria: 'RECTANGULAR' }
  ];

  // Catálogo oficial de espacios y herramientas arquitectónicas del local
  readonly ESPACIOS_CATALOGO: ModeloEspacioPreset[] = [
    // 1. Accesos y Circulación
    { id: 'esp_acceso', tipo: 'ACCESO', nombre: 'Ingreso / Salida', subtitulo: 'Puerta Principal', ancho: 0.14, alto: 0.08, categoria: 'ACCESOS' },
    { id: 'esp_escalera', tipo: 'ESCALERA', nombre: 'Escalera Planta Alta', subtitulo: 'Hacia otra planta', ancho: 0.13, alto: 0.10, categoria: 'ACCESOS' },

    // 2. Atención y Pagos
    { id: 'esp_caja', tipo: 'CAJA', nombre: 'Caja Principal', subtitulo: 'Punto de Cobro', ancho: 0.12, alto: 0.08, categoria: 'ATENCION' },
    { id: 'esp_retiro', tipo: 'RETIRO', nombre: 'Retiro de Pedidos', subtitulo: 'Take Away / Llevar', ancho: 0.14, alto: 0.08, categoria: 'ATENCION' },
    { id: 'esp_barra', tipo: 'BARRA', nombre: 'Barra de Bar', subtitulo: 'Bebidas & Cócteles', ancho: 0.18, alto: 0.08, categoria: 'ATENCION' },

    // 3. Servicios y Operaciones
    { id: 'esp_banos', tipo: 'BANOS', nombre: 'Baños / Sanitarios', subtitulo: 'Servicios Higiénicos', ancho: 0.13, alto: 0.08, categoria: 'SERVICIOS' },
    { id: 'esp_cocina', tipo: 'COCINA', nombre: 'Cocina / Despacho', subtitulo: 'Salida de Platos', ancho: 0.16, alto: 0.10, categoria: 'SERVICIOS' },
    { id: 'esp_espera', tipo: 'ESPERA', nombre: 'Zona de Espera', subtitulo: 'Lounge / Recepción', ancho: 0.15, alto: 0.09, categoria: 'SERVICIOS' },

    // 4. Entretenimiento y Ambientes
    { id: 'esp_juegos', tipo: 'JUEGOS', nombre: 'Patio de Juegos', subtitulo: 'Zona Infantil', ancho: 0.18, alto: 0.12, categoria: 'ENTRETENIMIENTO' },
    { id: 'esp_terraza', tipo: 'TERRAZA', nombre: 'Terraza Exterior', subtitulo: 'Área al Aire Libre', ancho: 0.18, alto: 0.12, categoria: 'ENTRETENIMIENTO' },
    { id: 'esp_escenario', tipo: 'ESCENARIO', nombre: 'Escenario / Música', subtitulo: 'Tarima en Vivo', ancho: 0.18, alto: 0.10, categoria: 'ENTRETENIMIENTO' },

    // 5. Personalizado / A Medida (CU06 - Espacio libre configurable)
    { id: 'esp_personalizado', tipo: 'PERSONALIZADO', nombre: 'Espacio Personalizado', subtitulo: 'Tamaño libre a placer', ancho: 0.18, alto: 0.12, categoria: 'PERSONALIZADO' }
  ];

  tabHerramientas = signal<'mesas' | 'espacios'>('mesas');
  filtroCategoriaCatalogo = signal<'TODAS' | 'REDONDA' | 'CUADRADA' | 'RECTANGULAR'>('TODAS');
  filtroCategoriaEspacios = signal<'TODOS' | 'ACCESOS' | 'ATENCION' | 'SERVICIOS' | 'ENTRETENIMIENTO' | 'PERSONALIZADO'>('TODOS');
  modeloArrastrando: ModeloMesaPreset | null = null;
  espacioArrastrando: ModeloEspacioPreset | null = null;
  espacios = signal<EspacioPlano[]>([]);
  espacioSeleccionado = signal<EspacioPlano | null>(null);
  espacioEnArrastre: EspacioPlano | null = null;
  espacioEnRedimension: EspacioPlano | null = null;
  initialEspacioAncho: number = 0.14;
  initialEspacioAlto: number = 0.08;

  modelosFiltrados(): ModeloMesaPreset[] {
    const cat = this.filtroCategoriaCatalogo();
    if (cat === 'TODAS') return this.MODELOS_CATALOGO;
    return this.MODELOS_CATALOGO.filter(m => m.categoria === cat);
  }

  espaciosFiltrados(): ModeloEspacioPreset[] {
    const cat = this.filtroCategoriaEspacios();
    if (cat === 'TODOS') return this.ESPACIOS_CATALOGO;
    return this.ESPACIOS_CATALOGO.filter(e => e.categoria === cat);
  }

  // Drag and Drop desde la barra lateral de herramientas hacia el lienzo 2D
  onDragStartFromCatalog(event: DragEvent, modelo: ModeloMesaPreset): void {
    this.modeloArrastrando = modelo;
    this.espacioArrastrando = null;
    if (event.dataTransfer) {
      event.dataTransfer.setData('application/json', JSON.stringify({ tipoObjeto: 'mesa', data: modelo }));
      event.dataTransfer.effectAllowed = 'copy';
    }
  }

  onDragStartEspacioFromCatalog(event: DragEvent, preset: ModeloEspacioPreset): void {
    this.espacioArrastrando = preset;
    this.modeloArrastrando = null;
    if (event.dataTransfer) {
      event.dataTransfer.setData('application/json', JSON.stringify({ tipoObjeto: 'espacio', data: preset }));
      event.dataTransfer.effectAllowed = 'copy';
    }
  }

  onCanvasDragOver(event: DragEvent): void {
    event.preventDefault();
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'copy';
    }
  }

  onCanvasDrop(event: DragEvent): void {
    event.preventDefault();
    const area = this.areaSeleccionada();
    if (!area) {
      this.mostrarError('Primero debe seleccionar un área física.');
      return;
    }

    if (!this.canvasContainer) return;

    const rect = this.canvasContainer.nativeElement.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    let posX = (event.clientX - rect.left) / rect.width;
    let posY = (event.clientY - rect.top) / rect.height;

    // Acotar posiciones para que el elemento no quede fuera de los márgenes
    posX = Math.max(0.06, Math.min(0.94, posX));
    posY = Math.max(0.06, Math.min(0.94, posY));
    posX = Math.round(posX * 10000) / 10000;
    posY = Math.round(posY * 10000) / 10000;

    let modeloMesa = this.modeloArrastrando;
    let modeloEspacio = this.espacioArrastrando;

    if (!modeloMesa && !modeloEspacio && event.dataTransfer) {
      const dataStr = event.dataTransfer.getData('application/json');
      if (dataStr) {
        try {
          const parsed = JSON.parse(dataStr);
          if (parsed.tipoObjeto === 'espacio') {
            modeloEspacio = parsed.data;
          } else if (parsed.tipoObjeto === 'mesa') {
            modeloMesa = parsed.data;
          } else if (parsed.tipo) {
            modeloEspacio = parsed;
          } else if (parsed.forma) {
            modeloMesa = parsed;
          }
        } catch {}
      }
    }

    if (modeloEspacio) {
      this.crearEspacioDirecto(modeloEspacio, posX, posY);
      this.espacioArrastrando = null;
    } else if (modeloMesa) {
      this.crearMesaDirecta(modeloMesa, posX, posY);
      this.modeloArrastrando = null;
    }
  }

  crearEspacioDirecto(preset: ModeloEspacioPreset, posX?: number, posY?: number): void {
    const area = this.areaSeleccionada();
    if (!area) {
      this.mostrarError('Primero seleccione o cree un área.');
      return;
    }

    const count = this.espacios().length;
    if (posX === undefined || posY === undefined) {
      const col = count % 4;
      const row = Math.floor(count / 4) % 3;
      posX = Math.round((0.15 + col * 0.22) * 100) / 100;
      posY = Math.round((0.15 + row * 0.22) * 100) / 100;
    }

    let nombreFinal = preset.nombre;
    if (preset.tipo === 'PERSONALIZADO') {
      const resp = prompt('Nombre o descripción del espacio a medida:', 'Zona VIP / Buffet');
      if (resp && resp.trim()) {
        nombreFinal = resp.trim();
      }
    }

    const nuevo: EspacioPlano = {
      id: 'esp_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
      tipo: preset.tipo,
      nombre: nombreFinal,
      posicion_x: posX,
      posicion_y: posY,
      ancho: preset.ancho,
      alto: preset.alto,
      rotacion: 0
    };

    this.espacios.update(list => [...list, nuevo]);
    this.seleccionarEspacio(nuevo);
    this.hayCambios.set(true);
    this.mostrarMensaje(`Espacio '${nuevo.nombre}' añadido al plano.`);
  }

  seleccionarEspacio(espacio: EspacioPlano, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    this.espacioSeleccionado.set(espacio);
    this.mesaSeleccionada.set(null);
  }

  onEspacioPointerDown(event: PointerEvent, espacio: EspacioPlano): void {
    event.stopPropagation();
    event.preventDefault();
    this.seleccionarEspacio(espacio);
    this.espacioEnArrastre = espacio;
    this.mesaEnArrastre = null;

    this.dragStartPointerX = event.clientX;
    this.dragStartPointerY = event.clientY;
    this.initialMesaX = espacio.posicion_x;
    this.initialMesaY = espacio.posicion_y;

    const target = event.currentTarget as HTMLElement;
    if (target.setPointerCapture) {
      target.setPointerCapture(event.pointerId);
    }
  }

  onEspacioResizePointerDown(event: PointerEvent, espacio: EspacioPlano): void {
    event.stopPropagation();
    event.preventDefault();
    this.seleccionarEspacio(espacio);
    this.espacioEnRedimension = espacio;
    this.espacioEnArrastre = null;
    this.mesaEnArrastre = null;

    this.dragStartPointerX = event.clientX;
    this.dragStartPointerY = event.clientY;
    this.initialEspacioAncho = espacio.ancho || 0.14;
    this.initialEspacioAlto = espacio.alto || 0.08;

    const target = event.currentTarget as HTMLElement;
    if (target.setPointerCapture) {
      target.setPointerCapture(event.pointerId);
    }
  }

  ajustarDimensionEspacio(espacio: EspacioPlano, deltaAncho: number, deltaAlto: number): void {
    const actAncho = espacio.ancho || 0.14;
    const actAlto = espacio.alto || 0.08;
    const nuevoAncho = Math.max(0.05, Math.min(0.85, Math.round((actAncho + deltaAncho) * 100) / 100));
    const nuevoAlto = Math.max(0.04, Math.min(0.85, Math.round((actAlto + deltaAlto) * 100) / 100));
    espacio.ancho = nuevoAncho;
    espacio.alto = nuevoAlto;
    this.hayCambios.set(true);
  }

  rotarEspacio(espacio: EspacioPlano): void {
    const rot = ((espacio.rotacion || 0) + 90) % 360;
    espacio.rotacion = rot;
    this.hayCambios.set(true);
    this.mostrarMensaje(`Rotación de '${espacio.nombre}': ${rot}°`);
  }

  renombrarEspacio(espacio: EspacioPlano): void {
    const nuevoNombre = prompt('Nombre o etiqueta para este espacio:', espacio.nombre);
    if (nuevoNombre && nuevoNombre.trim()) {
      espacio.nombre = nuevoNombre.trim();
      this.hayCambios.set(true);
    }
  }

  eliminarEspacio(espacio: EspacioPlano): void {
    if (!confirm(`¿Desea eliminar el espacio '${espacio.nombre}' del plano?`)) return;
    this.espacios.update(list => list.filter(e => e.id !== espacio.id));
    if (this.espacioSeleccionado()?.id === espacio.id) {
      this.espacioSeleccionado.set(null);
    }
    this.hayCambios.set(true);
    this.mostrarMensaje(`Espacio '${espacio.nombre}' retirado.`);
  }

  crearMesaDirecta(modelo: ModeloMesaPreset, posX?: number, posY?: number): void {
    const area = this.areaSeleccionada();
    if (!area) {
      this.mostrarError('Primero seleccione o cree un área.');
      return;
    }

    const count = this.mesas().length;
    const sugeridoNum = 'M' + (count + 1);

    if (posX === undefined || posY === undefined) {
      const col = count % 4;
      const row = Math.floor(count / 4) % 3;
      posX = Math.round((0.2 + col * 0.2) * 100) / 100;
      posY = Math.round((0.25 + row * 0.25) * 100) / 100;
    }

    const datos: MesaCrear = {
      numero: sugeridoNum,
      nombre: modelo.nombre,
      capacidad: modelo.capacidad,
      forma: modelo.forma,
      rotacion: 0,
      posicion_x: posX,
      posicion_y: posY,
      es_fija: false,
      combinable: true
    };

    this.mesaService.crearMesa(area.id_area, datos).subscribe({
      next: (nueva) => {
        this.mostrarMensaje(`Mesa '${nueva.numero}' (${modelo.nombre}) agregada.`);
        const listaActual = [...this.mesas(), nueva];
        this.mesas.set(listaActual);
        this.seleccionarMesa(nueva);
        this.hayCambios.set(true);
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al agregar la mesa.')
    });
  }
  restauranteId = signal<number>(0);
  restaurante = signal<Restaurante | null>(null);
  areas = signal<AreaRestaurante[]>([]);
  areaSeleccionada = signal<AreaRestaurante | null>(null);
  mesas = signal<Mesa[]>([]);
  combinaciones = signal<MesaCombinacion[]>([]);
  mesaSeleccionada = signal<Mesa | null>(null);
  mesaParaCombinar = signal<Mesa | null>(null);

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
    combinable: true,
    posicion_x: 0.5,
    posicion_y: 0.5
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

  mostrarError(err: any): void {
    let mensaje = 'Ha ocurrido un error inesperado.';
    if (typeof err === 'string') {
      mensaje = err;
    } else if (Array.isArray(err)) {
      mensaje = err.map(e => e.msg || e.detail || JSON.stringify(e)).join(', ');
    } else if (err && typeof err === 'object') {
      if (err.detail) {
        mensaje = Array.isArray(err.detail)
          ? err.detail.map((e: any) => e.msg || e.detail || JSON.stringify(e)).join(', ')
          : String(err.detail);
      } else if (err.message) {
        mensaje = String(err.message);
      } else {
        mensaje = JSON.stringify(err);
      }
    }
    this.error.set(mensaje);
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
        if (lista.length === 0) {
          this.crearAreaPorDefecto();
        } else if (!this.areaSeleccionada()) {
          this.seleccionarArea(lista[0]);
        }
      },
      error: () => {
        this.cargando.set(false);
        this.mostrarError('Error al listar las áreas del restaurante.');
      }
    });
  }

  crearAreaPorDefecto(): void {
    const datos: AreaRestauranteCrear = {
      nombre: 'Salón Principal',
      descripcion: 'Área física principal del establecimiento',
      ancho_mapa: 1000,
      alto_mapa: 600,
      orden: 1
    };
    this.areaService.crearArea(this.restauranteId(), datos).subscribe({
      next: (nueva) => {
        this.areaService.listarAreasPorRestaurante(this.restauranteId(), false).subscribe(lista => {
          this.areas.set(lista);
          this.seleccionarArea(nueva);
        });
      },
      error: () => this.cargando.set(false)
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
    this.espacioSeleccionado.set(null);
    this.espacios.set(area.elementos || []);
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
    if (!this.canvasContainer) return;
    const rect = this.canvasContainer.nativeElement.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    const deltaX = (event.clientX - this.dragStartPointerX) / rect.width;
    const deltaY = (event.clientY - this.dragStartPointerY) / rect.height;

    if (this.espacioEnRedimension) {
      let newW = Math.max(0.04, Math.min(0.85, this.initialEspacioAncho + deltaX));
      let newH = Math.max(0.04, Math.min(0.85, this.initialEspacioAlto + deltaY));
      newW = Math.round(newW * 1000) / 1000;
      newH = Math.round(newH * 1000) / 1000;
      this.espacioEnRedimension.ancho = newW;
      this.espacioEnRedimension.alto = newH;
      this.hayCambios.set(true);
    } else if (this.mesaEnArrastre) {
      let newX = Math.max(0.04, Math.min(0.94, this.initialMesaX + deltaX));
      let newY = Math.max(0.04, Math.min(0.94, this.initialMesaY + deltaY));
      newX = Math.round(newX * 10000) / 10000;
      newY = Math.round(newY * 10000) / 10000;
      this.mesaEnArrastre.posicion_x = newX;
      this.mesaEnArrastre.posicion_y = newY;
      this.hayCambios.set(true);
    } else if (this.espacioEnArrastre) {
      let newX = Math.max(0.04, Math.min(0.94, this.initialMesaX + deltaX));
      let newY = Math.max(0.04, Math.min(0.94, this.initialMesaY + deltaY));
      newX = Math.round(newX * 10000) / 10000;
      newY = Math.round(newY * 10000) / 10000;
      this.espacioEnArrastre.posicion_x = newX;
      this.espacioEnArrastre.posicion_y = newY;
      this.hayCambios.set(true);
    }
  }

  onPointerUp(event: PointerEvent): void {
    if (this.espacioEnRedimension) {
      const target = event.currentTarget as HTMLElement;
      if (target.releasePointerCapture && target.hasPointerCapture(event.pointerId)) {
        target.releasePointerCapture(event.pointerId);
      }
      this.espacioEnRedimension = null;
    }
    if (this.mesaEnArrastre) {
      const target = event.currentTarget as HTMLElement;
      if (target.releasePointerCapture && target.hasPointerCapture(event.pointerId)) {
        target.releasePointerCapture(event.pointerId);
      }
      this.mesaEnArrastre = null;
    }
    if (this.espacioEnArrastre) {
      const target = event.currentTarget as HTMLElement;
      if (target.releasePointerCapture && target.hasPointerCapture(event.pointerId)) {
        target.releasePointerCapture(event.pointerId);
      }
      this.espacioEnArrastre = null;
    }
  }

  seleccionarMesa(mesa: Mesa): void {
    this.mesaSeleccionada.set(mesa);
    this.espacioSeleccionado.set(null);
  }

  rotarMesa90(mesa: Mesa): void {
    mesa.rotacion = (mesa.rotacion + 90) % 360;
    this.hayCambios.set(true);
  }

  toggleFija(mesa: Mesa): void {
    this.mesaService.actualizarMesa(mesa.id_mesa, {
      es_fija: !mesa.es_fija,
      posicion_x: mesa.posicion_x,
      posicion_y: mesa.posicion_y
    }).subscribe({
      next: (actualizada) => {
        mesa.es_fija = actualizada.es_fija;
        if (this.mesaSeleccionada()?.id_mesa === mesa.id_mesa) {
          this.mesaSeleccionada.set({ ...mesa });
        }
        this.mesas.set([...this.mesas()]);
        this.mostrarMensaje(`Mesa ${mesa.numero} ahora es ${mesa.es_fija ? 'fija' : 'movible'}.`);
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al actualizar estado fijo de la mesa.')
    });
  }

  toggleCombinable(mesa: Mesa): void {
    this.mesaService.actualizarMesa(mesa.id_mesa, {
      combinable: !mesa.combinable,
      posicion_x: mesa.posicion_x,
      posicion_y: mesa.posicion_y
    }).subscribe({
      next: (actualizada) => {
        mesa.combinable = actualizada.combinable;
        if (this.mesaSeleccionada()?.id_mesa === mesa.id_mesa) {
          this.mesaSeleccionada.set({ ...mesa });
        }
        this.mesas.set([...this.mesas()]);
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

    this.distribucionService.guardarDistribucion(area.id_area, posiciones, this.espacios()).subscribe({
      next: (res) => {
        this.guardandoDistribucion.set(false);
        this.hayCambios.set(false);
        if (res && res.mesas && res.mesas.length > 0) {
          this.mesas.set(res.mesas);
        }
        if (res && res.elementos) {
          this.espacios.set(res.elementos);
        }
        this.mostrarMensaje(res.mensaje || 'Distribución y espacios guardados exitosamente.');
        if (onSuccess) onSuccess();
      },
      error: (err) => {
        this.guardandoDistribucion.set(false);
        this.mostrarError(err.error?.detail || err.error || 'Error al guardar la distribución del plano.');
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
    const count = this.mesas().length;
    const sugeridoNum = 'M' + (count + 1);
    const col = count % 4;
    const row = Math.floor(count / 4) % 3;
    const posX = Math.round((0.2 + (col * 0.2)) * 100) / 100;
    const posY = Math.round((0.25 + (row * 0.25)) * 100) / 100;

    this.formMesa = {
      numero: sugeridoNum,
      nombre: '',
      capacidad: 4,
      forma: 'CUADRADA',
      rotacion: 0,
      es_fija: false,
      combinable: true,
      posicion_x: posX,
      posicion_y: posY
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
      combinable: mesa.combinable,
      posicion_x: Number(mesa.posicion_x),
      posicion_y: Number(mesa.posicion_y)
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
      const nuevaCapacidad = Number(this.formMesa.capacidad) || 1;

      // Actualizar reactivamente de inmediato en memoria para que el diagrama cambie al instante
      m.numero = this.formMesa.numero.trim();
      m.capacidad = nuevaCapacidad;
      m.es_fija = this.formMesa.es_fija;
      m.combinable = this.formMesa.combinable;

      if (this.mesaSeleccionada()?.id_mesa === m.id_mesa) {
        this.mesaSeleccionada.set({ ...m });
      }
      this.mesas.set([...this.mesas()]);
      this.hayCambios.set(true);

      const datos: MesaActualizar = {
        numero: m.numero,
        nombre: m.nombre,
        capacidad: nuevaCapacidad,
        forma: m.forma,
        rotacion: m.rotacion,
        es_fija: m.es_fija,
        combinable: m.combinable,
        posicion_x: m.posicion_x,
        posicion_y: m.posicion_y
      };
      this.mesaService.actualizarMesa(m.id_mesa, datos).subscribe({
        next: (act) => {
          this.mostrarMensaje(`Mesa '${act.numero}' actualizada correctamente.`);
          this.cerrarModalMesa();
          const idx = this.mesas().findIndex(item => item.id_mesa === act.id_mesa);
          if (idx !== -1) {
            const list = [...this.mesas()];
            list[idx] = {
              ...list[idx],
              ...act,
              posicion_x: m.posicion_x,
              posicion_y: m.posicion_y
            };
            this.mesas.set(list);
            if (this.mesaSeleccionada()?.id_mesa === act.id_mesa) {
              this.mesaSeleccionada.set(list[idx]);
            }
          }
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
        combinable: this.formMesa.combinable,
        posicion_x: this.formMesa.posicion_x,
        posicion_y: this.formMesa.posicion_y
      };
      this.mesaService.crearMesa(area.id_area, datos).subscribe({
        next: (nueva) => {
          this.mostrarMensaje(`Mesa '${nueva.numero}' agregada correctamente.`);
          this.cerrarModalMesa();
          const list = [...this.mesas(), nueva];
          this.mesas.set(list);
          this.seleccionarMesa(nueva);
          this.hayCambios.set(true);
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
        this.mesas.set(this.mesas().filter(m => m.id_mesa !== mesa.id_mesa));
        this.hayCambios.set(true);
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

  // --- CU19: CONECTORES VISUALES Y COMBINACIÓN DE MESAS ---

  getLineasCombinaciones(): {
    combinacion: MesaCombinacion;
    m1: Mesa;
    m2: Mesa;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    midX: number;
    midY: number;
    capacidad: number;
  }[] {
    const res: any[] = [];
    const mesasMap = new Map<number, Mesa>();
    for (const m of this.mesas()) {
      if (m.activo) mesasMap.set(m.id_mesa, m);
    }

    for (const c of this.combinaciones()) {
      if (!c.activo) continue;
      const m1 = mesasMap.get(c.id_mesa_origen);
      const m2 = mesasMap.get(c.id_mesa_destino);
      if (m1 && m2) {
        const x1 = Number(m1.posicion_x) * 100;
        const y1 = Number(m1.posicion_y) * 100;
        const x2 = Number(m2.posicion_x) * 100;
        const y2 = Number(m2.posicion_y) * 100;
        const cap = c.capacidad_combinada || (m1.capacidad + m2.capacidad);
        res.push({
          combinacion: c,
          m1,
          m2,
          x1,
          y1,
          x2,
          y2,
          midX: Math.round(((x1 + x2) / 2) * 10) / 10,
          midY: Math.round(((y1 + y2) / 2) * 10) / 10,
          capacidad: cap
        });
      }
    }
    return res;
  }

  iniciarModoCombinacion(mesa: Mesa): void {
    if (mesa.es_fija) {
      this.mostrarError('Las mesas fijas no se pueden combinar con otras.');
      return;
    }
    if (!mesa.combinable) {
      this.toggleCombinable(mesa);
    }
    this.mesaParaCombinar.set(mesa);
    this.mostrarMensaje(`🔗 Modo Combinar: Seleccione otra mesa para unirla con Mesa ${mesa.numero}.`);
  }

  cancelarModoCombinar(): void {
    this.mesaParaCombinar.set(null);
  }

  onMesaClick(mesa: Mesa, event: MouseEvent): void {
    event.stopPropagation();
    const origen = this.mesaParaCombinar();
    if (origen) {
      if (origen.id_mesa === mesa.id_mesa) {
        this.cancelarModoCombinar();
        return;
      }
      this.combinarDirectamente(origen, mesa);
      return;
    }
    this.seleccionarMesa(mesa);
  }

  combinarDirectamente(m1: Mesa, m2: Mesa): void {
    if (m2.es_fija) {
      this.mostrarError(`La mesa ${m2.numero} está fijada y no puede combinarse.`);
      return;
    }

    const area = this.areaSeleccionada();
    if (!area) return;

    // Verificar si ya existe combinación activa entre ambas
    const yaExiste = this.combinaciones().some(c =>
      c.activo &&
      ((c.id_mesa_origen === m1.id_mesa && c.id_mesa_destino === m2.id_mesa) ||
       (c.id_mesa_origen === m2.id_mesa && c.id_mesa_destino === m1.id_mesa))
    );
    if (yaExiste) {
      this.mostrarError(`Las mesas ${m1.numero} y ${m2.numero} ya están combinadas.`);
      this.mesaParaCombinar.set(null);
      return;
    }

    // Si m2 no era combinable, activarla
    if (!m2.combinable) {
      m2.combinable = true;
      this.mesaService.actualizarMesa(m2.id_mesa, { combinable: true }).subscribe();
    }

    const payload: MesaCombinacionCrear = {
      id_mesa_origen: m1.id_mesa,
      id_mesa_destino: m2.id_mesa,
      descripcion: `Unión directa: ${m1.numero} + ${m2.numero}`
    };

    this.combinacionService.crearCombinacion(payload, area.id_area).subscribe({
      next: (nueva) => {
        const totalPax = nueva.capacidad_combinada || (m1.capacidad + m2.capacidad);
        this.mostrarMensaje(`¡Mesas ${m1.numero} y ${m2.numero} unidas con éxito! Capacidad combinada: ${totalPax} comensales.`);
        this.mesaParaCombinar.set(null);
        const lista = this.combinaciones().filter(c => c.id_mesa_combinacion !== nueva.id_mesa_combinacion);
        this.combinaciones.set([...lista, nueva]);
      },
      error: (err) => {
        this.mostrarError(err.error?.detail || 'Error al combinar las mesas.');
        this.mesaParaCombinar.set(null);
      }
    });
  }

  confirmarDescombinar(c: MesaCombinacion, event?: MouseEvent): void {
    if (event) event.stopPropagation();
    const nom1 = c.numero_mesa_origen || 'Mesa origen';
    const nom2 = c.numero_mesa_destino || 'Mesa destino';
    if (!confirm(`¿Desea separar y descombinar la unión entre ${nom1} y ${nom2}?`)) {
      return;
    }
    this.desactivarCombinacion(c);
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

    const area = this.areaSeleccionada();
    this.combinacionService.crearCombinacion(payload, area?.id_area).subscribe({
      next: (comb) => {
        const cap = comb.capacidad_combinada || comb.capacidad_total || this.capacidadCombinadaPreview;
        this.mostrarMensaje(`Combinación creada exitosamente (Capacidad total: ${cap} comensales).`);
        this.cerrarModalCombinacion();
        const lista = this.combinaciones().filter(c => c.id_mesa_combinacion !== comb.id_mesa_combinacion);
        this.combinaciones.set([...lista, comb]);
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al crear la combinación de mesas.')
    });
  }

  desactivarCombinacion(c: MesaCombinacion): void {
    this.combinacionService.desactivarCombinacion(c.id_mesa_combinacion).subscribe({
      next: () => {
        this.mostrarMensaje('Combinación de mesas desvinculada con éxito.');
        this.combinaciones.set(this.combinaciones().filter(item => item.id_mesa_combinacion !== c.id_mesa_combinacion));
      },
      error: (err) => this.mostrarError(err.error?.detail || 'Error al desactivar combinación.')
    });
  }
}
