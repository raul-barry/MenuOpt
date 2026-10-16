---
name: flutter-apk-internet-sin-vpn
description: "Habilita pruebas de una APK Flutter en un Android físico desde cualquier WiFi o datos móviles, con API y base de datos aún alojadas localmente en Docker, sin instalar VPN en el celular y sin desplegar infraestructura a producción."
summary: "Habilita pruebas de una APK Flutter en un Android físico desde cualquier WiFi o datos móviles, con API y base de datos aún alojadas localmente en Docker, sin instalar VPN en el celular y sin desplegar infraestructura a producción."
---

# Skill: Flutter APK por Internet sin VPN, backend Docker local

## Objetivo obligatorio

Soluciona la conectividad de una APK Android hecha con Flutter/Dart cuando el backend y la base de datos siguen ejecutándose localmente mediante Docker en mi computadora. La APK ya funciona cuando el celular está conectado al WiFi de mi casa, pero falla el inicio de sesión si el celular se conecta a otro WiFi o a datos móviles.

**Resultado exigido:** la APK instalada en mi Android físico debe abrir, iniciar sesión y funcionar desde cualquier conexión a Internet, sin instalar Tailscale, VPN, proxy, herramientas de desarrollo ni otras aplicaciones en el teléfono. La API y la base de datos deben permanecer en Docker en mi PC. No realizar un despliegue de producción.

El mecanismo recomendado es **Cloudflare Tunnel con hostname HTTPS estable** hacia la API local. Si la configuración real del proyecto lo requiere, evalúa una alternativa equivalente de túnel HTTPS con dirección estable. El celular solo usa Internet normal.

## Diagnóstico obligatorio antes de editar

1. Inspecciona la estructura del repositorio. Localiza `pubspec.yaml`, clientes HTTP (`dio`, `http`, etc.), configuración de URLs, autenticación, WebSockets y otros servicios externos usados por Flutter.
2. Inspecciona `compose.yaml` / `docker-compose.yml`, `.env.example`, puertos de la API, mapeos, reverse proxies, redes de Docker y las variables de backend relevantes. No muestres ni publiques secretos.
3. Determina si la APK usa `localhost`, `127.0.0.1`, `10.0.2.2`, una IP LAN como `192.168.x.x` o una URL que solo existe dentro de Docker. Explica cuál falla desde otras redes y por qué.
4. Confirma el puerto HTTP real del backend, la ruta de salud y la ruta de login. Verifica que la API responda desde la PC antes de configurar el túnel.
5. Revisa las restricciones de acceso, autenticación, cookies/JWT, uso de HTTPS, posibles callbacks, URLs absolutas y recursos como archivos e imágenes.

## Solución de red que debes implementar

1. Mantén funcionando el backend y la base de datos en Docker, sin moverlos a la nube.
2. Configura `cloudflared` en el host o como servicio/contenedor de Docker, según la arquitectura que ya exista. Crea una conexión saliente desde la PC hacia Cloudflare, sin abrir puertos entrantes en el router.
3. Publica **únicamente el endpoint HTTP/HTTPS de la API**, idealmente detrás de un reverse proxy con las rutas estrictamente necesarias. No publiques PostgreSQL/MySQL, Redis, Docker daemon, paneles de administración ni endpoints de depuración.
4. Prioriza un **túnel administrado/nominado con subdominio estable**, por ejemplo `https://api-dev.midominio.com`. Verifica si dispongo de dominio en Cloudflare y de acceso a su panel. Si es necesaria una cuenta, dominio, token o una intervención humana, detén solo ese paso, explica exactamente qué acción debo hacer y deja el resto implementado.
5. No presentes una URL aleatoria `*.trycloudflare.com` como solución definitiva: cambia al reiniciar el túnel y obligaría a volver a configurar o regenerar la APK. Puedes usarla para una prueba diagnóstica temporal, distinguiéndola del resultado estable.
6. Si no hay dominio propio, investiga y propone una opción de hostname público estable de un servicio de túnel, indicando sus condiciones reales y limitaciones. No inventes la disponibilidad de planes gratuitos ni prometas una URL permanente sin haberla confirmado.
7. Si `cloudflared` se ejecuta en Docker, revisa cómo alcanza la API desde su red. Dentro del contenedor, `localhost` apunta al propio contenedor y no necesariamente a la API. Usa el nombre del servicio de Compose y su puerto interno cuando comparten red, o una ruta al host verificada.
8. Conserva puertos de la base de datos inaccesibles desde Internet. Minimiza la exposición de otros servicios locales. Si es apropiado, publica el puerto de la API solo en `127.0.0.1` del host y deja el túnel apuntando al origen local, salvo que la configuración de redes Docker requiera otra solución.
9. Documenta cómo iniciar, reiniciar y detener el túnel, cómo verificar su conexión y qué debe permanecer encendido en la PC.

## Cambios Flutter / Android

1. Centraliza la URL base en una configuración única de la API. Elimina dependencias de IPs privadas/LAN para la APK de prueba remota.
2. Usa la URL HTTPS estable como endpoint remoto. Permite suministrarla por `--dart-define=API_BASE_URL=https://...` o por el sistema de configuración que ya utilice el proyecto. Conserva configuraciones independientes para emulador/desarrollo local y APK remota, sin romperlas.
3. Configura correctamente los endpoints de login y el cliente HTTP de la app. Revisa `baseUrl`, rutas, interceptores, cabeceras, manejo de errores, refresh token, cookies y tiempo de espera, de acuerdo con la implementación actual.
4. Verifica que Android tenga permiso `android.permission.INTERNET`. Utiliza HTTPS con validación TLS normal. No desactives la comprobación de certificados ni habilites `cleartextTraffic` como arreglo improvisado.
5. No cambies CORS sin una necesidad real: una app Flutter nativa normalmente no está sujeta a CORS del navegador. Revisa CORS si también hay frontend web.
6. Si existen WebSockets, notificaciones, archivos, imágenes o rutas absolutas, comprueba que usen endpoints públicos compatibles y que no apunten a IPs LAN.
7. Mantén las pantallas, lógica de negocio, diseño y flujos de autenticación actuales. Cambia únicamente lo necesario para conectividad y seguridad del entorno de pruebas.

## Seguridad mínima obligatoria

- El túnel hace accesible la API de desarrollo a través de Internet. No equivale a desplegar la base de datos ni la aplicación a producción, pero **sí expone la API**. Requiere autenticación y medidas de protección.
- Conserva JWT/autorizaciones y aplica control de acceso en rutas privadas. Revisa rate limiting y protección de login, errores sin datos sensibles y desactivación de interfaces de debug administrativas.
- Usa HTTPS y no incrustes claves de Cloudflare, tokens de administrador, contraseñas, claves de base de datos ni secretos permanentes en la APK. Trata `--dart-define` como configuración pública, no como almacén seguro de credenciales.
- No agregues Cloudflare Access con un inicio de sesión web obligatorio que impida las llamadas HTTP de Flutter sin diseñar primero un flujo compatible. Tampoco incrustes tokens de servicio privilegiados de Cloudflare Access en una APK distribuible.
- No ejecutes cambios destructivos, abras el router, actives DMZ, expongas la base de datos, publiques secretos ni modifiques credenciales reales sin autorización explícita.

## Pruebas de aceptación

1. Levanta API y base de datos en Docker en la PC. Confirma salud de la API desde el host.
2. Confirma que el túnel está conectado y que la URL HTTPS pública estable llega al endpoint de salud desde una red externa.
3. Genera APK Android de prueba configurada con la URL pública correcta. Confirma que no apunta a `localhost`, `10.0.2.2` ni a IP LAN.
4. Instala la APK en Android físico y verifica login, cierre de sesión y solicitudes autenticadas desde: (a) WiFi de casa, (b) WiFi diferente y (c) datos móviles. Estas pruebas deben hacerse realmente fuera de la LAN o usando datos móviles. Si no tienes acceso al celular, marca esas comprobaciones como **pendientes de ejecución por el usuario**, nunca como aprobadas.
5. Reinicia `cloudflared` y confirma que el dominio público se conserva. Reinicia Docker cuando sea necesario y verifica la recuperación.
6. Comprueba que no haya accesos públicos directos a los puertos de la base de datos ni a los paneles internos. Verifica errores manejables si la PC o el túnel se desconectan.
7. Ejecuta las pruebas y builds disponibles en el repositorio. Muestra comandos usados y sus resultados reales.

## Entregables

- Resumen de la causa original exacta, con evidencia del código.
- Archivos modificados y explicación puntual de cada cambio.
- Configuración del túnel/reverse proxy y Docker sin secretos incluidos en Git.
- Variable pública de URL y comando de compilación de la APK; instrucciones para Windows 11 si corresponde.
- Guía breve para iniciar Docker, iniciar el túnel, generar la APK y comprobar conexión desde otra red.
- Tabla de pruebas ejecutadas, aprobadas, fallidas o pendientes de ejecutar en el celular.
- Limitaciones: la PC debe permanecer encendida, Docker operativo, túnel activo e Internet disponible en ambos extremos. Si la PC se apaga, la app no accederá al backend.

## Prioridades

1. APK funcionando por WiFi externo y datos móviles **sin VPN ni aplicaciones auxiliares en el teléfono**.
2. Backend y base de datos mantenidos localmente en Docker.
3. Endpoint HTTPS público estable para evitar reinstalar APK al cambiar la IP del hogar.
4. Seguridad básica de la API expuesta.
5. Cero regresiones en funciones y diseño existentes.

**No afirmes que está solucionado hasta verificar la conectividad externa y las pruebas de la APK.**
