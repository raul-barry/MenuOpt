import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class ApiClient {
  static final ApiClient instance = ApiClient._();
  ApiClient._();

  // Configuración de URL base en tiempo de compilación (--dart-define=API_BASE_URL=https://...)
  // Compatible con API_BASE_URL (estándar de la skill) y BASE_URL (legacy)
  static const String _envApiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
  static const String _envBaseUrl = String.fromEnvironment('BASE_URL', defaultValue: '');
  static final String _compileTimeBaseUrl = _envApiBaseUrl.isNotEmpty ? _envApiBaseUrl : _envBaseUrl;

  // Si se pasa una URL explícita por --dart-define, se usa exclusivamente para evitar retardos
  // intentando IPs LAN privadas cuando el móvil está con datos o en otra red Wi-Fi.
  static final List<String> _candidateUrls = _compileTimeBaseUrl.isNotEmpty
      ? [_compileTimeBaseUrl]
      : [
          'http://192.168.0.4:8000', // IP activa de red local Wi-Fi de la PC
          'http://10.0.2.2:8000',     // Emulador Android estándar
          'http://localhost:8000',    // Web / Windows desktop
          'http://127.0.0.1:8000',
        ];

  String baseUrl = _candidateUrls.first;
  bool _hostLocked = false;

  String? token;
  Map<String, dynamic>? currentUser;

  bool get isAuthenticated => token != null && token!.isNotEmpty;
  String get userRole => currentUser?['rol']?['nombre'] ?? '';
  String get userName {
    final n = currentUser?['nombres'] ?? '';
    final a = currentUser?['apellidos'] ?? '';
    final full = '$n $a'.trim();
    return full.isNotEmpty ? full : (currentUser?['correo'] ?? 'Usuario');
  }
  String get userEmail => currentUser?['correo'] ?? '';

  void setSession({required String token, required Map<String, dynamic> user}) {
    this.token = token;
    currentUser = user;
  }

  void clearSession() {
    token = null;
    currentUser = null;
  }

  Map<String, String> _headers([Map<String, String>? extra]) {
    final map = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (token != null && token!.isNotEmpty) {
      map['Authorization'] = 'Bearer $token';
    }
    if (extra != null) {
      map.addAll(extra);
    }
    return map;
  }

  Uri _resolveUri(String base, String path) {
    final cleanBase = base.endsWith('/') ? base.substring(0, base.length - 1) : base;
    final cleanPath = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$cleanBase$cleanPath');
  }

  // Ejecuta la petición con intento de conmutación por error automática transparente si no conecta
  Future<http.Response> _executeWithFallback(
    Future<http.Response> Function(String candidate) requestFn,
  ) async {
    if (_hostLocked) {
      return await requestFn(baseUrl);
    }

    final tried = <String>[];
    for (final candidate in _candidateUrls) {
      tried.add(candidate);
      try {
        final res = await requestFn(candidate);
        // Si responde cualquier código HTTP (200, 401, 404, etc.), el servidor existe y responde
        baseUrl = candidate;
        _hostLocked = true;
        return res;
      } catch (e) {
        // Falló la conexión con este candidato, probar el siguiente
        continue;
      }
    }

    throw ApiException(
      'No se pudo conectar con el backend de MenuOpt (intentado en: ${tried.join(', ')}). Verifique su conexión a Internet o que el túnel/servidor esté activo.',
    );
  }

  Future<dynamic> get(String path) async {
    try {
      final res = await _executeWithFallback((base) {
        return http
            .get(_resolveUri(base, path), headers: _headers())
            .timeout(const Duration(seconds: 10));
      });
      return _handleResponse(res);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Error de conexión: $e');
    }
  }

  Future<dynamic> post(String path, [dynamic body]) async {
    try {
      final res = await _executeWithFallback((base) {
        return http
            .post(
              _resolveUri(base, path),
              headers: _headers(),
              body: body != null ? jsonEncode(body) : null,
            )
            .timeout(const Duration(seconds: 25));
      });
      return _handleResponse(res);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Error de conexión: $e');
    }
  }

  Future<dynamic> put(String path, [dynamic body]) async {
    try {
      final res = await _executeWithFallback((base) {
        return http
            .put(
              _resolveUri(base, path),
              headers: _headers(),
              body: body != null ? jsonEncode(body) : null,
            )
            .timeout(const Duration(seconds: 15));
      });
      return _handleResponse(res);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Error de conexión: $e');
    }
  }

  Future<dynamic> patch(String path, [dynamic body]) async {
    try {
      final res = await _executeWithFallback((base) {
        return http
            .patch(
              _resolveUri(base, path),
              headers: _headers(),
              body: body != null ? jsonEncode(body) : null,
            )
            .timeout(const Duration(seconds: 15));
      });
      return _handleResponse(res);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Error de conexión: $e');
    }
  }

  Future<dynamic> delete(String path) async {
    try {
      final res = await _executeWithFallback((base) {
        return http
            .delete(_resolveUri(base, path), headers: _headers())
            .timeout(const Duration(seconds: 15));
      });
      return _handleResponse(res);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Error de conexión: $e');
    }
  }

  dynamic _handleResponse(http.Response res) {
    if (res.statusCode == 204) {
      return null;
    }
    dynamic decoded;
    try {
      decoded = res.body.isNotEmpty ? jsonDecode(utf8.decode(res.bodyBytes)) : null;
    } catch (_) {
      decoded = res.body;
    }

    if (res.statusCode >= 200 && res.statusCode < 300) {
      return decoded;
    }

    String errorMsg = 'Error en el servidor (${res.statusCode})';
    if (decoded is Map<String, dynamic>) {
      if (decoded['detail'] != null) {
        if (decoded['detail'] is List) {
          final errs = (decoded['detail'] as List).map((e) {
            if (e is Map && e['msg'] != null) {
              final loc = e['loc'] is List ? (e['loc'] as List).where((p) => p != 'query' && p != 'body').join('.') : '';
              return loc.isNotEmpty ? '$loc: ${e['msg']}' : '${e['msg']}';
            }
            return e.toString();
          }).join('\n');
          errorMsg = errs.isNotEmpty ? errs : decoded['detail'].toString();
        } else {
          errorMsg = decoded['detail'].toString();
        }
      } else if (decoded['message'] != null) {
        errorMsg = decoded['message'].toString();
      }
    }
    throw ApiException(errorMsg, res.statusCode);
  }
}
