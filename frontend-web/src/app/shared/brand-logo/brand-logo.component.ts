import { Component, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-brand-logo',
  standalone: true,
  imports: [CommonModule],
  template: `
    <img
      class="brand-logo"
      [class.brand-logo-auth]="size === 'auth'"
      [class.brand-logo-header]="size === 'header'"
      [src]="currentSrc"
      (error)="handleImageError()"
      alt="MenuOpt"
      draggable="false"
    />
  `,
  styles: [`
    :host {
      display: inline-flex;
      align-items: center;
      flex: 0 1 auto;
      min-width: 0;
      max-width: 100%;
      max-height: 100%;
      line-height: 0;
    }
    .brand-logo {
      display: block;
      max-width: 100%;
      height: auto;
      object-fit: contain;
    }
    .brand-logo-auth {
      width: min(270px, 74vw);
      max-height: 88px;
    }
    .brand-logo-header {
      width: auto;
      height: 38px;
      max-width: 190px;
      max-height: 38px;
      object-fit: contain;
    }
    @media (max-width: 520px) {
      .brand-logo-auth {
        width: min(235px, 70vw);
        max-height: 76px;
      }
      .brand-logo-header {
        height: 32px;
        max-width: min(150px, calc(100vw - 150px));
      }
    }
  `]
})
export class BrandLogoComponent {
  @Input() size: 'auth' | 'header' = 'header';

  private errorAttempts = 0;
  private fallbackSrc = signal<string | null>(null);

  get currentSrc(): string {
    const fallback = this.fallbackSrc();
    if (fallback) return fallback;

    return this.size === 'header'
      ? '/branding/menuopt-logo-header.png'
      : '/branding/menuopt-logo.png';
  }

  handleImageError(): void {
    this.errorAttempts++;
    if (this.errorAttempts === 1) {
      // Fallback 1: Ruta relativa bajo assets
      this.fallbackSrc.set(
        this.size === 'header'
          ? 'assets/branding/menuopt-logo-header.png'
          : 'assets/branding/menuopt-logo.png'
      );
    } else if (this.errorAttempts === 2) {
      // Fallback 2: Ruta absoluta bajo assets
      this.fallbackSrc.set(
        this.size === 'header'
          ? '/assets/branding/menuopt-logo-header.png'
          : '/assets/branding/menuopt-logo.png'
      );
    }
  }
}
