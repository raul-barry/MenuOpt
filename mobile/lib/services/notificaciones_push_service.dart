import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/api_client.dart';

const _temaPromociones = 'menuopt_promociones';
const _clavePromocionesActivas = 'notificaciones_promociones_activas';
const _claveIdInstalacion = 'notificaciones_push_id_instalacion';
const _canalId = 'menuopt_promociones_high_v2';
const _canalNombre = 'Novedades y promociones';
const _canalDescripcion = 'Ofertas y novedades gastronómicas de MenuOpt.';
const _canalPrivadoId = 'menuopt_transacciones_v1';
const _canalPrivadoNombre = 'Reservas y pedidos';
const _canalPrivadoDescripcion =
    'Actualizaciones privadas de tus reservas y pedidos.';

const _seccionesNotificacion = <String, int>{
  'inicio': 0,
  'planificar': 1,
  'planificaciones': 2,
  'preferencias': 3,
  'reservas': 4,
  'pedidos': 5,
  'perfil': 6,
  'asistente': 7,
  'recetas': 8,
};

typedef NavegarSeccionNotificacion = void Function(
  int seccion,
  String? tipoRecurso,
  int? idRecurso,
);

final notificacionesNavigatorKey = GlobalKey<NavigatorState>();

class NotificacionesPushService {
  NotificacionesPushService._();

  static final instance = NotificacionesPushService._();

  final _preferencias = SharedPreferencesAsync();
  final _notificacionesLocales = FlutterLocalNotificationsPlugin();
  final _idsNotificados = <String>{};
  bool _inicializado = false;
  bool _notificacionesLocalesListas = false;
  int? _seccionPendiente;
  String? _tipoRecursoPendiente;
  int? _idRecursoPendiente;
  NavegarSeccionNotificacion? _navegarASeccion;
  StreamSubscription<String>? _tokenRefreshSubscription;
  StreamSubscription<String>? _tokenUnregisteredSubscription;
  Completer<String?>? _tokenRegistradoPendiente;
  String? _tokenInstalacionFirebase;
  String? _idInstalacion;

  void configurarNavegacion(NavegarSeccionNotificacion callback) {
    _navegarASeccion = callback;
  }

  void guardarSeccionPendiente(int seccion) {
    _seccionPendiente = seccion;
  }

  void guardarDestinoPendiente(int seccion, String? tipo, int? id) {
    _seccionPendiente = seccion;
    _tipoRecursoPendiente = tipo;
    _idRecursoPendiente = id;
  }

  int? tomarSeccionPendiente() {
    final seccion = _seccionPendiente;
    _seccionPendiente = null;
    return seccion;
  }

  Future<bool> inicializar() async {
    if (_inicializado) return true;

    try {
      if (Firebase.apps.isEmpty) {
        await Firebase.initializeApp();
      }

      await _inicializarNotificacionesLocales();
      FirebaseMessaging.onMessage.listen(_mostrarEnPrimerPlano);
      FirebaseMessaging.onMessageOpenedApp.listen(_abrirDesdeFirebase);
      _tokenRefreshSubscription ??= FirebaseMessaging.instance.onRegistered
          .listen(_alRegistrarTokenFirebase);
      _tokenUnregisteredSubscription ??= FirebaseMessaging
          .instance
          .onUnregistered
          .listen(_alRevocarTokenFirebase);
      await FirebaseMessaging.instance.register();
      _inicializado = true;

      final inicioLocal = await _notificacionesLocales
          .getNotificationAppLaunchDetails();
      if (inicioLocal?.didNotificationLaunchApp ?? false) {
        _procesarPayload(inicioLocal?.notificationResponse?.payload);
      }

      final mensajeInicial = await FirebaseMessaging.instance
          .getInitialMessage();
      if (mensajeInicial != null) {
        _abrirDesdeFirebase(mensajeInicial);
      }

      if (await promocionesActivas()) {
        await FirebaseMessaging.instance.subscribeToTopic(_temaPromociones);
      }
      return true;
    } catch (_) {
      // La app puede seguir funcionando mientras Firebase no esté disponible.
      return false;
    }
  }

  Future<void> _inicializarNotificacionesLocales() async {
    final inicializado = await _notificacionesLocales.initialize(
      const InitializationSettings(
        android: AndroidInitializationSettings('@mipmap/ic_launcher'),
      ),
      onDidReceiveNotificationResponse: _alTocarNotificacionLocal,
    );

    if (inicializado != true) {
      throw StateError('No se pudo inicializar el canal de notificaciones.');
    }

    const canal = AndroidNotificationChannel(
      _canalId,
      _canalNombre,
      description: _canalDescripcion,
      importance: Importance.high,
      playSound: true,
      enableVibration: true,
    );
    await _notificacionesLocales
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(canal);
    const canalPrivado = AndroidNotificationChannel(
      _canalPrivadoId,
      _canalPrivadoNombre,
      description: _canalPrivadoDescripcion,
      importance: Importance.high,
      playSound: true,
      enableVibration: true,
    );
    await _notificacionesLocales
        .resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin
        >()
        ?.createNotificationChannel(canalPrivado);
    _notificacionesLocalesListas = true;
  }

  Future<bool> promocionesActivas() async =>
      await _preferencias.getBool(_clavePromocionesActivas) ?? false;

  Future<String?> cambiarSuscripcionPromociones(bool activar) async {
    if (!await inicializar()) {
      return 'Falta vincular la app con Firebase para activar las notificaciones.';
    }

    try {
      final messaging = FirebaseMessaging.instance;
      if (activar) {
        final permiso = await messaging.requestPermission(
          alert: true,
          badge: true,
          sound: true,
        );
        if (permiso.authorizationStatus == AuthorizationStatus.denied) {
          return 'El permiso está desactivado en Android. Actívalo en los ajustes de MenuOpt.';
        }
        await messaging.subscribeToTopic(_temaPromociones);
      } else {
        await messaging.unsubscribeFromTopic(_temaPromociones);
      }

      await _preferencias.setBool(_clavePromocionesActivas, activar);
      if (activar && ApiClient.instance.isAuthenticated) {
        await vincularDispositivoActual();
      }
      return null;
    } catch (_) {
      return 'No se pudo actualizar la suscripción de notificaciones. Inténtalo de nuevo.';
    }
  }

  Future<void> vincularDispositivoActual() async {
    if (!ApiClient.instance.isAuthenticated || !await inicializar()) return;
    try {
      final token = _tokenInstalacionFirebase ?? await _esperarTokenFirebase();
      if (token == null || token.isEmpty) return;
      await _enviarTokenAlBackend(token);
    } catch (_) {
      // El registro FCM no debe impedir el inicio de sesión ni el uso normal.
    }
  }

  Future<String?> _esperarTokenFirebase() async {
    final pendiente = Completer<String?>();
    _tokenRegistradoPendiente = pendiente;
    await FirebaseMessaging.instance.register();
    return pendiente.future.timeout(
      const Duration(seconds: 15),
      onTimeout: () => null,
    );
  }

  Future<void> _alRegistrarTokenFirebase(String token) async {
    _tokenInstalacionFirebase = token;
    final pendiente = _tokenRegistradoPendiente;
    if (pendiente != null && !pendiente.isCompleted) {
      pendiente.complete(token);
    }
    if (ApiClient.instance.isAuthenticated) {
      await _enviarTokenAlBackend(token);
    }
  }

  void _alRevocarTokenFirebase(String token) {
    if (_tokenInstalacionFirebase == token) _tokenInstalacionFirebase = null;
  }

  Future<void> _enviarTokenAlBackend(String token) async {
    final idInstalacion = await _obtenerIdInstalacion();
    await ApiClient.instance.put('/notificaciones/dispositivos', {
      'id_instalacion': idInstalacion,
      'token': token,
      'plataforma': 'ANDROID',
    });
    if (await promocionesActivas()) {
      await FirebaseMessaging.instance.subscribeToTopic(_temaPromociones);
    }
  }

  Future<void> desvincularDispositivoActual() async {
    try {
      if (ApiClient.instance.isAuthenticated) {
        await ApiClient.instance.post('/notificaciones/dispositivos/revocar', {
          'id_instalacion': await _obtenerIdInstalacion(),
        });
      }
    } catch (_) {
      // deleteToken invalida el destino FCM local aunque no haya red.
    }
    try {
      if (await promocionesActivas()) {
        await FirebaseMessaging.instance.unsubscribeFromTopic(_temaPromociones);
      }
      await FirebaseMessaging.instance.unregister();
      _tokenInstalacionFirebase = null;
    } catch (_) {}
  }

  Future<String> _obtenerIdInstalacion() async {
    final existente =
        _idInstalacion ?? await _preferencias.getString(_claveIdInstalacion);
    if (existente != null && existente.isNotEmpty) {
      _idInstalacion = existente;
      return existente;
    }
    final random = Random.secure();
    final id = List.generate(
      48,
      (_) => random.nextInt(16).toRadixString(16),
    ).join();
    await _preferencias.setString(_claveIdInstalacion, id);
    _idInstalacion = id;
    return id;
  }

  Future<void> _mostrarEnPrimerPlano(RemoteMessage mensaje) async {
    if (!_notificacionesLocalesListas) return;

    final titulo =
        mensaje.notification?.title ?? mensaje.data['title']?.toString();
    final cuerpo =
        mensaje.notification?.body ?? mensaje.data['body']?.toString();
    if ((titulo == null || titulo.isEmpty) &&
        (cuerpo == null || cuerpo.isEmpty)) {
      return;
    }

    final firma = _firmaMensaje(mensaje, titulo, cuerpo);
    if (!_idsNotificados.add(firma)) return;
    if (_idsNotificados.length > 100) {
      _idsNotificados.remove(_idsNotificados.first);
    }

    try {
      final esTransaccional = <String>{
        'reserva',
        'pedido',
      }.contains(mensaje.data['type']?.toString().toLowerCase());
      final canalId = esTransaccional ? _canalPrivadoId : _canalId;
      final canalNombre = esTransaccional ? _canalPrivadoNombre : _canalNombre;
      final canalDescripcion = esTransaccional
          ? _canalPrivadoDescripcion
          : _canalDescripcion;
      await _notificacionesLocales.show(
        _idNotificacion(firma),
        titulo,
        cuerpo,
        NotificationDetails(
          android: AndroidNotificationDetails(
            canalId,
            canalNombre,
            channelDescription: canalDescripcion,
            importance: Importance.high,
            priority: Priority.high,
            playSound: true,
            enableVibration: true,
            autoCancel: true,
            ongoing: false,
            onlyAlertOnce: true,
          ),
        ),
        payload: jsonEncode(mensaje.data),
      );
    } catch (_) {
      _idsNotificados.remove(firma);
    }
  }

  String _firmaMensaje(RemoteMessage mensaje, String? titulo, String? cuerpo) {
    // El ID lógico de la outbox permanece estable entre reintentos FCM; usarlo
    // primero impide volver a publicar dos veces la misma operación de negocio.
    final eventId = mensaje.data['event_id']?.toString();
    if (eventId != null && eventId.isNotEmpty) return eventId;
    return mensaje.messageId ??
        '${mensaje.sentTime?.millisecondsSinceEpoch ?? ''}|$titulo|$cuerpo|${jsonEncode(mensaje.data)}';
  }

  int _idNotificacion(String firma) {
    var hash = 0;
    for (final unidad in firma.codeUnits) {
      hash = (hash * 31 + unidad) & 0x7fffffff;
    }
    return hash;
  }

  void _abrirDesdeFirebase(RemoteMessage mensaje) {
    _navegarConDatos(mensaje.data);
  }

  void _alTocarNotificacionLocal(NotificationResponse respuesta) {
    _procesarPayload(respuesta.payload);
  }

  void _procesarPayload(String? payload) {
    if (payload == null || payload.isEmpty) return;
    try {
      final decoded = jsonDecode(payload);
      if (decoded is Map) {
        _navegarConDatos(Map<String, dynamic>.from(decoded));
      }
    } on FormatException {
      // Un payload inválido abre MenuOpt sin navegar a una sección desconocida.
    }
  }

  void _navegarConDatos(Map<String, dynamic> data) {
    final tipo = data['type']?.toString().trim().toLowerCase();
    final rawId = data['resource_id']?.toString();
    final idRecurso = int.tryParse(rawId ?? '');
    if ((tipo == 'reserva' || tipo == 'pedido') &&
        idRecurso != null &&
        idRecurso > 0) {
      final navegar = _navegarASeccion;
      if (navegar == null || !ApiClient.instance.isAuthenticated) {
        _seccionPendiente = tipo == 'reserva' ? 4 : 5;
        _tipoRecursoPendiente = tipo;
        _idRecursoPendiente = idRecurso;
      } else {
        navegar(tipo == 'reserva' ? 4 : 5, tipo, idRecurso);
      }
      return;
    }

    final raw = data['route'] ?? data['screen'];
    if (raw == null) return;

    final seccion = _seccionesNotificacion[raw.toString().trim().toLowerCase()];
    if (seccion == null) return;

    final navegar = _navegarASeccion;
    if (navegar == null) {
      _seccionPendiente = seccion;
    } else {
      navegar(seccion, null, null);
    }
  }

  String? tomarTipoRecursoPendiente() {
    final tipo = _tipoRecursoPendiente;
    _tipoRecursoPendiente = null;
    return tipo;
  }

  int? tomarIdRecursoPendiente() {
    final id = _idRecursoPendiente;
    _idRecursoPendiente = null;
    return id;
  }
}
