import '../core/api_client.dart';

class PedidoService {
  static final PedidoService instance = PedidoService._();
  PedidoService._();

  final _api = ApiClient.instance;

  // CU24: Consultar mis pedidos (Cliente)
  Future<List<dynamic>> getMisPedidos() async {
    final res = await _api.get('/pedidos/mis-pedidos');
    return (res as List<dynamic>?) ?? [];
  }

  // CU23: Enviar pedido (Cliente)
  Future<Map<String, dynamic>> crearPedido(Map<String, dynamic> data) async {
    final res = await _api.post('/pedidos', data);
    return res as Map<String, dynamic>;
  }

  // CU24: Detalle de pedido
  Future<Map<String, dynamic>> getDetallePedido(int idPedido) async {
    final res = await _api.get('/pedidos/$idPedido');
    return res as Map<String, dynamic>;
  }

  // CU24: Cancelar pedido como cliente (sólo PENDIENTE)
  Future<Map<String, dynamic>> cancelarPedido(int idPedido) async {
    final res = await _api.patch('/pedidos/$idPedido/cancelar', {});
    return (res is Map<String, dynamic>) ? res : {'mensaje': 'Pedido cancelado'};
  }
}
