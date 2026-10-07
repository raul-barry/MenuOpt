// CASO DE USO: CU26 - Asistente MenuOpt con IA
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { AsistenteIAService } from '../../../core/services/asistente-ia.service';
import { PlanificacionService } from '../../../core/services/planificacion.service';
import {
  MensajeChat,
  SolicitudInterpretada,
  ContextoPrevio
} from '../../../core/models/asistente-ia.model';
import { PlanificacionCrear } from '../../../core/models/planificacion.model';

@Component({
  selector: 'app-asistente-chat',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './asistente-chat.component.html',
  styleUrls: ['./asistente-chat.component.css']
})
export class AsistenteChatComponent implements OnInit {
  private asistenteService = inject(AsistenteIAService);
  private planificacionService = inject(PlanificacionService);
  private router = inject(Router);

  // Historial de conversación
  mensajes = signal<MensajeChat[]>([]);
  mensajeInput: string = '';
  procesando = signal<boolean>(false);
  creandoPlanificacion = signal<boolean>(false);

  // Estado estructurado acumulado
  interpretacionActual = signal<SolicitudInterpretada | null>(null);

  // Campos editables por el usuario antes de confirmar
  editPresupuesto: number | null = null;
  editPersonas: number | null = null;
  editTipoComida: string = 'ALMUERZO';
  editUbicacion: string = '';

  error = signal<string | null>(null);
  mensajeExito = signal<string | null>(null);

  // Ejemplos visuales sugeridos
  ejemplosSugeridos: string[] = [
    'Tengo 300 Bs y somos 10 personas. Queremos almorzar comida vegetariana en Equipetrol.',
    'Somos 4 personas y tenemos 150 Bs para cenar en el Centro.',
    'Quiero almorzar sin gluten con 200 Bs para 5 personas en Calacoto.',
    'Quiero una opción barata para almorzar con mi familia (6 personas, 180 Bs).'
  ];

  ngOnInit(): void {
    // Mensaje inicial de bienvenida
    this.mensajes.set([
      {
        emisor: 'asistente',
        texto: '¡Hola! Soy el Asistente de MenuOpt. Cuéntame qué comida estás planificando: puedes indicar tu presupuesto, cantidad de personas, tipo de comida, preferencias o la zona de tu preferencia.',
        fecha: new Date(),
        interpretacion: null
      }
    ]);
  }

  usarEjemplo(ejemplo: string): void {
    this.mensajeInput = ejemplo;
  }

  enviarMensaje(): void {
    if (!this.mensajeInput.trim() || this.procesando()) return;

    const textoUsuario = this.mensajeInput.trim();
    this.mensajeInput = '';
    this.error.set(null);

    // Agregar mensaje del usuario al chat
    const nuevoHistorial = [...this.mensajes(), {
      emisor: 'usuario' as const,
      texto: textoUsuario,
      fecha: new Date(),
      interpretacion: null
    }];
    this.mensajes.set(nuevoHistorial);
    this.procesando.set(true);

    // Preparar contexto previo acumulado si existe
    let contexto: ContextoPrevio | null = null;
    const actual = this.interpretacionActual();
    if (actual) {
      contexto = {
        presupuesto: this.editPresupuesto !== null ? this.editPresupuesto : actual.presupuesto,
        cantidad_personas: this.editPersonas !== null ? this.editPersonas : actual.cantidad_personas,
        tipo_comida: this.editTipoComida || actual.tipo_comida,
        ubicacion_referencia: this.editUbicacion || actual.ubicacion_referencia,
        preferencias_detectadas: actual.preferencias_detectadas
      };
    }

    this.asistenteService.interpretar({
      mensaje: textoUsuario,
      contexto_previo: contexto
    }).subscribe({
      next: (resp: SolicitudInterpretada) => {
        this.procesando.set(false);
        this.interpretacionActual.set(resp);

        // Actualizar valores editables
        if (resp.presupuesto !== null && resp.presupuesto !== undefined) {
          this.editPresupuesto = Number(resp.presupuesto);
        }
        if (resp.cantidad_personas !== null && resp.cantidad_personas !== undefined) {
          this.editPersonas = Number(resp.cantidad_personas);
        }
        if (resp.tipo_comida) {
          this.editTipoComida = resp.tipo_comida;
        }
        if (resp.ubicacion_referencia) {
          this.editUbicacion = resp.ubicacion_referencia;
        }

        // Agregar respuesta del asistente al chat
        this.mensajes.set([...this.mensajes(), {
          emisor: 'asistente',
          texto: resp.mensaje_asistente,
          fecha: new Date(),
          interpretacion: resp
        }]);
      },
      error: (err: any) => {
        this.procesando.set(false);
        const errMsg = err.error?.detail || 'El asistente no está disponible en este momento. Puedes continuar manualmente.';
        this.error.set(errMsg);
        this.mensajes.set([...this.mensajes(), {
          emisor: 'asistente',
          texto: '⚠️ ' + errMsg,
          fecha: new Date(),
          interpretacion: null
        }]);
      }
    });
  }

  // --- Creación de la Planificación Real (Reutiliza CU11) ---
  confirmarYCrearPlanificacion(): void {
    if (this.creandoPlanificacion()) return;

    if (!this.editPresupuesto || this.editPresupuesto <= 0) {
      this.error.set('El presupuesto debe ser mayor a 0 Bs.');
      return;
    }
    if (!this.editPersonas || this.editPersonas <= 0) {
      this.error.set('La cantidad de comensales debe ser mayor a 0.');
      return;
    }
    if (!this.editUbicacion || this.editUbicacion.trim().length < 2) {
      this.error.set('La ubicación de referencia debe tener al menos 2 caracteres.');
      return;
    }

    this.creandoPlanificacion.set(true);
    this.error.set(null);

    // Obtener IDs reales de preferencias validadas en BD
    const actual = this.interpretacionActual();
    const prefsIds: number[] = actual
      ? actual.preferencias_validadas
          .filter(p => p.registrada && p.id_preferencia !== null && p.id_preferencia !== undefined)
          .map(p => p.id_preferencia as number)
      : [];

    const payload: PlanificacionCrear = {
      presupuesto: this.editPresupuesto,
      cantidad_personas: this.editPersonas,
      tipo_comida: this.editTipoComida,
      ubicacion_referencia: this.editUbicacion.trim(),
      preferencias: prefsIds
    };

    // Reutilizar servicio oficial de CU11
    this.planificacionService.crearPlanificacion(payload).subscribe({
      next: (planCreada) => {
        this.creandoPlanificacion.set(false);
        this.mensajeExito.set(`¡Planificación #${planCreada.id_planificacion} creada exitosamente con tus criterios!`);
        // Redirigir a la vista de recomendaciones (CU13)
        setTimeout(() => {
          this.router.navigate(['/planificaciones', planCreada.id_planificacion, 'recomendaciones']);
        }, 1200);
      },
      error: (err: any) => {
        this.creandoPlanificacion.set(false);
        this.error.set(err.error?.detail || 'Error al crear la planificación gastronómica.');
      }
    });
  }

  limpiarConversacion(): void {
    this.interpretacionActual.set(null);
    this.editPresupuesto = null;
    this.editPersonas = null;
    this.editTipoComida = 'ALMUERZO';
    this.editUbicacion = '';
    this.error.set(null);
    this.mensajeExito.set(null);
    this.mensajes.set([
      {
        emisor: 'asistente',
        texto: 'Conversación reiniciada. ¿Qué comida deseas planificar hoy?',
        fecha: new Date(),
        interpretacion: null
      }
    ]);
  }
}
