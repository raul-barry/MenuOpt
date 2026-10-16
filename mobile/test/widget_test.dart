import 'dart:ui';
import 'package:flutter_test/flutter_test.dart';
import 'package:menuopt_mobile/main.dart';

void main() {
  testWidgets('MenuOptApp login and client registration flow test', (WidgetTester tester) async {
    // Definir tamaño adecuado de pantalla para emular dispositivo móvil
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const MenuOptApp());
    await tester.pumpAndSettle();

    // 1. Verifica que se encuentre la pantalla de Iniciar Sesión
    expect(find.text('Iniciar Sesión'), findsOneWidget);

    // 2. Verifica que la cuenta de prueba sea únicamente Cliente 1
    expect(find.text('Cliente 1'), findsOneWidget);

    // 3. Verifica que NO existan botones de prueba para Admin ni Restaurante
    expect(find.text('Admin'), findsNothing);
    expect(find.text('Restaurante'), findsNothing);

    // 4. Verifica el enlace de registrarse como cliente
    final registroLink = find.text('Regístrate como Cliente');
    expect(registroLink, findsOneWidget);

    // 5. Toca en "Regístrate como Cliente" para navegar a la pantalla de Registro
    await tester.tap(registroLink);
    await tester.pumpAndSettle();

    // 6. Verifica que la pantalla de registro se muestre correctamente
    expect(find.text('Crear Cuenta de Cliente'), findsOneWidget);
    expect(find.text('Nombres *'), findsOneWidget);
    expect(find.text('Apellidos *'), findsOneWidget);
    expect(find.text('Crear Cuenta'), findsOneWidget);
    expect(find.text('Inicia Sesión'), findsOneWidget);

    // 7. Toca en "Inicia Sesión" o el botón volver para regresar al Login
    await tester.ensureVisible(find.text('Inicia Sesión'));
    await tester.tap(find.text('Inicia Sesión'));
    await tester.pumpAndSettle();

    // 8. Verifica que estamos de vuelta en el Login
    expect(find.text('Iniciar Sesión'), findsOneWidget);
  });
}
