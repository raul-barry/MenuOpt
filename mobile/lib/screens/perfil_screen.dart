import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../core/api_client.dart';
import '../services/usuario_service.dart';

class PerfilScreen extends StatefulWidget {
  const PerfilScreen({super.key});

  @override
  State<PerfilScreen> createState() => _PerfilScreenState();
}

class _PerfilScreenState extends State<PerfilScreen> {
  final _nombresCtrl = TextEditingController();
  final _apellidosCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();
  final _correoCtrl = TextEditingController();

  final _passActualCtrl = TextEditingController();
  final _passNuevaCtrl = TextEditingController();
  final _passConfirmCtrl = TextEditingController();

  bool _isLoading = true;
  bool _isSavingPerfil = false;
  bool _isSavingPass = false;

  String? _perfilSuccess;
  String? _perfilError;
  String? _passSuccess;
  String? _passError;

  Map<String, dynamic>? _perfilData;

  @override
  void initState() {
    super.initState();
    _loadPerfil();
  }

  @override
  void dispose() {
    _nombresCtrl.dispose();
    _apellidosCtrl.dispose();
    _telefonoCtrl.dispose();
    _correoCtrl.dispose();
    _passActualCtrl.dispose();
    _passNuevaCtrl.dispose();
    _passConfirmCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadPerfil() async {
    setState(() {
      _isLoading = true;
      _perfilError = null;
    });

    try {
      final user = await UsuarioService.instance.getPerfil();
      if (mounted) {
        setState(() {
          _perfilData = user;
          _nombresCtrl.text = user['nombres'] ?? '';
          _apellidosCtrl.text = user['apellidos'] ?? '';
          _telefonoCtrl.text = user['telefono'] ?? '';
          _correoCtrl.text = user['correo'] ?? '';
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _perfilError = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _actualizarPerfil() async {
    final nom = _nombresCtrl.text.trim();
    final ape = _apellidosCtrl.text.trim();
    final tel = _telefonoCtrl.text.trim();

    if (nom.isEmpty || ape.isEmpty) {
      setState(() => _perfilError = 'Nombres y apellidos son requeridos.');
      return;
    }

    setState(() {
      _isSavingPerfil = true;
      _perfilError = null;
      _perfilSuccess = null;
    });

    try {
      await UsuarioService.instance.actualizarPerfil(
        nombres: nom,
        apellidos: ape,
        telefono: tel,
      );
      if (!mounted) return;
      setState(() {
        _isSavingPerfil = false;
        _perfilSuccess = 'Datos personales actualizados correctamente.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Perfil actualizado con éxito'), backgroundColor: AppTheme.success),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isSavingPerfil = false;
        _perfilError = e.toString();
      });
    }
  }

  Future<void> _cambiarContrasena() async {
    final actual = _passActualCtrl.text;
    final nueva = _passNuevaCtrl.text;
    final conf = _passConfirmCtrl.text;

    if (actual.isEmpty || nueva.isEmpty || conf.isEmpty) {
      setState(() => _passError = 'Todos los campos de contraseña son requeridos.');
      return;
    }

    if (nueva != conf) {
      setState(() => _passError = 'La nueva contraseña y su confirmación no coinciden.');
      return;
    }

    if (nueva.length < 6) {
      setState(() => _passError = 'La nueva contraseña debe tener al menos 6 caracteres.');
      return;
    }

    setState(() {
      _isSavingPass = true;
      _passError = null;
      _passSuccess = null;
    });

    try {
      await UsuarioService.instance.cambiarContrasena(
        contrasenaActual: actual,
        nuevaContrasena: nueva,
      );
      if (!mounted) return;
      _passActualCtrl.clear();
      _passNuevaCtrl.clear();
      _passConfirmCtrl.clear();
      setState(() {
        _isSavingPass = false;
        _passSuccess = 'Contraseña actualizada correctamente.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Contraseña modificada con éxito'), backgroundColor: AppTheme.success),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isSavingPass = false;
        _passError = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: AppTheme.background,
        body: Center(child: CircularProgressIndicator(color: AppTheme.primary)),
      );
    }

    final user = _perfilData ?? ApiClient.instance.currentUser ?? {};
    final idUsuario = user['id_usuario'] ?? 'N/A';
    final rol = user['rol']?['nombre'] ?? 'CLIENTE';
    final estado = user['estado'] ?? 'ACTIVO';
    final fechaReg = user['fecha_registro'] ?? '';

    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Mi Perfil',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Gestiona tu información personal y credenciales de acceso.',
                  style: TextStyle(fontSize: 12.5, color: AppTheme.textMuted),
                ),
                const SizedBox(height: 18),

                // Tarjeta 1: Información de Cuenta
                Container(
                  decoration: AppTheme.cardDecoration,
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Información de Cuenta', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                          AppTheme.buildBadge(estado),
                        ],
                      ),
                      const Divider(height: 20),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('ID DE USUARIO', style: TextStyle(fontSize: 11, color: AppTheme.textMuted, fontWeight: FontWeight.w600)),
                                const SizedBox(height: 2),
                                Text('#$idUsuario', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                              ],
                            ),
                          ),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('ROL ASIGNADO', style: TextStyle(fontSize: 11, color: AppTheme.textMuted, fontWeight: FontWeight.w600)),
                                const SizedBox(height: 2),
                                Text(rol, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.primary)),
                              ],
                            ),
                          ),
                        ],
                      ),
                      if (fechaReg.toString().isNotEmpty) ...[
                        const SizedBox(height: 12),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('FECHA DE REGISTRO', style: TextStyle(fontSize: 11, color: AppTheme.textMuted, fontWeight: FontWeight.w600)),
                            const SizedBox(height: 2),
                            Text(fechaReg.toString().split('T').first, style: const TextStyle(fontSize: 13)),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Tarjeta 2: Editar Datos Personales
                Container(
                  decoration: AppTheme.cardDecoration,
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text('Editar Datos Personales', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 14),

                      if (_perfilSuccess != null)
                        Container(
                          padding: const EdgeInsets.all(10),
                          margin: const EdgeInsets.only(bottom: 12),
                          decoration: BoxDecoration(color: AppTheme.successLight, borderRadius: BorderRadius.circular(8)),
                          child: Text(_perfilSuccess!, style: const TextStyle(color: AppTheme.success, fontSize: 12)),
                        ),
                      if (_perfilError != null)
                        Container(
                          padding: const EdgeInsets.all(10),
                          margin: const EdgeInsets.only(bottom: 12),
                          decoration: BoxDecoration(color: AppTheme.dangerLight, borderRadius: BorderRadius.circular(8)),
                          child: Text(_perfilError!, style: const TextStyle(color: AppTheme.danger, fontSize: 12)),
                        ),

                      TextField(
                        controller: _nombresCtrl,
                        decoration: const InputDecoration(labelText: 'Nombres *'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _apellidosCtrl,
                        decoration: const InputDecoration(labelText: 'Apellidos *'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _correoCtrl,
                        enabled: false,
                        decoration: const InputDecoration(labelText: 'Correo Electrónico (No modificable)'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _telefonoCtrl,
                        keyboardType: TextInputType.phone,
                        decoration: const InputDecoration(labelText: 'Teléfono'),
                      ),
                      const SizedBox(height: 18),
                      ElevatedButton(
                        onPressed: _isSavingPerfil ? null : _actualizarPerfil,
                        child: Text(_isSavingPerfil ? 'Guardando...' : 'Actualizar Perfil'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Tarjeta 3: Seguridad / Cambiar Contraseña
                Container(
                  decoration: AppTheme.cardDecoration,
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text('Seguridad: Cambiar Contraseña', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 14),

                      if (_passSuccess != null)
                        Container(
                          padding: const EdgeInsets.all(10),
                          margin: const EdgeInsets.only(bottom: 12),
                          decoration: BoxDecoration(color: AppTheme.successLight, borderRadius: BorderRadius.circular(8)),
                          child: Text(_passSuccess!, style: const TextStyle(color: AppTheme.success, fontSize: 12)),
                        ),
                      if (_passError != null)
                        Container(
                          padding: const EdgeInsets.all(10),
                          margin: const EdgeInsets.only(bottom: 12),
                          decoration: BoxDecoration(color: AppTheme.dangerLight, borderRadius: BorderRadius.circular(8)),
                          child: Text(_passError!, style: const TextStyle(color: AppTheme.danger, fontSize: 12)),
                        ),

                      TextField(
                        controller: _passActualCtrl,
                        obscureText: true,
                        decoration: const InputDecoration(labelText: 'Contraseña Actual *'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _passNuevaCtrl,
                        obscureText: true,
                        decoration: const InputDecoration(labelText: 'Nueva Contraseña *'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _passConfirmCtrl,
                        obscureText: true,
                        decoration: const InputDecoration(labelText: 'Confirmar Nueva Contraseña *'),
                      ),
                      const SizedBox(height: 18),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: AppTheme.secondary),
                        onPressed: _isSavingPass ? null : _cambiarContrasena,
                        child: Text(_isSavingPass ? 'Modificando...' : 'Cambiar Contraseña'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
