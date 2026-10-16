import '../core/api_client.dart';

class AuthService {
  static final AuthService instance = AuthService._();
  AuthService._();

  final _api = ApiClient.instance;

  Future<Map<String, dynamic>> login(String correo, String contrasena) async {
    final response = await _api.post('/autenticacion/login', {
      'correo': correo.trim().toLowerCase(),
      'contrasena': contrasena,
    });

    final token = response['access_token'] as String;
    final usuario = response['usuario'] as Map<String, dynamic>;
    _api.setSession(token: token, user: usuario);
    return usuario;
  }

  Future<void> logout() async {
    _api.clearSession();
  }

  Future<Map<String, dynamic>> registro({
    required String nombres,
    required String apellidos,
    required String correo,
    required String contrasena,
    String? telefono,
  }) async {
    final payload = <String, dynamic>{
      'nombres': nombres.trim(),
      'apellidos': apellidos.trim(),
      'correo': correo.trim().toLowerCase(),
      'contrasena': contrasena,
      if (telefono != null && telefono.trim().isNotEmpty)
        'telefono': telefono.trim(),
    };
    final response = await _api.post('/autenticacion/registro', payload);
    return response as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getPerfil() async {
    final res = await _api.get('/usuarios/perfil');
    return res as Map<String, dynamic>;
  }
}
