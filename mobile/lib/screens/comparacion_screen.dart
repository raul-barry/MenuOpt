import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/planificacion_service.dart';
import '../services/asistente_service.dart';
import 'recomendacion_detalle_screen.dart';

class ComparacionScreen extends StatefulWidget {
  final int idPlanificacion;
  final Map<String, dynamic>? planData;
  final Map<String, dynamic>? initialComparacion;

  const ComparacionScreen({
    super.key,
    required this.idPlanificacion,
    this.planData,
    this.initialComparacion,
  });

  @override
  State<ComparacionScreen> createState() => _ComparacionScreenState();
}

class _ComparacionScreenState extends State<ComparacionScreen> {
  bool _isLoading = true;
  bool _isGenerating = false;
  Map<String, dynamic>? _comparacion;
  String? _error;
  String _filtroTipo = 'TODAS'; // 'TODAS', 'RESTAURANTE', 'PREPARACION_PROPIA'

  @override
  void initState() {
    super.initState();
    if (widget.initialComparacion != null) {
      _comparacion = Map<String, dynamic>.from(widget.initialComparacion!);
      _isLoading = false;
    }
    _cargarComparacion();
  }

  Future<void> _cargarComparacion() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final res = await PlanificacionService.instance.compararAlternativas(widget.idPlanificacion);
      if (mounted) {
        setState(() {
          _comparacion = res;
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

  Future<void> _generarRecomendaciones() async {
    setState(() => _isGenerating = true);
    try {
      await PlanificacionService.instance.generarRecomendaciones(widget.idPlanificacion);
      if (!mounted) return;
      setState(() => _isGenerating = false);
      _cargarComparacion();
    } catch (e) {
      if (!mounted) return;
      setState(() => _isGenerating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al generar: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _explicarComparacion() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator(color: AppTheme.primary)),
    );

    try {
      final res = await AsistenteService.instance.explicarComparacion(widget.idPlanificacion);
      if (!mounted) return;
      Navigator.pop(context); // cerrar loader

      final explicacion = res['explicacion'] ?? res['mensaje'] ?? 'Sin análisis comparativo detallado disponible.';
      final detallesClave = (res['detalles_clave'] as List<dynamic>?) ?? [];

      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(8)),
                child: const Icon(Icons.smart_toy_outlined, color: Color(0xFF2563EB), size: 20),
              ),
              const SizedBox(width: 8),
              const Expanded(
                child: Text('Explicación Asistente IA (CU26)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Análisis objetivo de las alternativas gastronómicas:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textMain),
                ),
                const SizedBox(height: 10),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Text(
                    explicacion.toString(),
                    style: const TextStyle(fontSize: 13, color: AppTheme.textMain, height: 1.4),
                  ),
                ),
                if (detallesClave.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text('PUNTOS CLAVE DE LA COMPARATIVA:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                  const SizedBox(height: 6),
                  ...detallesClave.map((d) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('• ', style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primary)),
                            Expanded(child: Text(d.toString(), style: const TextStyle(fontSize: 12))),
                          ],
                        ),
                      )),
                ],
              ],
            ),
          ),
          actions: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary, foregroundColor: Colors.white),
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Entendido'),
            ),
          ],
        ),
      );
    } catch (e) {
      if (!mounted) return;
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo obtener la explicación: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _verDetalleRecomendacion(Map<String, dynamic> alt) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => RecomendacionDetalleScreen(
          idRecomendacion: AppTheme.toInt(alt['id_recomendacion']),
          idPlanificacion: widget.idPlanificacion,
          planData: widget.planData,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final comp = _comparacion;
    final List<dynamic> todasAlt = (comp?['alternativas'] as List<dynamic>?) ?? [];
    final List<dynamic> alternativas = todasAlt.where((a) {
      if (_filtroTipo == 'TODAS') return true;
      return a['tipo_recomendacion'] == _filtroTipo;
    }).toList();

    final mejorCosto = comp?['mejor_opcion_costo'] as Map<String, dynamic>?;
    final mejorPuntuacion = comp?['mejor_opcion_puntuacion'] as Map<String, dynamic>?;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Comparar Alternativas (CU14)'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Volver',
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : _error != null && comp == null
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
                        ElevatedButton(onPressed: _cargarComparacion, child: const Text('Reintentar')),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _cargarComparacion,
                  color: AppTheme.primary,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      // Breadcrumb
                      GestureDetector(
                        onTap: () => Navigator.pop(context),
                        child: const Padding(
                          padding: EdgeInsets.only(bottom: 12),
                          child: Text(
                            '← Volver a la Planificación',
                            style: TextStyle(color: AppTheme.textMuted, fontSize: 13, fontWeight: FontWeight.w500),
                          ),
                        ),
                      ),

                      // Tarjeta Header Principal (Exacto a Web CU14)
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: AppTheme.cardDecoration,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Wrap(
                              alignment: WrapAlignment.spaceBetween,
                              crossAxisAlignment: WrapCrossAlignment.center,
                              spacing: 8,
                              runSpacing: 6,
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF1F5F9),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: const Text(
                                    'ANÁLISIS COMPARATIVO (CU14)',
                                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF475569), letterSpacing: 0.4),
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8FAFC),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: AppTheme.border),
                                  ),
                                  child: Text(
                                    '${comp?['total_alternativas'] ?? 0} Opciones Viables',
                                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'Comparación de Alternativas Gastronómicas',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Evaluación para ${comp?['cantidad_personas'] ?? ''} comensales con presupuesto límite de Bs ${AppTheme.toDouble(comp?['presupuesto']).toStringAsFixed(2)} (${comp?['tipo_comida'] ?? ''}).',
                              style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
                            ),
                            const SizedBox(height: 12),

                            // Botón Explicar Comparación Asistente IA
                            OutlinedButton.icon(
                              style: OutlinedButton.styleFrom(
                                side: const BorderSide(color: Color(0xFF0284C7)),
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              ),
                              onPressed: _explicarComparacion,
                              icon: const Icon(Icons.smart_toy_outlined, size: 16, color: Color(0xFF0284C7)),
                              label: const Text('Explicar Comparación con IA (CU26)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0284C7))),
                            ),

                            // Destacados Responsivos: Menor Costo & Mejor Puntuada
                            if (mejorCosto != null || mejorPuntuacion != null) ...[
                              const SizedBox(height: 14),
                              LayoutBuilder(
                                builder: (context, constraints) {
                                  final isNarrow = constraints.maxWidth < 340;

                                  Widget buildCostoBox() => Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFECFDF5),
                                      borderRadius: BorderRadius.circular(10),
                                      border: Border.all(color: const Color(0xFFA7F3D0)),
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          '💵 MENOR COSTO',
                                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF065F46)),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          mejorCosto!['nombre'] ?? '',
                                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        Text(
                                          'Costo: Bs ${AppTheme.toDouble(mejorCosto['costo_total']).toStringAsFixed(2)}',
                                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                                        ),
                                        Text(
                                          'Ahorro: Bs ${AppTheme.toDouble(mejorCosto['ahorro_respecto_presupuesto']).toStringAsFixed(2)}',
                                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF059669)),
                                        ),
                                      ],
                                    ),
                                  );

                                  Widget buildPuntuadaBox() => Container(
                                    padding: const EdgeInsets.all(12),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFEFF6FF),
                                      borderRadius: BorderRadius.circular(10),
                                      border: Border.all(color: const Color(0xFFBFDBFE)),
                                    ),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          '⭐ MEJOR PUNTUADA',
                                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF1E40AF)),
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          mejorPuntuacion!['nombre'] ?? '',
                                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        Text(
                                          'Afinidad: ${AppTheme.toDouble(mejorPuntuacion['puntuacion']).round()}/100',
                                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF1E40AF)),
                                        ),
                                        Text(
                                          'Costo: Bs ${AppTheme.toDouble(mejorPuntuacion['costo_total']).toStringAsFixed(2)}',
                                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                                        ),
                                      ],
                                    ),
                                  );

                                  if (isNarrow) {
                                    return Column(
                                      children: [
                                        if (mejorCosto != null) buildCostoBox(),
                                        if (mejorCosto != null && mejorPuntuacion != null) const SizedBox(height: 8),
                                        if (mejorPuntuacion != null) buildPuntuadaBox(),
                                      ],
                                    );
                                  }

                                  return Row(
                                    children: [
                                      if (mejorCosto != null) Expanded(child: buildCostoBox()),
                                      if (mejorCosto != null && mejorPuntuacion != null) const SizedBox(width: 8),
                                      if (mejorPuntuacion != null) Expanded(child: buildPuntuadaBox()),
                                    ],
                                  );
                                },
                              ),
                            ],
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Filtros por Tipo (Chips)
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: [
                            _buildFilterChip('Todas (${todasAlt.length})', 'TODAS'),
                            const SizedBox(width: 6),
                            _buildFilterChip('Restaurantes', 'RESTAURANTE'),
                            const SizedBox(width: 6),
                            _buildFilterChip('Casera', 'PREPARACION_PROPIA'),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Lista de Alternativas Comparadas
                      if (todasAlt.isEmpty)
                        Container(
                          padding: const EdgeInsets.all(24),
                          decoration: AppTheme.cardDecoration,
                          child: Column(
                            children: [
                              const Icon(Icons.compare_arrows, size: 48, color: AppTheme.textMuted),
                              const SizedBox(height: 12),
                              const Text(
                                'No hay alternativas para comparar',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'Aún no se han generado recomendaciones optimizadas para esta planificación. Pulsa el botón inferior para calcularlas.',
                                textAlign: TextAlign.center,
                                style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton.icon(
                                onPressed: _isGenerating ? null : _generarRecomendaciones,
                                icon: _isGenerating
                                    ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                    : const Icon(Icons.bolt, size: 18),
                                label: Text(_isGenerating ? 'Calculando...' : 'Generar Recomendaciones Ahora'),
                              ),
                            ],
                          ),
                        )
                      else
                        ...alternativas.map((altRaw) {
                          final alt = altRaw as Map<String, dynamic>;
                          final tipo = alt['tipo_recomendacion'] ?? 'RESTAURANTE';
                          final isResto = tipo == 'RESTAURANTE';
                          final puntuacion = AppTheme.toDouble(alt['puntuacion']);
                          final costoTotal = AppTheme.toDouble(alt['costo_total']);
                          final costoPersona = AppTheme.toDouble(alt['costo_por_persona']);
                          final ahorro = AppTheme.toDouble(alt['ahorro_respecto_presupuesto']);
                          final porcentaje = AppTheme.toDouble(alt['porcentaje_presupuesto_utilizado']);
                          final resumen = alt['resumen'] ?? '';
                          final platos = (alt['platos'] as List<dynamic>?) ?? [];
                          final ingredientes = (alt['ingredientes_resumen'] as List<dynamic>?) ?? [];
                          final lugares = (alt['lugares_compra_resumen'] as List<dynamic>?) ?? [];

                          return Container(
                            margin: const EdgeInsets.only(bottom: 14),
                            padding: const EdgeInsets.all(16),
                            decoration: AppTheme.cardDecoration,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Encabezado: Badge + Puntos
                                Wrap(
                                  alignment: WrapAlignment.spaceBetween,
                                  crossAxisAlignment: WrapCrossAlignment.center,
                                  spacing: 8,
                                  runSpacing: 6,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: isResto ? const Color(0xFFE2E8F0) : const Color(0xFFD1FAE5),
                                        borderRadius: BorderRadius.circular(6),
                                      ),
                                      child: Text(
                                        isResto ? 'RESTAURANTE' : 'PREPARACIÓN PROPIA',
                                        style: TextStyle(
                                          color: isResto ? const Color(0xFF1D3557) : const Color(0xFF065F46),
                                          fontSize: 10,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFFF8FAFC),
                                        borderRadius: BorderRadius.circular(6),
                                        border: Border.all(color: AppTheme.border),
                                      ),
                                      child: Text(
                                        '${puntuacion.round()} pts',
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textMain),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),

                                // Nombre de la opción
                                Text(
                                  alt['nombre'] ?? 'Alternativa',
                                  style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                ),
                                const SizedBox(height: 4),

                                // Resumen cualitativo
                                if (resumen.isNotEmpty) ...[
                                  Text(
                                    resumen,
                                    style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.3),
                                  ),
                                  const SizedBox(height: 10),
                                ],

                                // Tabla de Métricas Financieras
                                Container(
                                  padding: const EdgeInsets.all(10),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8FAFC),
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(color: const Color(0xFFF1F5F9)),
                                  ),
                                  child: Column(
                                    children: [
                                      _buildMetricRow('Presupuesto inicial:', 'Bs ${AppTheme.toDouble(comp?['presupuesto']).toStringAsFixed(2)}'),
                                      _buildMetricRow('Costo total de la opción:', 'Bs ${costoTotal.toStringAsFixed(2)}', isBold: true),
                                      _buildMetricRow('Costo por persona:', 'Bs ${costoPersona.toStringAsFixed(2)}'),
                                      _buildMetricRow('Ahorro conseguido:', 'Bs ${ahorro.toStringAsFixed(2)}', valueColor: const Color(0xFF059669), isBold: true),
                                      _buildMetricRow('Presupuesto utilizado:', '${porcentaje.toStringAsFixed(1)}%'),
                                    ],
                                  ),
                                ),

                                // Desglose de Platos (si es Restaurante)
                                if (isResto && platos.isNotEmpty) ...[
                                  const SizedBox(height: 10),
                                  const Text('Platos incluidos:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                                  const SizedBox(height: 4),
                                  ...platos.map((p) => Padding(
                                        padding: const EdgeInsets.only(bottom: 2),
                                        child: Text(
                                          '• ${p['cantidad']}x ${p['nombre_plato']} (Bs ${AppTheme.toDouble(p['subtotal']).toStringAsFixed(2)})',
                                          style: const TextStyle(fontSize: 12, color: AppTheme.textMain),
                                        ),
                                      )),
                                ],

                                // Desglose de Ingredientes y Lugares (si es Preparación Propia)
                                if (!isResto && (ingredientes.isNotEmpty || lugares.isNotEmpty)) ...[
                                  const SizedBox(height: 10),
                                  if (ingredientes.isNotEmpty) ...[
                                    const Text('Ingredientes clave:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                                    const SizedBox(height: 3),
                                    Text(ingredientes.join(', '), style: const TextStyle(fontSize: 12, color: AppTheme.textMain)),
                                    const SizedBox(height: 6),
                                  ],
                                  if (lugares.isNotEmpty) ...[
                                    const Text('Lugares sugeridos de compra:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                                    const SizedBox(height: 3),
                                    Text(lugares.join(', '), style: const TextStyle(fontSize: 12, color: AppTheme.primary, fontWeight: FontWeight.w600)),
                                  ],
                                ],

                                const SizedBox(height: 12),

                                // Botón Ver Detalle
                                SizedBox(
                                  width: double.infinity,
                                  child: OutlinedButton(
                                    style: OutlinedButton.styleFrom(
                                      padding: const EdgeInsets.symmetric(vertical: 8),
                                      side: const BorderSide(color: Color(0xFFCBD5E1)),
                                    ),
                                    onPressed: () => _verDetalleRecomendacion(alt),
                                    child: const Text('Ver Detalle General', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                                  ),
                                ),
                              ],
                            ),
                          );
                        }),
                    ],
                  ),
                ),
    );
  }

  Widget _buildFilterChip(String label, String value) {
    final bool isSelected = _filtroTipo == value;
    return InkWell(
      onTap: () => setState(() => _filtroTipo = value),
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primary : Colors.white,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: isSelected ? AppTheme.primary : AppTheme.border),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: isSelected ? Colors.white : AppTheme.textMain,
          ),
        ),
      ),
    );
  }

  Widget _buildMetricRow(String label, String value, {bool isBold = false, Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
          ),
          const SizedBox(width: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 12,
              fontWeight: isBold ? FontWeight.bold : FontWeight.w500,
              color: valueColor ?? AppTheme.textMain,
            ),
          ),
        ],
      ),
    );
  }
}
