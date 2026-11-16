// CASO DE USO: Biblioteca de Recetas
import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AppIconComponent } from '../../../shared/app-icon/app-icon.component';
import { AuthService } from '../../../core/services/auth.service';
import { RecetaService } from '../../../core/services/receta.service';
import { IngredienteService } from '../../../core/services/ingrediente.service';
import { Receta, RecetaCrear, RecetaConsultaIARespuesta } from '../../../core/models/receta.model';
import { Ingrediente } from '../../../core/models/ingrediente.model';

@Component({
  selector: 'app-biblioteca-recetas',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, AppIconComponent],
  template: `
    <div class="recetas-container">
      <!-- Encabezado Principal -->
      <div class="card header-card">
        <div class="header-main">
          <div>
            <span class="badge badge-primary">BIBLIOTECA GASTRONÓMICA</span>
            <h2 style="margin-top: 0.5rem;">Biblioteca de Recetas</h2>
            <p style="color: var(--text-muted); margin-top: 0.25rem;">
              Explora preparaciones culinarias caseras con sus ingredientes, porciones y costos estimados.
            </p>
          </div>
          <!-- Botón Exclusivo para Administrador -->
          <div *ngIf="esAdmin()">
            <button class="btn btn-primary" (click)="abrirModalCrear()">
              <app-icon name="plus" class="app-icon-inline"></app-icon> Añadir Receta (Admin)
            </button>
          </div>
        </div>
      </div>

      <!-- Panel Interactivo de Consulta Culinaria con IA -->
      <div class="card ai-consult-card">
        <div class="ai-consult-header">
          <div class="ai-icon-bubble">✨</div>
          <div>
            <h3 class="ai-title">Asistente Culinario IA: ¿Qué puedo cocinar hoy?</h3>
            <p class="ai-subtitle">
              Indica qué ingredientes tienes en casa y nuestro asistente te dirá qué plato preparar, para cuántas personas te alcanza y en qué tienda de Santa Cruz conseguir lo que te falte al mejor precio.
            </p>
          </div>
        </div>

        <div class="ai-input-wrapper">
          <div class="ai-input-row">
            <div class="ai-textarea-box">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Ej: Tengo pechuga de pollo, arroz, tomate y cebolla. ¿Qué puedo preparar?"
                [(ngModel)]="consultaIAMensaje"
                (keyup.enter)="ejecutarConsultaIA()"
              />
            </div>
            <div class="ai-person-box">
              <label class="ai-label-inline">Comensales:</label>
              <input 
                type="number" 
                min="1" 
                max="25" 
                class="form-control" 
                style="width: 75px; text-align: center;"
                [(ngModel)]="comensalesIA"
              />
            </div>
            <button 
              class="btn btn-primary btn-ai"
              (click)="ejecutarConsultaIA()"
              [disabled]="consultandoIA() || !consultaIAMensaje.trim()"
            >
              <span *ngIf="!consultandoIA()">🤖 Consultar con IA</span>
              <span *ngIf="consultandoIA()">Consultando...</span>
            </button>
          </div>

          <!-- Sugerencias Rápidas -->
          <div class="ai-chips-row">
            <span class="ai-chips-label">Prueba rápida:</span>
            <button class="ai-chip" (click)="usarSugerenciaIA('Tengo pechuga de pollo, arroz, tomate y cebolla para 2 personas')">
              🍗 Pollo, arroz y verduras
            </button>
            <button class="ai-chip" (click)="usarSugerenciaIA('Tengo carne molida, queso chaqueño y huevos para 4 personas')">
              🍔 Carne molida, queso y huevos
            </button>
            <button class="ai-chip" (click)="usarSugerenciaIA('Tengo papas, cebolla roja, huevos y aceite para 4 personas')">
              🥔 Tortilla de papas y huevos
            </button>
            <button class="ai-chip" (click)="usarSugerenciaIA('Tengo fideos espagueti, carne molida y queso chaqueño para 3 personas')">
              🍝 Espagueti a la bolognesa
            </button>
          </div>
        </div>

        <!-- Panel de Resultados de la Consulta IA -->
        <div *ngIf="respuestaIA()" class="ai-result-panel">
          <div class="ai-result-header">
            <div class="ai-result-tag">
              <span class="badge badge-primary">RESPUESTA DE IA CULINARIA</span>
              <span class="badge badge-success">👥 Calculado para {{ respuestaIA()?.porciones_sugeridas }} comensales</span>
            </div>
            <button class="btn-clear-ai" (click)="limpiarConsultaIA()" title="Cerrar resultado">✕</button>
          </div>

          <!-- Platos sugeridos con foto -->
          <div *ngIf="respuestaIA()?.platos_sugeridos?.length" class="ai-platos-grid">
            <div *ngFor="let ps of respuestaIA()?.platos_sugeridos" class="ai-plato-mini-card" (click)="verDetalle(ps)">
              <img [src]="ps.imagen_url || 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=800&auto=format&fit=crop&q=80'" [alt]="ps.nombre" class="ai-plato-img" (error)="onImgError($event)" />
              <div class="ai-plato-info">
                <span class="ai-plato-badge">{{ ps.tipo_comida }} • {{ ps.tiempo_minutos }} min</span>
                <strong class="ai-plato-name">{{ ps.nombre }}</strong>
                <span class="ai-ver-link">Ver receta completa &rarr;</span>
              </div>
            </div>
          </div>

          <!-- Respuesta Explicada -->
          <div class="ai-text-box">
            <p style="white-space: pre-line; margin: 0; line-height: 1.6; color: #1e293b;">
              {{ respuestaIA()?.respuesta_ia }}
            </p>
          </div>

          <!-- Tiendas Sugeridas para Faltantes -->
          <div *ngIf="respuestaIA()?.tiendas_recomendadas?.length" class="ai-stores-section">
            <h4 class="ai-stores-title">🏪 Tiendas y mercados sugeridos en Santa Cruz:</h4>
            <div class="ai-stores-grid">
              <div *ngFor="let tienda of respuestaIA()?.tiendas_recomendadas" class="ai-store-card">
                <div class="ai-store-top">
                  <span class="ai-store-name">{{ tienda.nombre_tienda }}</span>
                  <span class="badge badge-tipo">{{ tienda.tipo }}</span>
                </div>
                <div class="ai-store-body">
                  <span class="ai-store-items">Insumos: {{ tienda.insumos_disponibles.join(', ') }}</span>
                  <strong *ngIf="tienda.costo_estimado" class="text-success">Costo Est.: Bs {{ tienda.costo_estimado | number:'1.2-2' }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Barra de Filtros y Búsqueda -->
      <div class="card filter-bar">
        <div class="filter-group">
          <span class="filter-label">Tipo de Comida:</span>
          <button 
            class="btn btn-sm" 
            [ngClass]="filtroTipo() === 'TODAS' ? 'btn-primary' : 'btn-outline'"
            (click)="cambiarTipo('TODAS')"
          >
            Todas ({{ recetas().length }})
          </button>
          <button 
            class="btn btn-sm" 
            [ngClass]="filtroTipo() === 'ALMUERZO' ? 'btn-primary' : 'btn-outline'"
            (click)="cambiarTipo('ALMUERZO')"
          >
            Almuerzo
          </button>
          <button 
            class="btn btn-sm" 
            [ngClass]="filtroTipo() === 'CENA' ? 'btn-primary' : 'btn-outline'"
            (click)="cambiarTipo('CENA')"
          >
            Cena
          </button>
          <button 
            class="btn btn-sm" 
            [ngClass]="filtroTipo() === 'DESAYUNO' ? 'btn-primary' : 'btn-outline'"
            (click)="cambiarTipo('DESAYUNO')"
          >
            Desayuno
          </button>
        </div>

        <div class="search-box">
          <input 
            type="text" 
            class="form-control form-control-sm" 
            placeholder="Buscar por nombre o ingrediente..." 
            [(ngModel)]="busquedaTexto"
            (input)="onBuscar()"
          />
        </div>
      </div>

      <!-- Feedback de Éxito / Error -->
      <div *ngIf="mensajeExito()" class="alert alert-success">{{ mensajeExito() }}</div>
      <div *ngIf="mensajeError()" class="alert alert-danger">{{ mensajeError() }}</div>

      <!-- Estado de Carga -->
      <div *ngIf="cargando()" class="card" style="text-align: center; padding: 3rem;">
        <p style="color: var(--text-muted);">Cargando biblioteca de recetas...</p>
      </div>

      <!-- Sin Resultados -->
      <div *ngIf="!cargando() && recetasFiltradas().length === 0" class="card empty-card">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🍲</div>
        <h3>No se encontraron recetas</h3>
        <p style="color: var(--text-muted); max-width: 450px;">
          No hay recetas registradas que coincidan con los filtros seleccionados.
        </p>
      </div>

      <!-- Grid de Recetas con Fotos -->
      <div *ngIf="!cargando() && recetasFiltradas().length > 0" class="recetas-grid">
        <div *ngFor="let r of recetasFiltradas()" class="card receta-card">
          <!-- Imagen de la Receta -->
          <div class="receta-img-wrap">
            <img 
              [src]="r.imagen_url || 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=800&auto=format&fit=crop&q=80'" 
              [alt]="r.nombre" 
              class="receta-cover-img" 
              (error)="onImgError($event)" 
            />
            <span class="badge badge-tipo img-badge">{{ r.tipo_comida }}</span>
          </div>

          <div class="receta-card-body">
            <div class="card-top">
              <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                <span class="badge" [ngClass]="getBadgeDificultad(r.dificultad)">{{ r.dificultad }}</span>
                <span *ngIf="r.origen" class="badge badge-origen">{{ r.origen }}</span>
              </div>
              <button 
                *ngIf="esAdmin()" 
                class="btn-delete" 
                title="Eliminar receta (Admin)"
                (click)="eliminarReceta(r)"
              >
                <app-icon name="trash" class="app-icon-inline"></app-icon>
              </button>
            </div>

            <h3 class="receta-titulo">{{ r.nombre }}</h3>
            <p class="receta-desc">{{ r.descripcion || 'Sin descripción disponible.' }}</p>

            <!-- Métricas de la Receta -->
            <div class="receta-metricas">
              <div class="metrica-item" title="Tiempo de preparación">
                <span class="metrica-icon">⏱️</span>
                <span class="metrica-val">{{ r.tiempo_minutos }} min</span>
              </div>
              <div class="metrica-item" title="Porciones calculadas">
                <span class="metrica-icon">👥</span>
                <span class="metrica-val">{{ r.porciones }} porc.</span>
              </div>
              <div class="metrica-item" title="Ingredientes necesarios">
                <span class="metrica-icon">🥗</span>
                <span class="metrica-val">{{ r.total_ingredientes }} ingr.</span>
              </div>
              <div class="metrica-item highlight" title="Costo referencial de insumos en tiendas" *ngIf="r.costo_estimado_insumos">
                <span class="metrica-icon">💵</span>
                <span class="metrica-val text-success">Bs {{ r.costo_estimado_insumos | number:'1.2-2' }}</span>
              </div>
            </div>

            <div class="card-footer-action">
              <button class="btn btn-outline btn-sm w-full" (click)="verDetalle(r)">
                <app-icon name="search" class="app-icon-inline"></app-icon> Ver Ficha e Ingredientes
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- MODAL: Ver Ficha de Receta -->
      <div *ngIf="recetaSeleccionada()" class="modal-overlay" (click)="cerrarModalDetalle()">
        <div class="modal-card card" (click)="$event.stopPropagation()">
          <!-- Hero de Imagen en el Modal -->
          <div *ngIf="recetaSeleccionada()?.imagen_url" class="modal-hero-wrap">
            <img [src]="recetaSeleccionada()?.imagen_url!" [alt]="recetaSeleccionada()?.nombre" class="modal-hero-img" (error)="onImgError($event)" />
            <button class="btn-close-hero" (click)="cerrarModalDetalle()">&times;</button>
          </div>

          <div class="modal-header" [style.borderTop]="recetaSeleccionada()?.imagen_url ? 'none' : ''">
            <div>
              <span class="badge badge-primary">{{ recetaSeleccionada()?.tipo_comida }}</span>
              <span *ngIf="recetaSeleccionada()?.origen" class="badge badge-origen" style="margin-left: 0.5rem;">{{ recetaSeleccionada()?.origen }}</span>
              <h3 style="margin-top: 0.35rem;">{{ recetaSeleccionada()?.nombre }}</h3>
            </div>
            <button *ngIf="!recetaSeleccionada()?.imagen_url" class="btn-close" (click)="cerrarModalDetalle()">&times;</button>
          </div>

          <div class="modal-body">
            <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem;">
              {{ recetaSeleccionada()?.descripcion }}
            </p>

            <div class="grid-3" style="margin-bottom: 1.5rem;">
              <div class="mini-box">
                <span class="lbl">Porciones</span>
                <strong>{{ recetaSeleccionada()?.porciones }} comensales</strong>
              </div>
              <div class="mini-box">
                <span class="lbl">Tiempo</span>
                <strong>{{ recetaSeleccionada()?.tiempo_minutos }} minutos</strong>
              </div>
              <div class="mini-box">
                <span class="lbl">Costo Insumos</span>
                <strong class="text-success">
                  {{ recetaSeleccionada()?.costo_estimado_insumos ? 'Bs ' + (recetaSeleccionada()?.costo_estimado_insumos | number:'1.2-2') : 'A consultar' }}
                </strong>
              </div>
            </div>

            <!-- Tabla de Ingredientes -->
            <h4 style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <span>🥗</span> Lista de Ingredientes Requeridos
            </h4>
            <div class="table-responsive" style="margin-bottom: 1.5rem;">
              <table class="table">
                <thead>
                  <tr>
                    <th>Ingrediente</th>
                    <th>Cantidad</th>
                    <th>Unidad</th>
                    <th>Subtotal Est.</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let ing of recetaSeleccionada()?.ingredientes">
                    <td><strong>{{ ing.nombre_ingrediente }}</strong></td>
                    <td>{{ ing.cantidad }}</td>
                    <td>{{ ing.unidad_medida }}</td>
                    <td>
                      <span *ngIf="ing.costo_subtotal" class="text-success">Bs {{ ing.costo_subtotal | number:'1.2-2' }}</span>
                      <span *ngIf="!ing.costo_subtotal" style="color: var(--text-muted);">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Instrucciones de Preparación -->
            <div *ngIf="recetaSeleccionada()?.instrucciones">
              <h4 style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>📝</span> Paso a Paso de Preparación
              </h4>
              <div class="instrucciones-box">
                <p style="white-space: pre-line; margin: 0; line-height: 1.6; color: #334155;">
                  {{ recetaSeleccionada()?.instrucciones }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- MODAL: Añadir Nueva Receta (Solo Administrador) -->
      <div *ngIf="mostrarModalCrear()" class="modal-overlay" (click)="cerrarModalCrear()">
        <div class="modal-card card modal-lg" (click)="$event.stopPropagation()">
          <div class="modal-header">
            <h3><app-icon name="plus" class="app-icon-inline"></app-icon> Añadir Receta a la Biblioteca</h3>
            <button class="btn-close" (click)="cerrarModalCrear()">&times;</button>
          </div>

          <form [formGroup]="formReceta" (ngSubmit)="guardarNuevaReceta()">
            <div class="modal-body">
              <div class="grid-2">
                <div class="form-group">
                  <label class="form-label">Nombre de la Receta *</label>
                  <input type="text" class="form-control" formControlName="nombre" placeholder="Ej: Majadito de Pato" />
                </div>
                <div class="form-group">
                  <label class="form-label">Tipo de Comida *</label>
                  <select class="form-control" formControlName="tipo_comida">
                    <option value="ALMUERZO">ALMUERZO</option>
                    <option value="CENA">CENA</option>
                    <option value="DESAYUNO">DESAYUNO</option>
                    <option value="MERIENDA">MERIENDA</option>
                  </select>
                </div>
              </div>

              <div class="grid-3" style="margin-top: 1rem;">
                <div class="form-group">
                  <label class="form-label">Porciones *</label>
                  <input type="number" class="form-control" formControlName="porciones" min="1" max="50" />
                </div>
                <div class="form-group">
                  <label class="form-label">Tiempo (minutos) *</label>
                  <input type="number" class="form-control" formControlName="tiempo_minutos" min="1" max="600" />
                </div>
                <div class="form-group">
                  <label class="form-label">Dificultad *</label>
                  <select class="form-control" formControlName="dificultad">
                    <option value="FACIL">FÁCIL</option>
                    <option value="MEDIA">MEDIA</option>
                    <option value="DIFICIL">DIFÍCIL</option>
                  </select>
                </div>
              </div>

              <div class="grid-2" style="margin-top: 1rem;">
                <div class="form-group">
                  <label class="form-label">Origen / Región</label>
                  <input type="text" class="form-control" formControlName="origen" placeholder="Ej: Tradicional Cruceña" />
                </div>
                <div class="form-group">
                  <label class="form-label">URL de Imagen Representativa</label>
                  <input type="text" class="form-control" formControlName="imagen_url" placeholder="https://images.unsplash.com/..." />
                </div>
              </div>

              <div class="form-group" style="margin-top: 1rem;">
                <label class="form-label">Descripción Breve</label>
                <input type="text" class="form-control" formControlName="descripcion" placeholder="Reseña breve o características..." />
              </div>

              <div class="form-group" style="margin-top: 1rem;">
                <label class="form-label">Instrucciones de Preparación</label>
                <textarea class="form-control" rows="3" formControlName="instrucciones" placeholder="1. Calentar agua... 2. Saltear..."></textarea>
              </div>

              <!-- Sección de Ingredientes -->
              <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);">
                <h4 style="margin-bottom: 0.75rem;">Ingredientes de la Receta</h4>
                
                <div style="display: flex; gap: 0.5rem; align-items: flex-end; flex-wrap: wrap;">
                  <div style="flex: 2; min-width: 180px;">
                    <label class="form-label" style="font-size: 0.8rem;">Seleccionar del Catálogo</label>
                    <select class="form-control form-control-sm" [(ngModel)]="ingredienteSelect" [ngModelOptions]="{standalone: true}" (change)="alSeleccionarIngredienteCatalogo()">
                      <option [ngValue]="null">-- Elegir insumo --</option>
                      <option *ngFor="let cat of catalogoIngredientes()" [ngValue]="cat">
                        {{ cat.nombre }} ({{ cat.unidad_medida }})
                      </option>
                    </select>
                  </div>
                  <div style="flex: 2; min-width: 150px;">
                    <label class="form-label" style="font-size: 0.8rem;">Nombre Insumo *</label>
                    <input type="text" class="form-control form-control-sm" [(ngModel)]="nuevoIngNombre" [ngModelOptions]="{standalone: true}" placeholder="Nombre" />
                  </div>
                  <div style="flex: 1; min-width: 80px;">
                    <label class="form-label" style="font-size: 0.8rem;">Cantidad *</label>
                    <input type="number" class="form-control form-control-sm" [(ngModel)]="nuevoIngCantidad" [ngModelOptions]="{standalone: true}" step="0.05" min="0.01" />
                  </div>
                  <div style="flex: 1; min-width: 80px;">
                    <label class="form-label" style="font-size: 0.8rem;">Unidad *</label>
                    <input type="text" class="form-control form-control-sm" [(ngModel)]="nuevoIngUnidad" [ngModelOptions]="{standalone: true}" placeholder="kg/litro" />
                  </div>
                  <button type="button" class="btn btn-outline btn-sm" (click)="agregarIngredienteATabla()">
                    + Agregar
                  </button>
                </div>

                <div class="table-responsive" style="margin-top: 1rem;">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Ingrediente</th>
                        <th>Cantidad</th>
                        <th>Unidad</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr *ngFor="let item of listaIngredientesNuevos(); let i = index">
                        <td><strong>{{ item.nombre_ingrediente }}</strong></td>
                        <td>{{ item.cantidad }}</td>
                        <td>{{ item.unidad_medida }}</td>
                        <td style="text-align: right;">
                          <button type="button" class="btn btn-sm" style="color: #ef4444; padding: 0.1rem 0.4rem;" (click)="quitarIngredienteDeTabla(i)">
                            &times;
                          </button>
                        </td>
                      </tr>
                      <tr *ngIf="listaIngredientesNuevos().length === 0">
                        <td colspan="4" style="text-align: center; color: var(--text-muted); font-size: 0.85rem;">
                          Agrega al menos un ingrediente a la receta.
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div class="modal-footer" style="padding: 1rem; display: flex; justify-content: flex-end; gap: 0.5rem; border-top: 1px solid var(--border);">
              <button type="button" class="btn btn-outline btn-sm" (click)="cerrarModalCrear()">Cancelar</button>
              <button type="submit" class="btn btn-primary btn-sm" [disabled]="formReceta.invalid || guardando() || listaIngredientesNuevos().length === 0">
                <span *ngIf="guardando()">Guardando...</span>
                <span *ngIf="!guardando()">Guardar Receta</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .recetas-container {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }
    .header-card {
      padding: 1.5rem;
      border-radius: 8px;
    }
    .header-main {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    /* Panel de Consulta IA */
    .ai-consult-card {
      padding: 1.5rem;
      border-radius: 12px;
      background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 50%, #f0f9ff 100%);
      border: 1px solid #bbf7d0;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.08);
    }
    .ai-consult-header {
      display: flex;
      gap: 1rem;
      align-items: flex-start;
      margin-bottom: 1.25rem;
    }
    .ai-icon-bubble {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: #10b981;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.35rem;
      flex-shrink: 0;
      box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
    }
    .ai-title {
      font-size: 1.25rem;
      margin: 0 0 0.25rem 0;
      color: #065f46;
      font-weight: 700;
    }
    .ai-subtitle {
      font-size: 0.9rem;
      color: #475569;
      margin: 0;
      line-height: 1.45;
    }
    .ai-input-wrapper {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    .ai-input-row {
      display: flex;
      gap: 0.75rem;
      align-items: center;
      flex-wrap: wrap;
    }
    .ai-textarea-box {
      flex: 1;
      min-width: 280px;
    }
    .ai-person-box {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      background: #fff;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      border: 1px solid var(--border);
    }
    .ai-label-inline {
      font-size: 0.85rem;
      font-weight: 600;
      color: #334155;
      margin: 0;
    }
    .btn-ai {
      background: #059669;
      border-color: #059669;
      font-weight: 600;
      padding: 0.55rem 1.25rem;
      white-space: nowrap;
    }
    .btn-ai:hover {
      background: #047857;
      border-color: #047857;
    }
    .ai-chips-row {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      flex-wrap: wrap;
    }
    .ai-chips-label {
      font-size: 0.8rem;
      font-weight: 600;
      color: #64748b;
    }
    .ai-chip {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 16px;
      padding: 0.25rem 0.75rem;
      font-size: 0.8rem;
      cursor: pointer;
      color: #1e293b;
      transition: all 0.15s ease;
    }
    .ai-chip:hover {
      background: #e2e8f0;
      border-color: #94a3b8;
    }

    /* Panel de Resultado IA */
    .ai-result-panel {
      margin-top: 1.25rem;
      padding: 1.25rem;
      background: #ffffff;
      border-radius: 10px;
      border: 1px solid #a7f3d0;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      animation: fadeIn 0.25s ease-in-out;
    }
    .ai-result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #e2e8f0;
    }
    .ai-result-tag {
      display: flex;
      gap: 0.5rem;
      align-items: center;
      flex-wrap: wrap;
    }
    .btn-clear-ai {
      background: none;
      border: none;
      font-size: 1.2rem;
      color: #94a3b8;
      cursor: pointer;
      line-height: 1;
    }
    .btn-clear-ai:hover {
      color: #ef4444;
    }
    .ai-platos-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 1rem;
      margin-bottom: 1.25rem;
    }
    .ai-plato-mini-card {
      display: flex;
      gap: 0.75rem;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 0.6rem;
      cursor: pointer;
      transition: all 0.15s ease;
      align-items: center;
    }
    .ai-plato-mini-card:hover {
      background: #f1f5f9;
      border-color: #38bdf8;
      transform: translateY(-2px);
    }
    .ai-plato-img {
      width: 60px;
      height: 60px;
      object-fit: cover;
      border-radius: 6px;
      flex-shrink: 0;
    }
    .ai-plato-info {
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
      overflow: hidden;
    }
    .ai-plato-badge {
      font-size: 0.7rem;
      color: #0284c7;
      font-weight: 600;
    }
    .ai-plato-name {
      font-size: 0.88rem;
      color: #0f172a;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ai-ver-link {
      font-size: 0.75rem;
      color: #10b981;
      font-weight: 600;
    }
    .ai-text-box {
      background: #f8fafc;
      padding: 1rem 1.25rem;
      border-radius: 8px;
      border: 1px solid #e2e8f0;
      margin-bottom: 1rem;
    }
    .ai-stores-section {
      margin-top: 1rem;
    }
    .ai-stores-title {
      font-size: 0.95rem;
      font-weight: 700;
      color: #334155;
      margin-bottom: 0.5rem;
    }
    .ai-stores-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 0.75rem;
    }
    .ai-store-card {
      background: #f1f5f9;
      border-radius: 6px;
      padding: 0.75rem;
      border: 1px solid #cbd5e1;
    }
    .ai-store-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.35rem;
    }
    .ai-store-name {
      font-size: 0.88rem;
      font-weight: 600;
      color: #0f172a;
    }
    .ai-store-body {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      font-size: 0.8rem;
      color: #475569;
    }
    .ai-store-items {
      max-width: 70%;
    }

    /* Barra de Filtros */
    .filter-bar {
      padding: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .filter-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }
    .filter-label {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-muted);
      margin-right: 0.25rem;
    }
    .search-box {
      min-width: 260px;
    }

    /* Grid de Recetas */
    .recetas-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.25rem;
    }
    .receta-card {
      padding: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
      border: 1px solid var(--border);
      border-radius: 10px;
    }
    .receta-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }
    .receta-img-wrap {
      position: relative;
      height: 180px;
      width: 100%;
      background: #e2e8f0;
      overflow: hidden;
    }
    .receta-cover-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.25s ease;
    }
    .receta-card:hover .receta-cover-img {
      transform: scale(1.04);
    }
    .img-badge {
      position: absolute;
      top: 0.75rem;
      left: 0.75rem;
      background: rgba(255, 255, 255, 0.92);
      color: #0369a1;
      font-weight: 700;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
    .receta-card-body {
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }
    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.75rem;
    }
    .badge-tipo {
      background: #e0f2fe;
      color: #0369a1;
      font-weight: 600;
    }
    .badge-facil {
      background: #dcfce7;
      color: #15803d;
    }
    .badge-media {
      background: #fef3c7;
      color: #b45309;
    }
    .badge-dificil {
      background: #fee2e2;
      color: #b91c1c;
    }
    .badge-origen {
      background: #f1f5f9;
      color: #475569;
    }
    .btn-delete {
      background: none;
      border: none;
      color: #ef4444;
      cursor: pointer;
      padding: 0.25rem;
      border-radius: 4px;
    }
    .btn-delete:hover {
      background: #fee2e2;
    }
    .receta-titulo {
      font-size: 1.2rem;
      margin: 0 0 0.5rem 0;
      color: var(--text-main);
      font-weight: 700;
    }
    .receta-desc {
      font-size: 0.88rem;
      color: var(--text-muted);
      line-height: 1.4;
      margin-bottom: 1rem;
      flex-grow: 1;
    }
    .receta-metricas {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.5rem;
      background: #f8fafc;
      padding: 0.75rem;
      border-radius: 6px;
      margin-bottom: 1rem;
    }
    .metrica-item {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.82rem;
      color: var(--text-main);
    }
    .metrica-icon {
      font-size: 0.95rem;
    }
    .metrica-val {
      font-weight: 600;
    }
    .w-full {
      width: 100%;
    }
    .empty-card {
      text-align: center;
      padding: 3rem;
      align-items: center;
      justify-content: center;
    }

    /* Modales */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1050;
      padding: 1rem;
    }
    .modal-card {
      width: 100%;
      max-width: 600px;
      max-height: 90vh;
      overflow-y: auto;
      padding: 0;
      border-radius: 12px;
      background: #fff;
    }
    .modal-hero-wrap {
      position: relative;
      width: 100%;
      height: 220px;
      overflow: hidden;
    }
    .modal-hero-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .btn-close-hero {
      position: absolute;
      top: 0.75rem;
      right: 0.75rem;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: rgba(0, 0, 0, 0.6);
      color: #fff;
      border: none;
      font-size: 1.4rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }
    .modal-lg {
      max-width: 750px;
    }
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 1.25rem 1.5rem 0.75rem 1.5rem;
      border-bottom: 1px solid var(--border);
    }
    .modal-body {
      padding: 1.25rem 1.5rem;
    }
    .btn-close {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: var(--text-muted);
      line-height: 1;
    }
    .mini-box {
      background: #f8fafc;
      padding: 0.75rem;
      border-radius: 6px;
      text-align: center;
      border: 1px solid var(--border);
    }
    .mini-box .lbl {
      display: block;
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-bottom: 0.25rem;
    }
    .instrucciones-box {
      background: #f8fafc;
      padding: 1rem;
      border-radius: 6px;
      border: 1px solid var(--border);
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-6px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `]
})
export class BibliotecaRecetasComponent implements OnInit {
  private recetaService = inject(RecetaService);
  private ingredienteService = inject(IngredienteService);
  private authService = inject(AuthService);
  private fb = inject(FormBuilder);

  recetas = signal<Receta[]>([]);
  recetasFiltradas = signal<Receta[]>([]);
  catalogoIngredientes = signal<Ingrediente[]>([]);
  cargando = signal<boolean>(true);
  guardando = signal<boolean>(false);
  filtroTipo = signal<string>('TODAS');
  busquedaTexto = '';

  // Consulta IA Culinaria
  consultaIAMensaje = '';
  comensalesIA: number = 2;
  consultandoIA = signal<boolean>(false);
  respuestaIA = signal<RecetaConsultaIARespuesta | null>(null);

  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  // Modales
  recetaSeleccionada = signal<Receta | null>(null);
  mostrarModalCrear = signal<boolean>(false);

  // Formulario de creación
  formReceta = this.fb.group({
    nombre: ['', [Validators.required, Validators.minLength(3)]],
    tipo_comida: ['ALMUERZO', Validators.required],
    porciones: [2, [Validators.required, Validators.min(1)]],
    tiempo_minutos: [30, [Validators.required, Validators.min(1)]],
    dificultad: ['FACIL', Validators.required],
    origen: ['Tradicional Cruceña'],
    imagen_url: [''],
    descripcion: [''],
    instrucciones: ['']
  });

  // Lista temporal de ingredientes para nueva receta
  listaIngredientesNuevos = signal<{ id_ingrediente: number | null; nombre_ingrediente: string; cantidad: number; unidad_medida: string }[]>([]);
  ingredienteSelect: Ingrediente | null = null;
  nuevoIngNombre = '';
  nuevoIngCantidad = 0.50;
  nuevoIngUnidad = 'kg';

  esAdmin = () => this.authService.userRole() === 'ADMINISTRADOR';

  ngOnInit(): void {
    this.cargarRecetas();
    this.cargarCatalogoIngredientes();
  }

  cargarRecetas(): void {
    this.cargando.set(true);
    this.recetaService.listarRecetas().subscribe({
      next: (data) => {
        this.recetas.set(data);
        this.aplicarFiltros();
        this.cargando.set(false);
      },
      error: (err) => {
        this.mensajeError.set(err.error?.detail || 'Error al cargar la biblioteca de recetas.');
        this.cargando.set(false);
      }
    });
  }

  cargarCatalogoIngredientes(): void {
    this.ingredienteService.getIngredientes('ACTIVO').subscribe({
      next: (data) => this.catalogoIngredientes.set(data),
      error: () => {}
    });
  }

  cambiarTipo(tipo: string): void {
    this.filtroTipo.set(tipo);
    this.aplicarFiltros();
  }

  onBuscar(): void {
    this.aplicarFiltros();
  }

  aplicarFiltros(): void {
    let list = this.recetas();
    const tipo = this.filtroTipo();
    const q = this.busquedaTexto.toLowerCase().trim();

    if (tipo !== 'TODAS') {
      list = list.filter(r => r.tipo_comida.toUpperCase() === tipo.toUpperCase());
    }

    if (q) {
      list = list.filter(r =>
        r.nombre.toLowerCase().includes(q) ||
        (r.descripcion && r.descripcion.toLowerCase().includes(q)) ||
        (r.origen && r.origen.toLowerCase().includes(q)) ||
        r.ingredientes.some(i => i.nombre_ingrediente.toLowerCase().includes(q))
      );
    }

    this.recetasFiltradas.set(list);
  }

  // --- Consulta Asistente Culinario IA ---
  ejecutarConsultaIA(): void {
    const texto = this.consultaIAMensaje.trim();
    if (!texto) return;

    this.consultandoIA.set(true);
    this.recetaService.consultarIA({
      mensaje: texto,
      comensales: this.comensalesIA > 0 ? this.comensalesIA : 2
    }).subscribe({
      next: (resp) => {
        this.respuestaIA.set(resp);
        this.consultandoIA.set(false);
      },
      error: (err) => {
        this.mensajeError.set(err.error?.detail || 'Error al consultar con el asistente culinario.');
        this.consultandoIA.set(false);
        setTimeout(() => this.mensajeError.set(null), 4000);
      }
    });
  }

  usarSugerenciaIA(sugerencia: string): void {
    this.consultaIAMensaje = sugerencia;
    this.ejecutarConsultaIA();
  }

  limpiarConsultaIA(): void {
    this.respuestaIA.set(null);
    this.consultaIAMensaje = '';
  }

  onImgError(event: any): void {
    event.target.src = 'https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=800&auto=format&fit=crop&q=80';
  }

  getBadgeDificultad(dificultad: string): string {
    const d = dificultad?.toUpperCase();
    if (d === 'FACIL') return 'badge-facil';
    if (d === 'MEDIA') return 'badge-media';
    return 'badge-dificil';
  }

  verDetalle(receta: Receta): void {
    this.recetaSeleccionada.set(receta);
  }

  cerrarModalDetalle(): void {
    this.recetaSeleccionada.set(null);
  }

  abrirModalCrear(): void {
    this.formReceta.reset({
      nombre: '',
      tipo_comida: 'ALMUERZO',
      porciones: 2,
      tiempo_minutos: 30,
      dificultad: 'FACIL',
      origen: 'Tradicional Cruceña',
      imagen_url: '',
      descripcion: '',
      instrucciones: ''
    });
    this.listaIngredientesNuevos.set([]);
    this.ingredienteSelect = null;
    this.nuevoIngNombre = '';
    this.nuevoIngCantidad = 0.50;
    this.nuevoIngUnidad = 'kg';
    this.mostrarModalCrear.set(true);
  }

  cerrarModalCrear(): void {
    this.mostrarModalCrear.set(false);
  }

  alSeleccionarIngredienteCatalogo(): void {
    if (this.ingredienteSelect) {
      this.nuevoIngNombre = this.ingredienteSelect.nombre;
      this.nuevoIngUnidad = this.ingredienteSelect.unidad_medida;
    }
  }

  agregarIngredienteATabla(): void {
    if (!this.nuevoIngNombre.trim() || this.nuevoIngCantidad <= 0 || !this.nuevoIngUnidad.trim()) {
      alert('Por favor completa el nombre, cantidad y unidad del ingrediente.');
      return;
    }

    const item = {
      id_ingrediente: this.ingredienteSelect ? this.ingredienteSelect.id_ingrediente : null,
      nombre_ingrediente: this.nuevoIngNombre.trim(),
      cantidad: Number(this.nuevoIngCantidad),
      unidad_medida: this.nuevoIngUnidad.trim()
    };

    this.listaIngredientesNuevos.update(prev => [...prev, item]);
    this.ingredienteSelect = null;
    this.nuevoIngNombre = '';
    this.nuevoIngCantidad = 0.50;
    this.nuevoIngUnidad = 'kg';
  }

  quitarIngredienteDeTabla(index: number): void {
    this.listaIngredientesNuevos.update(prev => prev.filter((_, i) => i !== index));
  }

  guardarNuevaReceta(): void {
    if (this.formReceta.invalid || this.listaIngredientesNuevos().length === 0) {
      return;
    }

    this.guardando.set(true);
    const val = this.formReceta.value;
    const payload: RecetaCrear = {
      nombre: val.nombre!,
      tipo_comida: val.tipo_comida!,
      porciones: Number(val.porciones),
      tiempo_minutos: Number(val.tiempo_minutos),
      dificultad: val.dificultad!,
      origen: val.origen || 'Tradicional Cruceña',
      imagen_url: val.imagen_url || undefined,
      descripcion: val.descripcion || undefined,
      instrucciones: val.instrucciones || undefined,
      ingredientes: this.listaIngredientesNuevos()
    };

    this.recetaService.crearReceta(payload).subscribe({
      next: (creada) => {
        this.guardando.set(false);
        this.cerrarModalCrear();
        this.mensajeExito.set(`Receta '${creada.nombre}' añadida exitosamente a la biblioteca.`);
        this.cargarRecetas();
        setTimeout(() => this.mensajeExito.set(null), 4000);
      },
      error: (err) => {
        this.guardando.set(false);
        this.mensajeError.set(err.error?.detail || 'Error al guardar la receta.');
        setTimeout(() => this.mensajeError.set(null), 4000);
      }
    });
  }

  eliminarReceta(receta: Receta): void {
    if (!confirm(`¿Estás seguro de eliminar la receta '${receta.nombre}' de la biblioteca?`)) {
      return;
    }

    this.recetaService.eliminarReceta(receta.id_receta).subscribe({
      next: (res) => {
        this.mensajeExito.set(res.mensaje);
        this.cargarRecetas();
        setTimeout(() => this.mensajeExito.set(null), 3000);
      },
      error: (err) => {
        this.mensajeError.set(err.error?.detail || 'Error al eliminar receta.');
        setTimeout(() => this.mensajeError.set(null), 3000);
      }
    });
  }
}
