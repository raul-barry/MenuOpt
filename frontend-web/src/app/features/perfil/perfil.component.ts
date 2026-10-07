import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, AbstractControl } from '@angular/forms';
import { UsuarioService } from '../../core/services/usuario.service';
import { AuthService } from '../../core/services/auth.service';
import { Usuario } from '../../core/models/usuario.model';

function confirmarPasswordValidator(control: AbstractControl) {
  const nueva = control.get('contrasena_nueva')?.value;
  const confirmar = control.get('confirmar_nueva')?.value;
  if (nueva && confirmar && nueva !== confirmar) {
    control.get('confirmar_nueva')?.setErrors({ noCoincide: true });
    return { noCoincide: true };
  }
  return null;
}

// =========================================================================
// CASO DE USO: CU03 - GESTIONAR PERFIL
// Vista para consultar perfil, actualizar datos personales y cambiar contraseña.
// =========================================================================
@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="perfil-container">
      <h2>Mi Perfil</h2>
      <p style="color: var(--text-muted); margin-bottom: 1.5rem;">
        Gestiona tu información personal y credenciales de acceso.
      </p>

      <!-- Mensajes -->
      <div *ngIf="perfilSuccess()" class="alert alert-success">{{ perfilSuccess() }}</div>
      <div *ngIf="perfilError()" class="alert alert-danger">{{ perfilError() }}</div>

      <!-- Tarjeta: Datos Generales e Inmutables -->
      <div class="card" *ngIf="usuario() as user">
        <div class="card-header">
          <h3>Información de Cuenta</h3>
          <span class="badge badge-success">{{ user.estado }}</span>
        </div>
        <div class="grid-2">
          <div>
            <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">ID de Usuario</span>
            <p style="font-weight: 600;">#{{ user.id_usuario }}</p>
          </div>
          <div>
            <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Rol Asignado</span>
            <p style="font-weight: 600; color: var(--primary);">{{ user.rol?.nombre }}</p>
          </div>
          <div>
            <span style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Fecha de Registro</span>
            <p>{{ user.fecha_registro | date:'medium' }}</p>
          </div>
        </div>
      </div>

      <!-- Tarjeta: Modificar Perfil -->
      <div class="card">
        <div class="card-header">
          <h3>Editar Datos Personales</h3>
        </div>
        <form [formGroup]="perfilForm" (ngSubmit)="onActualizarPerfil()">
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label" for="nombres">Nombres</label>
              <input id="nombres" type="text" class="form-control" formControlName="nombres" />
            </div>
            <div class="form-group">
              <label class="form-label" for="apellidos">Apellidos</label>
              <input id="apellidos" type="text" class="form-control" formControlName="apellidos" />
            </div>
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label" for="correo">Correo Electrónico</label>
              <input id="correo" type="email" class="form-control" formControlName="correo" />
            </div>
            <div class="form-group">
              <label class="form-label" for="telefono">Teléfono</label>
              <input id="telefono" type="text" class="form-control" formControlName="telefono" />
            </div>
          </div>
          <button type="submit" class="btn btn-primary" [disabled]="loadingPerfil() || perfilForm.invalid">
            <span *ngIf="loadingPerfil()">Guardando...</span>
            <span *ngIf="!loadingPerfil()">Actualizar Perfil</span>
          </button>
        </form>
      </div>

      <!-- Tarjeta: Cambiar Contraseña -->
      <div class="card">
        <div class="card-header">
          <h3>Seguridad: Cambiar Contraseña</h3>
        </div>
        <div *ngIf="passSuccess()" class="alert alert-success">{{ passSuccess() }}</div>
        <div *ngIf="passError()" class="alert alert-danger">{{ passError() }}</div>

        <form [formGroup]="passForm" (ngSubmit)="onCambiarContrasena()">
          <div class="form-group">
            <label class="form-label" for="actual">Contraseña Actual</label>
            <input id="actual" type="password" class="form-control" formControlName="contrasena_actual" placeholder="••••••••" />
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label" for="nueva">Nueva Contraseña (mínimo 8 caracteres)</label>
              <input id="nueva" type="password" class="form-control" formControlName="contrasena_nueva" placeholder="••••••••" />
            </div>
            <div class="form-group">
              <label class="form-label" for="confirmar">Confirmar Nueva Contraseña</label>
              <input id="confirmar" type="password" class="form-control" formControlName="confirmar_nueva" placeholder="••••••••" />
            </div>
          </div>
          <button type="submit" class="btn btn-secondary" [disabled]="loadingPass() || passForm.invalid">
            <span *ngIf="loadingPass()">Cambiando...</span>
            <span *ngIf="!loadingPass()">Cambiar Contraseña</span>
          </button>
        </form>
      </div>
    </div>
  `
})
export class PerfilComponent implements OnInit {
  private fb = inject(FormBuilder);
  private usuarioService = inject(UsuarioService);
  private authService = inject(AuthService);

  usuario = signal<Usuario | null>(null);
  loadingPerfil = signal(false);
  loadingPass = signal(false);
  perfilSuccess = signal<string | null>(null);
  perfilError = signal<string | null>(null);
  passSuccess = signal<string | null>(null);
  passError = signal<string | null>(null);

  perfilForm = this.fb.group({
    nombres: ['', [Validators.required, Validators.minLength(2)]],
    apellidos: ['', [Validators.required, Validators.minLength(2)]],
    correo: ['', [Validators.required, Validators.email]],
    telefono: ['']
  });

  passForm = this.fb.group({
    contrasena_actual: ['', [Validators.required]],
    contrasena_nueva: ['', [Validators.required, Validators.minLength(8)]],
    confirmar_nueva: ['', [Validators.required]]
  }, { validators: confirmarPasswordValidator });

  ngOnInit(): void {
    this.cargarPerfil();
  }

  // --- LÓGICA CU03: Consultar Perfil mediante GET /usuarios/perfil ---
  cargarPerfil(): void {
    this.usuarioService.getPerfil().subscribe({
      next: (user) => {
        this.usuario.set(user);
        this.perfilForm.patchValue({
          nombres: user.nombres,
          apellidos: user.apellidos,
          correo: user.correo,
          telefono: user.telefono || ''
        });
      },
      error: () => {
        this.perfilError.set('No se pudo cargar la información del perfil.');
      }
    });
  }

  // --- LÓGICA CU03: Modificar Perfil mediante PUT /usuarios/perfil ---
  onActualizarPerfil(): void {
    if (this.perfilForm.invalid) return;

    this.loadingPerfil.set(true);
    this.perfilSuccess.set(null);
    this.perfilError.set(null);

    const datos = {
      nombres: this.perfilForm.value.nombres!.trim(),
      apellidos: this.perfilForm.value.apellidos!.trim(),
      correo: this.perfilForm.value.correo!.trim().toLowerCase(),
      telefono: this.perfilForm.value.telefono?.trim() || undefined
    };

    this.usuarioService.updatePerfil(datos).subscribe({
      next: (userActualizado) => {
        this.loadingPerfil.set(false);
        this.usuario.set(userActualizado);
        this.authService.updateCurrentUser(userActualizado);
        this.perfilSuccess.set('Perfil actualizado exitosamente.');
      },
      error: (err) => {
        this.loadingPerfil.set(false);
        if (err.status === 409) {
          this.perfilError.set('El correo electrónico ya está en uso por otra cuenta.');
        } else {
          this.perfilError.set('Error al actualizar el perfil.');
        }
      }
    });
  }

  // --- LÓGICA CU03: Cambiar Contraseña mediante PUT /usuarios/perfil/contrasena ---
  onCambiarContrasena(): void {
    if (this.passForm.invalid) return;

    this.loadingPass.set(true);
    this.passSuccess.set(null);
    this.passError.set(null);

    const datos = {
      contrasena_actual: this.passForm.value.contrasena_actual!,
      contrasena_nueva: this.passForm.value.contrasena_nueva!
    };

    this.usuarioService.cambiarContrasena(datos).subscribe({
      next: (res) => {
        this.loadingPass.set(false);
        this.passSuccess.set(res.mensaje || 'Contraseña actualizada con éxito.');
        this.passForm.reset();
      },
      error: (err) => {
        this.loadingPass.set(false);
        if (err.status === 400) {
          this.passError.set(err.error?.detail || 'La contraseña actual no es correcta.');
        } else {
          this.passError.set('Error al cambiar contraseña.');
        }
      }
    });
  }
}
