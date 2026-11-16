import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type TipoEspacio =
  | 'CAJA'
  | 'ACCESO'
  | 'JUEGOS'
  | 'BANOS'
  | 'ESCALERA'
  | 'RETIRO'
  | 'BARRA'
  | 'COCINA'
  | 'ESPERA'
  | 'TERRAZA'
  | 'ESCENARIO'
  | 'PERSONALIZADO';

export interface ConfiguracionEspacioVisual {
  colorBorde: string;
  colorFondo: string;
  colorTexto: string;
  colorIcono: string;
  subtitulo: string;
}

@Component({
  selector: 'app-espacio-svg',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="espacio-svg-card"
      [style.border-color]="tema.colorBorde"
      [style.background]="tema.colorFondo"
      [style.color]="tema.colorTexto"
      [style.width]="anchoPx ? anchoPx + 'px' : '100%'"
      [style.height]="altoPx ? altoPx + 'px' : '100%'"
    >
      <!-- Iconografía Vectorial SVG Específica por Espacio -->
      <div class="espacio-icon-wrap" [style.color]="tema.colorIcono">
        <!-- 1. CAJA / COBRO -->
        <svg *ngIf="tipoNormalizado === 'CAJA'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="4" width="20" height="16" rx="2"></rect>
          <line x1="2" y1="10" x2="22" y2="10"></line>
          <line x1="6" y1="15" x2="10" y2="15"></line>
          <circle cx="17" cy="15" r="1.5" fill="currentColor"></circle>
          <path d="M12 2v2M8 2v2M16 2v2"></path>
        </svg>

        <!-- 2. INGRESO Y SALIDA (ACCESO) -->
        <svg *ngIf="tipoNormalizado === 'ACCESO'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 21h18M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16"></path>
          <polyline points="9 11 12 8 15 11"></polyline>
          <line x1="12" y1="8" x2="12" y2="16"></line>
          <circle cx="15" cy="12" r="1"></circle>
        </svg>

        <!-- 3. PATIO DE JUEGOS (KIDS ZONE) -->
        <svg *ngIf="tipoNormalizado === 'JUEGOS'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 19l4-14 4 14M16 5l4 14M2 19h20M9 13h6"></path>
          <circle cx="8" cy="7" r="1.5" fill="currentColor"></circle>
          <circle cx="18" cy="12" r="1.5" fill="currentColor"></circle>
        </svg>

        <!-- 4. BAÑOS / SANITARIOS (WC) -->
        <svg *ngIf="tipoNormalizado === 'BANOS'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="7" cy="5" r="2"></circle>
          <path d="M7 9v11M4 13h6"></path>
          <circle cx="17" cy="5" r="2"></circle>
          <path d="M14 10l3 10 3-10M14 14h6"></path>
          <line x1="12" y1="3" x2="12" y2="21" stroke-dasharray="2 2"></line>
        </svg>

        <!-- 5. ESCALERA HACIA OTRA PLANTA -->
        <svg *ngIf="tipoNormalizado === 'ESCALERA'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 19h4v-4h4v-4h4V7h4"></path>
          <polyline points="15 3 19 3 19 7"></polyline>
          <line x1="10" y1="12" x2="19" y2="3"></line>
        </svg>

        <!-- 6. RETIRO DE PEDIDO (TAKE AWAY / PICKUP) -->
        <svg *ngIf="tipoNormalizado === 'RETIRO'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <path d="M16 10a4 4 0 0 1-8 0"></path>
        </svg>

        <!-- 7. BARRA DE BAR / CAFETERÍA -->
        <svg *ngIf="tipoNormalizado === 'BARRA'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M8 22h8M12 15v7M5 3l7 8 7-8z"></path>
          <line x1="3" y1="3" x2="21" y2="3"></line>
        </svg>

        <!-- 8. COCINA / DESPACHO -->
        <svg *ngIf="tipoNormalizado === 'COCINA'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 13.8a4.5 4.5 0 1 1 7.2-5.4 4.5 4.5 0 1 1 4.8 5.4H6z"></path>
          <path d="M6 17h12a2 2 0 0 1 2 2v2H4v-2a2 2 0 0 1 2-2z"></path>
        </svg>

        <!-- 9. ZONA DE ESPERA (LOUNGE) -->
        <svg *ngIf="tipoNormalizado === 'ESPERA'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 11a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6H4z"></path>
          <path d="M2 13v4a2 2 0 0 0 2 2h1v2h2v-2h10v2h2v-2h1a2 2 0 0 0 2-2v-4"></path>
        </svg>

        <!-- 10. TERRAZA / AIRE LIBRE -->
        <svg *ngIf="tipoNormalizado === 'TERRAZA'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2v20M4 12a8 8 0 0 1 16 0z"></path>
          <path d="M6 12c0-3 2.5-6 6-6s6 3 6 6"></path>
        </svg>

        <!-- 11. ESCENARIO / SHOW EN VIVO -->
        <svg *ngIf="tipoNormalizado === 'ESCENARIO'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
        </svg>

        <!-- 12. PERSONALIZADO / A MEDIDA (CU06) -->
        <svg *ngIf="tipoNormalizado === 'PERSONALIZADO'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="3" stroke-dasharray="3 3"></rect>
          <path d="M12 8v8M8 12h8"></path>
          <circle cx="12" cy="12" r="1.5" fill="currentColor"></circle>
        </svg>
      </div>

      <!-- Nombre / Etiqueta del Espacio -->
      <div class="espacio-info">
        <span class="espacio-titulo" [title]="nombre">{{ nombre || tipoNormalizado }}</span>
        <span *ngIf="mostrarSubtitulo" class="espacio-subtitulo">{{ tema.subtitulo }}</span>
      </div>
    </div>
  `,
  styles: [`
    .espacio-svg-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 0.35rem 0.5rem;
      border-radius: 8px;
      border: 2px dashed #94a3b8;
      box-shadow: 0 2px 5px rgba(0,0,0,0.06);
      user-select: none;
      box-sizing: border-box;
      text-align: center;
      transition: all 0.2s ease;
      overflow: hidden;
      gap: 0.2rem;
    }

    .espacio-icon-wrap {
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }

    .espacio-info {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
      overflow: hidden;
    }

    .espacio-titulo {
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      max-width: 100%;
      text-transform: uppercase;
    }

    .espacio-subtitulo {
      font-size: 0.6rem;
      opacity: 0.75;
      white-space: nowrap;
    }
  `]
})
export class EspacioSvgComponent {
  @Input() tipo: TipoEspacio | string = 'CAJA';
  @Input() nombre: string = '';
  @Input() anchoPx?: number;
  @Input() altoPx?: number;
  @Input() mostrarSubtitulo: boolean = false;

  get tipoNormalizado(): TipoEspacio {
    const t = (this.tipo || '').toUpperCase().trim();
    switch (t) {
      case 'CAJA':
      case 'COBRO':
        return 'CAJA';
      case 'ACCESO':
      case 'INGRESO':
      case 'SALIDA':
      case 'PUERTA':
        return 'ACCESO';
      case 'JUEGOS':
      case 'PATIO_JUEGOS':
      case 'KIDS':
        return 'JUEGOS';
      case 'BANOS':
      case 'BANO':
      case 'SANITARIOS':
      case 'WC':
        return 'BANOS';
      case 'ESCALERA':
      case 'ESCALERAS':
        return 'ESCALERA';
      case 'RETIRO':
      case 'RETIRO_PEDIDO':
      case 'TAKEAWAY':
      case 'PICKUP':
        return 'RETIRO';
      case 'BARRA':
      case 'BAR':
        return 'BARRA';
      case 'COCINA':
        return 'COCINA';
      case 'ESPERA':
      case 'LOUNGE':
        return 'ESPERA';
      case 'TERRAZA':
      case 'BALCON':
        return 'TERRAZA';
      case 'ESCENARIO':
      case 'SHOW':
      case 'DJ':
        return 'ESCENARIO';
      case 'PERSONALIZADO':
      case 'OTRO':
      case 'CUSTOM':
      case 'MEDIDA':
      case 'ZONA':
        return 'PERSONALIZADO';
      default:
        return 'PERSONALIZADO';
    }
  }

  get tema(): ConfiguracionEspacioVisual {
    switch (this.tipoNormalizado) {
      case 'CAJA':
        return {
          colorBorde: '#059669',
          colorFondo: '#ecfdf5',
          colorTexto: '#065f46',
          colorIcono: '#059669',
          subtitulo: 'Punto de Pago'
        };
      case 'ACCESO':
        return {
          colorBorde: '#2563eb',
          colorFondo: '#eff6ff',
          colorTexto: '#1e40af',
          colorIcono: '#2563eb',
          subtitulo: 'Entrada / Salida'
        };
      case 'JUEGOS':
        return {
          colorBorde: '#d97706',
          colorFondo: '#fffbeb',
          colorTexto: '#92400e',
          colorIcono: '#d97706',
          subtitulo: 'Área Infantil'
        };
      case 'BANOS':
        return {
          colorBorde: '#0284c7',
          colorFondo: '#f0f9ff',
          colorTexto: '#075985',
          colorIcono: '#0284c7',
          subtitulo: 'Sanitarios'
        };
      case 'ESCALERA':
        return {
          colorBorde: '#7c3aed',
          colorFondo: '#f5f3ff',
          colorTexto: '#5b21b6',
          colorIcono: '#7c3aed',
          subtitulo: 'Nivel Superior'
        };
      case 'RETIRO':
        return {
          colorBorde: '#ea580c',
          colorFondo: '#fff7ed',
          colorTexto: '#9a3412',
          colorIcono: '#ea580c',
          subtitulo: 'Pick-up / Llevar'
        };
      case 'BARRA':
        return {
          colorBorde: '#b45309',
          colorFondo: '#fef3c7',
          colorTexto: '#78350f',
          colorIcono: '#b45309',
          subtitulo: 'Bebidas & Bar'
        };
      case 'COCINA':
        return {
          colorBorde: '#dc2626',
          colorFondo: '#fef2f2',
          colorTexto: '#991b1b',
          colorIcono: '#dc2626',
          subtitulo: 'Área Operativa'
        };
      case 'ESPERA':
        return {
          colorBorde: '#0891b2',
          colorFondo: '#ecfeff',
          colorTexto: '#155e75',
          colorIcono: '#0891b2',
          subtitulo: 'Lounge'
        };
      case 'TERRAZA':
        return {
          colorBorde: '#65a30d',
          colorFondo: '#f7fee7',
          colorTexto: '#3f6212',
          colorIcono: '#65a30d',
          subtitulo: 'Al Aire Libre'
        };
      case 'ESCENARIO':
        return {
          colorBorde: '#db2777',
          colorFondo: '#fdf2f8',
          colorTexto: '#9d174d',
          colorIcono: '#db2777',
          subtitulo: 'Tarima / Música'
        };
      case 'PERSONALIZADO':
        return {
          colorBorde: '#4f46e5',
          colorFondo: '#eef2ff',
          colorTexto: '#3730a3',
          colorIcono: '#4f46e5',
          subtitulo: 'A Medida'
        };
    }
  }
}
