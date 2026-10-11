import { AppIconComponent } from '../../shared/app-icon/app-icon.component';
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { BrandLogoComponent } from '../../shared/brand-logo/brand-logo.component';

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [AppIconComponent, CommonModule, RouterOutlet, RouterLink, RouterLinkActive, BrandLogoComponent],
  template: `
    <div class="layout-container">
      <!-- Barra Superior -->
      <header class="topbar">
        <div class="brand">
          <app-brand-logo size="header" />
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
                <span><app-icon name="users" class="app-icon-inline"></app-icon></span> Usuarios
              </a>
              <a routerLink="/restaurantes" routerLinkActive="active" class="nav-link">
                <span><app-icon name="store" class="app-icon-inline"></app-icon></span> Restaurantes
              </a>
              <a routerLink="/admin/categorias" routerLinkActive="active" class="nav-link">
                <span><app-icon name="layers" class="app-icon-inline"></app-icon></span> Categorías
              </a>
              <div class="nav-section-title">PLANIFICACIÓN & IA</div>
              <a routerLink="/asistente" routerLinkActive="active" class="nav-link">
                <span><app-icon name="bot" class="app-icon-inline"></app-icon></span> Asistente IA
              </a>
              <a routerLink="/inicio" routerLinkActive="active" class="nav-link">
                <span><app-icon name="house" class="app-icon-inline"></app-icon></span> Panel Cliente
              </a>
              <a routerLink="/planificaciones" routerLinkActive="active" class="nav-link">
                <span><app-icon name="clipboard-list" class="app-icon-inline"></app-icon></span> Planificaciones
              </a>
              <a routerLink="/preferencias" routerLinkActive="active" class="nav-link">
                <span><app-icon name="sliders-horizontal" class="app-icon-inline"></app-icon></span> Preferencias
              </a>
            </ng-container>

            <!-- Menú para CLIENTE -->
            <ng-container *ngIf="authService.userRole() === 'CLIENTE'">
              <div class="nav-section-title">ASISTENTE VIRTUAL</div>
              <a routerLink="/asistente" routerLinkActive="active" class="nav-link">
                <span><app-icon name="bot" class="app-icon-inline"></app-icon></span> Asistente IA
              </a>
              <div class="nav-section-title">PLANIFICACIÓN</div>
              <a routerLink="/inicio" routerLinkActive="active" class="nav-link">
                <span><app-icon name="house" class="app-icon-inline"></app-icon></span> Inicio
              </a>
              <a routerLink="/planificaciones/nueva" routerLinkActive="active" class="nav-link">
                <span><app-icon name="utensils" class="app-icon-inline"></app-icon></span> Planificar comida
              </a>
              <a routerLink="/planificaciones" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" class="nav-link">
                <span><app-icon name="clipboard-list" class="app-icon-inline"></app-icon></span> Mis planificaciones
              </a>
              <a routerLink="/preferencias" routerLinkActive="active" class="nav-link">
                <span><app-icon name="sliders-horizontal" class="app-icon-inline"></app-icon></span> Mis preferencias
              </a>
              <div class="nav-section-title">PEDIDOS & RESERVAS</div>
              <a routerLink="/mis-reservas" routerLinkActive="active" class="nav-link">
                <span><app-icon name="calendar-days" class="app-icon-inline"></app-icon></span> Mis Reservas
              </a>
              <a routerLink="/mis-pedidos" routerLinkActive="active" class="nav-link">
                <span><app-icon name="receipt" class="app-icon-inline"></app-icon></span> Mis Pedidos
              </a>
            </ng-container>

            <!-- Menú para RESTAURANTE -->
            <ng-container *ngIf="authService.userRole() === 'RESTAURANTE'">
              <div class="nav-section-title">MI NEGOCIO</div>
              <a routerLink="/restaurantes" routerLinkActive="active" class="nav-link">
                <span><app-icon name="store" class="app-icon-inline"></app-icon></span> Mis Restaurantes
              </a>
            </ng-container>

            <!-- Menú Común: Perfil -->
            <div class="nav-section-title">CUENTA</div>
            <a routerLink="/perfil" routerLinkActive="active" class="nav-link">
              <span><app-icon name="user-round" class="app-icon-inline"></app-icon></span> Mi Perfil
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
      height: 64px;
      min-height: 64px;
      flex: 0 0 64px;
      padding: 0 1.5rem;
      background-color: var(--surface);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 10px rgb(35 27 18 / 0.035);
    }
    .brand {
      display: flex;
      align-items: center;
      min-width: 0;
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
      width: 100%;
      min-width: 0;
      max-width: 1600px;
      margin: 0 auto;
    }
    .sidebar {
      width: 258px;
      flex: 0 0 258px;
      background-color: var(--surface);
      border-right: 1px solid var(--border);
      padding: 1.65rem 1rem;
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
      background-color: #f7f7f6;
      text-decoration: none;
    }
    .nav-link.active {
      background-color: var(--primary-light);
      color: var(--primary);
      font-weight: 600;
      box-shadow: inset 3px 0 0 var(--primary);
    }
    .main-content {
      flex: 1;
      min-width: 0;
      padding: clamp(1.25rem, 3vw, 2.5rem);
      overflow-y: auto;
      max-width: 1320px;
      margin: 0;
      width: 100%;
    }
    @media (max-width: 768px) {
      .body-wrapper {
        flex-direction: column;
      }
      .sidebar {
        width: 100%;
        flex: 0 0 auto;
        border-right: none;
        border-bottom: 1px solid var(--border);
        padding: 0.55rem 0.75rem;
      }
      .nav-menu {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
      }
      .nav-link { margin-bottom: 0; }
      .main-content { padding: 1.25rem 1rem; }
      .nav-section-title {
        display: none;
      }
    }
    @media (max-width: 520px) {
      .topbar {
        height: 64px;
        min-height: 64px;
        flex-basis: 64px;
        padding: 0 0.75rem;
        gap: 0.5rem;
      }
      .brand { flex: 0 1 auto; }
      .user-menu { margin-left: auto; gap: 0.2rem; flex: 0 0 auto; flex-direction: column; align-items: flex-end; }
      .user-info { flex-direction: column; align-items: flex-end; gap: 0.1rem; }
      .user-name { display: none; }
      .user-info .badge { font-size: 0.65rem; line-height: 1.2; }
      .user-menu .btn { min-height: 32px; padding: 0.35rem 0.55rem; font-size: 0.75rem; }
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
