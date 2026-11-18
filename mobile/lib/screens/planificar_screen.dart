import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/planificacion_service.dart';
import '../services/preferencia_service.dart';

class PlanificarScreen extends StatefulWidget {
  final VoidCallback? onPlanCreated;

  const PlanificarScreen({super.key, this.onPlanCreated});

  @override
  State<PlanificarScreen> createState() => _PlanificarScreenState();
}

class _PlanificarScreenState extends State<PlanificarScreen> {
  final _formKey = GlobalKey<FormState>();
  final _presupuestoCtrl = TextEditingController(text: '300.00');
  final _comensalesCtrl = TextEditingController(text: '20');
  final _ubicacionCtrl = TextEditingController(text: 'Equipetrol');
  String _tipoComida = 'ALMUERZO';

  final List<Map<String, String>> _tiposComida = [
    {'valor': 'DESAYUNO', 'etiqueta': 'Desayuno'},
    {'valor': 'ALMUERZO', 'etiqueta': 'Almuerzo'},
    {'valor': 'CENA', 'etiqueta': 'Cena'},
    {'valor': 'REFRIGERIO', 'etiqueta': 'Refrigerio'},
  ];

  List<dynamic> _catalogoPreferencias = [];
  final Set<int> _preferenciasSeleccionadas = {};
  bool _isLoadingPrefs = true;
  bool _isSaving = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void initState() {
    super.initState();
    _loadPreferencias();
  }

  @override
  void dispose() {
    _presupuestoCtrl.dispose();
    _comensalesCtrl.dispose();
    _ubicacionCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadPreferencias() async {
    try {
      final list = await PreferenciaService.instance.listarPreferencias();
      // Intentar cargar las preferencias guardadas del usuario para pre-seleccionarlas
      Set<int> userPrefIds = {};
      try {
        final userPref = await PreferenciaService.instance.obtenerPreferenciasUsuario();
        for (final p in userPref) {
          if (p is Map && p['id_preferencia'] != null) {
            userPrefIds.add(AppTheme.toInt(p['id_preferencia']));
          }
        }
      } catch (_) {}

      if (mounted) {
        setState(() {
          _catalogoPreferencias = list;
          _preferenciasSeleccionadas.addAll(userPrefIds);
          _isLoadingPrefs = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoadingPrefs = false;
        });
      }
    }
  }

  void _togglePreferencia(int id) {
    setState(() {
      if (_preferenciasSeleccionadas.contains(id)) {
        _preferenciasSeleccionadas.remove(id);
      } else {
        _preferenciasSeleccionadas.add(id);
      }
    });
  }

  Future<void> _submitPlanificacion() async {
    if (!_formKey.currentState!.validate()) return;

    final presupuesto = double.tryParse(_presupuestoCtrl.text.trim()) ?? 0;
    final comensales = int.tryParse(_comensalesCtrl.text.trim()) ?? 1;
    final ubicacion = _ubicacionCtrl.text.trim();

    setState(() {
      _isSaving = true;
      _errorMessage = null;
      _successMessage = null;
    });

    try {
      final plan = await PlanificacionService.instance.crearPlanificacion(
        presupuesto: presupuesto,
        cantidadPersonas: comensales,
        tipoComida: _tipoComida,
        ubicacionReferencia: ubicacion,
        preferencias: _preferenciasSeleccionadas.toList(),
      );

      final idPlan = plan['id_planificacion'];

      if (!mounted) return;
      setState(() {
        _isSaving = false;
        _successMessage = '¡Planificación #$idPlan registrada con éxito!';
      });

      // Diálogo de confirmación con opción de calcular recomendaciones
      _showCreatedDialog(idPlan, plan);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isSaving = false;
        _errorMessage = e.toString();
      });
    }
  }

  void _showCreatedDialog(int idPlan, Map<String, dynamic> plan) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(color: AppTheme.successLight, shape: BoxShape.circle),
              child: const Icon(Icons.check, color: AppTheme.success, size: 22),
            ),
            const SizedBox(width: 10),
            const Text('Planificación Creada', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Se registró exitosamente la planificación #$idPlan.'),
            const SizedBox(height: 8),
            Text(
              '${plan['tipo_comida']} para ${plan['cantidad_personas']} comensales • Bs ${plan['presupuesto']}',
              style: const TextStyle(fontWeight: FontWeight.w600, color: AppTheme.textMain),
            ),
            const SizedBox(height: 12),
            const Text(
              '¿Deseas calcular las recomendaciones óptimas de restaurantes y preparación casera ahora?',
              style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              widget.onPlanCreated?.call();
            },
            child: const Text('Ver Después'),
          ),
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.primary,
              foregroundColor: Colors.white,
            ),
            icon: const Icon(Icons.bolt, size: 18),
            label: const Text('Calcular Recomendaciones'),
            onPressed: () async {
              Navigator.pop(ctx);
              _generarRecomendaciones(idPlan);
            },
          ),
        ],
      ),
    );
  }

  Future<void> _generarRecomendaciones(int idPlan) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator(color: AppTheme.primary)),
    );

    try {
      final recs = await PlanificacionService.instance.generarRecomendaciones(idPlan);
      if (!mounted) return;
      Navigator.pop(context); // cerrar loader

      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
        builder: (ctx) => _RecomendacionesSheet(idPlan: idPlan, recomendaciones: recs),
      );
    } catch (e) {
      if (!mounted) return;
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al calcular recomendaciones: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Título y Subtítulo exactos de la versión Web
                const Text(
                  'Registrar Planificación Gastronómica',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textMain,
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Indica los parámetros de tu comida o evento. El motor de recomendaciones calculará opciones de restaurantes adaptadas a tu presupuesto.',
                  style: TextStyle(
                    fontSize: 13,
                    color: AppTheme.textMuted,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 20),

                // Alertas de Éxito o Error
                if (_successMessage != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppTheme.successLight,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFC9EAD8)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.check_circle_outline, color: AppTheme.success, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(_successMessage!, style: const TextStyle(color: AppTheme.success, fontSize: 13)),
                        ),
                      ],
                    ),
                  ),

                if (_errorMessage != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppTheme.dangerLight,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFFFD1CE)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: AppTheme.danger, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(_errorMessage!, style: const TextStyle(color: AppTheme.danger, fontSize: 13)),
                        ),
                      ],
                    ),
                  ),

                // Tarjeta de Formulario
                Container(
                  decoration: AppTheme.cardDecoration,
                  padding: const EdgeInsets.all(20),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Presupuesto y Comensales
                        LayoutBuilder(
                          builder: (ctx, constraints) {
                            final isNarrow = constraints.maxWidth < 450;
                            final presWidget = Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Presupuesto Disponible (Bs) *',
                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                                ),
                                const SizedBox(height: 6),
                                TextFormField(
                                  controller: _presupuestoCtrl,
                                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                  decoration: const InputDecoration(
                                    hintText: 'Ej. 300.00',
                                    prefixText: 'Bs  ',
                                    prefixStyle: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textMuted),
                                  ),
                                  validator: (val) {
                                    if (val == null || val.trim().isEmpty) return 'El presupuesto es obligatorio.';
                                    final d = double.tryParse(val);
                                    if (d == null || d <= 0) return 'Debe ser mayor a 0 Bs.';
                                    return null;
                                  },
                                ),
                              ],
                            );

                            final comWidget = Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Cantidad de Comensales *',
                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                                ),
                                const SizedBox(height: 6),
                                TextFormField(
                                  controller: _comensalesCtrl,
                                  keyboardType: TextInputType.number,
                                  decoration: const InputDecoration(
                                    hintText: 'Ej. 20',
                                  ),
                                  validator: (val) {
                                    if (val == null || val.trim().isEmpty) return 'La cantidad es obligatoria.';
                                    final i = int.tryParse(val);
                                    if (i == null || i < 1) return 'Al menos 1 comensal.';
                                    return null;
                                  },
                                ),
                              ],
                            );

                            if (isNarrow) {
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  presWidget,
                                  const SizedBox(height: 14),
                                  comWidget,
                                ],
                              );
                            }

                            return Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(child: presWidget),
                                const SizedBox(width: 14),
                                Expanded(child: comWidget),
                              ],
                            );
                          },
                        ),
                        const SizedBox(height: 16),

                        // Tipo de Comida y Ubicación de Referencia
                        LayoutBuilder(
                          builder: (ctx, constraints) {
                            final isNarrow = constraints.maxWidth < 450;
                            final tipoWidget = Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Tipo de Comida *',
                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                                ),
                                const SizedBox(height: 6),
                                DropdownButtonFormField<String>(
                                  initialValue: _tipoComida,
                                  decoration: const InputDecoration(),
                                  items: _tiposComida.map((t) {
                                    return DropdownMenuItem(
                                      value: t['valor'],
                                      child: Text(t['etiqueta']!),
                                    );
                                  }).toList(),
                                  onChanged: (val) {
                                    if (val != null) setState(() => _tipoComida = val);
                                  },
                                ),
                              ],
                            );

                            final ubiWidget = Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Ubicación de Referencia *',
                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                                ),
                                const SizedBox(height: 6),
                                TextFormField(
                                  controller: _ubicacionCtrl,
                                  decoration: const InputDecoration(
                                    hintText: 'Ej. Equipetrol, Centro, Zona Norte',
                                  ),
                                  validator: (val) {
                                    if (val == null || val.trim().isEmpty) return 'La ubicación es obligatoria.';
                                    if (val.trim().length < 2) return 'Mínimo 2 caracteres.';
                                    return null;
                                  },
                                ),
                              ],
                            );

                            if (isNarrow) {
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  tipoWidget,
                                  const SizedBox(height: 14),
                                  ubiWidget,
                                ],
                              );
                            }

                            return Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(child: tipoWidget),
                                const SizedBox(width: 14),
                                Expanded(child: ubiWidget),
                              ],
                            );
                          },
                        ),
                        const SizedBox(height: 22),

                        // Preferencias Gastronómicas para este evento (Opcional)
                        const Text(
                          'Preferencias Gastronómicas para este evento (Opcional)',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Selecciona los requerimientos alimentarios para este grupo de comensales. Modificar esto no alterará las preferencias guardadas en tu perfil general.',
                          style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                        ),
                        const SizedBox(height: 12),

                        if (_isLoadingPrefs)
                          const Padding(
                            padding: EdgeInsets.symmetric(vertical: 12),
                            child: Row(
                              children: [
                                SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primary)),
                                SizedBox(width: 10),
                                Expanded(
                                  child: Text('Cargando catálogo de preferencias...', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                                ),
                              ],
                            ),
                          )
                        else
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: _catalogoPreferencias.map((p) {
                              final id = AppTheme.toInt(p['id_preferencia']);
                              final nombre = p['nombre'] ?? '';
                              final selected = _preferenciasSeleccionadas.contains(id);

                              return InkWell(
                                onTap: () => _togglePreferencia(id),
                                borderRadius: BorderRadius.circular(999),
                                child: AnimatedContainer(
                                  duration: const Duration(milliseconds: 180),
                                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                  decoration: BoxDecoration(
                                    color: selected ? AppTheme.primary : AppTheme.surface,
                                    borderRadius: BorderRadius.circular(999),
                                    border: Border.all(
                                      color: selected ? AppTheme.primary : AppTheme.border,
                                      width: selected ? 1.5 : 1,
                                    ),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      if (selected) ...[
                                        const Icon(Icons.check, size: 14, color: Colors.white),
                                        const SizedBox(width: 6),
                                      ],
                                      Text(
                                        nombre,
                                        style: TextStyle(
                                          fontSize: 12.5,
                                          fontWeight: selected ? FontWeight.bold : FontWeight.normal,
                                          color: selected ? Colors.white : AppTheme.textMain,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                        const SizedBox(height: 28),

                        // Botones de acción responsivos
                        Wrap(
                          alignment: WrapAlignment.end,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          spacing: 12,
                          runSpacing: 10,
                          children: [
                            OutlinedButton(
                              onPressed: () {
                                _presupuestoCtrl.text = '300.00';
                                _comensalesCtrl.text = '20';
                                _ubicacionCtrl.text = 'Equipetrol';
                                setState(() {
                                  _preferenciasSeleccionadas.clear();
                                });
                              },
                              child: const Text('Limpiar'),
                            ),
                            ElevatedButton.icon(
                              onPressed: _isSaving ? null : _submitPlanificacion,
                              icon: _isSaving
                                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                  : const Icon(Icons.check, size: 18),
                              label: Text(_isSaving ? 'Guardando...' : 'Guardar Planificación'),
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
    );
  }
}

class _RecomendacionesSheet extends StatelessWidget {
  final int idPlan;
  final List<dynamic> recomendaciones;

  const _RecomendacionesSheet({required this.idPlan, required this.recomendaciones});

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      maxChildSize: 0.95,
      minChildSize: 0.4,
      expand: false,
      builder: (ctx, scrollController) {
        return Container(
          padding: const EdgeInsets.all(20),
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: ListView(
            controller: scrollController,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)),
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Recomendaciones para Plan #$idPlan', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      Text('${recomendaciones.length} alternativa(s) calculada(s)', style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                    ],
                  ),
                  IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                ],
              ),
              const Divider(height: 24),
              if (recomendaciones.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 40),
                  child: Center(
                    child: Text('No se encontraron platos que cumplan con el presupuesto y filtros exactos.'),
                  ),
                )
              else
                ...recomendaciones.map((rec) {
                  final tipoModalidad = rec['tipo_modalidad'] ?? rec['modalidad'] ?? 'RESTAURANTE';
                  final costoTotal = rec['costo_total'] ?? rec['presupuesto_utilizado'] ?? 0;
                  final balance = rec['balance_presupuesto'] ?? rec['ahorro'] ?? 0;
                  final nombre = rec['restaurante_nombre'] ?? rec['titulo'] ?? 'Propuesta Gastronómica';
                  final items = (rec['items'] as List<dynamic>?) ?? (rec['platos'] as List<dynamic>?) ?? [];

                  final isResto = tipoModalidad.toString().toUpperCase().contains('RESTAURANTE');

                  return Container(
                    margin: const EdgeInsets.only(bottom: 14),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.surface,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                Icon(isResto ? Icons.restaurant : Icons.kitchen, color: AppTheme.primary, size: 20),
                                const SizedBox(width: 8),
                                Text(
                                  isResto ? 'Opción Restaurante' : 'Preparación Casera',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppTheme.textMain),
                                ),
                              ],
                            ),
                            AppTheme.buildBadge(isResto ? 'RESTAURANTE' : 'CASERA'),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(nombre, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Text('Costo Estimado: Bs $costoTotal', style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold)),
                            const SizedBox(width: 14),
                            Text('Ahorro/Balance: Bs $balance', style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.w600, fontSize: 12)),
                          ],
                        ),
                        if (items.isNotEmpty) ...[
                          const SizedBox(height: 10),
                          const Text('Platos recomendados:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.textMuted)),
                          const SizedBox(height: 4),
                          ...items.map((it) {
                            final platoNom = it['nombre_plato'] ?? it['nombre'] ?? '';
                            final precio = it['precio_unitario'] ?? it['precio'] ?? '';
                            return Padding(
                              padding: const EdgeInsets.symmetric(vertical: 2),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text('• $platoNom', style: const TextStyle(fontSize: 13)),
                                  Text('Bs $precio', style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                                ],
                              ),
                            );
                          }),
                        ],
                      ],
                    ),
                  );
                }),
            ],
          ),
        );
      },
    );
  }
}
