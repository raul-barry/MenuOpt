import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormaMesa } from '../../core/models/mesa.model';

export type DisposicionMesa =
  | 'redonda'
  | 'cuadrada-2'
  | 'cuadrada-4'
  | 'cuadrada-8'
  | 'rect-4'
  | 'rect-6-cabecera'
  | 'rect-6-largo'
  | 'rect-8-cabecera'
  | 'rect-8-largo';

export interface SillaCoords {
  cx: number;
  cy: number;
  r: number;
}

@Component({
  selector: 'app-mesa-svg',
  standalone: true,
  imports: [CommonModule],
  template: `
    <svg
      [attr.viewBox]="viewBox()"
      [style.width]="tamanoPx + 'px'"
      [style.height]="tamanoPx + 'px'"
      class="mesa-svg-graphic"
    >
      <!-- CAPA 1: SILLAS (Detrás de la mesa) -->
      <g class="sillas-group" [attr.stroke]="colorTrazo" [attr.fill]="colorSilla" [attr.stroke-width]="strokeWidth">
        <circle
          *ngFor="let s of sillasCalculadas()"
          [attr.cx]="s.cx"
          [attr.cy]="s.cy"
          [attr.r]="s.r"
        />
      </g>

      <!-- CAPA 2: MESA CENTRAL -->
      <g class="mesa-central-group">
        <!-- Mesa Redonda -->
        <circle
          *ngIf="formaNormalizada === 'REDONDA'"
          cx="50"
          cy="50"
          [attr.r]="radioMesaRedonda()"
          [attr.fill]="colorFondoMesa"
          [attr.stroke]="colorTrazo"
          [attr.stroke-width]="strokeWidthMesa"
        />

        <!-- Mesa Cuadrada -->
        <rect
          *ngIf="formaNormalizada === 'CUADRADA'"
          [attr.x]="cuadradaDim().x"
          [attr.y]="cuadradaDim().y"
          [attr.width]="cuadradaDim().w"
          [attr.height]="cuadradaDim().h"
          [attr.rx]="cuadradaDim().rx"
          [attr.fill]="colorFondoMesa"
          [attr.stroke]="colorTrazo"
          [attr.stroke-width]="strokeWidthMesa"
        />

        <!-- Mesa Rectangular -->
        <rect
          *ngIf="formaNormalizada === 'RECTANGULAR'"
          [attr.x]="rectDim().x"
          [attr.y]="rectDim().y"
          [attr.width]="rectDim().w"
          [attr.height]="rectDim().h"
          [attr.rx]="rectDim().rx"
          [attr.fill]="colorFondoMesa"
          [attr.stroke]="colorTrazo"
          [attr.stroke-width]="strokeWidthMesa"
        />
      </g>

      <!-- CAPA 3: TEXTO / NÚMERO DE CAPACIDAD EN EL CENTRO -->
      <text
        x="50"
        y="55"
        text-anchor="middle"
        dominant-baseline="middle"
        [attr.fill]="colorTexto"
        [attr.font-size]="fontSize()"
        font-weight="bold"
        font-family="system-ui, -apple-system, sans-serif"
      >
        {{ textoVisual() }}
      </text>
    </svg>
  `,
  styles: [`
    :host {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      user-select: none;
    }
    .mesa-svg-graphic {
      display: block;
      overflow: visible;
      filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
    }
  `]
})
export class MesaSvgComponent {
  @Input() forma: FormaMesa = 'CUADRADA';
  @Input() capacidad: number | string = 4;
  @Input() disposicion?: DisposicionMesa;
  @Input() texto?: string;
  @Input() numeroMesa?: string;

  @Input() tamanoPx: number = 72;
  @Input() colorTrazo: string = '#1e293b';
  @Input() colorSilla: string = '#ffffff';
  @Input() colorFondoMesa: string = '#ffffff';
  @Input() colorTexto: string = '#1e293b';
  @Input() strokeWidth: number = 2.2;
  @Input() strokeWidthMesa: number = 2.4;

  viewBox = () => '0 0 100 100';

  get numCapacidad(): number {
    const val = Number(this.capacidad);
    return isNaN(val) || val < 1 ? 1 : Math.min(val, 24);
  }

  get formaNormalizada(): FormaMesa {
    return this.forma ? (this.forma.toUpperCase() as FormaMesa) : 'CUADRADA';
  }

  sillasCalculadas(): SillaCoords[] {
    const n = this.numCapacidad;

    if (this.formaNormalizada === 'REDONDA') {
      return this.sillasRedondas(n);
    }

    if (this.formaNormalizada === 'CUADRADA') {
      return this.sillasCuadradas(n);
    }

    // RECTANGULAR
    return this.sillasRectangulares(n);
  }

  sillasRedondas(n: number): SillaCoords[] {
    const rMesa = this.radioMesaRedonda();
    const rSilla = n <= 2 ? 12 : n <= 4 ? 11 : n <= 6 ? 9.5 : 8.5;
    const distCentro = rMesa + rSilla * 0.45;

    const res: SillaCoords[] = [];
    for (let i = 0; i < n; i++) {
      const angle = (2 * Math.PI * i) / n - Math.PI / 2;
      const cx = 50 + distCentro * Math.cos(angle);
      const cy = 50 + distCentro * Math.sin(angle);
      res.push({
        cx: Math.round(cx * 10) / 10,
        cy: Math.round(cy * 10) / 10,
        r: rSilla
      });
    }
    return res;
  }

  sillasCuadradas(n: number): SillaCoords[] {
    // Si viene una disposición del catálogo y coincide la capacidad:
    if (this.disposicion === 'cuadrada-2' && n === 2) {
      return [
        { cx: 50, cy: 18, r: 12 },
        { cx: 50, cy: 82, r: 12 }
      ];
    }
    if (this.disposicion === 'cuadrada-4' && n === 4) {
      return [
        { cx: 50, cy: 16, r: 12 },
        { cx: 50, cy: 84, r: 12 },
        { cx: 16, cy: 50, r: 12 },
        { cx: 84, cy: 50, r: 12 }
      ];
    }
    if (this.disposicion === 'cuadrada-8' && n === 8) {
      return [
        { cx: 38, cy: 14, r: 10.5 },
        { cx: 62, cy: 14, r: 10.5 },
        { cx: 38, cy: 86, r: 10.5 },
        { cx: 62, cy: 86, r: 10.5 },
        { cx: 14, cy: 38, r: 10.5 },
        { cx: 14, cy: 62, r: 10.5 },
        { cx: 86, cy: 38, r: 10.5 },
        { cx: 86, cy: 62, r: 10.5 }
      ];
    }

    // Comportamiento dinámico para cualquier número de comensales en cuadrada:
    if (n === 1) {
      return [{ cx: 50, cy: 16, r: 12 }];
    }
    if (n === 2) {
      return [
        { cx: 50, cy: 18, r: 12 },
        { cx: 50, cy: 82, r: 12 }
      ];
    }
    if (n === 3) {
      return [
        { cx: 50, cy: 16, r: 12 },
        { cx: 16, cy: 54, r: 12 },
        { cx: 84, cy: 54, r: 12 }
      ];
    }
    if (n === 4) {
      return [
        { cx: 50, cy: 16, r: 12 },
        { cx: 50, cy: 84, r: 12 },
        { cx: 16, cy: 50, r: 12 },
        { cx: 84, cy: 50, r: 12 }
      ];
    }
    if (n === 5) {
      return [
        { cx: 38, cy: 14, r: 10.5 },
        { cx: 62, cy: 14, r: 10.5 },
        { cx: 50, cy: 86, r: 11 },
        { cx: 14, cy: 50, r: 11 },
        { cx: 86, cy: 50, r: 11 }
      ];
    }
    if (n === 6) {
      return [
        { cx: 38, cy: 14, r: 10.5 },
        { cx: 62, cy: 14, r: 10.5 },
        { cx: 38, cy: 86, r: 10.5 },
        { cx: 62, cy: 86, r: 10.5 },
        { cx: 14, cy: 50, r: 10.5 },
        { cx: 86, cy: 50, r: 10.5 }
      ];
    }
    if (n === 7) {
      return [
        { cx: 38, cy: 14, r: 10 },
        { cx: 62, cy: 14, r: 10 },
        { cx: 38, cy: 86, r: 10 },
        { cx: 62, cy: 86, r: 10 },
        { cx: 14, cy: 38, r: 10 },
        { cx: 14, cy: 62, r: 10 },
        { cx: 86, cy: 50, r: 10 }
      ];
    }
    // Para 8 o más
    return [
      { cx: 38, cy: 14, r: 10.5 },
      { cx: 62, cy: 14, r: 10.5 },
      { cx: 38, cy: 86, r: 10.5 },
      { cx: 62, cy: 86, r: 10.5 },
      { cx: 14, cy: 38, r: 10.5 },
      { cx: 14, cy: 62, r: 10.5 },
      { cx: 86, cy: 38, r: 10.5 },
      { cx: 86, cy: 62, r: 10.5 }
    ];
  }

  sillasRectangulares(n: number): SillaCoords[] {
    // Si viene una disposición del catálogo y coincide la capacidad:
    if (this.disposicion === 'rect-4' && n === 4) {
      return [
        { cx: 36, cy: 20, r: 11 },
        { cx: 64, cy: 20, r: 11 },
        { cx: 36, cy: 80, r: 11 },
        { cx: 64, cy: 80, r: 11 }
      ];
    }
    if (this.disposicion === 'rect-6-cabecera' && n === 6) {
      return [
        { cx: 36, cy: 19, r: 11 },
        { cx: 64, cy: 19, r: 11 },
        { cx: 36, cy: 81, r: 11 },
        { cx: 64, cy: 81, r: 11 },
        { cx: 12, cy: 50, r: 11 },
        { cx: 88, cy: 50, r: 11 }
      ];
    }
    if (this.disposicion === 'rect-6-largo' && n === 6) {
      return [
        { cx: 28, cy: 20, r: 10.5 },
        { cx: 50, cy: 20, r: 10.5 },
        { cx: 72, cy: 20, r: 10.5 },
        { cx: 28, cy: 80, r: 10.5 },
        { cx: 50, cy: 80, r: 10.5 },
        { cx: 72, cy: 80, r: 10.5 }
      ];
    }
    if (this.disposicion === 'rect-8-cabecera' && n === 8) {
      return [
        { cx: 30, cy: 19, r: 10 },
        { cx: 50, cy: 19, r: 10 },
        { cx: 70, cy: 19, r: 10 },
        { cx: 30, cy: 81, r: 10 },
        { cx: 50, cy: 81, r: 10 },
        { cx: 70, cy: 81, r: 10 },
        { cx: 10, cy: 50, r: 10 },
        { cx: 90, cy: 50, r: 10 }
      ];
    }
    if (this.disposicion === 'rect-8-largo' && n === 8) {
      return [
        { cx: 23, cy: 20, r: 9.5 },
        { cx: 41, cy: 20, r: 9.5 },
        { cx: 59, cy: 20, r: 9.5 },
        { cx: 77, cy: 20, r: 9.5 },
        { cx: 23, cy: 80, r: 9.5 },
        { cx: 41, cy: 80, r: 9.5 },
        { cx: 59, cy: 80, r: 9.5 },
        { cx: 77, cy: 80, r: 9.5 }
      ];
    }

    // Comportamiento dinámico para cualquier número de sillas en rectangular:
    if (n === 1) {
      return [{ cx: 50, cy: 20, r: 11 }];
    }
    if (n === 2) {
      return [
        { cx: 50, cy: 20, r: 11 },
        { cx: 50, cy: 80, r: 11 }
      ];
    }
    if (n === 3) {
      return [
        { cx: 50, cy: 20, r: 11 },
        { cx: 50, cy: 80, r: 11 },
        { cx: 12, cy: 50, r: 11 }
      ];
    }
    if (n === 4) {
      return [
        { cx: 36, cy: 20, r: 11 },
        { cx: 64, cy: 20, r: 11 },
        { cx: 36, cy: 80, r: 11 },
        { cx: 64, cy: 80, r: 11 }
      ];
    }
    // CASO CLAVE: 5 SILLAS (2 arriba, 2 abajo y 1 en cabecera)
    if (n === 5) {
      return [
        { cx: 36, cy: 19, r: 11 },
        { cx: 64, cy: 19, r: 11 },
        { cx: 36, cy: 81, r: 11 },
        { cx: 64, cy: 81, r: 11 },
        { cx: 12, cy: 50, r: 11 }
      ];
    }
    if (n === 6) {
      return [
        { cx: 36, cy: 19, r: 11 },
        { cx: 64, cy: 19, r: 11 },
        { cx: 36, cy: 81, r: 11 },
        { cx: 64, cy: 81, r: 11 },
        { cx: 12, cy: 50, r: 11 },
        { cx: 88, cy: 50, r: 11 }
      ];
    }
    if (n === 7) {
      return [
        { cx: 30, cy: 19, r: 10 },
        { cx: 50, cy: 19, r: 10 },
        { cx: 70, cy: 19, r: 10 },
        { cx: 30, cy: 81, r: 10 },
        { cx: 50, cy: 81, r: 10 },
        { cx: 70, cy: 81, r: 10 },
        { cx: 10, cy: 50, r: 10 }
      ];
    }
    if (n === 8) {
      return [
        { cx: 30, cy: 19, r: 10 },
        { cx: 50, cy: 19, r: 10 },
        { cx: 70, cy: 19, r: 10 },
        { cx: 30, cy: 81, r: 10 },
        { cx: 50, cy: 81, r: 10 },
        { cx: 70, cy: 81, r: 10 },
        { cx: 10, cy: 50, r: 10 },
        { cx: 90, cy: 50, r: 10 }
      ];
    }
    if (n === 9) {
      return [
        { cx: 23, cy: 20, r: 9.5 },
        { cx: 41, cy: 20, r: 9.5 },
        { cx: 59, cy: 20, r: 9.5 },
        { cx: 77, cy: 20, r: 9.5 },
        { cx: 23, cy: 80, r: 9.5 },
        { cx: 41, cy: 80, r: 9.5 },
        { cx: 59, cy: 80, r: 9.5 },
        { cx: 77, cy: 80, r: 9.5 },
        { cx: 8, cy: 50, r: 9.5 }
      ];
    }
    // 10 o más
    return [
      { cx: 23, cy: 20, r: 9.5 },
      { cx: 41, cy: 20, r: 9.5 },
      { cx: 59, cy: 20, r: 9.5 },
      { cx: 77, cy: 20, r: 9.5 },
      { cx: 23, cy: 80, r: 9.5 },
      { cx: 41, cy: 80, r: 9.5 },
      { cx: 59, cy: 80, r: 9.5 },
      { cx: 77, cy: 80, r: 9.5 },
      { cx: 8, cy: 50, r: 9.5 },
      { cx: 92, cy: 50, r: 9.5 }
    ];
  }

  radioMesaRedonda(): number {
    const n = this.numCapacidad;
    if (n <= 2) return 22;
    if (n <= 4) return 25;
    if (n <= 6) return 27;
    return 29;
  }

  cuadradaDim(): { x: number; y: number; w: number; h: number; rx: number } {
    const n = this.numCapacidad;
    if (n >= 8 || this.disposicion === 'cuadrada-8') {
      return { x: 26, y: 26, w: 48, h: 48, rx: 7 };
    }
    return { x: 29, y: 29, w: 42, h: 42, rx: 6 };
  }

  rectDim(): { x: number; y: number; w: number; h: number; rx: number } {
    const n = this.numCapacidad;
    if (n >= 9 || this.disposicion === 'rect-8-largo') {
      return { x: 13, y: 31, w: 74, h: 38, rx: 6 };
    }
    if (n >= 7 || this.disposicion === 'rect-8-cabecera' || this.disposicion === 'rect-6-largo') {
      return { x: 18, y: 31, w: 64, h: 38, rx: 6 };
    }
    if (n === 5 || n === 6 || this.disposicion === 'rect-6-cabecera') {
      return { x: 20, y: 31, w: 60, h: 38, rx: 6 };
    }
    return { x: 23, y: 31, w: 54, h: 38, rx: 6 };
  }

  textoVisual(): string {
    if (this.texto !== undefined && this.texto !== null && this.texto !== '') {
      return this.texto;
    }
    if (this.numeroMesa) {
      return this.numeroMesa;
    }
    return this.numCapacidad.toString();
  }

  fontSize(): number {
    const txt = this.textoVisual();
    if (txt.length >= 4) return 11;
    if (txt.length >= 3) return 13;
    if (txt.length >= 2) return 15;
    return 18;
  }
}
