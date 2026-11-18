import '../core/api_client.dart';

class RecetaService {
  static final RecetaService instance = RecetaService._();
  RecetaService._();

  final _api = ApiClient.instance;

  Future<List<dynamic>> getRecetas({String? tipoComida, String? busqueda}) async {
    String query = '';
    final params = <String>[];
    if (tipoComida != null && tipoComida.isNotEmpty && tipoComida != 'TODAS') {
      params.add('tipo_comida=${Uri.encodeComponent(tipoComida)}');
    }
    if (busqueda != null && busqueda.trim().isNotEmpty) {
      params.add('busqueda=${Uri.encodeComponent(busqueda.trim())}');
    }
    if (params.isNotEmpty) {
      query = '?${params.join('&')}';
    }

    final res = await _api.get('/recetas$query');
    return (res as List<dynamic>?) ?? [];
  }

  Future<Map<String, dynamic>> getReceta(int idReceta) async {
    final res = await _api.get('/recetas/$idReceta');
    return res as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> consultarIA({
    required String mensaje,
    int comensales = 2,
  }) async {
    final res = await _api.post('/recetas/consulta-ia', {
      'mensaje': mensaje,
      'comensales': comensales,
    });
    return res as Map<String, dynamic>;
  }
}
