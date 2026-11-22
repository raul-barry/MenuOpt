import { HttpBackend, HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

interface FirebaseCompat {
  apps: unknown[];
  initializeApp(config: object): unknown;
  messaging(): {
    getToken(options: { vapidKey: string; serviceWorkerRegistration: ServiceWorkerRegistration }): Promise<string>;
    onMessage(callback: (payload: { notification?: { title?: string; body?: string }; data?: Record<string, string> }) => void): () => void;
    deleteToken(): Promise<boolean>;
  };
}

declare global {
  interface Window { firebase?: FirebaseCompat; }
}

@Injectable({ providedIn: 'root' })
export class PushNotificationsService {
  private readonly http = new HttpClient(inject(HttpBackend));
  private readonly router = inject(Router);
  private readonly installationKey = 'menuopt_push_installation';
  private listening = false;
  private activeToken: string | null = null;

  async registrarParaRestaurante(tokenSesion: string): Promise<void> {
    this.activeToken = tokenSesion;
    const config = environment.firebase;
    const firebase = window.firebase;
    if (!this.configValida(config) || !firebase || !('serviceWorker' in navigator) || !('Notification' in window)) return;
    if (!window.isSecureContext) return;

    try {
      if (!firebase.apps.length) firebase.initializeApp(config);
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') return;
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
      const messaging = firebase.messaging();
      const fcmToken = await messaging.getToken({ vapidKey: config.vapidKey, serviceWorkerRegistration: registration });
      const idInstalacion = this.obtenerIdInstalacion();
      await firstValueFrom(this.http.put(
        `${environment.apiUrl}/notificaciones/dispositivos`,
        { id_instalacion: idInstalacion, token: fcmToken, plataforma: 'WEB' },
        { headers: new HttpHeaders({ Authorization: `Bearer ${tokenSesion}` }) },
      ));

      if (!this.listening) {
        this.listening = true;
        messaging.onMessage((payload) => {
          const data = payload.data || {};
          const type = data['type'] === 'pedido' ? 'pedidos' : data['type'] === 'reserva' ? 'reservas' : '';
          const id = data['resource_id'];
          if (type && id && /^\d+$/.test(id)) {
            registration.showNotification(payload.notification?.title || 'MenuOpt', {
              body: payload.notification?.body || 'Tienes una actualización pendiente.',
              tag: data['event_id'],
              data: { url: `/${type}/${id}` },
            });
          }
        });
        navigator.serviceWorker.addEventListener('message', (event: MessageEvent) => {
          if (event.data?.type === 'MENUOPT_PUSH_OPEN' && typeof event.data.url === 'string') {
            void this.abrirRecursoAutorizado(event.data.url);
          }
        });
      }
    } catch {
      // FCM no debe interrumpir el inicio de sesión ni el uso normal del panel.
      console.warn('No se pudo registrar la notificación web de MenuOpt.');
    }
  }

  async revocar(tokenSesion: string | null): Promise<void> {
    this.activeToken = null;
    const idInstalacion = localStorage.getItem(this.installationKey);
    if (!idInstalacion) return;
    try {
      if (tokenSesion) {
        await firstValueFrom(this.http.post(
          `${environment.apiUrl}/notificaciones/dispositivos/revocar`,
          { id_instalacion: idInstalacion },
          { headers: new HttpHeaders({ Authorization: `Bearer ${tokenSesion}` }) },
        ));
      }
      const firebase = window.firebase;
      if (firebase?.apps.length) await firebase.messaging().deleteToken().catch(() => false);
    } catch {
      // Se cierra la sesión aunque el servidor de notificaciones no esté disponible.
    } finally {
      localStorage.removeItem(this.installationKey);
    }
  }

  private async abrirRecursoAutorizado(url: string): Promise<void> {
    if (!this.activeToken) return;
    const parsed = new URL(url, window.location.origin);
    if (parsed.origin !== window.location.origin || !/^\/(reservas|pedidos)\/\d+$/.test(parsed.pathname)) return;
    const [, type, id] = parsed.pathname.split('/');
    const apiResource = type === 'reservas' ? 'reservas' : 'pedidos';
    try {
      // El backend comprueba titularidad o restaurante propietario antes de navegar.
      await firstValueFrom(this.http.get(`${environment.apiUrl}/${apiResource}/${id}`, {
        headers: new HttpHeaders({ Authorization: `Bearer ${this.activeToken}` }),
      }));
      await this.router.navigate([parsed.pathname]);
    } catch {
      await this.router.navigate(['/restaurantes']);
    }
  }

  private configValida(config: typeof environment.firebase): boolean {
    return Boolean(config.apiKey && config.authDomain && config.projectId && config.messagingSenderId && config.appId && config.vapidKey);
  }

  private obtenerIdInstalacion(): string {
    let id = localStorage.getItem(this.installationKey);
    if (!id) {
      id = `web-${crypto.randomUUID()}`;
      localStorage.setItem(this.installationKey, id);
    }
    return id;
  }
}
