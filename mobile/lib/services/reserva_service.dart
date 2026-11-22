import '../core/api_client.dart';

class ReservaService {
  static final ReservaService instance = ReservaService._();
  ReservaService._();

  final _api = ApiClient.instance;

  // CU21: Consultar reservas del cliente
  Future<List<dynamic>> getMisReservas() async {
    final res = await _api.get('/reservas/mis-reservas');
    return (res as List<dynamic>?) ?? [];
  }

  Future<Map<String, dynamic>> getDetalleReserva(int idReserva) async {
    final res = await _api.get('/reservas/$idReserva');
    return res as Map<String, dynamic>;
  }

  // CU20: Consultar disponibilidad de mesas (lista simple)
  Future<List<dynamic>> getMesasDisponibles(
    int idRestaurante,
    String fecha,
    String horaInicio,
    String horaFin,
    int cantidadPersonas, {
    int? idArea,
  }) async {
    String url =
        '/restaurantes/$idRestaurante/mesas-disponibles?fecha=$fecha&hora_inicio=$horaInicio&hora_fin=$horaFin&cantidad_personas=$cantidadPersonas';
    if (idArea != null) {
      url += '&id_area=$idArea';
    }
    final res = await _api.get(url);
    if (res is List) return res;
    if (res is Map) {
      if (res['mesas'] is List) {
        return res['mesas'] as List;
      }
      if (res['mesas_disponibles'] is List) {
        return res['mesas_disponibles'] as List;
      }
    }
    return [];
  }

  // CU20: Consultar disponibilidad completa (incluyendo plano 2D, áreas y combinaciones)
  Future<Map<String, dynamic>> consultarDisponibilidad({
    required int idRestaurante,
    required String fecha,
    required String horaInicio,
    required String horaFin,
    required int cantidadPersonas,
    int? idArea,
  }) async {
    var url =
        '/restaurantes/$idRestaurante/mesas-disponibles?fecha=$fecha&hora_inicio=$horaInicio&hora_fin=$horaFin&cantidad_personas=$cantidadPersonas';
    if (idArea != null) {
      url += '&id_area=$idArea';
    }
    final res = await _api.get(url);
    if (res is Map<String, dynamic>) {
      return res;
    }
    return {'mesas': res is List ? res : [], 'combinaciones': []};
  }

  // Áreas del restaurante

  Future<List<dynamic>> getAreasRestaurante(int idRestaurante) async {
    try {
      final res = await _api.get('/restaurantes/$idRestaurante/areas');
      return (res as List<dynamic>?) ?? [];
    } catch (_) {
      return [];
    }
  }

  // CU21: Confirmar reserva
  Future<Map<String, dynamic>> crearReserva(Map<String, dynamic> data) async {
    final res = await _api.post('/reservas', data);
    return res as Map<String, dynamic>;
  }

  // CU21: Cancelar reserva como cliente
  Future<Map<String, dynamic>> cancelarReserva(int idReserva) async {
    final res = await _api.patch('/reservas/$idReserva/cancelar', {});
    return (res is Map<String, dynamic>)
        ? res
        : {'mensaje': 'Reserva cancelada'};
  }

  // Invitados de la reserva
  Future<List<dynamic>> getInvitados(int idReserva) async {
    final res = await _api.get('/reservas/$idReserva/invitados');
    return (res as List<dynamic>?) ?? [];
  }

  Future<Map<String, dynamic>> agregarInvitado(
    int idReserva,
    Map<String, dynamic> data,
  ) async {
    final res = await _api.post('/reservas/$idReserva/invitados', data);
    return res as Map<String, dynamic>;
  }
}
