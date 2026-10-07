import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-dashboard-cliente',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="dashboard-container">
      <div class="welcome-banner card" *ngIf="authService.currentUser() as user">
        <div class="welcome-text">
          <h1>¡Hola, {{ user.nombres }}! 👋</h1>
          <p class="subtitle">
            Bienvenido a tu panel de planificación gastronómica inteligente. Optimiza tu presupuesto y encuentra las mejores alternativas.
          </p>
        </div>
        <div class="quick-action">
          <a routerLink="/planificaciones/nueva" class="btn btn-primary btn-lg">
            <span>✨</span> Planificar una Comida
          </a>
        </div>
      </div>

      <!-- Accesos Principales -->
      <h2 style="margin-top: 1.5rem; margin-bottom: 1rem;">Acciones Rápidas</h2>
      <div class="grid-3">
        <div class="card action-card">
          <div class="card-icon">🍲</div>
          <h3>Nueva Planificación</h3>
          <p>Define comensales, presupuesto y zona para obtener recomendaciones optimizadas.</p>
          <a routerLink="/planificaciones/nueva" class="btn btn-primary btn-sm" style="margin-top: auto;">
            Empezar ahora &rarr;
          </a>
        </div>

        <div class="card action-card">
          <div class="card-icon">📋</div>
          <h3>Mis Planificaciones</h3>
          <p>Revisa el historial de tus eventos, alternativas calculadas y comparaciones de ahorro.</p>
          <a routerLink="/planificaciones" class="btn btn-outline btn-sm" style="margin-top: auto;">
            Ver historial &rarr;
          </a>
        </div>

        <div class="card action-card">
          <div class="card-icon">🥗</div>
          <h3>Mis Preferencias</h3>
          <p>Configura restricciones y gustos (vegetariano, sin gluten, picante, etc.).</p>
          <a routerLink="/preferencias" class="btn btn-outline btn-sm" style="margin-top: auto;">
            Configurar gustos &rarr;
          </a>
        </div>
      </div>

      <!-- Explicación del Flujo de Trabajo MenuOpt -->
      <div class="card workflow-card" style="margin-top: 2rem;">
        <div class="card-header">
          <h3>¿Cómo funciona MenuOpt?</h3>
          <span class="badge badge-secondary">Flujo de Optimización</span>
        </div>
        <div class="steps-container">
          <div class="step-item">
            <div class="step-number">1</div>
            <h4>1. Planifica</h4>
            <p>Ingresa tu presupuesto en Bs, la cantidad de comensales y tus preferencias dietéticas.</p>
          </div>
          <div class="step-arrow">&rarr;</div>
          <div class="step-item">
            <div class="step-number">2</div>
            <h4>2. Recomendaciones</h4>
            <p>El sistema analiza menús de restaurantes y recetas caseras con precios reales de mercado.</p>
          </div>
          <div class="step-arrow">&rarr;</div>
          <div class="step-item">
            <div class="step-number">3</div>
            <h4>3. Compara y Elige</h4>
            <p>Contrasta costos, ahorro e insumos de Restaurante vs Preparación Propia.</p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      max-width: 1100px;
      margin: 0 auto;
    }
    .welcome-banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: linear-gradient(135deg, #1d3557 0%, #457b9d 100%);
      color: white;
      border: none;
      padding: 2rem;
    }
    .welcome-banner h1 {
      color: white;
      margin-bottom: 0.5rem;
    }
    .subtitle {
      color: #e2e8f0;
      font-size: 1rem;
      max-width: 600px;
    }
    .btn-lg {
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      font-weight: 600;
      background-color: var(--primary);
    }
    .action-card {
      display: flex;
      flex-direction: column;
      height: 100%;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .action-card:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-md);
    }
    .card-icon {
      font-size: 2.25rem;
      margin-bottom: 0.75rem;
    }
    .action-card p {
      color: var(--text-muted);
      font-size: 0.875rem;
      margin-bottom: 1.25rem;
    }
    .workflow-card {
      background-color: var(--surface);
    }
    .steps-container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      padding: 1rem 0;
    }
    .step-item {
      flex: 1;
      text-align: center;
      padding: 1rem;
    }
    .step-number {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background-color: var(--primary-light);
      color: var(--primary);
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 0.75rem auto;
    }
    .step-item h4 {
      margin-bottom: 0.5rem;
    }
    .step-item p {
      font-size: 0.825rem;
      color: var(--text-muted);
    }
    .step-arrow {
      font-size: 1.5rem;
      color: var(--border);
      font-weight: bold;
    }
    @media (max-width: 768px) {
      .welcome-banner {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
      }
      .steps-container {
        flex-direction: column;
      }
      .step-arrow {
        transform: rotate(90deg);
      }
    }
  `]
})
export class DashboardClienteComponent {
  authService = inject(AuthService);
}
