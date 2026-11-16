import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
import { MesaSvgComponent } from '../../../shared/mesa-svg/mesa-svg.component';
import { EspacioSvgComponent } from '../../../shared/espacio-svg/espacio-svg.component';
// CASO DE USO: CU20 - Consultar disponibilidad & CU21 - Realizar reserva
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { RestauranteService } from '../../../core/services/restaurante.service';
import { AreaRestauranteService } from '../../../core/services/area-restaurante.service';
import { ReservaService } from '../../../core/services/reserva.service';
import { PlanificacionService } from '../../../core/services/planificacion.service';

import { Restaurante } from '../../../core/models/restaurante.model';
import { AreaRestaurante } from '../../../core/models/area-restaurante.model';
import {
  MesaDisponibilidad,
  CombinacionDisponible,
  DisponibilidadRespuesta,
  ConsultaDisponibilidad,
  ReservaCrear
} from '../../../core/models/reserva.model';

@Component({
  selector: 'app-nueva-reserva',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule, MesaSvgComponent, EspacioSvgComponent],
  templateUrl: './nueva-reserva.component.html',
  styleUrls: ['./nueva-reserva.component.css']
})
export class NuevaReservaComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private restauranteService = inject(RestauranteService);
  private areaService = inject(AreaRestauranteService);
  private reservaService = inject(ReservaService);
  private planificacionService = inject(PlanificacionService);

  restauranteId = signal<number>(0);
  restaurante = signal<Restaurante | null>(null);
  areas = signal<AreaRestaurante[]>([]);
  idPlanificacion: number | null = null;

  // Filtros de Consulta
  filtroArea: number | null = null;
  filtroFecha: string = '';
  filtroHoraInicio: string = '20:00';
  filtroHoraFin: string = '22:00';
  filtroPersonas: number = 2;
  fechaMinima: string = '';

  // Estado de Consulta y Mapa
  disponibilidad = signal<DisponibilidadRespuesta | null>(null);
  consultando = signal<boolean>(false);
  filtrosModificados = signal<boolean>(false);

  // Selección de mesas para reservar
  mesasSeleccionadasIds: number[] = [];
  combinacionSeleccionada: CombinacionDisponible | null = null;
  observaciones: string = '';
  confirmandoReserva = signal<boolean>(false);

  mensajeExito = signal<string | null>(null);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.restauranteId.set(Number(idParam));
      this.cargarRestaurante();
      this.cargarAreas();
    }

    const qPersonas = this.route.snapshot.queryParamMap.get('personas');
    if (qPersonas) {
      this.filtroPersonas = Math.max(1, Number(qPersonas));
    }

    const qPlan = this.route.snapshot.queryParamMap.get('id_planificacion');
    if (qPlan) {
      this.idPlanificacion = Number(qPlan);
      this.planificacionService.obtenerPlanificacion(this.idPlanificacion).subscribe({
        next: (plan) => {
          if (plan && plan.cantidad_personas) {
            this.filtroPersonas = plan.cantidad_personas;
            if (this.filtroArea) {
              this.consultarDisponibilidad();
            }
          }
        }
      });
    }

    const hoy = new Date();
    this.fechaMinima = hoy.toISOString().split('T')[0];
    this.filtroFecha = this.fechaMinima;
  }

  cargarRestaurante(): void {
    this.restauranteService.getRestaurante(this.restauranteId()).subscribe({
      next: (resto) => this.restaurante.set(resto),
      error: () => this.error.set('No se pudo cargar la información del restaurante.')
    });
  }

  cargarAreas(): void {
    this.areaService.listarAreasPorRestaurante(this.restauranteId(), true).subscribe({
      next: (lista) => {
        this.areas.set(lista);
        if (lista.length > 0) {
          this.filtroArea = lista[0].id_area;
          this.consultarDisponibilidad();
        }
      },
      error: () => this.error.set('No se pudieron cargar las áreas del restaurante.')
    });
  }

  onFiltroCambiado(): void {
    if (this.filtroArea && this.filtroFecha && this.filtroHoraInicio && this.filtroHoraFin && this.filtroPersonas >= 1) {
      this.consultarDisponibilidad();
    } else if (this.disponibilidad()) {
      this.filtrosModificados.set(true);
    }
  }

  // --- NAVEGACIÓN POR PESTAÑAS ESTILO EXCEL (CU20) ---
  seleccionarArea(idArea: number): void {
    if (this.filtroArea === idArea) return;
    this.filtroArea = idArea;
    this.deseleccionarTodo();
    if (this.filtroFecha && this.filtroHoraInicio && this.filtroHoraFin && this.filtroPersonas > 0) {
      this.consultarDisponibilidad();
    } else {
      this.onFiltroCambiado();
    }
  }

  getMesasDisponiblesArea(): number {
    const disp = this.disponibilidad();
    if (!disp) return 0;
    return disp.mesas.filter(m => m.estado_disponibilidad === 'DISPONIBLE').length;
  }

  // --- CU20: CONSULTAR DISPONIBILIDAD ---
  consultarDisponibilidad(): void {
    if (!this.filtroArea || !this.filtroFecha || !this.filtroHoraInicio || !this.filtroHoraFin || this.filtroPersonas < 1) {
      return;
    }

    this.consultando.set(true);
    this.error.set(null);
    this.deseleccionarTodo();

    const consulta: ConsultaDisponibilidad = {
      id_area: this.filtroArea,
      fecha: this.filtroFecha,
      hora_inicio: this.filtroHoraInicio.length === 5 ? `${this.filtroHoraInicio}:00` : this.filtroHoraInicio,
      hora_fin: this.filtroHoraFin.length === 5 ? `${this.filtroHoraFin}:00` : this.filtroHoraFin,
      cantidad_personas: Number(this.filtroPersonas)
    };

    this.reservaService.consultarDisponibilidad(this.restauranteId(), consulta).subscribe({
      next: (resp) => {
        this.disponibilidad.set(resp);
        this.consultando.set(false);
        this.filtrosModificados.set(false);
      },
      error: (err) => {
        this.consultando.set(false);
        this.error.set(err.error?.detail || 'Error al consultar disponibilidad de mesas.');
      }
    });
  }

  // --- INTERACCIÓN Y SELECCIÓN DE MESAS & COMBINACIONES ---
  estaMesaSeleccionada(idMesa: number): boolean {
    return this.mesasSeleccionadasIds.includes(idMesa);
  }

  encontrarCombinacionParaMesa(idMesa: number): CombinacionDisponible | null {
    const disp = this.disponibilidad();
    if (!disp || !disp.combinaciones) return null;
    return disp.combinaciones.find(c => c.mesas.includes(idMesa)) || null;
  }

  combMesaApta(idMesa: number): CombinacionDisponible | null {
    const comb = this.encontrarCombinacionParaMesa(idMesa);
    if (comb && comb.seleccionable) {
      return comb;
    }
    return null;
  }

  seleccionarMesaIndividual(mesa: MesaDisponibilidad): void {
    // Si ya confirmó la reserva, bloquear selección hasta pulsar 'Hacer otra reserva'
    if (this.mensajeExito()) {
      return;
    }

    if (mesa.estado_disponibilidad === 'NO_DISPONIBLE') {
      return;
    }

    // 1. Si la mesa clicada ya forma parte de la selección activa (individual o combinación), se desmarca
    if (this.estaMesaSeleccionada(mesa.id_mesa)) {
      this.deseleccionarTodo();
      return;
    }

    // 2. Si ya hay OTRA selección activa, no permitir cambiar sin desmarcar primero la selección anterior
    if (this.mesasSeleccionadasIds.length > 0) {
      return;
    }

    const combApta = this.combMesaApta(mesa.id_mesa);

    // Si la mesa individual es chica para el grupo, pero forma parte de una combinación apta:
    if (mesa.capacidad < this.filtroPersonas && combApta) {
      this.seleccionarCombinacion(combApta);
      return;
    }

    // Si la mesa es chica para el grupo y no tiene combinación apta, no se permite reservar individualmente
    if (mesa.capacidad < this.filtroPersonas) {
      return;
    }

    // Selección de mesa individual que cubre la capacidad
    this.combinacionSeleccionada = null;
    this.mesasSeleccionadasIds = [mesa.id_mesa];
  }

  esCombinacionSeleccionada(comb: CombinacionDisponible): boolean {
    return this.combinacionSeleccionada?.id_combinacion === comb.id_combinacion;
  }

  seleccionarCombinacion(comb: CombinacionDisponible): void {
    // Si ya confirmó la reserva, bloquear selección
    if (this.mensajeExito()) {
      return;
    }

    if (!comb.seleccionable) {
      return;
    }

    // Si ya está seleccionada esta combinación, se desmarca
    if (this.esCombinacionSeleccionada(comb)) {
      this.deseleccionarTodo();
      return;
    }

    // Si ya hay OTRA selección activa, exigir desmarcar primero
    if (this.mesasSeleccionadasIds.length > 0) {
      return;
    }

    this.combinacionSeleccionada = comb;
    this.mesasSeleccionadasIds = [...comb.mesas];
  }

  deseleccionarTodo(): void {
    this.mesasSeleccionadasIds = [];
    this.combinacionSeleccionada = null;
  }

  nuevaReservaNueva(): void {
    this.mensajeExito.set(null);
    this.error.set(null);
    this.deseleccionarTodo();
    this.consultarDisponibilidad();
  }

  getTextoMesasSeleccionadas(): string {
    if (this.combinacionSeleccionada) {
      return `Combinación (${this.combinacionSeleccionada.numeros_mesas.join(' + ')})`;
    }
    const disp = this.disponibilidad();
    if (!disp) return '';
    const seleccionadas = disp.mesas.filter(m => this.mesasSeleccionadasIds.includes(m.id_mesa));
    return seleccionadas.map(m => m.numero).join(', ');
  }

  getCapacidadTotalSeleccionada(): number {
    if (this.combinacionSeleccionada) {
      return this.combinacionSeleccionada.capacidad_total;
    }
    const disp = this.disponibilidad();
    if (!disp) return 0;
    const seleccionadas = disp.mesas.filter(m => this.mesasSeleccionadasIds.includes(m.id_mesa));
    return seleccionadas.reduce((acc, m) => acc + m.capacidad, 0);
  }

  getTooltipMesa(mesa: MesaDisponibilidad): string {
    if (this.estaMesaSeleccionada(mesa.id_mesa)) {
      if (this.combinacionSeleccionada) {
        return `Mesa ${mesa.numero} (Seleccionada como parte de la combinación de ${this.combinacionSeleccionada.capacidad_total}p). Clic para desmarcar.`;
      }
      return `Mesa ${mesa.numero} (Seleccionada para reservar). Clic para desmarcar.`;
    }
    if (mesa.estado_disponibilidad === 'NO_DISPONIBLE') {
      return `Mesa ${mesa.numero} - Ya cuenta con una reserva en este horario`;
    }

    const combApta = this.combMesaApta(mesa.id_mesa);
    if (combApta && mesa.capacidad < this.filtroPersonas) {
      return `Mesa ${mesa.numero} (${mesa.capacidad}p) - En combinación apta con ${combApta.numeros_mesas.filter(n => n !== mesa.numero).join(',')} (${combApta.capacidad_total}p para el grupo). Clic para seleccionar grupo`;
    }

    if (mesa.capacidad >= this.filtroPersonas) {
      return `Mesa ${mesa.numero} (${mesa.capacidad}p) - Clic para seleccionar`;
    }
    return `Mesa ${mesa.numero} - Capacidad insuficiente (${mesa.capacidad}p para ${this.filtroPersonas} personas)`;
  }

  // --- SEMÁFORO VISUAL ARQUITECTÓNICO (CU20) ---
  getColorFondoMesa(mesa: MesaDisponibilidad): string {
    if (this.estaMesaSeleccionada(mesa.id_mesa)) return '#eff6ff'; // 🔵 Azul selección (alineado con leyenda)
    if (mesa.estado_disponibilidad === 'NO_DISPONIBLE') return '#fef2f2'; // 🔴 Rojo reservado

    // Si forma parte de una combinación activa apta para el grupo:
    const combApta = this.combMesaApta(mesa.id_mesa);
    if (combApta && mesa.capacidad < this.filtroPersonas) {
      return '#ecfdf5'; // 🟢 Verde por combinación apta
    }

    if (mesa.capacidad >= this.filtroPersonas) return '#ecfdf5'; // 🟢 Verde libre compatible
    return '#fffbeb'; // 🟡 Amarillo incompatible
  }

  getColorTrazoMesa(mesa: MesaDisponibilidad): string {
    if (this.estaMesaSeleccionada(mesa.id_mesa)) return '#2563eb'; // 🔵 Azul trazo
    if (mesa.estado_disponibilidad === 'NO_DISPONIBLE') return '#dc2626';

    const combApta = this.combMesaApta(mesa.id_mesa);
    if (combApta && mesa.capacidad < this.filtroPersonas) {
      return '#059669';
    }

    if (mesa.capacidad >= this.filtroPersonas) return '#059669';
    return '#d97706';
  }

  getColorSillaMesa(mesa: MesaDisponibilidad): string {
    if (this.estaMesaSeleccionada(mesa.id_mesa)) return '#dbeafe'; // 🔵 Azul silla
    if (mesa.estado_disponibilidad === 'NO_DISPONIBLE') return '#fee2e2';

    const combApta = this.combMesaApta(mesa.id_mesa);
    if (combApta && mesa.capacidad < this.filtroPersonas) {
      return '#d1fae5';
    }

    if (mesa.capacidad >= this.filtroPersonas) return '#d1fae5';
    return '#fef3c7';
  }

  getColorTextoMesa(mesa: MesaDisponibilidad): string {
    if (this.estaMesaSeleccionada(mesa.id_mesa)) return '#1d4ed8'; // 🔵 Azul texto
    if (mesa.estado_disponibilidad === 'NO_DISPONIBLE') return '#991b1b';

    const combApta = this.combMesaApta(mesa.id_mesa);
    if (combApta && mesa.capacidad < this.filtroPersonas) {
      return '#065f46';
    }

    if (mesa.capacidad >= this.filtroPersonas) return '#065f46';
    return '#92400e';
  }

  getLineasCombinaciones(): {
    combinacion: CombinacionDisponible;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    midX: number;
    midY: number;
    capacidad: number;
    disponible: boolean;
    seleccionable: boolean;
    seleccionada: boolean;
  }[] {
    const disp = this.disponibilidad();
    if (!disp || !disp.combinaciones) return [];
    const res: any[] = [];
    const mesasMap = new Map<number, MesaDisponibilidad>();
    for (const m of disp.mesas) {
      mesasMap.set(m.id_mesa, m);
    }

    for (const c of disp.combinaciones) {
      if (c.mesas.length >= 2) {
        const m1 = mesasMap.get(c.mesas[0]);
        const m2 = mesasMap.get(c.mesas[1]);
        if (m1 && m2) {
          const x1 = Number(m1.posicion_x) * 100;
          const y1 = Number(m1.posicion_y) * 100;
          const x2 = Number(m2.posicion_x) * 100;
          const y2 = Number(m2.posicion_y) * 100;
          res.push({
            combinacion: c,
            x1,
            y1,
            x2,
            y2,
            midX: Math.round(((x1 + x2) / 2) * 10) / 10,
            midY: Math.round(((y1 + y2) / 2) * 10) / 10,
            capacidad: c.capacidad_total,
            disponible: c.disponible,
            seleccionable: c.seleccionable,
            seleccionada: this.esCombinacionSeleccionada(c)
          });
        }
      }
    }
    return res;
  }

  // --- CU21: CONFIRMAR RESERVA ---
  confirmarReserva(): void {
    const disp = this.disponibilidad();
    if (!disp || this.mesasSeleccionadasIds.length === 0) {
      return;
    }

    this.confirmandoReserva.set(true);
    this.error.set(null);

    const payload: ReservaCrear = {
      id_restaurante: this.restauranteId(),
      id_area: disp.id_area,
      fecha_reserva: disp.fecha,
      hora_inicio: disp.hora_inicio,
      hora_fin: disp.hora_fin,
      cantidad_personas: disp.cantidad_personas,
      mesas: this.mesasSeleccionadasIds,
      id_planificacion: this.idPlanificacion,
      observaciones: this.observaciones.trim() ? this.observaciones.trim() : null
    };

    this.reservaService.crearReserva(payload).subscribe({
      next: (reserva) => {
        this.confirmandoReserva.set(false);
        this.deseleccionarTodo();
        this.mensajeExito.set(
          `¡Reserva confirmada con éxito! Código #${reserva.id_reserva} en ${reserva.nombre_restaurante} para el ${reserva.fecha_reserva} a las ${reserva.hora_inicio.substring(0, 5)}.`
        );
        // Actualizar disponibilidad para reflejar la mesa recién reservada
        this.consultarDisponibilidad();
      },
      error: (err) => {
        this.confirmandoReserva.set(false);
        if (err.status === 409) {
          // Manejo del conflicto 409: la mesa fue tomada concurrentemente
          this.error.set(
            err.error?.detail ||
            'La mesa seleccionada ya no está disponible para el horario solicitado. El mapa se ha actualizado para que seleccione otra opción.'
          );
          this.deseleccionarTodo();
          this.consultarDisponibilidad();
        } else {
          this.error.set(err.error?.detail || 'Error al procesar la reserva.');
        }
      }
    });
  }
}
