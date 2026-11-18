import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/planificacion_service.dart';
import '../services/asistente_service.dart';
import 'recomendacion_detalle_screen.dart';
import 'comparacion_screen.dart';

class RecomendacionesListScreen extends StatefulWidget {
  final int idPlanificacion;
  final Map<String, dynamic>? planData;
  final List<dynamic>? initialRecomendaciones;

  const RecomendacionesListScreen({
    super.key,
    required this.idPlanificacion,
    this.planData,
    this.initialRecomendaciones,
  });

  @override
  State<RecomendacionesListScreen> createState() => _RecomendacionesListScreenState();
}

class _RecomendacionesListScreenState extends State<RecomendacionesListScreen> {
  bool _isLoading = true;
  bool _isRegenerating = false;
  List<dynamic> _recomendaciones = [];
  Map<String, dynamic>? _plan;
  String? _error;

  @override
  void initState() {
    super.initState();
    _plan = widget.planData;
    if (widget.initialRecomendaciones != null && widget.initialRecomendaciones!.isNotEmpty) {
      _recomendaciones = widget.initialRecomendaciones!;
      _isLoading = false;
    } else {
      _cargarDatos();
    }
  }

  Future<void> _cargarDatos() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      _plan ??= await PlanificacionService.instance.obtenerPlanificacion(widget.idPlanificacion);
      final recs = await PlanificacionService.instance.obtenerRecomendaciones(widget.idPlanificacion);
      if (mounted) {
        setState(() {
          _recomendaciones = recs;
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

  Future<void> _regenerarRecomendaciones() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Regenerar Recomendaciones'),
        content: const Text('¿Deseas recalcular las recomendaciones con los datos actuales?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary, foregroundColor: Colors.white),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Sí, Regenerar'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    setState(() => _isRegenerating = true);
    try {
      final recs = await PlanificacionService.instance.generarRecomendaciones(widget.idPlanificacion);
      if (!mounted) return;
      setState(() {
        _recomendaciones = recs;
        _isRegenerating = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Recomendaciones actualizadas con éxito'), backgroundColor: AppTheme.success),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isRegenerating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al regenerar: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _explicarRecomendacion(Map<String, dynamic> rec) async {
    final idRec = AppTheme.toInt(rec['id_recomendacion']);
    final nombre = rec['nombre'] ?? rec['nombre_restaurante'] ?? 'esta opción';

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator(color: AppTheme.primary)),
    );

    try {
      final res = await AsistenteService.instance.explicarRecomendacion(idRec);
      if (!mounted) return;
      Navigator.pop(context); // cerrar loader

      final explicacion = res['explicacion'] ?? res['mensaje'] ?? 'Sin explicación detallada disponible.';
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
                child: Text('Explicación Asistente IA', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '¿Por qué recomendamos $nombre?',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textMain),
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
                  const Text('DATOS REALES VERIFICADOS:', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
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

  void _verDetalleRecomendacion(Map<String, dynamic> rec) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => RecomendacionDetalleScreen(
          idRecomendacion: AppTheme.toInt(rec['id_recomendacion']),
          recomendacionData: rec,
          idPlanificacion: widget.idPlanificacion,
          planData: _plan,
        ),
      ),
    );
  }

  void _abrirComparacion() {
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

  double _calcularAhorro(Map<String, dynamic> rec) {
    if (_plan == null) return 0.0;
    final presupuesto = AppTheme.toDouble(_plan!['presupuesto']);
    final costo = AppTheme.toDouble(rec['costo_total']);
    final ahorro = presupuesto - costo;
    return ahorro > 0 ? ahorro : 0.0;
  }

  @override
  Widget build(BuildContext context) {
    final plan = _plan;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Recomendaciones Gastronómicas'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Volver a la Planificación',
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.tune),
            tooltip: 'Comparar Alternativas',
            onPressed: _abrirComparacion,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : _error != null && _recomendaciones.isEmpty
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
                        ElevatedButton(onPressed: _cargarDatos, child: const Text('Reintentar')),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _cargarDatos,
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

                      // Header Card (Exacto a Imagen 3 y Web)
                      if (plan != null)
                        Container(
                          margin: const EdgeInsets.only(bottom: 16),
                          padding: const EdgeInsets.all(16),
                          decoration: AppTheme.cardDecoration,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Planificación #${plan['id_planificacion']}',
                                style: const TextStyle(
                                  color: AppTheme.primary,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  letterSpacing: 0.5,
                                ),
                              ),
                              const SizedBox(height: 4),
                              const Text(
                                'Alternativas Gastronómicas Recomendadas',
                                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'Para ${plan['cantidad_personas']} comensales con presupuesto de Bs ${AppTheme.toDouble(plan['presupuesto']).toStringAsFixed(2)} (${plan['tipo_comida']}).',
                                style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
                              ),
                              const SizedBox(height: 12),
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children: [
                                  ElevatedButton.icon(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.primary,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                    ),
                                    onPressed: _abrirComparacion,
                                    icon: const Icon(Icons.tune, size: 16),
                                    label: const Text('Comparar Alternativas', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                  ),
                                  if (plan['estado'] == 'ACTIVA')
                                    OutlinedButton.icon(
                                      style: OutlinedButton.styleFrom(
                                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                      ),
                                      onPressed: _isRegenerating ? null : _regenerarRecomendaciones,
                                      icon: _isRegenerating
                                          ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primary))
                                          : const Icon(Icons.refresh, size: 16),
                                      label: Text(_isRegenerating ? 'Regenerando...' : 'Regenerar', style: const TextStyle(fontSize: 12)),
                                    ),
                                ],
                              ),
                            ],
                          ),
                        ),

                      // Si no hay resultados
                      if (_recomendaciones.isEmpty)
                        Container(
                          padding: const EdgeInsets.all(24),
                          decoration: AppTheme.cardDecoration,
                          child: Column(
                            children: [
                              const Icon(Icons.search_off, size: 48, color: AppTheme.textMuted),
                              const SizedBox(height: 12),
                              const Text(
                                'No encontramos alternativas dentro del presupuesto',
                                textAlign: TextAlign.center,
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'No se hallaron opciones comerciales o recetas caseras que cumplan estrictamente con tu presupuesto disponible de Bs ${plan?['presupuesto'] ?? ''} y tus preferencias.',
                                textAlign: TextAlign.center,
                                style: const TextStyle(fontSize: 12, color: AppTheme.textMuted),
                              ),
                            ],
                          ),
                        )
                      else
                        // Listado de Tarjetas de Recomendaciones (Exacto a Imagen 3)
                        ..._recomendaciones.map((recRaw) {
                          final rec = recRaw as Map<String, dynamic>;
                          final tipo = (rec['tipo_recomendacion'] ?? 'RESTAURANTE').toString();
                          final isResto = tipo == 'RESTAURANTE';
                          final puntuacion = AppTheme.toDouble(rec['puntuacion']);
                          final nombre = rec['nombre'] ?? rec['nombre_restaurante'] ?? (isResto ? 'Restaurante' : 'Preparación Propia');
                          final desc = rec['descripcion'] ?? '';
                          final platos = (rec['platos'] as List<dynamic>?) ?? [];
                          final costoTotal = AppTheme.toDouble(rec['costo_total']);
                          final costoPorPersona = AppTheme.toDouble(rec['costo_por_persona']);
                          final ahorro = _calcularAhorro(rec);

                          return Container(
                            margin: const EdgeInsets.only(bottom: 16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: const Color(0xFFE2E8F0),
                                width: 1.5,
                              ),
                              boxShadow: const [
                                BoxShadow(
                                  color: Color.fromRGBO(0, 0, 0, 0.04),
                                  blurRadius: 8,
                                  offset: Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Encabezado de la Tarjeta (Badge + Score)
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      // Badge modalidad
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: isResto ? const Color(0xFFE2E8F0) : const Color(0xFFD1FAE5),
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: Text(
                                          isResto ? 'RESTAURANTE' : 'PREPARACIÓN PROPIA',
                                          style: TextStyle(
                                            color: isResto ? const Color(0xFF1D3557) : const Color(0xFF065F46),
                                            fontSize: 11,
                                            fontWeight: FontWeight.bold,
                                            letterSpacing: 0.3,
                                          ),
                                        ),
                                      ),

                                      // Score Badge (ej: 91/100)
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFFF8FAFC),
                                          borderRadius: BorderRadius.circular(8),
                                          border: Border.all(color: const Color(0xFFE2E8F0)),
                                        ),
                                        child: RichText(
                                          text: TextSpan(
                                            children: [
                                              TextSpan(
                                                text: '${puntuacion.round()}',
                                                style: const TextStyle(
                                                  fontSize: 16,
                                                  fontWeight: FontWeight.bold,
                                                  color: AppTheme.textMain,
                                                ),
                                              ),
                                              const TextSpan(
                                                text: '/100',
                                                style: TextStyle(
                                                  fontSize: 11,
                                                  color: AppTheme.textMuted,
                                                  fontWeight: FontWeight.w500,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 10),

                                  // Nombre del restaurante / alternativa
                                  Text(
                                    nombre,
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: AppTheme.textMain,
                                    ),
                                  ),

                                  // Descripción / menú
                                  if (desc.isNotEmpty) ...[
                                    const SizedBox(height: 4),
                                    Text(
                                      desc,
                                      style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
                                    ),
                                  ],

                                  // Desglose de Platos para Restaurante (Menú sugerido)
                                  if (isResto && platos.isNotEmpty) ...[
                                    const SizedBox(height: 12),
                                    Container(
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFFF8FAFC),
                                        borderRadius: BorderRadius.circular(10),
                                        border: Border.all(color: const Color(0xFFF1F5F9)),
                                      ),
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          const Text(
                                            'MENÚ SUGERIDO:',
                                            style: TextStyle(
                                              fontSize: 11,
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF64748B),
                                              letterSpacing: 0.4,
                                            ),
                                          ),
                                          const SizedBox(height: 6),
                                          ...platos.map((p) {
                                            final cant = p['cantidad'] ?? 1;
                                            final nomPlato = p['nombre_plato'] ?? 'Plato';
                                            final pers = p['personas_cubiertas'] ?? 1;
                                            final sub = AppTheme.toDouble(p['subtotal']);
                                            return Padding(
                                              padding: const EdgeInsets.only(bottom: 4),
                                              child: Row(
                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                children: [
                                                  Expanded(
                                                    child: Text(
                                                      '${cant}x $nomPlato ($pers pers/plato)',
                                                      style: const TextStyle(fontSize: 12, color: AppTheme.textMain),
                                                    ),
                                                  ),
                                                  Text(
                                                    'Bs ${sub.toStringAsFixed(2)}',
                                                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                                  ),
                                                ],
                                              ),
                                            );
                                          }),
                                        ],
                                      ),
                                    ),
                                  ],

                                  const SizedBox(height: 14),

                                  // Métricas Financieras Responsivas
                                  Container(
                                    padding: const EdgeInsets.all(10),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFF8FAFC),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: Row(
                                      children: [
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              const Text('COSTO TOTAL', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                                              const SizedBox(height: 3),
                                              FittedBox(
                                                fit: BoxFit.scaleDown,
                                                alignment: Alignment.centerLeft,
                                                child: Text('Bs ${costoTotal.toStringAsFixed(2)}', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textMain)),
                                              ),
                                            ],
                                          ),
                                        ),
                                        Container(width: 1, height: 28, color: const Color(0xFFE2E8F0)),
                                        const SizedBox(width: 8),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              const Text('COSTO / PERS.', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                                              const SizedBox(height: 3),
                                              FittedBox(
                                                fit: BoxFit.scaleDown,
                                                alignment: Alignment.centerLeft,
                                                child: Text('Bs ${costoPorPersona.toStringAsFixed(2)}', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textMain)),
                                              ),
                                            ],
                                          ),
                                        ),
                                        Container(width: 1, height: 28, color: const Color(0xFFE2E8F0)),
                                        const SizedBox(width: 8),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              const Text('AHORRO ESTIMADO', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                                              const SizedBox(height: 3),
                                              FittedBox(
                                                fit: BoxFit.scaleDown,
                                                alignment: Alignment.centerLeft,
                                                child: Text(
                                                  'Bs ${ahorro.toStringAsFixed(2)}',
                                                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF059669)),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),

                                  const SizedBox(height: 14),

                                  // Acciones de la Tarjeta Responsivas
                                  LayoutBuilder(
                                    builder: (context, constraints) {
                                      final isNarrow = constraints.maxWidth < 340;
                                      final btnDetalle = OutlinedButton(
                                        style: OutlinedButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(vertical: 10),
                                          side: const BorderSide(color: Color(0xFFCBD5E1)),
                                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                        ),
                                        onPressed: () => _verDetalleRecomendacion(rec),
                                        child: const Text('Ver Detalle', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF1E293B))),
                                      );

                                      final btnExplicar = OutlinedButton.icon(
                                        style: OutlinedButton.styleFrom(
                                          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
                                          side: const BorderSide(color: Color(0xFF3B82F6)),
                                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                        ),
                                        onPressed: () => _explicarRecomendacion(rec),
                                        icon: const Icon(Icons.smart_toy_outlined, size: 16, color: Color(0xFF2563EB)),
                                        label: const Text(
                                          '¿Por qué esta opción?',
                                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF2563EB)),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      );

                                      if (isNarrow) {
                                        return Column(
                                          crossAxisAlignment: CrossAxisAlignment.stretch,
                                          children: [
                                            btnDetalle,
                                            const SizedBox(height: 8),
                                            btnExplicar,
                                          ],
                                        );
                                      }

                                      return Row(
                                        children: [
                                          Expanded(child: btnDetalle),
                                          const SizedBox(width: 10),
                                          Expanded(child: btnExplicar),
                                        ],
                                      );
                                    },
                                  ),
                                ],
                              ),
                            ),
                          );
                        }),
                    ],
                  ),
                ),
    );
  }
}
