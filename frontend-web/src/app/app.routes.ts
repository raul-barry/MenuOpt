import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';
import { AuthLayoutComponent } from './layouts/auth-layout/auth-layout.component';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';

export const routes: Routes = [
  // Rutas Públicas (Autenticación)
  {
    path: '',
    component: AuthLayoutComponent,
    children: [
      {
        path: '',
        redirectTo: 'login',
        pathMatch: 'full'
      },
      // CASO DE USO: CU02 - INICIAR SESIÓN
      {
        path: 'login',
        loadComponent: () => import('./features/autenticacion/login/login.component').then(m => m.LoginComponent)
      },
      // CASO DE USO: CU01 - REGISTRARSE
      {
        path: 'registro',
        loadComponent: () => import('./features/autenticacion/registro/registro.component').then(m => m.RegistroComponent)
      }
    ]
  },

  // Rutas Protegidas (Panel Principal)
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      // DASHBOARD CLIENTE (Inicio)
      {
        path: 'inicio',
        loadComponent: () => import('./features/dashboard-cliente/dashboard-cliente.component').then(m => m.DashboardClienteComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU26 - USAR ASISTENCIA CON IA
      {
        path: 'asistente',
        loadComponent: () => import('./features/asistente/asistente-chat/asistente-chat.component').then(m => m.AsistenteChatComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU12 - DEFINIR PREFERENCIAS
      {
        path: 'preferencias',
        loadComponent: () => import('./features/preferencias/preferencias.component').then(m => m.PreferenciasComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU11 - MIS PLANIFICACIONES
      {
        path: 'planificaciones',
        loadComponent: () => import('./features/planificaciones/planificaciones-lista/planificaciones-lista.component').then(m => m.PlanificacionesListaComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU11 - NUEVA PLANIFICACIÓN
      {
        path: 'planificaciones/nueva',
        loadComponent: () => import('./features/planificaciones/nueva-planificacion/nueva-planificacion.component').then(m => m.NuevaPlanificacionComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU11 - DETALLE DE PLANIFICACIÓN
      {
        path: 'planificaciones/:id',
        loadComponent: () => import('./features/planificaciones/detalle-planificacion/detalle-planificacion.component').then(m => m.DetallePlanificacionComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU11 - EDITAR PLANIFICACIÓN
      {
        path: 'planificaciones/:id/editar',
        loadComponent: () => import('./features/planificaciones/editar-planificacion/editar-planificacion.component').then(m => m.EditarPlanificacionComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU13 - LISTAR RECOMENDACIONES
      {
        path: 'planificaciones/:id/recomendaciones',
        loadComponent: () => import('./features/recomendaciones/lista-recomendaciones/lista-recomendaciones.component').then(m => m.ListaRecomendacionesComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU14 - COMPARAR ALTERNATIVAS
      {
        path: 'planificaciones/:id/comparacion',
        loadComponent: () => import('./features/planificaciones/comparacion/comparacion.component').then(m => m.ComparacionComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU13 - DETALLE DE RECOMENDACIÓN
      {
        path: 'recomendaciones/:id',
        loadComponent: () => import('./features/recomendaciones/detalle-recomendacion/detalle-recomendacion.component').then(m => m.DetalleRecomendacionComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU15 - INGREDIENTES PARA PREPARACIÓN PROPIA
      {
        path: 'recomendaciones/:id/preparacion',
        loadComponent: () => import('./features/preparacion/detalle-preparacion/detalle-preparacion.component').then(m => m.DetallePreparacionComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU16 - LUGARES DE COMPRA AGRUPADOS
      {
        path: 'recomendaciones/:id/lugares-compra',
        loadComponent: () => import('./features/preparacion/lugares-compra/lugares-compra.component').then(m => m.LugaresCompraComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU03 - GESTIONAR PERFIL
      {
        path: 'perfil',
        loadComponent: () => import('./features/perfil/perfil.component').then(m => m.PerfilComponent)
      },

      // CASO DE USO: CU04 - GESTIONAR USUARIOS (Solo ADMINISTRADOR)
      {
        path: 'admin/usuarios',
        loadComponent: () => import('./features/usuarios/usuarios-lista/usuarios-lista.component').then(m => m.UsuariosListaComponent),
        canActivate: [roleGuard],
        data: { roles: ['ADMINISTRADOR'] }
      },

      // CASO DE USO: CU07 - GESTIONAR CATEGORÍAS (Solo ADMINISTRADOR)
      {
        path: 'admin/categorias',
        loadComponent: () => import('./features/categorias/categorias-lista/categorias-lista.component').then(m => m.CategoriasListaComponent),
        canActivate: [roleGuard],
        data: { roles: ['ADMINISTRADOR'] }
      },

      // CASO DE USO: CU06 - GESTIONAR RESTAURANTE (Lista de restaurantes)
      {
        path: 'restaurantes',
        loadComponent: () => import('./features/restaurantes/restaurantes-lista/restaurantes-lista.component').then(m => m.RestaurantesListaComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU05 - REGISTRAR RESTAURANTE
      {
        path: 'restaurantes/nuevo',
        loadComponent: () => import('./features/restaurantes/restaurante-form/restaurante-form.component').then(m => m.RestauranteFormComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU06 - GESTIONAR RESTAURANTE (Detalle)
      {
        path: 'restaurantes/:id',
        loadComponent: () => import('./features/restaurantes/restaurante-detalle/restaurante-detalle.component').then(m => m.RestauranteDetalleComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU06 - GESTIONAR RESTAURANTE (Editar)
      {
        path: 'restaurantes/:id/editar',
        loadComponent: () => import('./features/restaurantes/restaurante-form/restaurante-form.component').then(m => m.RestauranteFormComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU08 - GESTIONAR PLATOS & CU10 - GESTIONAR DISPONIBILIDAD
      {
        path: 'restaurantes/:id/platos',
        loadComponent: () => import('./features/platos/platos-lista/platos-lista.component').then(m => m.PlatosListaComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU17, CU18, CU19 - PLANO 2D Y DISTRIBUCIÓN DE MESAS
      {
        path: 'restaurantes/:id/distribucion',
        loadComponent: () => import('./features/distribucion/distribucion-editor/distribucion-editor.component').then(m => m.DistribucionEditorComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU20, CU21 - RESERVAR MESA EN RESTAURANTE
      {
        path: 'restaurantes/:id/reservar',
        loadComponent: () => import('./features/reservas/nueva-reserva/nueva-reserva.component').then(m => m.NuevaReservaComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU22 - GESTIONAR RESERVAS DE RESTAURANTE
      {
        path: 'restaurantes/:id/reservas',
        loadComponent: () => import('./features/reservas/gestion-reservas/gestion-reservas.component').then(m => m.GestionReservasComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU21 - MIS RESERVAS (CLIENTE)
      {
        path: 'mis-reservas',
        loadComponent: () => import('./features/reservas/mis-reservas/mis-reservas.component').then(m => m.MisReservasComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU21 & CU22 - DETALLE DE RESERVA
      {
        path: 'reservas/:id',
        loadComponent: () => import('./features/reservas/detalle-reserva/detalle-reserva.component').then(m => m.DetalleReservaComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU23 - ENVIAR PEDIDO (CLIENTE)
      {
        path: 'restaurantes/:id/pedido',
        loadComponent: () => import('./features/pedidos/crear-pedido/crear-pedido.component').then(m => m.CrearPedidoComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU24 - MIS PEDIDOS (HISTORIAL CLIENTE)
      {
        path: 'mis-pedidos',
        loadComponent: () => import('./features/pedidos/mis-pedidos/mis-pedidos.component').then(m => m.MisPedidosComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU24 - DETALLE DE PEDIDO
      {
        path: 'pedidos/:id',
        loadComponent: () => import('./features/pedidos/detalle-pedido/detalle-pedido.component').then(m => m.DetallePedidoComponent),
        canActivate: [roleGuard],
        data: { roles: ['CLIENTE', 'RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU24 - GESTIÓN DE PEDIDOS DEL RESTAURANTE
      {
        path: 'restaurantes/:id/pedidos',
        loadComponent: () => import('./features/pedidos/gestion-pedidos/gestion-pedidos.component').then(m => m.GestionPedidosComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU08 - GESTIONAR PLATOS (Crear Plato)
      {
        path: 'restaurantes/:id/platos/nuevo',
        loadComponent: () => import('./features/platos/plato-form/plato-form.component').then(m => m.PlatoFormComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      },

      // CASO DE USO: CU08 - GESTIONAR PLATOS (Editar Plato)
      {
        path: 'platos/:id/editar',
        loadComponent: () => import('./features/platos/plato-form/plato-form.component').then(m => m.PlatoFormComponent),
        canActivate: [roleGuard],
        data: { roles: ['RESTAURANTE', 'ADMINISTRADOR'] }
      }
    ]
  },

  // Ruta comodín para rutas no encontradas
  {
    path: '**',
    redirectTo: 'login'
  }
];
