import '../core/api_client.dart';

class RestauranteService {
  static final RestauranteService instance = RestauranteService._();
  RestauranteService._();

  final _api = ApiClient.instance;

  Future<List<dynamic>> getRestaurantes() async {
    try {
      final res = await _api.get('/restaurantes');
      return (res as List<dynamic>?) ?? [];
    } catch (_) {
      try {
        final res = await _api.get('/restaurantes/mis-restaurantes');
        return (res as List<dynamic>?) ?? [];
      } catch (e) {
        rethrow;
      }
    }
  }

  Future<List<dynamic>> getPlatos(int idRestaurante) async {
    final res = await _api.get('/restaurantes/$idRestaurante/platos');
    return (res as List<dynamic>?) ?? [];
  }

  Future<Map<String, dynamic>> getRestaurante(int idRestaurante) async {
    final res = await _api.get('/restaurantes/$idRestaurante');
    return res as Map<String, dynamic>;
  }
}

