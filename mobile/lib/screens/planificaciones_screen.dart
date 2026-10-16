import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/planificacion_service.dart';
import 'planificacion_detalle_screen.dart';

class PlanificacionesScreen extends StatefulWidget {
  final VoidCallback? onNavigateToNueva;

  const PlanificacionesScreen({super.key, this.onNavigateToNueva});

  @override
  State<PlanificacionesScreen> createState() => _PlanificacionesScreenState();
}

class _PlanificacionesScreenState extends State<PlanificacionesScreen> {
  bool _isLoading = true;
  List<dynamic> _planificaciones = [];
  String? _error;
  String _selectedFiltro = 'TODAS'; // 'TODAS', 'ACTIVA', 'CANCELADA'

  @override
  void initState() {
    super.initState();
    _loadPlanificaciones();
  }

  Future<void> _loadPlanificaciones() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final estadoParam = _selectedFiltro == 'TODAS' ? null : _selectedFiltro;
      final res = await PlanificacionService.instance.listarMisPlanificaciones(
        estado: estadoParam,
      );
      final List<dynamic> items = (res['planificaciones'] as List<dynamic>?) ??
          (res['items'] as List<dynamic>?) ??
          [];

      if (mounted) {
        setState(() {
          _planificaciones = items;
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

  void _onFilterChanged(String filtro) {
    setState(() => _selectedFiltro = filtro);
    _loadPlanificaciones();
  }

  Future<void> _cancelarPlan(int id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancelar Planificación'),
        content: Text('¿Está seguro de que desea cancelar la planificación #$id?'),
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
      await PlanificacionService.instance.cancelarPlanificacion(id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Planificación cancelada correctamente'), backgroundColor: AppTheme.success),
      );
      _loadPlanificaciones();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cancelar: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _editarPlan(Map<String, dynamic> plan) {
    final id = plan['id_planificacion'];
    final presCtrl = TextEditingController(text: plan['presupuesto'].toString());
    final comCtrl = TextEditingController(text: plan['cantidad_personas'].toString());
    final ubiCtrl = TextEditingController(text: plan['ubicacion_referencia'] ?? '');
    String tipo = plan['tipo_comida'] ?? 'ALMUERZO';

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
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Editar Planificación #$id', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
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
                    await PlanificacionService.instance.actualizarPlanificacion(id, {
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
                    _loadPlanificaciones();
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
    );
  }

  void _verDetalleYRecomendaciones(Map<String, dynamic> plan) {
    final id = AppTheme.toInt(plan['id_planificacion']);
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => PlanificacionDetalleScreen(
          idPlanificacion: id,
          initialPlan: plan,
          onUpdated: _loadPlanificaciones,
        ),
      ),
    ).then((_) {
      if (mounted) _loadPlanificaciones();
    });
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Mis Planificaciones', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textMain)),
                        Text('Gestiona tus eventos gastronómicos', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                      ],
                    ),
                  ),
                  if (widget.onNavigateToNueva != null) ...[
                    const SizedBox(width: 8),
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                      ),
                      onPressed: widget.onNavigateToNueva,
                      icon: const Icon(Icons.add, size: 16),
                      label: const Text('Nueva', style: TextStyle(fontSize: 12)),
                    ),
                  ],
                ],
              ),
            ),

            // Filtros tipo chip responsivos con scroll horizontal
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    _FilterChipBtn(
                      label: 'Todas',
                      selected: _selectedFiltro == 'TODAS',
                      onTap: () => _onFilterChanged('TODAS'),
                    ),
                    const SizedBox(width: 8),
                    _FilterChipBtn(
                      label: 'Activas',
                      selected: _selectedFiltro == 'ACTIVA',
                      onTap: () => _onFilterChanged('ACTIVA'),
                    ),
                    const SizedBox(width: 8),
                    _FilterChipBtn(
                      label: 'Canceladas',
                      selected: _selectedFiltro == 'CANCELADA',
                      onTap: () => _onFilterChanged('CANCELADA'),
                    ),
                  ],
                ),
              ),
            ),

            // Contenido lista
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
                  : _error != null
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
                                ElevatedButton(onPressed: _loadPlanificaciones, child: const Text('Reintentar')),
                              ],
                            ),
                          ),
                        )
                      : _planificaciones.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.calendar_today_outlined, size: 48, color: AppTheme.textMuted),
                                  const SizedBox(height: 10),
                                  const Text('No hay planificaciones en esta categoría', style: TextStyle(fontSize: 14, color: AppTheme.textMuted)),
                                  const SizedBox(height: 14),
                                  if (widget.onNavigateToNueva != null)
                                    ElevatedButton(
                                      onPressed: widget.onNavigateToNueva,
                                      child: const Text('Planificar Comida Ahora'),
                                    ),
                                ],
                              ),
                            )
                          : RefreshIndicator(
                              onRefresh: _loadPlanificaciones,
                              color: AppTheme.primary,
                              child: ListView.builder(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                itemCount: _planificaciones.length,
                                itemBuilder: (ctx, i) {
                                  final p = _planificaciones[i] as Map<String, dynamic>;
                                  final id = p['id_planificacion'];
                                  final tipo = p['tipo_comida'] ?? 'Comida';
                                  final comensales = p['cantidad_personas'] ?? 1;
                                  final presupuesto = p['presupuesto'] ?? 0;
                                  final estado = (p['estado'] ?? 'ACTIVA').toString();
                                  final ubicacion = p['ubicacion_referencia'] ?? '';
                                  final fecha = p['fecha_planificacion'] ?? '';

                                  return Container(
                                    margin: const EdgeInsets.only(bottom: 12),
                                    decoration: AppTheme.cardDecoration,
                                    child: Material(
                                      color: Colors.transparent,
                                      child: InkWell(
                                        borderRadius: BorderRadius.circular(16),
                                        onTap: () => _verDetalleYRecomendaciones(p),
                                        child: Padding(
                                          padding: const EdgeInsets.all(16),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                          Row(
                                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                            crossAxisAlignment: CrossAxisAlignment.center,
                                            children: [
                                              Expanded(
                                                child: Row(
                                                  children: [
                                                    Container(
                                                      padding: const EdgeInsets.all(6),
                                                      decoration: BoxDecoration(color: AppTheme.primaryLight, borderRadius: BorderRadius.circular(8)),
                                                      child: const Icon(Icons.restaurant, color: AppTheme.primary, size: 18),
                                                    ),
                                                    const SizedBox(width: 8),
                                                    Expanded(
                                                      child: Text(
                                                        'Plan #$id • $tipo',
                                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.textMain),
                                                        overflow: TextOverflow.ellipsis,
                                                        maxLines: 1,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                              const SizedBox(width: 8),
                                              AppTheme.buildBadge(estado),
                                            ],
                                          ),
                                          const SizedBox(height: 10),
                                          Wrap(
                                            spacing: 14,
                                            runSpacing: 4,
                                            crossAxisAlignment: WrapCrossAlignment.center,
                                            children: [
                                              Text('Presupuesto: Bs $presupuesto', style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primary, fontSize: 13)),
                                              Text('$comensales comensales', style: const TextStyle(fontSize: 13, color: AppTheme.textMuted)),
                                            ],
                                          ),
                                          if (ubicacion.isNotEmpty || fecha.toString().isNotEmpty) ...[
                                            const SizedBox(height: 4),
                                            Wrap(
                                              spacing: 12,
                                              runSpacing: 4,
                                              crossAxisAlignment: WrapCrossAlignment.center,
                                              children: [
                                                if (ubicacion.isNotEmpty) ...[
                                                  Row(
                                                    mainAxisSize: MainAxisSize.min,
                                                    children: [
                                                      const Icon(Icons.location_on_outlined, size: 14, color: AppTheme.textMuted),
                                                      const SizedBox(width: 4),
                                                      Text(ubicacion, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                                                    ],
                                                  ),
                                                ],
                                                if (fecha.toString().isNotEmpty) ...[
                                                  Row(
                                                    mainAxisSize: MainAxisSize.min,
                                                    children: [
                                                      const Icon(Icons.calendar_today, size: 13, color: AppTheme.textMuted),
                                                      const SizedBox(width: 4),
                                                      Text(fecha.toString().split('T').first, style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                                                    ],
                                                  ),
                                                ],
                                              ],
                                            ),
                                          ],
                                          const Divider(height: 20),
                                          Wrap(
                                            alignment: WrapAlignment.end,
                                            crossAxisAlignment: WrapCrossAlignment.center,
                                            spacing: 4,
                                            runSpacing: 4,
                                            children: [
                                              TextButton.icon(
                                                onPressed: () => _verDetalleYRecomendaciones(p),
                                                icon: const Icon(Icons.visibility_outlined, size: 16),
                                                label: const Text('Detalle / Recs', style: TextStyle(fontSize: 12)),
                                              ),
                                              if (estado == 'ACTIVA') ...[
                                                TextButton.icon(
                                                  onPressed: () => _editarPlan(p),
                                                  icon: const Icon(Icons.edit_outlined, size: 16),
                                                  label: const Text('Editar', style: TextStyle(fontSize: 12)),
                                                ),
                                                TextButton.icon(
                                                  style: TextButton.styleFrom(foregroundColor: AppTheme.danger),
                                                  onPressed: () => _cancelarPlan(id),
                                                  icon: const Icon(Icons.cancel_outlined, size: 16),
                                                  label: const Text('Cancelar', style: TextStyle(fontSize: 12)),
                                                ),
                                              ],
                                            ],
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              );
                            },

                              ),
                            ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FilterChipBtn extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _FilterChipBtn({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
        decoration: BoxDecoration(
          color: selected ? AppTheme.primary : Colors.white,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: selected ? AppTheme.primary : AppTheme.border),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: selected ? Colors.white : AppTheme.textMain,
          ),
        ),
      ),
    );
  }
}
