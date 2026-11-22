import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AsistenteIAService, GuiaAccion } from '../../core/services/asistente-ia.service';

interface MensajeGuiaUI {
  emisor: 'user' | 'assistant';
  contenido: string;
  destino?: string | null;
}

@Component({
  selector: 'app-agente-guia-flotante',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <section class="guide-widget" aria-label="Agente guía de MenuOpt">
      <div class="guide-panel" *ngIf="abierto()" role="dialog" aria-label="Conversación con el agente guía">
        <header class="guide-header">
          <div class="guide-avatar">✦</div>
          <div class="guide-heading"><strong>Agente guía</strong><small>Ayuda para usar MenuOpt</small></div>
          <button class="icon-button" type="button" aria-label="Cerrar chat" (click)="abierto.set(false)">×</button>
        </header>
        <div class="guide-messages" #messageList>
          <article *ngFor="let item of mensajes()" class="bubble" [class.from-user]="item.emisor === 'user'">
            <p>{{ item.contenido }}</p>
            <button *ngIf="item.destino" type="button" class="go-button" (click)="irA(item.destino!)">Abrir esta función</button>
          </article>
          <div class="action-list" *ngIf="acciones().length">
            <button type="button" *ngFor="let accion of acciones()" (click)="elegirAccion(accion)">{{ accion.nombre }}</button>
          </div>
          <div class="typing" *ngIf="cargando()">El agente está escribiendo…</div>
        </div>
        <form class="guide-compose" (ngSubmit)="enviar()">
          <input name="mensaje" [(ngModel)]="borrador" maxlength="1000" placeholder="¿Qué quieres hacer?" aria-label="Escribe tu pregunta" [disabled]="cargando()" />
          <button type="submit" aria-label="Enviar mensaje" [disabled]="cargando() || !borrador.trim()">➤</button>
        </form>
      </div>
      <button class="guide-launcher" type="button" (click)="alternar()" [attr.aria-expanded]="abierto()" aria-label="Abrir agente guía">
        <span aria-hidden="true">{{ abierto() ? '×' : '✦' }}</span><span class="launcher-label" *ngIf="!abierto()">¿Necesitas ayuda?</span>
      </button>
    </section>
  `,
  styles: [`
    .guide-widget{position:fixed;right:24px;bottom:24px;z-index:2000;font-family:inherit;color:#1f2937}
    .guide-launcher{display:flex;align-items:center;gap:9px;border:0;border-radius:999px;background:#6b3f24;color:#fff;padding:13px 18px;box-shadow:0 8px 28px #24130640;cursor:pointer;font-weight:700;font-size:15px}
    .guide-launcher>span:first-child{font-size:20px;line-height:1}
    .guide-panel{width:360px;height:min(540px,calc(100dvh - 110px));display:flex;flex-direction:column;background:#fff;border:1px solid #e7ded7;border-radius:18px;box-shadow:0 14px 48px #24130630;overflow:hidden;margin-bottom:12px}
    .guide-header{display:flex;align-items:center;gap:10px;padding:14px 16px;background:#6b3f24;color:#fff}
    .guide-avatar{width:34px;height:34px;border-radius:50%;background:#ffffff25;display:grid;place-items:center;font-size:21px}
    .guide-heading{display:flex;flex-direction:column;flex:1}.guide-heading small{opacity:.8;margin-top:2px}
    .icon-button{border:0;background:transparent;color:#fff;font-size:26px;cursor:pointer;line-height:1}
    .guide-messages{flex:1;overflow:auto;padding:14px;background:#faf8f6;display:flex;flex-direction:column;align-items:flex-start;gap:10px}
    .bubble{max-width:90%;background:#fff;border:1px solid #eee6df;border-radius:14px 14px 14px 4px;padding:10px 12px;white-space:pre-wrap;font-size:13px;line-height:1.5}
    .bubble p{margin:0}.bubble.from-user{align-self:flex-end;background:#f0e3d8;border-color:#f0e3d8;border-radius:14px 14px 4px 14px}
    .go-button{margin-top:9px;border:0;border-radius:8px;background:#6b3f24;color:white;padding:8px 10px;font-weight:600;cursor:pointer}
    .action-list{display:flex;flex-direction:column;align-items:stretch;gap:6px;width:100%}
    .action-list button{background:#fff;border:1px solid #dbc8b9;color:#58351f;text-align:left;border-radius:10px;padding:9px 11px;font:inherit;font-size:12px;cursor:pointer}
    .action-list button:hover{background:#f4ebe4}.typing{font-size:12px;color:#76675d;padding:4px}
    .guide-compose{display:flex;gap:8px;padding:11px;border-top:1px solid #eee6df;background:white}
    .guide-compose input{flex:1;min-width:0;border:1px solid #ddd3cb;border-radius:999px;padding:10px 13px;font:inherit;font-size:13px;outline-color:#6b3f24}
    .guide-compose button{width:40px;border:0;border-radius:50%;background:#6b3f24;color:white;font-size:18px;cursor:pointer}.guide-compose button:disabled{opacity:.45;cursor:default}
    @media(max-width:520px){.guide-widget{right:12px;bottom:12px}.guide-panel{width:min(360px,calc(100vw - 24px));height:min(560px,calc(100dvh - 92px))}.guide-launcher{padding:12px 15px}}
  `]
})
export class AgenteGuiaFlotanteComponent {
  private service = inject(AsistenteIAService);
  private router = inject(Router);
  abierto = signal(false);
  cargando = signal(false);
  mensajes = signal<MensajeGuiaUI[]>([]);
  acciones = signal<GuiaAccion[]>([]);
  borrador = '';

  alternar(): void {
    this.abierto.update(value => !value);
    if (this.abierto() && !this.mensajes().length) {
      this.solicitar('¿Qué funciones puedo realizar con mi rol?');
    }
  }

  elegirAccion(accion: GuiaAccion): void {
    this.solicitar(accion.nombre, accion.id);
  }

  enviar(): void {
    const texto = this.borrador.trim();
    if (!texto || this.cargando()) return;
    this.borrador = '';
    this.solicitar(texto);
  }

  irA(destino: string): void {
    void this.router.navigateByUrl(destino);
    this.abierto.set(false);
  }

  private solicitar(texto: string, accionId?: string): void {
    const historial = this.mensajes().slice(-10).map(item => ({ emisor: item.emisor, contenido: item.contenido }));
    this.mensajes.update(items => [...items, { emisor: 'user', contenido: texto }]);
    this.acciones.set([]);
    this.cargando.set(true);
    this.service.guiarUsuario({
      mensaje: texto,
      plataforma: 'web',
      accion_id: accionId,
      pagina_actual: this.router.url,
      historial,
    }).subscribe({
      next: respuesta => {
        this.mensajes.update(items => [...items, { emisor: 'assistant', contenido: respuesta.respuesta, destino: respuesta.destino }]);
        this.acciones.set(respuesta.acciones || []);
        this.cargando.set(false);
      },
      error: () => {
        this.mensajes.update(items => [...items, { emisor: 'assistant', contenido: 'No pude conectar con el agente guía. Inténtalo de nuevo en un momento.' }]);
        this.cargando.set(false);
      }
    });
  }
}
