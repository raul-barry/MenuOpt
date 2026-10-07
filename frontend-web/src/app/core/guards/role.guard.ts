import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const allowedRoles = route.data?.['roles'] as string[] | undefined;

  if (!authService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  if (allowedRoles && !authService.hasRole(allowedRoles)) {
    // Si no tiene el rol permitido, redirigir a su pantalla por defecto
    const currentRole = authService.userRole();
    if (currentRole === 'RESTAURANTE') {
      router.navigate(['/restaurantes']);
    } else if (currentRole === 'ADMINISTRADOR') {
      router.navigate(['/admin/usuarios']);
    } else if (currentRole === 'CLIENTE') {
      router.navigate(['/inicio']);
    } else {
      router.navigate(['/perfil']);
    }
    return false;
  }

  return true;
};
