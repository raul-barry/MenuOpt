import { AppIconComponent } from '../../shared/app-icon/app-icon.component';
import { Component, inject, signal } from '@angular/core';
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
        <div class="topbar-left">
          <!-- Botón Menú Hamburguesa para Móviles -->
          <button
            class="menu-toggle-btn"
            (click)="toggleMenuMovil()"
            [attr.aria-expanded]="menuMovilAbierto()"
            aria-label="Abrir o cerrar menú de navegación"
          >
            <app-icon [name]="menuMovilAbierto() ? 'close' : 'menu-toggle'" class="app-icon-inline"></app-icon>
          </button>
          <div class="brand">
            <app-brand-logo size="header" />
          </div>
        </div>

        <div class="user-menu" *ngIf="authService.currentUser() as user">
          <div class="user-info">
            <span class="user-name">{{ user.nombres }} {{ user.apellidos }}</span>
            <span class="badge" [ngClass]="getRoleBadgeClass(user.rol?.nombre)">{{ user.rol?.nombre }}</span>
          </div>
          <button class="btn btn-outline btn-sm btn-logout" (click)="authService.logout()" title="Cerrar Sesión">
            <app-icon name="log-out" class="app-icon-inline"></app-icon>
            <span class="logout-text">Salir</span>
          </button>
        </div>
      </header>

      <div class="body-wrapper">
        <!-- Backdrop para Móviles -->
        <div
          class="sidebar-backdrop"
          *ngIf="menuMovilAbierto()"
          (click)="cerrarMenuMovil()"
          aria-hidden="true"
        ></div>

        <!-- Barra Lateral Dinámica según Rol (Drawer en móvil) -->
        <aside class="sidebar" [class.open]="menuMovilAbierto()">
          <div class="sidebar-header-movil">
            <span class="sidebar-movil-title">Navegación</span>
            <button class="btn-close-sidebar" (click)="cerrarMenuMovil()" aria-label="Cerrar menú">
              <app-icon name="close" class="app-icon-inline"></app-icon>
            </button>
          </div>

          <nav class="nav-menu">
            <!-- Menú para ADMINISTRADOR -->
            <ng-container *ngIf="authService.userRole() === 'ADMINISTRADOR'">
              <div class="nav-section-title">ADMINISTRACIÓN</div>
              <a routerLink="/admin/usuarios" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="users" class="app-icon-inline"></app-icon></span> Usuarios
              </a>
              <a routerLink="/restaurantes" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="store" class="app-icon-inline"></app-icon></span> Restaurantes
              </a>
              <a routerLink="/admin/categorias" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="layers" class="app-icon-inline"></app-icon></span> Categorías
              </a>
              <a routerLink="/proveedores" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="store" class="app-icon-inline"></app-icon></span> Proveedores & Precios
              </a>
              <a routerLink="/ingredientes" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="carrot" class="app-icon-inline"></app-icon></span> Ingredientes
              </a>
              <a routerLink="/admin/bitacora" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="shield" class="app-icon-inline"></app-icon></span> Bitácora
              </a>
              <div class="nav-section-title">PLANIFICACIÓN & IA</div>
              <a routerLink="/asistente" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="bot" class="app-icon-inline"></app-icon></span> Asistente IA
              </a>
              <a routerLink="/inicio" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="house" class="app-icon-inline"></app-icon></span> Panel Cliente
              </a>
              <a routerLink="/planificaciones" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="clipboard-list" class="app-icon-inline"></app-icon></span> Planificaciones
              </a>
              <a routerLink="/preferencias" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="sliders-horizontal" class="app-icon-inline"></app-icon></span> Preferencias
              </a>
              <a routerLink="/recetas" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="salad" class="app-icon-inline"></app-icon></span> Biblioteca Recetas (CU15)
              </a>
            </ng-container>

            <!-- Menú para CLIENTE -->
            <ng-container *ngIf="authService.userRole() === 'CLIENTE'">
              <div class="nav-section-title">ASISTENTE VIRTUAL</div>
              <a routerLink="/asistente" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="bot" class="app-icon-inline"></app-icon></span> Asistente IA
              </a>
              <div class="nav-section-title">PLANIFICACIÓN</div>
              <a routerLink="/inicio" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="house" class="app-icon-inline"></app-icon></span> Inicio
              </a>
              <a routerLink="/planificaciones/nueva" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="utensils" class="app-icon-inline"></app-icon></span> Planificar comida
              </a>
              <a routerLink="/planificaciones" routerLinkActive="active" (click)="cerrarMenuMovil()" [routerLinkActiveOptions]="{exact: true}" class="nav-link">
                <span><app-icon name="clipboard-list" class="app-icon-inline"></app-icon></span> Mis planificaciones
              </a>
              <a routerLink="/preferencias" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="sliders-horizontal" class="app-icon-inline"></app-icon></span> Mis preferencias
              </a>
              <a routerLink="/recetas" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="salad" class="app-icon-inline"></app-icon></span> Biblioteca de Recetas (CU15)
              </a>
              <div class="nav-section-title">PEDIDOS & RESERVAS</div>
              <a routerLink="/mis-reservas" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="calendar-days" class="app-icon-inline"></app-icon></span> Mis Reservas
              </a>
              <a routerLink="/mis-pedidos" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="receipt" class="app-icon-inline"></app-icon></span> Mis Pedidos
              </a>
            </ng-container>

            <!-- Menú para RESTAURANTE -->
            <ng-container *ngIf="authService.userRole() === 'RESTAURANTE'">
              <div class="nav-section-title">MI NEGOCIO</div>
              <a routerLink="/restaurantes" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="store" class="app-icon-inline"></app-icon></span> Mis Restaurantes
              </a>
              <a routerLink="/ingredientes" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="carrot" class="app-icon-inline"></app-icon></span> Catálogo Ingredientes
              </a>
            </ng-container>

            <!-- Menú para ADMINISTRADOR_TIENDA -->
            <ng-container *ngIf="authService.userRole() === 'ADMINISTRADOR_TIENDA'">
              <div class="nav-section-title">MI TIENDA / PROVEEDOR</div>
              <a routerLink="/proveedores" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="store" class="app-icon-inline"></app-icon></span> Mis Tiendas & Precios
              </a>
              <a routerLink="/ingredientes" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
                <span><app-icon name="carrot" class="app-icon-inline"></app-icon></span> Catálogo Ingredientes
              </a>
            </ng-container>

            <!-- Menú Común: Perfil -->
            <div class="nav-section-title">CUENTA</div>
            <a routerLink="/perfil" routerLinkActive="active" (click)="cerrarMenuMovil()" class="nav-link">
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
      overflow-x: hidden;
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
    .topbar-left {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      min-width: 0;
    }
    .menu-toggle-btn {
      display: none;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: transparent;
      color: var(--text-main);
      cursor: pointer;
      padding: 0;
      transition: background 0.15s ease, color 0.15s ease;
    }
    .menu-toggle-btn:hover {
      background: #f1f5f9;
      color: var(--primary);
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
      flex-shrink: 0;
    }
    .user-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .user-name {
      font-weight: 500;
      font-size: 0.875rem;
      white-space: nowrap;
    }
    .btn-logout {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }
    .body-wrapper {
      display: flex;
      flex: 1;
      width: 100%;
      min-width: 0;
      max-width: 1600px;
      margin: 0 auto;
      position: relative;
    }
    .sidebar-backdrop {
      display: none;
    }
    .sidebar-header-movil {
      display: none;
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
      padding: clamp(1rem, 2.5vw, 2.5rem);
      overflow-y: auto;
      max-width: 1320px;
      margin: 0;
      width: 100%;
    }

    /* =========================================================================
       RESPONSIVE BREAKPOINTS (TABLETS Y MÓVILES)
       ========================================================================= */
    @media (max-width: 768px) {
      .topbar {
        padding: 0 1rem;
      }
      .menu-toggle-btn {
        display: flex;
      }
      .sidebar-backdrop {
        display: block;
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(2px);
        z-index: 998;
      }
      .sidebar {
        position: fixed;
        top: 0;
        left: -290px;
        width: 280px;
        height: 100vh;
        z-index: 999;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.18);
        overflow-y: auto;
        padding: 1rem 0.85rem;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .sidebar.open {
        transform: translateX(290px);
      }
      .sidebar-header-movil {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 0.75rem;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
      }
      .sidebar-movil-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: var(--text-main);
      }
      .btn-close-sidebar {
        background: transparent;
        border: none;
        color: var(--text-muted);
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 6px;
      }
      .btn-close-sidebar:hover {
        background: #f1f5f9;
        color: var(--text-main);
      }
      .nav-menu {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }
      .nav-section-title {
        display: block;
        margin: 0.75rem 0 0.35rem 0.5rem;
      }
      .main-content {
        padding: 1rem 0.75rem;
      }
    }

    @media (max-width: 520px) {
      .topbar {
        height: 58px;
        min-height: 58px;
        flex-basis: 58px;
        padding: 0 0.65rem;
        gap: 0.4rem;
      }
      .topbar-left {
        gap: 0.4rem;
      }
      .menu-toggle-btn {
        width: 36px;
        height: 36px;
      }
      .user-menu {
        gap: 0.4rem;
      }
      .user-name {
        display: none;
      }
      .user-info .badge {
        font-size: 0.65rem;
        padding: 0.2rem 0.45rem;
      }
      .logout-text {
        display: none;
      }
      .btn-logout {
        padding: 0.35rem 0.5rem;
        min-height: 34px;
      }
    }
  `]
})
export class MainLayoutComponent {
  authService = inject(AuthService);
  menuMovilAbierto = signal<boolean>(false);

  toggleMenuMovil(): void {
    this.menuMovilAbierto.update(v => !v);
  }

  cerrarMenuMovil(): void {
    this.menuMovilAbierto.set(false);
  }

  getRoleBadgeClass(role?: string): string {
    switch (role) {
      case 'ADMINISTRADOR': return 'badge-danger';
      case 'RESTAURANTE': return 'badge-warning';
      case 'ADMINISTRADOR_TIENDA': return 'badge-info';
      default: return 'badge-secondary';
    }
  }
}

