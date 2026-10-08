import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { BrandLogoComponent } from '../../shared/brand-logo/brand-logo.component';

@Component({
  selector: 'app-auth-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, BrandLogoComponent],
  template: `
    <div class="auth-wrapper">
      <div class="auth-card-container">
        <div class="auth-header">
          <app-brand-logo size="auth" />
          <p class="auth-subtitle">Plataforma de Planificación Gastronómica</p>
        </div>
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styles: [`
    .auth-wrapper {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: radial-gradient(ellipse at 15% 10%, rgb(255 111 0 / 0.09), transparent 38%), var(--background);
      padding: 2rem 1.25rem;
    }
    .auth-card-container {
      width: 100%;
      max-width: 480px;
      background: var(--surface);
      border: 1px solid #ededed;
      border-radius: 22px;
      box-shadow: var(--shadow-lg);
      padding: 2.75rem 2.5rem;
    }
    .auth-header {
      text-align: center;
      margin-bottom: 2.2rem;
    }
    .auth-subtitle {
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 0.45rem;
    }
    @media (max-width: 520px) {
      .auth-card-container { padding: 2rem 1.25rem; border-radius: 18px; }
      .auth-header { margin-bottom: 1.7rem; }
    }
  `]
})
export class AuthLayoutComponent {}
