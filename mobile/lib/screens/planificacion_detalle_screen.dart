import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/planificacion_service.dart';
import 'recomendaciones_list_screen.dart';
import 'comparacion_screen.dart';

class PlanificacionDetalleScreen extends StatefulWidget {
  final int idPlanificacion;
  final Map<String, dynamic>? initialPlan;
  final VoidCallback? onUpdated;

  const PlanificacionDetalleScreen({
    super.key,
    required this.idPlanificacion,
    this.initialPlan,
    this.onUpdated,
  });

  @override
  State<PlanificacionDetalleScreen> createState() => _PlanificacionDetalleScreenState();
}

class _PlanificacionDetalleScreenState extends State<PlanificacionDetalleScreen> {
  bool _isLoading = true;
  bool _isGenerating = false;
  Map<String, dynamic>? _plan;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.initialPlan != null) {
      _plan = Map<String, dynamic>.from(widget.initialPlan!);
      _isLoading = false;
    }
    _cargarDetalle();
  }

  Future<void> _cargarDetalle() async {
    try {
      final res = await PlanificacionService.instance.obtenerPlanificacion(widget.idPlanificacion);
      if (mounted) {
        setState(() {
          _plan = res;
          _isLoading = false;
          _error = null;
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

  Future<void> _generarRecomendaciones() async {
    setState(() => _isGenerating = true);
    try {
      final recs = await PlanificacionService.instance.generarRecomendaciones(widget.idPlanificacion);
      if (!mounted) return;
      setState(() => _isGenerating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('¡${recs.length} recomendaciones generadas con éxito!'),
          backgroundColor: AppTheme.success,
        ),
      );
      _navegarARecomendaciones(recs);
    } catch (e) {
      if (!mounted) return;
      setState(() => _isGenerating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al generar: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _navegarARecomendaciones([List<dynamic>? preloadedRecs]) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => RecomendacionesListScreen(
          idPlanificacion: widget.idPlanificacion,
          planData: _plan,
          initialRecomendaciones: preloadedRecs,
        ),
      ),
    );
  }

  void _compararAlternativas() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ComparacionScreen(
          idPlanificacion: widget.idPlanificacion,
          planData: _plan,
        ),
      ),
    );
  }


  Future<void> _cancelarPlan() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancelar Planificación'),
        content: Text('¿Está seguro de que desea cancelar la planificación #${widget.idPlanificacion}?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Volver')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.danger, foregroundColor: Colors.white),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Sí, Cancelar'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await PlanificacionService.instance.cancelarPlanificacion(widget.idPlanificacion);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Planificación cancelada correctamente'), backgroundColor: AppTheme.success),
      );
      widget.onUpdated?.call();
      _cargarDetalle();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cancelar: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _editarPlan() {
    if (_plan == null) return;
    final presCtrl = TextEditingController(text: _plan!['presupuesto'].toString());
    final comCtrl = TextEditingController(text: _plan!['cantidad_personas'].toString());
    final ubiCtrl = TextEditingController(text: _plan!['ubicacion_referencia'] ?? '');
    String tipo = _plan!['tipo_comida'] ?? 'ALMUERZO';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text('Editar Planificación #${widget.idPlanificacion}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    ),
                    IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(ctx)),
                  ],
                ),
              const Divider(),
              const SizedBox(height: 10),
              TextField(
                controller: presCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Presupuesto (Bs) *'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: comCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Cantidad de Comensales *'),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: tipo,
                decoration: const InputDecoration(labelText: 'Tipo de Comida *'),
                items: const [
                  DropdownMenuItem(value: 'DESAYUNO', child: Text('Desayuno')),
                  DropdownMenuItem(value: 'ALMUERZO', child: Text('Almuerzo')),
                  DropdownMenuItem(value: 'CENA', child: Text('Cena')),
                  DropdownMenuItem(value: 'REFRIGERIO', child: Text('Refrigerio')),
                ],
                onChanged: (v) {
                  if (v != null) setSheetState(() => tipo = v);
                },
              ),
              const SizedBox(height: 12),
              TextField(
                controller: ubiCtrl,
                decoration: const InputDecoration(labelText: 'Ubicación de Referencia *'),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () async {
                  final pres = double.tryParse(presCtrl.text.trim()) ?? 0;
                  final com = int.tryParse(comCtrl.text.trim()) ?? 1;
                  final ubi = ubiCtrl.text.trim();

                  try {
                    await PlanificacionService.instance.actualizarPlanificacion(widget.idPlanificacion, {
                      'presupuesto': pres,
                      'cantidad_personas': com,
                      'tipo_comida': tipo,
                      'ubicacion_referencia': ubi,
                    });
                    if (!mounted) return;
                    if (ctx.mounted) Navigator.pop(ctx);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Planificación actualizada con éxito'), backgroundColor: AppTheme.success),
                    );
                    widget.onUpdated?.call();
                    _cargarDetalle();
                  } catch (e) {
                    if (!mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Error: $e'), backgroundColor: AppTheme.danger),
                    );
                  }
                },
                child: const Text('Guardar Cambios'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

  @override
  Widget build(BuildContext context) {
    final plan = _plan;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text('Planificación #${widget.idPlanificacion}'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Volver a Mis Planificaciones',
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _isLoading && plan == null
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : _error != null && plan == null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.error_outline, size: 40, color: AppTheme.danger),
                        const SizedBox(height: 8),
                        Text(_error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 13)),
                        const SizedBox(height: 12),
                        ElevatedButton(onPressed: _cargarDetalle, child: const Text('Reintentar')),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _cargarDetalle,
                  color: AppTheme.primary,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      // Breadcrumb link visual
                      GestureDetector(
                        onTap: () => Navigator.pop(context),
                        child: const Padding(
                          padding: EdgeInsets.only(bottom: 12),
                          child: Text(
                            '← Volver a Mis Planificaciones',
                            style: TextStyle(color: AppTheme.textMuted, fontSize: 13, fontWeight: FontWeight.w500),
                          ),
                        ),
                      ),

                      // Tarjeta Principal Header (Exacto a Imagen 2)
                      Container(
                        padding: const EdgeInsets.all(18),
                        decoration: AppTheme.cardDecoration,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // ID y Badge
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    'PLANIFICACIÓN #${plan!['id_planificacion']}',
                                    style: const TextStyle(
                                      color: AppTheme.primary,
                                      fontSize: 13,
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: 0.5,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                AppTheme.buildBadge((plan['estado'] ?? 'ACTIVA').toString()),
                              ],
                            ),
                            const SizedBox(height: 6),

                            // Título principal
                            Text(
                              '${plan['tipo_comida']} para ${plan['cantidad_personas']} personas',
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: AppTheme.textMain,
                              ),
                            ),
                            const SizedBox(height: 4),

                            // Fecha registrada
                            Text(
                              'Registrada el ${AppTheme.formatDate(plan['fecha_planificacion'], includeTime: true)}',
                              style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                            ),
                            const SizedBox(height: 16),

                            // Acciones principales (Exacto a Imagen 2)
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: [
                                if (plan['estado'] == 'ACTIVA')
                                  ElevatedButton.icon(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.primary,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                                    ),
                                    onPressed: _isGenerating ? null : _generarRecomendaciones,
                                    icon: _isGenerating
                                        ? const SizedBox(
                                            width: 14,
                                            height: 14,
                                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                          )
                                        : const Icon(Icons.bolt, size: 18),
                                    label: Text(_isGenerating ? 'Calculando...' : 'Generar Recomendaciones'),
                                  ),
                                OutlinedButton.icon(
                                  style: OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                  ),
                                  onPressed: () => _navegarARecomendaciones(),
                                  icon: const Icon(Icons.list_alt, size: 16),
                                  label: const Text('Ver Recomendaciones'),
                                ),
                                OutlinedButton.icon(
                                  style: OutlinedButton.styleFrom(
                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                  ),
                                  onPressed: _compararAlternativas,
                                  icon: const Icon(Icons.tune, size: 16),
                                  label: const Text('Comparar Alternativas (CU14)'),
                                ),
                                if (plan['estado'] == 'ACTIVA') ...[
                                  OutlinedButton.icon(
                                    style: OutlinedButton.styleFrom(
                                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                                    ),
                                    onPressed: _editarPlan,
                                    icon: const Icon(Icons.edit_outlined, size: 16),
                                    label: const Text('Editar'),
                                  ),
                                  ElevatedButton(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.danger,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                                    ),
                                    onPressed: _cancelarPlan,
                                    child: const Text('Cancelar'),
                                  ),
                                ],
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Tarjetas de Métricas Responsivas
                      LayoutBuilder(
                        builder: (context, constraints) {
                          final isNarrow = constraints.maxWidth < 460;
                          final presTotal = 'Bs ${AppTheme.toDouble(plan['presupuesto']).toStringAsFixed(2)}';
                          final presPorPersona = 'Bs ${(AppTheme.toDouble(plan['presupuesto']) / (AppTheme.toInt(plan['cantidad_personas'], 1))).toStringAsFixed(2)}';
                          final comensalesTxt = '${plan['cantidad_personas']} personas';

                          if (isNarrow) {
                            return Column(
                              children: [
                                Row(
                                  children: [
                                    Expanded(
                                      child: _buildMetricCard(
                                        label: 'PRESUPUESTO TOTAL',
                                        value: presTotal,
                                        subtitle: 'Límite económico total',
                                        isHighlight: true,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: _buildMetricCard(
                                        label: 'PRESUPUESTO / PERS.',
                                        value: presPorPersona,
                                        subtitle: 'Promedio máx / persona',
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                _buildMetricCard(
                                  label: 'COMENSALES CUBIERTOS',
                                  value: comensalesTxt,
                                  subtitle: 'Personas cubiertas en el evento',
                                ),
                              ],
                            );
                          }

                          return Row(
                            children: [
                              Expanded(
                                child: _buildMetricCard(
                                  label: 'PRESUPUESTO',
                                  value: presTotal,
                                  subtitle: 'Límite total',
                                  isHighlight: true,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: _buildMetricCard(
                                  label: 'COMENSALES',
                                  value: '${plan['cantidad_personas']}',
                                  subtitle: 'Cubiertos',
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: _buildMetricCard(
                                  label: 'PRESUPUESTO / P.',
                                  value: presPorPersona,
                                  subtitle: 'Por persona',
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                      const SizedBox(height: 16),

                      // Parámetros de Ubicación de Referencia (Exacto a Imagen 2)
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: AppTheme.cardDecoration,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Ubicación de Referencia',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                const Icon(Icons.location_on, color: AppTheme.primary, size: 20),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    plan['ubicacion_referencia'] ?? 'No especificada',
                                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AppTheme.textMain),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            const Text(
                              'Zona aproximada utilizada para estimar cercanía de restaurantes y mercados.',
                              style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Parámetros de Preferencias Asociadas (Exacto a Imagen 2)
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: AppTheme.cardDecoration,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: const Text(
                                    'Preferencias Asociadas',
                                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFE2E8F0),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    '${(plan['preferencias'] as List<dynamic>?)?.length ?? 0}',
                                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            if ((plan['preferencias'] as List<dynamic>?) == null ||
                                (plan['preferencias'] as List<dynamic>).isEmpty)
                              const Text(
                                'Sin preferencias dietéticas específicas seleccionadas para este evento.',
                                style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
                              )
                            else
                              Wrap(
                                spacing: 8,
                                runSpacing: 6,
                                children: (plan['preferencias'] as List<dynamic>).map((p) {
                                  final nombre = p is Map ? (p['nombre'] ?? p.toString()) : p.toString();
                                  return Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: AppTheme.primaryLight,
                                      borderRadius: BorderRadius.circular(999),
                                      border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3)),
                                    ),
                                    child: Text(
                                      nombre,
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.primary),
                                    ),
                                  );
                                }).toList(),
                              ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildMetricCard({
    required String label,
    required String value,
    required String subtitle,
    bool isHighlight = false,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
      decoration: AppTheme.cardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 9.5,
              fontWeight: FontWeight.bold,
              color: AppTheme.textMuted,
              letterSpacing: 0.2,
              height: 1.15,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 6),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: isHighlight ? AppTheme.primary : AppTheme.textMain,
              ),
            ),
          ),
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: const TextStyle(fontSize: 9, color: AppTheme.textMuted, height: 1.15),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
