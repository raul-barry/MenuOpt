import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
// CASO DE USO: CU20 - Consultar disponibilidad & CU21 - Realizar reserva
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { RestauranteService } from '../../../core/services/restaurante.service';
import { AreaRestauranteService } from '../../../core/services/area-restaurante.service';
import { ReservaService } from '../../../core/services/reserva.service';

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
  imports: [AppIconComponent, CommonModule, RouterModule, FormsModule],
  templateUrl: './nueva-reserva.component.html',
  styleUrls: ['./nueva-reserva.component.css']
})
export class NuevaReservaComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private restauranteService = inject(RestauranteService);
  private areaService = inject(AreaRestauranteService);
  private reservaService = inject(ReservaService);

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

    const qPlan = this.route.snapshot.queryParamMap.get('id_planificacion');
    if (qPlan) {
      this.idPlanificacion = Number(qPlan);
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
        }
      },
      error: () => this.error.set('No se pudieron cargar las áreas del restaurante.')
    });
  }

  onFiltroCambiado(): void {
    if (this.disponibilidad()) {
      this.filtrosModificados.set(true);
    }
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

  // --- INTERACCIÓN Y SELECCIÓN DE MESAS ---
  estaMesaSeleccionada(idMesa: number): boolean {
    return this.mesasSeleccionadasIds.includes(idMesa);
  }

  seleccionarMesaIndividual(mesa: MesaDisponibilidad): void {
    if (!mesa.seleccionable) {
      return;
    }

    if (this.estaMesaSeleccionada(mesa.id_mesa) && this.mesasSeleccionadasIds.length === 1) {
      // Deseleccionar si ya estaba elegida
      this.deseleccionarTodo();
      return;
    }

    // Selección individual
    this.combinacionSeleccionada = null;
    this.mesasSeleccionadasIds = [mesa.id_mesa];
  }

  esCombinacionSeleccionada(comb: CombinacionDisponible): boolean {
    return this.combinacionSeleccionada?.id_combinacion === comb.id_combinacion;
  }

  seleccionarCombinacion(comb: CombinacionDisponible): void {
    if (!comb.seleccionable) {
      return;
    }

    if (this.esCombinacionSeleccionada(comb)) {
      this.deseleccionarTodo();
      return;
    }

    this.combinacionSeleccionada = comb;
    this.mesasSeleccionadasIds = [...comb.mesas];
  }

  deseleccionarTodo(): void {
    this.mesasSeleccionadasIds = [];
    this.combinacionSeleccionada = null;
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
      return `Mesa ${mesa.numero} (Seleccionada para reservar)`;
    }
    if (mesa.estado_disponibilidad === 'DISPONIBLE') {
      return `Mesa ${mesa.numero} (${mesa.capacidad}p) - Clic para seleccionar`;
    }
    if (mesa.estado_disponibilidad === 'NO_DISPONIBLE') {
      return `Mesa ${mesa.numero} - Ya cuenta con una reserva en este horario`;
    }
    if (mesa.capacidad < this.filtroPersonas) {
      return `Mesa ${mesa.numero} - Capacidad insuficiente (${mesa.capacidad}p para ${this.filtroPersonas} personas)`;
    }
    return `Mesa ${mesa.numero} - Capacidad excesiva (${mesa.capacidad}p)`;
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
