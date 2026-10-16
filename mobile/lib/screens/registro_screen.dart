import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/auth_service.dart';

class RegistroScreen extends StatefulWidget {
  const RegistroScreen({super.key});

  @override
  State<RegistroScreen> createState() => _RegistroScreenState();
}

class _RegistroScreenState extends State<RegistroScreen> {
  final _formKey = GlobalKey<FormState>();

  final _nombresCtrl = TextEditingController();
  final _apellidosCtrl = TextEditingController();
  final _correoCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _confirmPassCtrl = TextEditingController();

  bool _obscurePass = true;
  bool _obscureConfirmPass = true;
  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _nombresCtrl.dispose();
    _apellidosCtrl.dispose();
    _correoCtrl.dispose();
    _telefonoCtrl.dispose();
    _passCtrl.dispose();
    _confirmPassCtrl.dispose();
    super.dispose();
  }

  Future<void> _submitRegistro() async {
    setState(() {
      _errorMessage = null;
      _successMessage = null;
    });

    final nombres = _nombresCtrl.text.trim();
    final apellidos = _apellidosCtrl.text.trim();
    final correo = _correoCtrl.text.trim().toLowerCase();
    final telefono = _telefonoCtrl.text.trim();
    final contrasena = _passCtrl.text;
    final confirmarContrasena = _confirmPassCtrl.text;

    // Validaciones del formulario
    if (nombres.isEmpty || apellidos.isEmpty || correo.isEmpty || contrasena.isEmpty || confirmarContrasena.isEmpty) {
      setState(() => _errorMessage = 'Por favor complete todos los campos obligatorios (*).');
      return;
    }

    if (nombres.length < 2) {
      setState(() => _errorMessage = 'Los nombres deben tener al menos 2 caracteres.');
      return;
    }

    if (apellidos.length < 2) {
      setState(() => _errorMessage = 'Los apellidos deben tener al menos 2 caracteres.');
      return;
    }

    final emailRegExp = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegExp.hasMatch(correo)) {
      setState(() => _errorMessage = 'Ingrese un correo electrónico válido.');
      return;
    }

    if (contrasena.length < 8) {
      setState(() => _errorMessage = 'La contraseña debe tener al menos 8 caracteres.');
      return;
    }

    if (contrasena != confirmarContrasena) {
      setState(() => _errorMessage = 'Las contraseñas no coinciden.');
      return;
    }

    setState(() => _isLoading = true);

    try {
      await AuthService.instance.registro(
        nombres: nombres,
        apellidos: apellidos,
        correo: correo,
        contrasena: contrasena,
        telefono: telefono.isNotEmpty ? telefono : null,
      );

      if (!mounted) return;
      setState(() {
        _successMessage = '¡Registro completado exitosamente! Redirigiendo al inicio de sesión...';
      });

      await Future.delayed(const Duration(milliseconds: 1500));
      if (!mounted) return;
      Navigator.of(context).pop(correo);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppTheme.textMain),
          onPressed: () => Navigator.of(context).pop(),
          tooltip: 'Volver al login',
        ),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo de la marca
                  Center(child: AppTheme.buildBrandLogo(fontSize: 34)),
                  const SizedBox(height: 8),
                  const Text(
                    'Planificación Gastronómica Inteligente',
                    style: TextStyle(
                      fontSize: 13,
                      color: AppTheme.textMuted,
                      fontWeight: FontWeight.w500,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),

                  // Tarjeta Principal de Registro
                  Container(
                    decoration: AppTheme.cardDecoration,
                    padding: const EdgeInsets.all(24),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'Crear Cuenta de Cliente',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.textMain,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 6),
                          const Text(
                            'Regístrate para planificar tus comidas y descubrir recomendaciones',
                            style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 20),

                          // Mensaje de Error
                          if (_errorMessage != null)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                              margin: const EdgeInsets.only(bottom: 16),
                              decoration: BoxDecoration(
                                color: AppTheme.dangerLight,
                                border: Border.all(color: const Color(0xFFFFD1CE)),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Icon(Icons.error_outline, color: AppTheme.danger, size: 20),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Text(
                                      _errorMessage!,
                                      style: const TextStyle(color: AppTheme.danger, fontSize: 13),
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          // Mensaje de Éxito
                          if (_successMessage != null)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                              margin: const EdgeInsets.only(bottom: 16),
                              decoration: BoxDecoration(
                                color: AppTheme.successLight,
                                border: Border.all(color: const Color(0xFFB7E4C7)),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Icon(Icons.check_circle_outline, color: AppTheme.success, size: 20),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Text(
                                      _successMessage!,
                                      style: const TextStyle(color: AppTheme.success, fontSize: 13),
                                    ),
                                  ),
                                ],
                              ),
                            ),

                          // Nombres
                          const Text(
                            'Nombres *',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _nombresCtrl,
                            textCapitalization: TextCapitalization.words,
                            decoration: const InputDecoration(
                              hintText: 'Ej. Juan',
                              prefixIcon: Icon(Icons.person_outline, size: 20, color: AppTheme.textMuted),
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Apellidos
                          const Text(
                            'Apellidos *',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _apellidosCtrl,
                            textCapitalization: TextCapitalization.words,
                            decoration: const InputDecoration(
                              hintText: 'Ej. Pérez',
                              prefixIcon: Icon(Icons.person_outline, size: 20, color: AppTheme.textMuted),
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Correo Electrónico
                          const Text(
                            'Correo Electrónico *',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _correoCtrl,
                            keyboardType: TextInputType.emailAddress,
                            decoration: const InputDecoration(
                              hintText: 'juan@example.com',
                              prefixIcon: Icon(Icons.email_outlined, size: 20, color: AppTheme.textMuted),
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Teléfono
                          const Text(
                            'Teléfono (Opcional)',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _telefonoCtrl,
                            keyboardType: TextInputType.phone,
                            decoration: const InputDecoration(
                              hintText: '71234567',
                              prefixIcon: Icon(Icons.phone_outlined, size: 20, color: AppTheme.textMuted),
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Contraseña
                          const Text(
                            'Contraseña (Mínimo 8 caracteres) *',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _passCtrl,
                            obscureText: _obscurePass,
                            decoration: InputDecoration(
                              hintText: '••••••••',
                              prefixIcon: const Icon(Icons.lock_outline, size: 20, color: AppTheme.textMuted),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscurePass ? Icons.visibility_off : Icons.visibility,
                                  size: 20,
                                  color: AppTheme.textMuted,
                                ),
                                onPressed: () => setState(() => _obscurePass = !_obscurePass),
                              ),
                            ),
                          ),
                          const SizedBox(height: 14),

                          // Confirmar Contraseña
                          const Text(
                            'Confirmar Contraseña *',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _confirmPassCtrl,
                            obscureText: _obscureConfirmPass,
                            decoration: InputDecoration(
                              hintText: '••••••••',
                              prefixIcon: const Icon(Icons.lock_reset, size: 20, color: AppTheme.textMuted),
                              suffixIcon: IconButton(
                                icon: Icon(
                                  _obscureConfirmPass ? Icons.visibility_off : Icons.visibility,
                                  size: 20,
                                  color: AppTheme.textMuted,
                                ),
                                onPressed: () => setState(() => _obscureConfirmPass = !_obscureConfirmPass),
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),

                          // Botón de Enviar
                          ElevatedButton(
                            onPressed: _isLoading ? null : _submitRegistro,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppTheme.primary,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                            child: _isLoading
                                ? const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                  )
                                : const Text(
                                    'Crear Cuenta',
                                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                                  ),
                          ),

                          const SizedBox(height: 20),

                          // Enlace hacia Login
                          Wrap(
                            alignment: WrapAlignment.center,
                            crossAxisAlignment: WrapCrossAlignment.center,
                            children: [
                              const Text(
                                '¿Ya tienes cuenta? ',
                                style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
                              ),
                              GestureDetector(
                                onTap: () => Navigator.of(context).pop(),
                                child: const Text(
                                  'Inicia Sesión',
                                  style: TextStyle(
                                    fontSize: 13,
                                    fontWeight: FontWeight.bold,
                                    color: AppTheme.primary,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
