import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/planificacion_service.dart';
import 'reservar_mesa_plano_screen.dart';

class RecomendacionDetalleScreen extends StatefulWidget {
  final int idRecomendacion;
  final Map<String, dynamic>? recomendacionData;
  final int? idPlanificacion;
  final Map<String, dynamic>? planData;

  const RecomendacionDetalleScreen({
    super.key,
    required this.idRecomendacion,
    this.recomendacionData,
    this.idPlanificacion,
    this.planData,
  });

  @override
  State<RecomendacionDetalleScreen> createState() => _RecomendacionDetalleScreenState();
}

class _RecomendacionDetalleScreenState extends State<RecomendacionDetalleScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _rec;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.recomendacionData != null) {
      _rec = Map<String, dynamic>.from(widget.recomendacionData!);
      _isLoading = false;
    }
    _cargarDetalle();
  }

  Future<void> _cargarDetalle() async {
    try {
      final res = await PlanificacionService.instance.obtenerDetalleRecomendacion(widget.idRecomendacion);
      if (mounted) {
        setState(() {
          _rec = res;
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

  void _irAReservarMesa() {
    if (_rec == null) return;
    final idResto = AppTheme.toInt(_rec!['id_restaurante']);
    final nombreResto = _rec!['nombre_restaurante'] ?? _rec!['nombre'] ?? 'Restaurante';
    final idPlan = _rec!['id_planificacion'] ?? widget.idPlanificacion;
    final cantPersonas = widget.planData?['cantidad_personas'] ?? 2;

    if (idResto <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Esta opción no tiene un restaurante asociado.'), backgroundColor: AppTheme.warning),
      );
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ReservarMesaPlanoScreen(
          idRestaurante: idResto,
          nombreRestaurante: nombreResto.toString(),
          idPlanificacion: idPlan != null ? AppTheme.toInt(idPlan) : null,
          cantidadPersonasInicial: AppTheme.toInt(cantPersonas, 2),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final rec = _rec;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Detalle de Recomendación'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Volver a las recomendaciones',
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _isLoading && rec == null
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : _error != null && rec == null
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
                      // Breadcrumb
                      GestureDetector(
                        onTap: () => Navigator.pop(context),
                        child: const Padding(
                          padding: EdgeInsets.only(bottom: 12),
                          child: Text(
                            '← Volver a las recomendaciones',
                            style: TextStyle(color: AppTheme.textMuted, fontSize: 13, fontWeight: FontWeight.w500),
                          ),
                        ),
                      ),

                      // Tarjeta Principal de la Recomendación (Exacto a Imagen 4)
                      Container(
                        padding: const EdgeInsets.all(18),
                        decoration: AppTheme.cardDecoration,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Fila Superior: Badge + Score Box
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: rec!['tipo_recomendacion'] == 'RESTAURANTE'
                                              ? const Color(0xFFE2E8F0)
                                              : const Color(0xFFD1FAE5),
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: Text(
                                          rec['tipo_recomendacion'] == 'RESTAURANTE' ? 'RESTAURANTE' : 'PREPARACIÓN PROPIA',
                                          style: TextStyle(
                                            color: rec['tipo_recomendacion'] == 'RESTAURANTE'
                                                ? const Color(0xFF1D3557)
                                                : const Color(0xFF065F46),
                                            fontSize: 11,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(height: 10),
                                      Text(
                                        rec['nombre'] ?? rec['nombre_restaurante'] ?? 'Alternativa',
                                        style: const TextStyle(
                                          fontSize: 22,
                                          fontWeight: FontWeight.bold,
                                          color: AppTheme.textMain,
                                        ),
                                      ),
                                      if (rec['descripcion'] != null && rec['descripcion'].toString().isNotEmpty) ...[
                                        const SizedBox(height: 4),
                                        Text(
                                          rec['descripcion'].toString(),
                                          style: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 12),

                                // Score Box (91 / Puntos / 100)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8FAFC),
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: AppTheme.border),
                                  ),
                                  child: Column(
                                    children: [
                                      Text(
                                        '${AppTheme.toDouble(rec['puntuacion']).round()}',
                                        style: const TextStyle(
                                          fontSize: 26,
                                          fontWeight: FontWeight.w900,
                                          color: AppTheme.textMain,
                                          height: 1.1,
                                        ),
                                      ),
                                      const Text(
                                        'Puntos / 100',
                                        style: TextStyle(fontSize: 10, color: AppTheme.textMuted, fontWeight: FontWeight.w500),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 18),

                            // 3 Cajas Métricas Responsivas
                            LayoutBuilder(
                              builder: (context, constraints) {
                                final isNarrow = constraints.maxWidth < 340;
                                final boxCosto = Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8FAFC),
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: const Color(0xFFF1F5F9)),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text('COSTO TOTAL', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                                      const SizedBox(height: 4),
                                      FittedBox(
                                        fit: BoxFit.scaleDown,
                                        alignment: Alignment.centerLeft,
                                        child: Text(
                                          'Bs ${AppTheme.toDouble(rec['costo_total']).toStringAsFixed(2)}',
                                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.primary),
                                        ),
                                      ),
                                    ],
                                  ),
                                );

                                final boxPersona = Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8FAFC),
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: const Color(0xFFF1F5F9)),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text('COSTO / PERS.', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                                      const SizedBox(height: 4),
                                      FittedBox(
                                        fit: BoxFit.scaleDown,
                                        alignment: Alignment.centerLeft,
                                        child: Text(
                                          'Bs ${AppTheme.toDouble(rec['costo_por_persona']).toStringAsFixed(2)}',
                                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                        ),
                                      ),
                                    ],
                                  ),
                                );

                                final boxFecha = Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8FAFC),
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: const Color(0xFFF1F5F9)),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Text('FECHA CÁLCULO', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppTheme.textMuted)),
                                      const SizedBox(height: 4),
                                      FittedBox(
                                        fit: BoxFit.scaleDown,
                                        alignment: Alignment.centerLeft,
                                        child: Text(
                                          AppTheme.formatDate(rec['fecha_generacion']),
                                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                        ),
                                      ),
                                    ],
                                  ),
                                );

                                if (isNarrow) {
                                  return Column(
                                    children: [
                                      Row(
                                        children: [
                                          Expanded(child: boxCosto),
                                          const SizedBox(width: 8),
                                          Expanded(child: boxPersona),
                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      SizedBox(width: double.infinity, child: boxFecha),
                                    ],
                                  );
                                }

                                return Row(
                                  children: [
                                    Expanded(child: boxCosto),
                                    const SizedBox(width: 8),
                                    Expanded(child: boxPersona),
                                    const SizedBox(width: 8),
                                    Expanded(child: boxFecha),
                                  ],
                                );
                              },
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Card: Detalle de Platos a Consumir (Exacto a Imagen 4)
                      if (rec['tipo_recomendacion'] == 'RESTAURANTE') ...[
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: AppTheme.cardDecoration,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Encabezado de la tabla
                              Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text(
                                          'Detalle de Platos a Consumir',
                                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                        ),
                                        const SizedBox(height: 4),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: const Color(0xFFF1F5F9),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Text(
                                            (rec['nombre_restaurante'] ?? rec['nombre'] ?? '').toString().toUpperCase(),
                                            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 12),

                              // Botón "Reservar Mesa" bien acomodado y sin desbordamiento
                              SizedBox(
                                width: double.infinity,
                                child: ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: AppTheme.primary,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                    elevation: 2,
                                  ),
                                  onPressed: _irAReservarMesa,
                                  icon: const Icon(Icons.calendar_month, size: 18),
                                  label: const Text(
                                    'Reservar Mesa en el Restaurante',
                                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 16),

                              // Indicador de desplazamiento horizontal
                              Padding(
                                padding: const EdgeInsets.only(bottom: 8),
                                child: Row(
                                  children: const [
                                    Icon(Icons.swipe, size: 14, color: AppTheme.textMuted),
                                    SizedBox(width: 6),
                                    Expanded(
                                      child: Text(
                                        'Desliza horizontalmente para ver todos los detalles del plato',
                                        style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              // Tabla de Platos
                              SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: DataTable(
                                  headingRowHeight: 38,
                                  dataRowMinHeight: 44,
                                  dataRowMaxHeight: 52,
                                  columnSpacing: 18,
                                  horizontalMargin: 8,
                                  headingTextStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMuted),
                                  columns: const [
                                    DataColumn(label: Text('PLATO')),
                                    DataColumn(label: Text('RENDIMIENTO')),
                                    DataColumn(label: Text('CANTIDAD')),
                                    DataColumn(label: Text('PRECIO UNITARIO')),
                                    DataColumn(label: Text('SUBTOTAL')),
                                  ],
                                  rows: ((rec['platos'] as List<dynamic>?) ?? []).map((pRaw) {
                                    final p = pRaw as Map<String, dynamic>;
                                    final nombrePlato = p['nombre_plato'] ?? 'Plato';
                                    final rendimiento = '${p['personas_cubiertas'] ?? 1} personas';
                                    final cantidad = '${p['cantidad'] ?? 1} unidad(es)';
                                    final precioUni = 'Bs ${AppTheme.toDouble(p['precio_unitario']).toStringAsFixed(2)}';
                                    final subtotal = 'Bs ${AppTheme.toDouble(p['subtotal']).toStringAsFixed(2)}';

                                    return DataRow(cells: [
                                      DataCell(Text(nombrePlato, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13))),
                                      DataCell(Text(rendimiento, style: const TextStyle(fontSize: 12))),
                                      DataCell(Text(cantidad, style: const TextStyle(fontSize: 12))),
                                      DataCell(Text(precioUni, style: const TextStyle(fontSize: 12))),
                                      DataCell(Text(subtotal, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textMain))),
                                    ]);
                                  }).toList(),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ] else ...[
                        // Preparación Casera
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: AppTheme.cardDecoration,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Detalle de Preparación Casera',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'Esta alternativa fue calculada reuniendo las cantidades de ingredientes y consultando los mejores precios disponibles en mercados registrados.',
                                style: TextStyle(fontSize: 13, color: AppTheme.textMuted),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
    );
  }
}
