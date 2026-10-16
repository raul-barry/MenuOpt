import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:menuopt_mobile/core/app_theme.dart';
import 'package:menuopt_mobile/screens/login_screen.dart';
import 'package:menuopt_mobile/screens/registro_screen.dart';
import 'package:menuopt_mobile/screens/planificaciones_screen.dart';
import 'package:menuopt_mobile/screens/planificar_screen.dart';
import 'package:menuopt_mobile/screens/planificacion_detalle_screen.dart';
import 'package:menuopt_mobile/screens/recomendacion_detalle_screen.dart';
import 'package:menuopt_mobile/screens/comparacion_screen.dart';
import 'package:menuopt_mobile/screens/reservar_mesa_plano_screen.dart';

void main() {
  const targetSizes = [
    Size(320, 640), // iPhone SE 1st gen / ultra-compact
    Size(360, 740), // Android Compact (e.g. Galaxy S series)
    Size(375, 667), // iPhone SE 2nd/3rd gen / iPhone 8
    Size(390, 844), // iPhone 12 / 13 / 14
    Size(414, 896), // iPhone 11 / XR / Plus
    Size(430, 932), // iPhone 14/15 Pro Max
    Size(600, 1024), // Tablet / Foldable
  ];

  final samplePlan = {
    'id_planificacion': 12,
    'presupuesto': 180.0,
    'cantidad_personas': 4,
    'tipo_comida': 'ALMUERZO',
    'ubicacion_referencia': 'Calacoto / San Miguel, Zona Sur',
    'estado': 'ACTIVA',
    'fecha_planificacion': '2026-10-15T12:00:00Z',
    'preferencias_resumen': ['Comida Saludable', 'Sin Mariscos'],
  };

  final sampleRec = {
    'id_recomendacion': 45,
    'id_planificacion': 12,
    'tipo_recomendacion': 'RESTAURANTE',
    'nombre': 'Restaurante Gourmet La Casona Colonial',
    'nombre_restaurante': 'Restaurante Gourmet La Casona Colonial',
    'puntuacion': 91.5,
    'costo_total': 185.50,
    'costo_por_persona': 46.38,
    'fecha_generacion': '2026-10-15T12:00:00Z',
    'id_restaurante': 3,
    'descripcion': 'Opción altamente compatible con presupuesto y comensales.',
    'platos': [
      {
        'nombre_plato': 'Plato Especial de la Casa con Guarnición',
        'personas_cubiertas': 4,
        'cantidad': 1,
        'precio_unitario': 185.50,
        'subtotal': 185.50,
      }
    ],
  };

  final sampleComparacion = {
    'id_planificacion': 12,
    'presupuesto': 200.0,
    'cantidad_personas': 4,
    'tipo_comida': 'ALMUERZO',
    'total_alternativas': 2,
    'mejor_opcion_costo': {
      'id_recomendacion': 46,
      'nombre': 'Preparación Casera Equilibrada',
      'tipo_recomendacion': 'PREPARACION_PROPIA',
      'costo_total': 120.0,
      'ahorro_respecto_presupuesto': 80.0,
      'puntuacion': 85.0,
    },
    'mejor_opcion_puntuacion': {
      'id_recomendacion': 45,
      'nombre': 'Restaurante Gourmet La Casona Colonial',
      'tipo_recomendacion': 'RESTAURANTE',
      'costo_total': 185.50,
      'ahorro_respecto_presupuesto': 14.50,
      'puntuacion': 92.0,
    },
    'alternativas': [
      {
        'id_recomendacion': 45,
        'nombre': 'Restaurante Gourmet La Casona Colonial',
        'tipo_recomendacion': 'RESTAURANTE',
        'puntuacion': 92.0,
        'costo_total': 185.50,
        'costo_por_persona': 46.38,
        'ahorro_respecto_presupuesto': 14.50,
        'porcentaje_presupuesto_utilizado': 92.75,
        'resumen': 'Excelente balance calidad-precio.',
        'platos': [
          {
            'nombre_plato': 'Menú Ejecutivo',
            'cantidad': 4,
            'subtotal': 185.50,
          }
        ],
      },
      {
        'id_recomendacion': 46,
        'nombre': 'Preparación Casera Equilibrada',
        'tipo_recomendacion': 'PREPARACION_PROPIA',
        'puntuacion': 85.0,
        'costo_total': 120.0,
        'costo_por_persona': 30.0,
        'ahorro_respecto_presupuesto': 80.0,
        'porcentaje_presupuesto_utilizado': 60.0,
        'resumen': 'Ahorro considerable con ingredientes de mercado local.',
        'ingredientes_resumen': ['Pollo', 'Arroz', 'Verduras'],
        'lugares_compra_resumen': ['Mercado Rodríguez'],
      }
    ],
  };

  final sampleAreas = [
    {
      'id_area': 1,
      'nombre': 'Salón Principal',
      'mesas': [
        {'id_mesa': 101, 'numero': '1', 'capacidad': 4, 'pos_x': 80, 'pos_y': 80, 'ancho': 60, 'alto': 60, 'estado': 'DISPONIBLE'},
        {'id_mesa': 102, 'numero': '2', 'capacidad': 2, 'pos_x': 180, 'pos_y': 80, 'ancho': 50, 'alto': 50, 'estado': 'DISPONIBLE'},
      ]
    }
  ];

  final sampleDisponibilidad = {
    'combinaciones_sugeridas': [],
    'mesas_libres': [101, 102],
  };

  setUp(() {
    FlutterError.onError = FlutterError.dumpErrorToConsole;
  });

  Widget buildTestableWidget(Widget child, {double textScale = 1.0}) {
    return MaterialApp(
      theme: AppTheme.theme,
      home: MediaQuery(
        data: MediaQueryData(
          textScaler: TextScaler.linear(textScale),
        ),
        child: child,
      ),
    );
  }

  for (final size in targetSizes) {
    group('Viewport Width ${size.width.toInt()}px (Height ${size.height.toInt()}px):', () {
      testWidgets('LoginScreen adapts without RenderFlex overflow', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(const LoginScreen()));
        await tester.pump();

        expect(find.text('Iniciar Sesión'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('RegistroScreen adapts without overflow', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(const RegistroScreen()));
        await tester.pump();

        expect(find.text('Crear Cuenta de Cliente'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('PlanificarScreen adapts form and action buttons', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(const PlanificarScreen()));
        await tester.pump();

        expect(find.text('Registrar Planificación Gastronómica (CU11)'), findsOneWidget);
        expect(find.text('Guardar Planificación'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('PlanificacionesScreen adapts list and filter chips', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(const PlanificacionesScreen()));
        await tester.pump();

        expect(find.text('Mis Planificaciones'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('PlanificacionDetalleScreen adapts metrics and action wrap', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(PlanificacionDetalleScreen(
          idPlanificacion: 12,
          initialPlan: samplePlan,
        )));
        await tester.pump();

        expect(find.text('PLANIFICACIÓN #12'), findsOneWidget);
        expect(find.text('Generar Recomendaciones'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('RecomendacionDetalleScreen adapts header, cards, table and reservation button', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(RecomendacionDetalleScreen(
          idRecomendacion: 45,
          recomendacionData: sampleRec,
          idPlanificacion: 12,
          planData: samplePlan,
        )));
        await tester.pump();

        expect(find.text('Detalle de Recomendación'), findsOneWidget);
        expect(find.text('Restaurante Gourmet La Casona Colonial'), findsOneWidget);

        // Scroll down to bring second card into view if needed
        await tester.scrollUntilVisible(
          find.text('Reservar Mesa en el Restaurante'),
          300,
          scrollable: find.byType(Scrollable).first,
        );
        await tester.pump();

        expect(find.text('Reservar Mesa en el Restaurante'), findsOneWidget);
        expect(find.text('Detalle de Platos a Consumir'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('ComparacionScreen adapts header, highlight cards and alternatives list', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(ComparacionScreen(
          idPlanificacion: 12,
          planData: samplePlan,
          initialComparacion: sampleComparacion,
        )));
        await tester.pump();

        expect(find.text('Comparar Alternativas (CU14)'), findsOneWidget);
        expect(find.text('Explicar Comparación con IA (CU26)'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('ReservarMesaPlanoScreen adapts filters, 2D floor plan, and bottom confirm button', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(ReservarMesaPlanoScreen(
          idRestaurante: 3,
          nombreRestaurante: 'Restaurante Gourmet La Casona',
          idPlanificacion: 12,
          cantidadPersonasInicial: 4,
          initialAreas: sampleAreas,
          initialDisponibilidad: sampleDisponibilidad,
        )));
        await tester.pump();

        expect(find.textContaining('Restaurante Gourmet La Casona'), findsWidgets);
        expect(tester.takeException(), isNull);

        await tester.drag(find.byType(ListView), const Offset(0, -400));
        await tester.pump();

        expect(find.text('Plano 2D Interactivo'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });

      testWidgets('Accessibility text scale 1.25x does not cause overflow on RecomendacionDetalle', (WidgetTester tester) async {
        tester.view.physicalSize = Size(size.width * 2.0, size.height * 2.0);
        tester.view.devicePixelRatio = 2.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(buildTestableWidget(
          RecomendacionDetalleScreen(
            idRecomendacion: 45,
            recomendacionData: sampleRec,
            idPlanificacion: 12,
            planData: samplePlan,
          ),
          textScale: 1.25,
        ));
        await tester.pump();

        expect(find.text('Detalle de Recomendación'), findsOneWidget);

        await tester.scrollUntilVisible(
          find.text('Reservar Mesa en el Restaurante'),
          300,
          scrollable: find.byType(Scrollable).first,
        );
        await tester.pump();

        expect(find.text('Reservar Mesa en el Restaurante'), findsOneWidget);
        expect(tester.takeException(), isNull);
      });
    });
  }
}
