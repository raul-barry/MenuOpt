import '../core/api_client.dart';

class PreferenciaService {
  static final PreferenciaService instance = PreferenciaService._();
  PreferenciaService._();

  final _api = ApiClient.instance;

  // Catálogo completo de preferencias activas
  Future<List<dynamic>> listarPreferencias() async {
    final res = await _api.get('/preferencias');
    return (res as List<dynamic>?) ?? [];
  }

  // Preferencias actuales del usuario autenticado (retorna lista de preferencias)
  Future<List<dynamic>> obtenerPreferenciasUsuario() async {
    final res = await _api.get('/usuarios/preferencias');
    if (res is List) {
      return res;
    }
    if (res is Map && res['preferencias'] is List) {
      return res['preferencias'] as List<dynamic>;
    }
    return [];
  }

  // Guardar preferencias del usuario autenticado (CU12)
  Future<dynamic> guardarPreferenciasUsuario(List<int> idsPreferencias) async {
    final res = await _api.put('/usuarios/preferencias', {
      'preferencias': idsPreferencias,
    });
    return res;
  }
}
