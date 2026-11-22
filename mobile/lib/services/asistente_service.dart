import '../core/api_client.dart';

class AsistenteService {
  static final AsistenteService instance = AsistenteService._();
  AsistenteService._();

  final _api = ApiClient.instance;

  // Guía contextual de la plataforma para el rol autenticado.
  Future<Map<String, dynamic>> guiarUsuario({
    required String mensaje,
    String? accionId,
    String? paginaActual,
    List<Map<String, String>> historial = const [],
  }) async {
    final res = await _api.post('/asistente/guia', {
      'mensaje': mensaje,
      'plataforma': 'mobile',
      if (accionId != null) 'accion_id': accionId,
      if (paginaActual != null) 'pagina_actual': paginaActual,
      'historial': historial,
    });
    return res as Map<String, dynamic>;
  }

  // CU26: Interpretar solicitud en lenguaje natural
  Future<Map<String, dynamic>> interpretar(String mensaje) async {
    final res = await _api.post('/asistente/interpretar', {
      'mensaje': mensaje,
      'solicitud': mensaje,
    });
    return res as Map<String, dynamic>;
  }

  // CU26: Explicar recomendación existente
  Future<Map<String, dynamic>> explicarRecomendacion(int idRecomendacion) async {
    final res = await _api.post('/asistente/explicar-recomendacion', {
      'id_recomendacion': idRecomendacion,
    });
    return res as Map<String, dynamic>;
  }

  // CU26: Explicar comparación entre Restaurante y Preparación Propia
  Future<Map<String, dynamic>> explicarComparacion(int idPlanificacion) async {
    final res = await _api.post('/asistente/explicar-comparacion', {
      'id_planificacion': idPlanificacion,
    });
    return res as Map<String, dynamic>;
  }
}
