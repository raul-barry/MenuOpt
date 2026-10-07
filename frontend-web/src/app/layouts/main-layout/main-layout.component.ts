import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="layout-container">
      <!-- Barra Superior -->
      <header class="topbar">
        <div class="brand">
          <span class="logo-icon">🍽️</span>
          <span class="logo-text">MenuOpt</span>
        </div>
        <div class="user-menu" *ngIf="authService.currentUser() as user">
          <div class="user-info">
            <span class="user-name">{{ user.nombres }} {{ user.apellidos }}</span>
            <span class="badge" [ngClass]="getRoleBadgeClass(user.rol?.nombre)">{{ user.rol?.nombre }}</span>
          </div>
          <button class="btn btn-outline btn-sm" (click)="authService.logout()">Cerrar Sesión</button>
        </div>
      </header>

      <div class="body-wrapper">
        <!-- Barra Lateral Dinámica según Rol -->
        <aside class="sidebar">
          <nav class="nav-menu">
            <!-- Menú para ADMINISTRADOR -->
            <ng-container *ngIf="authService.userRole() === 'ADMINISTRADOR'">
              <div class="nav-section-title">ADMINISTRACIÓN</div>
              <a routerLink="/admin/usuarios" routerLinkActive="active" class="nav-link">
                <span>👥</span> Usuarios
              </a>
              <a routerLink="/restaurantes" routerLinkActive="active" class="nav-link">
                <span>🏪</span> Restaurantes
              </a>
              <a routerLink="/admin/categorias" routerLinkActive="active" class="nav-link">
                <span>📂</span> Categorías
              </a>
              <a routerLink="/ingredientes" routerLinkActive="active" class="nav-link">
                <span>🥗</span> Ingredientes
              </a>
              <div class="nav-section-title">PLANIFICACIÓN & IA</div>
              <a routerLink="/asistente" routerLinkActive="active" class="nav-link">
                <span>🤖</span> Asistente IA
              </a>
              <a routerLink="/inicio" routerLinkActive="active" class="nav-link">
                <span>🏠</span> Panel Cliente
              </a>
              <a routerLink="/planificaciones" routerLinkActive="active" class="nav-link">
                <span>📋</span> Planificaciones
              </a>
              <a routerLink="/preferencias" routerLinkActive="active" class="nav-link">
                <span>🥗</span> Preferencias
              </a>
            </ng-container>

            <!-- Menú para CLIENTE -->
            <ng-container *ngIf="authService.userRole() === 'CLIENTE'">
              <div class="nav-section-title">ASISTENTE VIRTUAL</div>
              <a routerLink="/asistente" routerLinkActive="active" class="nav-link">
                <span>🤖</span> Asistente IA
              </a>
              <div class="nav-section-title">PLANIFICACIÓN</div>
              <a routerLink="/inicio" routerLinkActive="active" class="nav-link">
                <span>🏠</span> Inicio
              </a>
              <a routerLink="/planificaciones/nueva" routerLinkActive="active" class="nav-link">
                <span>🍲</span> Planificar comida
              </a>
              <a routerLink="/planificaciones" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" class="nav-link">
                <span>📋</span> Mis planificaciones
              </a>
              <a routerLink="/preferencias" routerLinkActive="active" class="nav-link">
                <span>🥗</span> Mis preferencias
              </a>
              <div class="nav-section-title">PEDIDOS & RESERVAS</div>
              <a routerLink="/mis-reservas" routerLinkActive="active" class="nav-link">
                <span>📅</span> Mis Reservas
              </a>
              <a routerLink="/mis-pedidos" routerLinkActive="active" class="nav-link">
                <span>📦</span> Mis Pedidos
              </a>
            </ng-container>

            <!-- Menú para RESTAURANTE -->
            <ng-container *ngIf="authService.userRole() === 'RESTAURANTE'">
              <div class="nav-section-title">MI NEGOCIO</div>
              <a routerLink="/restaurantes" routerLinkActive="active" class="nav-link">
                <span>🏪</span> Mis Restaurantes
              </a>
              <a routerLink="/ingredientes" routerLinkActive="active" class="nav-link">
                <span>🥗</span> Catálogo Ingredientes
              </a>
            </ng-container>

            <!-- Menú Común: Perfil -->
            <div class="nav-section-title">CUENTA</div>
            <a routerLink="/perfil" routerLinkActive="active" class="nav-link">
              <span>👤</span> Mi Perfil
            </a>
          </nav>
        </aside>

        <!-- Contenido Central -->
        <main class="main-content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .layout-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 1.5rem;
      background-color: var(--surface);
      border-bottom: 1px solid var(--border);
      height: 64px;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--secondary);
    }
    .user-menu {
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }
    .user-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .user-name {
      font-weight: 500;
      font-size: 0.875rem;
    }
    .body-wrapper {
      display: flex;
      flex: 1;
    }
    .sidebar {
      width: 240px;
      background-color: var(--surface);
      border-right: 1px solid var(--border);
      padding: 1.5rem 1rem;
    }
    .nav-section-title {
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.05em;
      margin: 1rem 0 0.5rem 0.5rem;
    }
    .nav-link {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.625rem 0.75rem;
      border-radius: var(--radius);
      color: var(--text-main);
      font-weight: 500;
      font-size: 0.875rem;
      margin-bottom: 0.25rem;
      transition: background 0.15s;
    }
    .nav-link:hover {
      background-color: #f1f5f9;
      text-decoration: none;
    }
    .nav-link.active {
      background-color: var(--primary-light);
      color: var(--primary);
      font-weight: 600;
    }
    .main-content {
      flex: 1;
      padding: 2rem;
      overflow-y: auto;
      max-width: 1200px;
      margin: 0 auto;
      width: 100%;
    }
    @media (max-width: 768px) {
      .body-wrapper {
        flex-direction: column;
      }
      .sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border);
        padding: 0.5rem;
      }
      .nav-menu {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
      }
      .nav-section-title {
        display: none;
      }
    }
  `]
})
export class MainLayoutComponent {
  authService = inject(AuthService);

  getRoleBadgeClass(role?: string): string {
    switch (role) {
      case 'ADMINISTRADOR': return 'badge-danger';
      case 'RESTAURANTE': return 'badge-warning';
      default: return 'badge-secondary';
    }
  }
}
