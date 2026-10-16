import '../core/api_client.dart';

class PlanificacionService {
  static final PlanificacionService instance = PlanificacionService._();
  PlanificacionService._();

  final _api = ApiClient.instance;

  // CU11: Crear planificación
  Future<Map<String, dynamic>> crearPlanificacion({
    required double presupuesto,
    required int cantidadPersonas,
    required String tipoComida,
    required String ubicacionReferencia,
    List<int>? preferencias,
  }) async {
    final payload = {
      'presupuesto': presupuesto,
      'cantidad_personas': cantidadPersonas,
      'tipo_comida': tipoComida.toUpperCase(),
      'ubicacion_referencia': ubicacionReferencia,
      'preferencias': preferencias ?? [],
    };

    final res = await _api.post('/planificaciones', payload);
    return res as Map<String, dynamic>;
  }

  // CU11: Listar mis planificaciones
  Future<Map<String, dynamic>> listarMisPlanificaciones({
    int pagina = 1,
    int limite = 20,
    String? estado,
  }) async {
    var path = '/planificaciones/mis-planificaciones?pagina=$pagina&limite=$limite';
    if (estado != null && estado.isNotEmpty) {
      path += '&estado=$estado';
    }
    final res = await _api.get(path);
    return res as Map<String, dynamic>;
  }

  // CU11: Obtener detalle
  Future<Map<String, dynamic>> obtenerPlanificacion(int idPlanificacion) async {
    final res = await _api.get('/planificaciones/$idPlanificacion');
    return res as Map<String, dynamic>;
  }

  // CU11: Editar planificación
  Future<Map<String, dynamic>> actualizarPlanificacion(
    int idPlanificacion,
    Map<String, dynamic> datos,
  ) async {
    final res = await _api.put('/planificaciones/$idPlanificacion', datos);
    return res as Map<String, dynamic>;
  }

  // CU11: Cancelar planificación
  Future<Map<String, dynamic>> cancelarPlanificacion(int idPlanificacion) async {
    final res = await _api.patch('/planificaciones/$idPlanificacion/estado', {
      'estado': 'CANCELADA',
    });
    return res as Map<String, dynamic>;
  }

  // CU13: Generar recomendaciones
  Future<List<dynamic>> generarRecomendaciones(int idPlanificacion) async {
    final res = await _api.post(
      '/planificaciones/$idPlanificacion/recomendaciones/generar',
      {},
    );
    if (res is List) return res;
    if (res is Map && res['recomendaciones'] is List) {
      return res['recomendaciones'] as List;
    }
    return [];
  }

  // CU13 / CU14: Obtener recomendaciones generadas
  Future<List<dynamic>> obtenerRecomendaciones(int idPlanificacion) async {
    final res = await _api.get('/planificaciones/$idPlanificacion/recomendaciones');
    return (res as List<dynamic>?) ?? [];
  }

  // CU13: Obtener detalle de una recomendación específica
  Future<Map<String, dynamic>> obtenerDetalleRecomendacion(int idRecomendacion) async {
    final res = await _api.get('/recomendaciones/$idRecomendacion');
    return res as Map<String, dynamic>;
  }

  // CU14: Comparar alternativas de la planificación
  Future<Map<String, dynamic>> compararAlternativas(int idPlanificacion) async {
    final res = await _api.get('/planificaciones/$idPlanificacion/comparacion');
    return res as Map<String, dynamic>;
  }
}

