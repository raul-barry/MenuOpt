import '../core/api_client.dart';

class UsuarioService {
  static final UsuarioService instance = UsuarioService._();
  UsuarioService._();

  final _api = ApiClient.instance;

  // CU03: Obtener perfil
  Future<Map<String, dynamic>> getPerfil() async {
    final res = await _api.get('/usuarios/perfil');
    return res as Map<String, dynamic>;
  }

  // CU03: Actualizar perfil (nombres, apellidos, telefono)
  Future<Map<String, dynamic>> actualizarPerfil({
    required String nombres,
    required String apellidos,
    String? telefono,
  }) async {
    final res = await _api.put('/usuarios/perfil', {
      'nombres': nombres.trim(),
      'apellidos': apellidos.trim(),
      if (telefono != null) 'telefono': telefono.trim(),
    });
    // Actualizar usuario en sesión
    if (res is Map<String, dynamic>) {
      _api.currentUser = res;
    }
    return res as Map<String, dynamic>;
  }

  // CU03: Cambiar contraseña
  Future<Map<String, dynamic>> cambiarContrasena({
    required String contrasenaActual,
    required String nuevaContrasena,
  }) async {
    final res = await _api.put('/usuarios/perfil/contrasena', {
      'contrasena_actual': contrasenaActual,
      'nueva_contrasena': nuevaContrasena,
    });
    return (res is Map<String, dynamic>) ? res : {'mensaje': 'Contraseña actualizada'};
  }
}
