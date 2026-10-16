import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

// =========================================================================
// CASO DE USO: CU02 - INICIAR SESIÓN
// Pantalla de inicio de sesión con validación y emisión de JWT.
// =========================================================================
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div>
      <h3 style="margin-bottom: 1.5rem; text-align: center;">Iniciar Sesión</h3>

      <div *ngIf="errorMessage()" class="alert alert-danger">
        {{ errorMessage() }}
      </div>

      <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
        <div class="form-group">
          <label class="form-label" for="correo">Correo Electrónico</label>
          <input
            id="correo"
            type="email"
            class="form-control"
            [class.is-invalid]="f['correo'].touched && f['correo'].invalid"
            formControlName="correo"
            placeholder="ejemplo@menuopt.com"
          />
          <div *ngIf="f['correo'].touched && f['correo'].invalid" class="invalid-feedback">
            <span *ngIf="f['correo'].errors?.['required']">El correo es obligatorio.</span>
            <span *ngIf="f['correo'].errors?.['email']">Ingrese un formato de correo válido.</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="contrasena">Contraseña</label>
          <input
            id="contrasena"
            type="password"
            class="form-control"
            [class.is-invalid]="f['contrasena'].touched && f['contrasena'].invalid"
            formControlName="contrasena"
            placeholder="••••••••"
          />
          <div *ngIf="f['contrasena'].touched && f['contrasena'].invalid" class="invalid-feedback">
            <span *ngIf="f['contrasena'].errors?.['required']">La contraseña es obligatoria.</span>
          </div>
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;" [disabled]="isLoading() || loginForm.invalid">
          <span *ngIf="isLoading()">Ingresando...</span>
          <span *ngIf="!isLoading()">Entrar</span>
        </button>
      </form>

      <div style="margin-top: 1.5rem; text-align: center; font-size: 0.875rem;">
        ¿No tienes cuenta? <a routerLink="/registro">Regístrate como Cliente</a>
      </div>
    </div>
  `
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);

  loginForm = this.fb.group({
    correo: ['', [Validators.required, Validators.email]],
    contrasena: ['', [Validators.required]]
  });

  isLoading = signal(false);
  errorMessage = signal<string | null>(null);

  get f() {
    return this.loginForm.controls;
  }

  // --- LÓGICA CU02: Envío de credenciales a POST /autenticacion/login ---
  onSubmit(): void {
    if (this.loginForm.invalid) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);

    const credenciales = {
      correo: this.loginForm.value.correo!.trim().toLowerCase(),
      contrasena: this.loginForm.value.contrasena!
    };

    this.authService.login(credenciales).subscribe({
      next: () => {
        this.isLoading.set(false);
      },
      error: (err) => {
        this.isLoading.set(false);
        if (err.status === 401) {
          this.errorMessage.set('Correo electrónico o contraseña incorrectos.');
        } else if (err.status === 403) {
          this.errorMessage.set('Su cuenta se encuentra inactiva o suspendida.');
        } else if (err.status === 0) {
          this.errorMessage.set('No se pudo conectar con el servidor backend. Verifique su conexión.');
        } else if (err.status >= 500) {
          this.errorMessage.set('Error interno del servidor. Por favor, intente nuevamente más tarde.');
        } else {
          this.errorMessage.set(err.error?.detail || 'Ocurrió un error al intentar iniciar sesión.');
        }
      }
    });
  }
}
