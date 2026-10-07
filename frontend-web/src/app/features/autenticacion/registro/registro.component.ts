import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

// Validador de coincidencia de contraseñas
function confirmarPasswordValidator(control: AbstractControl) {
  const contrasena = control.get('contrasena')?.value;
  const confirmar = control.get('confirmarContrasena')?.value;
  if (contrasena && confirmar && contrasena !== confirmar) {
    control.get('confirmarContrasena')?.setErrors({ noCoincide: true });
    return { noCoincide: true };
  }
  return null;
}

// =========================================================================
// CASO DE USO: CU01 - REGISTRARSE
// Pantalla de registro de cliente con validación y confirmación.
// =========================================================================
@Component({
  selector: 'app-registro',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
    <div>
      <h3 style="margin-bottom: 1.5rem; text-align: center;">Crear Cuenta de Cliente</h3>

      <div *ngIf="errorMessage()" class="alert alert-danger">
        {{ errorMessage() }}
      </div>

      <div *ngIf="successMessage()" class="alert alert-success">
        {{ successMessage() }}
      </div>

      <form [formGroup]="registroForm" (ngSubmit)="onSubmit()">
        <div class="form-group">
          <label class="form-label" for="nombres">Nombres</label>
          <input
            id="nombres"
            type="text"
            class="form-control"
            [class.is-invalid]="f['nombres'].touched && f['nombres'].invalid"
            formControlName="nombres"
            placeholder="Juan"
          />
          <div *ngIf="f['nombres'].touched && f['nombres'].invalid" class="invalid-feedback">
            <span *ngIf="f['nombres'].errors?.['required']">Los nombres son obligatorios.</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="apellidos">Apellidos</label>
          <input
            id="apellidos"
            type="text"
            class="form-control"
            [class.is-invalid]="f['apellidos'].touched && f['apellidos'].invalid"
            formControlName="apellidos"
            placeholder="Pérez"
          />
          <div *ngIf="f['apellidos'].touched && f['apellidos'].invalid" class="invalid-feedback">
            <span *ngIf="f['apellidos'].errors?.['required']">Los apellidos son obligatorios.</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="correo">Correo Electrónico</label>
          <input
            id="correo"
            type="email"
            class="form-control"
            [class.is-invalid]="f['correo'].touched && f['correo'].invalid"
            formControlName="correo"
            placeholder="juan@example.com"
          />
          <div *ngIf="f['correo'].touched && f['correo'].invalid" class="invalid-feedback">
            <span *ngIf="f['correo'].errors?.['required']">El correo es obligatorio.</span>
            <span *ngIf="f['correo'].errors?.['email']">Ingrese un correo válido.</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="telefono">Teléfono (Opcional)</label>
          <input
            id="telefono"
            type="text"
            class="form-control"
            formControlName="telefono"
            placeholder="71234567"
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="contrasena">Contraseña (Mínimo 8 caracteres)</label>
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
            <span *ngIf="f['contrasena'].errors?.['minlength']">Debe tener al menos 8 caracteres.</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="confirmarContrasena">Confirmar Contraseña</label>
          <input
            id="confirmarContrasena"
            type="password"
            class="form-control"
            [class.is-invalid]="f['confirmarContrasena'].touched && f['confirmarContrasena'].invalid"
            formControlName="confirmarContrasena"
            placeholder="••••••••"
          />
          <div *ngIf="f['confirmarContrasena'].touched && f['confirmarContrasena'].invalid" class="invalid-feedback">
            <span *ngIf="f['confirmarContrasena'].errors?.['required']">Confirme su contraseña.</span>
            <span *ngIf="f['confirmarContrasena'].errors?.['noCoincide']">Las contraseñas no coinciden.</span>
          </div>
        </div>

        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 1rem;" [disabled]="isLoading() || registroForm.invalid">
          <span *ngIf="isLoading()">Registrando...</span>
          <span *ngIf="!isLoading()">Crear Cuenta</span>
        </button>
      </form>

      <div style="margin-top: 1.5rem; text-align: center; font-size: 0.875rem;">
        ¿Ya tienes cuenta? <a routerLink="/login">Inicia Sesión</a>
      </div>
    </div>
  `
})
export class RegistroComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  registroForm = this.fb.group({
    nombres: ['', [Validators.required, Validators.minLength(2)]],
    apellidos: ['', [Validators.required, Validators.minLength(2)]],
    correo: ['', [Validators.required, Validators.email]],
    telefono: [''],
    contrasena: ['', [Validators.required, Validators.minLength(8)]],
    confirmarContrasena: ['', [Validators.required]]
  }, { validators: confirmarPasswordValidator });

  isLoading = signal(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);

  get f() {
    return this.registroForm.controls;
  }

  // --- LÓGICA CU01: Registro de nuevo cliente a través de POST /autenticacion/registro ---
  onSubmit(): void {
    if (this.registroForm.invalid) return;

    this.isLoading.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    const formValues = this.registroForm.value;
    const requestData = {
      nombres: formValues.nombres!.trim(),
      apellidos: formValues.apellidos!.trim(),
      correo: formValues.correo!.trim().toLowerCase(),
      contrasena: formValues.contrasena!,
      telefono: formValues.telefono ? formValues.telefono.trim() : undefined
    };

    this.authService.registro(requestData).subscribe({
      next: () => {
        this.isLoading.set(false);
        this.successMessage.set('¡Registro completado exitosamente! Redirigiendo al inicio de sesión...');
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.isLoading.set(false);
        if (err.status === 0) {
          this.errorMessage.set('No se pudo comunicar con el backend. Verifique que el servicio esté activo.');
        } else if (err.status === 409) {
          this.errorMessage.set('El correo electrónico ya se encuentra registrado.');
        } else if (err.error?.detail) {
          if (typeof err.error.detail === 'string') {
            this.errorMessage.set(err.error.detail);
          } else if (Array.isArray(err.error.detail)) {
            const mensajes = err.error.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
            this.errorMessage.set(`Datos inválidos: ${mensajes}`);
          } else {
            this.errorMessage.set('Error al registrar usuario. Verifique los datos ingresados.');
          }
        } else {
          this.errorMessage.set('Error al registrar usuario. Verifique los datos ingresados.');
        }
      }
    });
  }
}
