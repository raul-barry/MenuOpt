/* Firebase Web Messaging for the MenuOpt restaurant panel. */
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js');
importScripts('/firebase-messaging-config.js');

const config = self.MENUOPT_FIREBASE_CONFIG || {};
if (config.apiKey && config.projectId && config.messagingSenderId && config.appId) {
  firebase.initializeApp(config);
  const messaging = firebase.messaging();
  messaging.onBackgroundMessage((payload) => {
    const notification = payload.notification || {};
    const data = payload.data || {};
    const type = data.type === 'pedido' ? 'pedidos' : 'reservas';
    const id = String(data.resource_id || '');
    const url = id && /^\d+$/.test(id) ? `/${type}/${encodeURIComponent(id)}` : '/restaurantes';
    self.registration.showNotification(notification.title || 'MenuOpt', {
      body: notification.body || 'Tienes una actualización pendiente.',
      tag: data.event_id || undefined,
      data: { url }
    });
  });
}

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const target = new URL(event.notification.data?.url || '/restaurantes', self.location.origin).href;
  event.waitUntil((async () => {
    const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const client of clients) {
      if ('focus' in client) {
        await client.focus();
        client.postMessage({ type: 'MENUOPT_PUSH_OPEN', url: target });
        return;
      }
    }
    await self.clients.openWindow(target);
  })());
});
