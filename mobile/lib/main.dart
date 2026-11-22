import 'package:flutter/material.dart';

import 'core/app_theme.dart';
import 'core/api_client.dart';
import 'screens/home_screen.dart';
import 'services/notificaciones_push_service.dart';
import 'screens/login_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final notificaciones = NotificacionesPushService.instance;
  notificaciones.configurarNavegacion((seccion, tipoRecurso, idRecurso) {
    final navigator = notificacionesNavigatorKey.currentState;
    if (navigator == null || !ApiClient.instance.isAuthenticated) {
      notificaciones.guardarDestinoPendiente(seccion, tipoRecurso, idRecurso);
      return;
    }

    navigator.pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (_) => HomeScreen(
          initialSection: seccion,
          initialResourceType: tipoRecurso,
          initialResourceId: idRecurso,
        ),
      ),
      (_) => false,
    );
  });
  await notificaciones.inicializar();
  runApp(const MenuOptApp());
}

class MenuOptApp extends StatelessWidget {
  const MenuOptApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MenuOpt Mobile',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.theme,
      navigatorKey: notificacionesNavigatorKey,
      home: const LoginScreen(),
    );
  }
}
