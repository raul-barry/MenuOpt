# Notificaciones push en MenuOpt

La app Android usa Firebase Cloud Messaging (FCM) para novedades y promociones de los clientes que se suscriben desde **Mi Perfil**. Las campañas generales se dirigen al tema `menuopt_promociones`. Las reservas y pedidos usan envíos privados por token de dispositivo; nunca se publican en ese tema.

## Presentación en Android

- En primer plano, FCM se muestra con `flutter_local_notifications` en el panel del sistema. El canal `menuopt_promociones_high_v2` usa importancia y prioridad altas, sonido predeterminado y vibración habilitada; el sistema y el usuario conservan el control de estas opciones.
- En segundo plano o con la app cerrada, Android presenta directamente las notificaciones FCM en el panel, usando el mismo canal predeterminado.
- Las notificaciones privadas de eventos usan el canal `menuopt_transacciones_v1`, de importancia alta.
- Al tocar una notificación de reserva o pedido se abre su detalle. La app consulta el recurso con el JWT de la sesión; FastAPI valida la titularidad o la propiedad del restaurante antes de devolver datos.
- El ID de instalación estable permite actualizar tokens FCM rotados. Al cerrar sesión, la app revoca ese dispositivo para el usuario actual e invalida el token FCM local.
- Los mensajes de primer plano no muestran además un SnackBar. Para eventos transaccionales, la app usa el `event_id` estable de la outbox para deduplicar reintentos.

## Proyecto configurado

- Proyecto Firebase: `menuopt-fcm-2026-11-20` (MenuOpt, plan Spark).
- Aplicación Android: `com.menuopt.menuopt_mobile`.
- `google-services.json` se guarda localmente en `mobile/android/app/google-services.json` y está excluido de Git.
- `google-services.json` es configuración del cliente, no una credencial privada del Admin SDK.
- El backend usa Firebase Admin con credenciales de cuenta de servicio guardadas solo como variables secretas de Render.

## Eventos privados automatizados

FastAPI crea un registro idempotente en `notificacion_outbox` en la transacción de negocio y lo despacha como tarea en segundo plano después del commit. Las reservas nuevas conservan su estado inicial vigente `CONFIRMADA` y crean, en esa misma transacción, un evento para el restaurante y otro para el cliente. La posterior actualización de estado no vuelve a publicar esa misma confirmación.

- Cliente crea reserva válida → responsable del restaurante.
- Reserva creada correctamente en estado `CONFIRMADA` → titular de la reserva.
- Restaurante confirma una reserva que estaba pendiente → titular de la reserva (misma clave idempotente si ese evento ya existía).
- Se cancela una reserva → la otra parte (cliente o restaurante, según quién la cancele).
- Cliente registra pedido → responsable del restaurante.
- Restaurante cambia pedido a `LISTO` → titular del pedido.

Los avisos son genéricos y solo incluyen el tipo e ID del recurso. El backend no envía nombre, teléfono ni otros datos personales en el payload. Los errores de Firebase quedan con estado de envío en la outbox sin revertir reservas o pedidos.

## Configurar Firebase Admin en Render

En el servicio `menuopt-api` de Render, agrega estas variables desde **Environment** (no las guardes en el repositorio ni en `render.yaml`):

1. `FIREBASE_PROJECT_ID` = `menuopt-fcm-2026-11-20`.
2. `FIREBASE_SERVICE_ACCOUNT_JSON` = contenido JSON completo de una clave de cuenta de servicio del proyecto Firebase. Pégalo como variable secreta, conservando los saltos de línea escapados del campo `private_key`.

La cuenta debe tener permiso de Firebase Cloud Messaging para enviar mensajes. Reinicia o despliega el servicio después de añadirlas; el arranque ya ejecuta `alembic upgrade head`. No se requiere ninguna clave privada en Flutter.

Los reintentos manuales de eventos `FALLIDA`, `SIN_DESTINATARIOS` o `PENDIENTE` están limitados al rol `ADMINISTRADOR` mediante `POST /notificaciones/outbox/{id_notificacion}/reintentar`. Esto permite recuperar también un evento que quedó pendiente después de una interrupción del proceso. La clave única del evento se conserva y la outbox registra los dispositivos que Firebase aceptó; un reintento parcial solo vuelve a enviar a los dispositivos fallidos. Los eventos `ENVIADA` o `ENVIANDO` no se programan de nuevo. La outbox conserva errores e intentos para diagnóstico.

La cuenta de Render observada ejecuta el backend Docker `menuopt-api` en Oregon, con una instancia y despliegue automático desde `main`. Esta implementación no cambia esos recursos ni sus variables.

## Notificaciones web para restaurantes

El panel Angular ya incluye Firebase Web Messaging, un service worker y registro `WEB` usando la sesión existente. Solo registra usuarios de rol `RESTAURANTE`; al cerrar sesión intenta revocar el dispositivo antes de borrar la sesión. Al abrir una notificación existente, el panel consulta primero `GET /reservas/{id}` o `GET /pedidos/{id}` con el JWT actual, y solo navega si el backend autoriza ese recurso.

La app Web y su clave VAPID aún deben configurarse en Firebase. La consulta local con Firebase CLI no pudo listar las apps web por un error de actualización/red de `firebase-tools`; no se creó ni se modificó ninguna app del proyecto. En Firebase Console, registra una aplicación Web bajo `menuopt-fcm-2026-11-20`, habilita Cloud Messaging y copia su configuración web y la clave pública VAPID. En las variables de entorno del **servicio de frontend** de Render, antes de compilar, configura:

- `FIREBASE_WEB_CONFIG_JSON`: JSON de configuración Web con `apiKey`, `authDomain`, `projectId`, `messagingSenderId` y `appId`.
- `FIREBASE_WEB_VAPID_KEY`: clave pública Web Push (VAPID) generada/mostrada por Firebase Cloud Messaging.

`build:render` los inserta en el bundle y en `firebase-messaging-config.js`, servidos públicamente como configuración de cliente. Son valores públicos de Firebase, no claves de cuenta de servicio; nunca pongas aquí `FIREBASE_SERVICE_ACCOUNT_JSON`. El navegador requiere HTTPS y permiso explícito del usuario. Sin estas dos variables, el registro web queda desactivado sin impedir el uso del panel.

## Probar los eventos

Con la migración desplegada, Firebase Admin configurado y dispositivos registrados en sus cuentas:

1. Como cliente, crea una reserva válida. El responsable recibe “Nueva reserva” y el cliente titular recibe “Reserva confirmada” al completarse la creación (`CONFIRMADA`).
2. Para probar la confirmación posterior, cambia una reserva pendiente existente/importada a `CONFIRMADA`; una actualización repetida no genera otro evento. Las reservas nuevas ya se crean confirmadas por el diseño vigente.
3. Cancela otra reserva como cliente; el restaurante recibe “Reserva cancelada”. También se puede cancelar desde el restaurante para verificar que el titular reciba el aviso.
4. Como cliente, registra un pedido. El responsable del restaurante recibe “Nuevo pedido”.
5. En la cuenta web del restaurante, avanza el pedido por `ACEPTADO` y `EN_PREPARACION` hasta `LISTO`. El titular recibe “Pedido listo”.

Los tokens móviles siguen vinculados a la cuenta autenticada del cliente. El panel Angular de restaurantes usa su propio token `WEB`, registrado con el JWT de la cuenta del restaurante.

## Activar notificaciones en un dispositivo

1. Instala la APK y abre MenuOpt.
2. Inicia sesión, entra a **Mi Perfil** y activa **Novedades y promociones**.
3. Acepta el permiso de Android 13 o posterior. La app solicita autorización y se suscribe al tema.
4. La suscripción se puede desactivar desde el mismo control.

## Probar desde Firebase Console

Con un dispositivo instalado, autorizado y suscrito:

1. En Firebase Console, abre **Messaging** y crea una campaña de notificación.
2. Elige el tema `menuopt_promociones` como destino.
3. Prueba la entrega con MenuOpt en primer plano, después en segundo plano y luego cerrada.
4. Para probar navegación, agrega un dato personalizado `route` con uno de los valores admitidos arriba.

Android puede suprimir el aviso emergente o el sonido según los ajustes del usuario, el modo No molestar y el fabricante. La notificación permanece en el panel hasta que el usuario la descarte o la toque.

## Compilar la APK

Desde `mobile`:

```powershell
flutter build apk --release --dart-define=BASE_URL=https://menuopt-api.onrender.com
```

La versión local actual está marcada como `1.0.0+6`.
