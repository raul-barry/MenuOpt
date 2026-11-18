import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/preferencia_service.dart';

class PreferenciasScreen extends StatefulWidget {
  const PreferenciasScreen({super.key});

  @override
  State<PreferenciasScreen> createState() => _PreferenciasScreenState();
}

class _PreferenciasScreenState extends State<PreferenciasScreen> {
  bool _isLoading = true;
  bool _isSaving = false;
  List<dynamic> _catalogo = [];
  final Set<int> _seleccionadas = {};
  String? _error;
  String? _success;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final catalogo = await PreferenciaService.instance.listarPreferencias();
      Set<int> userIds = {};
      try {
        final userPref = await PreferenciaService.instance.obtenerPreferenciasUsuario();
        for (final p in userPref) {
          if (p is Map && p['id_preferencia'] != null) {
            userIds.add(AppTheme.toInt(p['id_preferencia']));
          }
        }
      } catch (_) {}

      if (mounted) {
        setState(() {
          _catalogo = catalogo;
          _seleccionadas.clear();
          _seleccionadas.addAll(userIds);
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  void _togglePreferencia(int id) {
    setState(() {
      if (_seleccionadas.contains(id)) {
        _seleccionadas.remove(id);
      } else {
        _seleccionadas.add(id);
      }
    });
  }

  Future<void> _guardar() async {
    setState(() {
      _isSaving = true;
      _error = null;
      _success = null;
    });

    try {
      await PreferenciaService.instance.guardarPreferenciasUsuario(_seleccionadas.toList());
      if (!mounted) return;
      setState(() {
        _isSaving = false;
        _success = 'Tus preferencias han sido guardadas y actualizadas con éxito.';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preferencias guardadas con éxito'), backgroundColor: AppTheme.success),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isSaving = false;
        _error = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
            : RefreshIndicator(
                onRefresh: _loadData,
                color: AppTheme.primary,
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Header
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Mis Preferencias Gastronómicas',
                                  style: TextStyle(fontSize: 19, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  'Selecciona tus dietas, restricciones y gustos culinarios habituales para personalizar tus recomendaciones.',
                                  style: TextStyle(fontSize: 12.5, color: AppTheme.textMuted),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppTheme.primaryLight,
                              borderRadius: BorderRadius.circular(999),
                              border: Border.all(color: AppTheme.primary),
                            ),
                            child: Text(
                              '${_seleccionadas.length} seleccionada(s)',
                              style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 11),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Alertas
                      if (_success != null)
                        Container(
                          padding: const EdgeInsets.all(12),
                          margin: const EdgeInsets.only(bottom: 14),
                          decoration: BoxDecoration(
                            color: AppTheme.successLight,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFFC9EAD8)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.check_circle_outline, color: AppTheme.success, size: 20),
                              const SizedBox(width: 8),
                              Expanded(child: Text(_success!, style: const TextStyle(color: AppTheme.success, fontSize: 13))),
                            ],
                          ),
                        ),

                      if (_error != null)
                        Container(
                          padding: const EdgeInsets.all(12),
                          margin: const EdgeInsets.only(bottom: 14),
                          decoration: BoxDecoration(
                            color: AppTheme.dangerLight,
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFFFFD1CE)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.error_outline, color: AppTheme.danger, size: 20),
                              const SizedBox(width: 8),
                              Expanded(child: Text(_error!, style: const TextStyle(color: AppTheme.danger, fontSize: 13))),
                            ],
                          ),
                        ),

                      // Botón superior de guardar
                      ElevatedButton.icon(
                        onPressed: _isSaving ? null : _guardar,
                        icon: _isSaving
                            ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                            : const Icon(Icons.save_outlined, size: 18),
                        label: Text(_isSaving ? 'Guardando...' : 'Guardar Preferencias'),
                      ),
                      const SizedBox(height: 16),

                      // Grid o Lista de preferencias
                      if (_catalogo.isEmpty)
                        const Center(
                          child: Padding(
                            padding: EdgeInsets.all(32),
                            child: Text('No hay preferencias en el catálogo.'),
                          ),
                        )
                      else
                        ..._catalogo.map((p) {
                          final id = AppTheme.toInt(p['id_preferencia']);
                          final nombre = p['nombre'] ?? '';
                          final categoria = p['categoria'] ?? 'DIETA';
                          final descripcion = p['descripcion'] ?? '';
                          final isSelected = _seleccionadas.contains(id);

                          return Container(
                            margin: const EdgeInsets.only(bottom: 10),
                            decoration: BoxDecoration(
                              color: isSelected ? AppTheme.primaryLight.withValues(alpha: 0.3) : AppTheme.surface,
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: isSelected ? AppTheme.primary : AppTheme.border,
                                width: isSelected ? 1.5 : 1,
                              ),
                            ),
                            child: InkWell(
                              onTap: () => _togglePreferencia(id),
                              borderRadius: BorderRadius.circular(12),
                              child: Padding(
                                padding: const EdgeInsets.all(14),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Checkbox(
                                      value: isSelected,
                                      activeColor: AppTheme.primary,
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                      onChanged: (_) => _togglePreferencia(id),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            crossAxisAlignment: CrossAxisAlignment.center,
                                            children: [
                                              Expanded(
                                                child: Text(
                                                  nombre,
                                                  style: TextStyle(
                                                    fontSize: 15,
                                                    fontWeight: FontWeight.bold,
                                                    color: isSelected ? AppTheme.primary : AppTheme.textMain,
                                                  ),
                                                  overflow: TextOverflow.ellipsis,
                                                  maxLines: 2,
                                                ),
                                              ),
                                              const SizedBox(width: 8),
                                              AppTheme.buildBadge(categoria),
                                            ],
                                          ),
                                          if (descripcion.isNotEmpty) ...[
                                            const SizedBox(height: 4),
                                            Text(
                                              descripcion,
                                              style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                            ),
                                          ],
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        }),
                      const SizedBox(height: 20),

                      // Botón inferior de guardar
                      ElevatedButton.icon(
                        onPressed: _isSaving ? null : _guardar,
                        icon: _isSaving
                            ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                            : const Icon(Icons.save_outlined, size: 18),
                        label: Text(_isSaving ? 'Guardando...' : 'Guardar Preferencias'),
                      ),
                    ],
                  ),
                ),
              ),
      ),
    );
  }
}
