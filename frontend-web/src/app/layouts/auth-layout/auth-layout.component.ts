import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-auth-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet],
  template: `
    <div class="auth-wrapper">
      <div class="auth-card-container">
        <div class="auth-header">
          <span class="auth-logo">🍽️</span>
          <h2>MenuOpt</h2>
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
      background: linear-gradient(135deg, #1d3557 0%, #457b9d 100%);
      padding: 1.5rem;
    }
    .auth-card-container {
      width: 100%;
      max-width: 440px;
      background: var(--surface);
      border-radius: var(--radius);
      box-shadow: var(--shadow-lg);
      padding: 2.5rem 2rem;
    }
    .auth-header {
      text-align: center;
      margin-bottom: 2rem;
    }
    .auth-logo {
      font-size: 3rem;
      display: inline-block;
      margin-bottom: 0.5rem;
    }
    .auth-subtitle {
      color: var(--text-muted);
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  `]
})
export class AuthLayoutComponent {}
