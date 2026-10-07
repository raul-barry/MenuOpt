import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { LoginRequest, LoginResponse, RegistroRequest, Usuario } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private readonly apiUrl = `${environment.apiUrl}/autenticacion`;

  private readonly TOKEN_KEY = 'menuopt_token';
  private readonly USER_KEY = 'menuopt_user';

  // Signals reactivos para estado de usuario y sesión
  private currentUserSignal = signal<Usuario | null>(this.getStoredUser());

  currentUser = this.currentUserSignal.asReadonly();
  isAuthenticated = computed(() => !!this.currentUserSignal());
  userRole = computed(() => {
    const u = this.currentUserSignal();
    if (u?.rol?.nombre) return u.rol.nombre.trim().toUpperCase();
    // Fallback: decodificar desde el token JWT almacenado
    const token = this.getToken();
    if (token) {
      try {
        const payloadBase64 = token.split('.')[1];
        if (payloadBase64) {
          const decodedJson = JSON.parse(atob(payloadBase64));
          if (decodedJson.rol) return String(decodedJson.rol).trim().toUpperCase();
        }
      } catch (e) {
        // Ignorar error de parsing
      }
    }
    return '';
  });

  // =========================================================================
  // CASO DE USO: CU02 - INICIAR SESIÓN
  // =========================================================================
  login(credenciales: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credenciales).pipe(
      tap((res) => {
        this.saveSession(res.access_token, res.usuario);
        this.redirectAfterLogin(res.usuario.rol?.nombre);
      })
    );
  }

  // =========================================================================
  // CASO DE USO: CU01 - REGISTRARSE
  // =========================================================================
  registro(datos: RegistroRequest): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.apiUrl}/registro`, datos);
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUserSignal.set(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  hasRole(allowedRoles: string[]): boolean {
    const currentRole = this.userRole();
    return allowedRoles.includes(currentRole);
  }

  updateCurrentUser(usuario: Usuario): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(usuario));
    this.currentUserSignal.set(usuario);
  }

  private saveSession(token: string, usuario: Usuario): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(usuario));
    this.currentUserSignal.set(usuario);
  }

  private getStoredUser(): Usuario | null {
    const stored = localStorage.getItem(this.USER_KEY);
    if (!stored) return null;
    try {
      return JSON.parse(stored) as Usuario;
    } catch {
      return null;
    }
  }

  private redirectAfterLogin(role?: string): void {
    switch (role) {
      case 'ADMINISTRADOR':
        this.router.navigate(['/admin/usuarios']);
        break;
      case 'RESTAURANTE':
        this.router.navigate(['/restaurantes']);
        break;
      case 'CLIENTE':
        this.router.navigate(['/inicio']);
        break;
      default:
        this.router.navigate(['/perfil']);
        break;
    }
  }
}
