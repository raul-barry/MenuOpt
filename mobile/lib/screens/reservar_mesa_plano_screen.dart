import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/reserva_service.dart';

class ReservarMesaPlanoScreen extends StatefulWidget {
  final int idRestaurante;
  final String nombreRestaurante;
  final int? idPlanificacion;
  final int cantidadPersonasInicial;
  final List<dynamic>? initialAreas;
  final Map<String, dynamic>? initialDisponibilidad;

  const ReservarMesaPlanoScreen({
    super.key,
    required this.idRestaurante,
    required this.nombreRestaurante,
    this.idPlanificacion,
    this.cantidadPersonasInicial = 2,
    this.initialAreas,
    this.initialDisponibilidad,
  });

  @override
  State<ReservarMesaPlanoScreen> createState() => _ReservarMesaPlanoScreenState();
}

class _ReservarMesaPlanoScreenState extends State<ReservarMesaPlanoScreen> {
  // Filtros de Consulta
  late DateTime _fecha;
  TimeOfDay _horaInicio = const TimeOfDay(hour: 20, minute: 0);
  TimeOfDay _horaFin = const TimeOfDay(hour: 22, minute: 0);
  late int _personas;
  int? _idAreaSeleccionada;

  List<dynamic> _areas = [];
  Map<String, dynamic>? _disponibilidad;
  bool _isLoadingAreas = true;
  bool _isConsulting = false;
  bool _isConfirming = false;
  String? _error;
  String? _mensajeExito;

  // Selección de mesas
  final Set<int> _mesasSeleccionadasIds = {};
  Map<String, dynamic>? _combinacionSeleccionada;
  final TextEditingController _observacionesCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _personas = math.max(1, widget.cantidadPersonasInicial);
    _fecha = DateTime.now().add(const Duration(days: 1));
    if (widget.initialAreas != null) {
      _areas = List<dynamic>.from(widget.initialAreas!);
      _isLoadingAreas = false;
      if (_areas.isNotEmpty) {
        _idAreaSeleccionada = _areas.first['id_area'];
      }
    }
    if (widget.initialDisponibilidad != null) {
      _disponibilidad = Map<String, dynamic>.from(widget.initialDisponibilidad!);
    }
    if (widget.initialAreas == null) {
      _cargarAreasYDisponibilidad();
    }
  }

  @override
  void dispose() {
    _observacionesCtrl.dispose();
    super.dispose();
  }

  String _formatTime(TimeOfDay t) {
    final h = t.hour.toString().padLeft(2, '0');
    final m = t.minute.toString().padLeft(2, '0');
    return '$h:$m:00';
  }

  String _formatTimeDisplay(TimeOfDay t) {
    final h = t.hour.toString().padLeft(2, '0');
    final m = t.minute.toString().padLeft(2, '0');
    return '$h:$m';
  }

  String _formatFechaIso(DateTime d) {
    final y = d.year.toString().padLeft(4, '0');
    final m = d.month.toString().padLeft(2, '0');
    final dia = d.day.toString().padLeft(2, '0');
    return '$y-$m-$dia';
  }

  String _formatFechaDisplay(DateTime d) {
    final dia = d.day.toString().padLeft(2, '0');
    final m = d.month.toString().padLeft(2, '0');
    return '$dia/$m/${d.year}';
  }

  Future<void> _cargarAreasYDisponibilidad() async {
    setState(() {
      _isLoadingAreas = true;
      _error = null;
    });

    try {
      final areas = await ReservaService.instance.getAreasRestaurante(widget.idRestaurante);
      if (mounted) {
        setState(() {
          _areas = areas;
          if (areas.isNotEmpty) {
            _idAreaSeleccionada = AppTheme.toInt(areas.first['id_area']);
          }
          _isLoadingAreas = false;
        });
      }

      if (_idAreaSeleccionada != null) {
        await _consultarDisponibilidad();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Error al cargar áreas: $e';
          _isLoadingAreas = false;
        });
      }
    }
  }

  Future<void> _consultarDisponibilidad() async {
    if (_idAreaSeleccionada == null) return;

    setState(() {
      _isConsulting = true;
      _error = null;
      _mesasSeleccionadasIds.clear();
      _combinacionSeleccionada = null;
    });

    final fechaStr = _formatFechaIso(_fecha);
    final hi = _formatTime(_horaInicio);
    final hf = _formatTime(_horaFin);

    try {
      final disp = await ReservaService.instance.consultarDisponibilidad(
        idRestaurante: widget.idRestaurante,
        fecha: fechaStr,
        horaInicio: hi,
        horaFin: hf,
        cantidadPersonas: _personas,
        idArea: _idAreaSeleccionada,
      );

      if (mounted) {
        setState(() {
          _disponibilidad = disp;
          _isConsulting = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Error al consultar disponibilidad: $e';
          _isConsulting = false;
        });
      }
    }
  }

  void _seleccionarArea(int idArea) {
    if (_idAreaSeleccionada == idArea) return;
    setState(() {
      _idAreaSeleccionada = idArea;
    });
    _consultarDisponibilidad();
  }

  int _getMesasLibresArea() {
    if (_disponibilidad == null) return 0;
    final mesas = (_disponibilidad!['mesas'] as List<dynamic>?) ?? [];
    return mesas.where((m) {
      final estado = m['estado_disponibilidad'] ?? 'DISPONIBLE';
      final cap = AppTheme.toInt(m['capacidad']);
      return estado != 'NO_DISPONIBLE' && cap >= _personas;
    }).length;
  }

  void _toggleMesa(Map<String, dynamic> mesa) {
    final idMesa = AppTheme.toInt(mesa['id_mesa']);
    final estado = mesa['estado_disponibilidad'] ?? 'DISPONIBLE';
    final cap = AppTheme.toInt(mesa['capacidad']);

    // Si está no disponible, no permitir
    if (estado == 'NO_DISPONIBLE') {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Esta mesa ya se encuentra reservada en este horario.'), backgroundColor: AppTheme.danger),
      );
      return;
    }

    // Verificar si es compatible o parte de una combinación
    final bool esCompatible = cap >= _personas;
    final bool esParteComb = _esParteDeCombinacionApta(idMesa);

    if (!esCompatible && !esParteComb) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Esta mesa tiene capacidad para $cap comensales (insuficiente para $_personas personas).'),
          backgroundColor: AppTheme.warning,
        ),
      );
      return;
    }

    setState(() {
      if (_mesasSeleccionadasIds.contains(idMesa)) {
        _mesasSeleccionadasIds.remove(idMesa);
        _combinacionSeleccionada = null;
      } else {
        // En selección individual, limpia previa y asigna esta
        _mesasSeleccionadasIds.clear();
        _mesasSeleccionadasIds.add(idMesa);
        _combinacionSeleccionada = null;
      }
    });
  }

  bool _esParteDeCombinacionApta(int idMesa) {
    if (_disponibilidad == null) return false;
    final combs = (_disponibilidad!['combinaciones'] as List<dynamic>?) ?? [];
    for (final c in combs) {
      final mesas = (c['mesas'] as List<dynamic>?) ?? [];
      final cap = AppTheme.toInt(c['capacidad_total']);
      final bool disp = c['disponible'] ?? true;
      if (disp && cap >= _personas && mesas.map((m) => AppTheme.toInt(m)).contains(idMesa)) {
        return true;
      }
    }
    return false;
  }

  void _seleccionarCombinacion(Map<String, dynamic> comb) {
    final bool disp = comb['disponible'] ?? true;
    final int cap = AppTheme.toInt(comb['capacidad_total']);

    if (!disp) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Esta combinación contiene mesas no disponibles.'), backgroundColor: AppTheme.danger),
      );
      return;
    }

    if (cap < _personas) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Capacidad insuficiente ($cap comensales < $_personas solicitados).'), backgroundColor: AppTheme.warning),
      );
      return;
    }

    final mesas = (comb['mesas'] as List<dynamic>?)?.map((m) => AppTheme.toInt(m)).toList() ?? [];

    setState(() {
      _mesasSeleccionadasIds.clear();
      _mesasSeleccionadasIds.addAll(mesas);
      _combinacionSeleccionada = comb;
    });
  }

  void _limpiarSeleccion() {
    setState(() {
      _mesasSeleccionadasIds.clear();
      _combinacionSeleccionada = null;
    });
  }

  Future<void> _confirmarReserva() async {
    if (_mesasSeleccionadasIds.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor, seleccione una mesa en el plano.'), backgroundColor: AppTheme.warning),
      );
      return;
    }

    setState(() => _isConfirming = true);

    final payload = {
      'id_restaurante': widget.idRestaurante,
      'id_area': _idAreaSeleccionada ?? 1,
      'fecha_reserva': _formatFechaIso(_fecha),
      'hora_inicio': _formatTime(_horaInicio),
      'hora_fin': _formatTime(_horaFin),
      'cantidad_personas': _personas,
      'mesas': _mesasSeleccionadasIds.toList(),
      if (widget.idPlanificacion != null) 'id_planificacion': widget.idPlanificacion,
      if (_observacionesCtrl.text.trim().isNotEmpty) 'observaciones': _observacionesCtrl.text.trim(),
    };

    try {
      final res = await ReservaService.instance.crearReserva(payload);
      if (!mounted) return;
      setState(() {
        _isConfirming = false;
        _mensajeExito = '¡Reserva #${res['id_reserva'] ?? ''} confirmada exitosamente!';
      });

      // Diálogo de confirmación
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Row(
            children: [
              Icon(Icons.check_circle, color: AppTheme.success, size: 28),
              SizedBox(width: 8),
              Text('¡Reserva Confirmada!', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Tu mesa ha sido reservada con éxito en ${widget.nombreRestaurante}.'),
              const SizedBox(height: 8),
              Text('Fecha: ${_formatFechaDisplay(_fecha)}'),
              Text('Horario: ${_formatTimeDisplay(_horaInicio)} - ${_formatTimeDisplay(_horaFin)}'),
              Text('Comensales: $_personas personas'),
              Text('Mesa(s): ${_getTextoMesasSeleccionadas()}'),
            ],
          ),
          actions: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary, foregroundColor: Colors.white),
              onPressed: () {
                Navigator.pop(ctx); // cerrar dialogo
                Navigator.pop(context); // volver al detalle
              },
              child: const Text('Aceptar'),
            ),
          ],
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() => _isConfirming = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al crear reserva: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  String _getTextoMesasSeleccionadas() {
    if (_disponibilidad == null) return _mesasSeleccionadasIds.join(', ');
    final mesas = (_disponibilidad!['mesas'] as List<dynamic>?) ?? [];
    final nums = mesas
        .where((m) => _mesasSeleccionadasIds.contains(AppTheme.toInt(m['id_mesa'])))
        .map((m) => 'Mesa ${m['numero']}')
        .toList();
    return nums.isNotEmpty ? nums.join(' + ') : _mesasSeleccionadasIds.join(', ');
  }

  int _getCapacidadTotalSeleccionada() {
    if (_disponibilidad == null) return 0;
    final mesas = (_disponibilidad!['mesas'] as List<dynamic>?) ?? [];
    return mesas
        .where((m) => _mesasSeleccionadasIds.contains(AppTheme.toInt(m['id_mesa'])))
        .fold(0, (sum, m) => sum + AppTheme.toInt(m['capacidad']));
  }

  Future<void> _elegirFecha() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _fecha,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 90)),
      builder: (context, child) => Theme(
        data: Theme.of(context).copyWith(
          colorScheme: const ColorScheme.light(primary: AppTheme.primary),
        ),
        child: child!,
      ),
    );
    if (picked != null) {
      setState(() => _fecha = picked);
      _consultarDisponibilidad();
    }
  }

  Future<void> _elegirHoraInicio() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _horaInicio,
      builder: (context, child) => Theme(
        data: Theme.of(context).copyWith(
          colorScheme: const ColorScheme.light(primary: AppTheme.primary),
        ),
        child: child!,
      ),
    );
    if (picked != null) {
      setState(() {
        _horaInicio = picked;
        // Auto ajustar hora fin 2 horas despues
        final hf = (picked.hour + 2) % 24;
        _horaFin = TimeOfDay(hour: hf, minute: picked.minute);
      });
      _consultarDisponibilidad();
    }
  }

  Future<void> _elegirHoraFin() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _horaFin,
      builder: (context, child) => Theme(
        data: Theme.of(context).copyWith(
          colorScheme: const ColorScheme.light(primary: AppTheme.primary),
        ),
        child: child!,
      ),
    );
    if (picked != null) {
      setState(() => _horaFin = picked);
      _consultarDisponibilidad();
    }
  }

  @override
  Widget build(BuildContext context) {
    final disp = _disponibilidad;
    final mesas = (disp?['mesas'] as List<dynamic>?) ?? [];
    final combinaciones = (disp?['combinaciones'] as List<dynamic>?) ?? [];

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text('Reservar — ${widget.nombreRestaurante}'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          tooltip: 'Volver',
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _isLoadingAreas
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Header (Exacto a Imagen 5)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    InkWell(
                      onTap: () => Navigator.pop(context),
                      borderRadius: BorderRadius.circular(6),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          border: Border.all(color: AppTheme.border),
                          borderRadius: BorderRadius.circular(6),
                          color: Colors.white,
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.arrow_back, size: 14, color: AppTheme.textMain),
                            SizedBox(width: 4),
                            Text('Volver', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.calendar_month, color: AppTheme.primary, size: 20),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  'Reservar Mesa — ${widget.nombreRestaurante}',
                                  style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold, color: AppTheme.textMain),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 3),
                          const Text(
                            'Seleccione fecha, horario, área y comensales para consultar la disponibilidad en tiempo real sobre el plano 2D.',
                            style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                if (_mensajeExito != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppTheme.successLight,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.success),
                    ),
                    child: Text(
                      _mensajeExito!,
                      style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                if (_error != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppTheme.dangerLight,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.danger),
                    ),
                    child: Text(
                      _error!,
                      style: const TextStyle(color: AppTheme.danger, fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                // Card de Filtros de Consulta (Exacto a Imagen 5)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: AppTheme.cardDecoration,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Fila 1: Fecha y Horarios
                      Row(
                        children: [
                          // Fecha
                          Expanded(
                            child: _buildInputBox(
                              label: 'Fecha *',
                              icon: Icons.calendar_today,
                              text: _formatFechaDisplay(_fecha),
                              onTap: _elegirFecha,
                            ),
                          ),
                          const SizedBox(width: 8),
                          // Hora Inicio
                          Expanded(
                            child: _buildInputBox(
                              label: 'Hora de Inicio *',
                              icon: Icons.access_time,
                              text: _formatTimeDisplay(_horaInicio),
                              onTap: _elegirHoraInicio,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),

                      // Fila 2: Hora Fin y Personas
                      Row(
                        children: [
                          Expanded(
                            child: _buildInputBox(
                              label: 'Hora de Fin *',
                              icon: Icons.access_time,
                              text: _formatTimeDisplay(_horaFin),
                              onTap: _elegirHoraFin,
                            ),
                          ),
                          const SizedBox(width: 8),
                          // Personas selector
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Personas *', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMain)),
                                const SizedBox(height: 4),
                                Container(
                                  height: 44,
                                  padding: const EdgeInsets.symmetric(horizontal: 10),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(color: const Color(0xFFD8D8D8)),
                                  ),
                                  child: DropdownButtonHideUnderline(
                                    child: DropdownButton<int>(
                                      value: _personas,
                                      isExpanded: true,
                                      items: List.generate(24, (i) => i + 1).map((n) {
                                        return DropdownMenuItem(value: n, child: Text('$n personas', style: const TextStyle(fontSize: 13)));
                                      }).toList(),
                                      onChanged: (v) {
                                        if (v != null) {
                                          setState(() => _personas = v);
                                          _consultarDisponibilidad();
                                        }
                                      },
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),

                      // Botón Consultar Disponibilidad
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.primary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          onPressed: _isConsulting ? null : _consultarDisponibilidad,
                          icon: _isConsulting
                              ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : const Icon(Icons.search, size: 18),
                          label: Text(_isConsulting ? 'Consultando disponibilidad...' : 'Ver Mesas Disponibles'),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Pestañas de Áreas estilo Excel (Exacto a Imagen 5)
                      const Text(
                        'AMBIENTE DEL RESTAURANTE (PESTAÑAS DE ÁREAS):',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF475569), letterSpacing: 0.4),
                      ),
                      const SizedBox(height: 8),

                      if (_areas.isEmpty)
                        const Text('No se registraron áreas para este restaurante.', style: TextStyle(fontSize: 12, color: AppTheme.textMuted))
                      else
                        SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: _areas.map((a) {
                              final idA = AppTheme.toInt(a['id_area']);
                              final nombreA = a['nombre'] ?? 'Área';
                              final bool isActive = _idAreaSeleccionada == idA;
                              final int libres = isActive ? _getMesasLibresArea() : 0;

                              return Padding(
                                padding: const EdgeInsets.only(right: 6),
                                child: InkWell(
                                  onTap: () => _seleccionarArea(idA),
                                  borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                                    decoration: BoxDecoration(
                                      color: isActive ? Colors.white : const Color(0xFFE2E8F0),
                                      borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
                                      border: Border.all(
                                        color: isActive ? AppTheme.primary : const Color(0xFFCBD5E1),
                                        width: isActive ? 1.8 : 1.0,
                                      ),
                                    ),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Icon(Icons.storefront_outlined, size: 15, color: isActive ? AppTheme.primary : const Color(0xFF475569)),
                                        const SizedBox(width: 6),
                                        Text(
                                          nombreA,
                                          style: TextStyle(
                                            fontSize: 13,
                                            fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
                                            color: isActive ? AppTheme.primary : const Color(0xFF334155),
                                          ),
                                        ),
                                        if (isActive && disp != null) ...[
                                          const SizedBox(width: 6),
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: const Color(0xFFDCFCE7),
                                              borderRadius: BorderRadius.circular(10),
                                            ),
                                            child: Text(
                                              '$libres libres',
                                              style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF166534)),
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Leyenda de Estados Visuales (Exacto a Imagen 5)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final itemMaxWidth = constraints.maxWidth;
                      return Wrap(
                        spacing: 16,
                        runSpacing: 8,
                        children: [
                          _buildLegendItem(maxWidth: itemMaxWidth, color: const Color(0xFF10B981), isDashed: false, label: 'Disponible', sub: '(Apta para reservar)'),
                          _buildLegendItem(maxWidth: itemMaxWidth, color: const Color(0xFFEF4444), isDashed: true, label: 'No disponible', sub: '(Reservada en este horario)'),
                          _buildLegendItem(maxWidth: itemMaxWidth, color: const Color(0xFFF59E0B), isDotted: true, label: 'No compatible', sub: '(Capacidad inadecuada)'),
                          _buildLegendItem(maxWidth: itemMaxWidth, color: const Color(0xFF2563EB), isSolidBox: true, label: 'Seleccionada', sub: ''),
                        ],
                      );
                    },
                  ),
                ),
                const SizedBox(height: 16),

                // Lienzo 2D del Plano (Exacto a Imagen 5)
                Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppTheme.border),
                  ),
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    children: [
                      // Encabezado del Lienzo con instrucción de zoom
                      LayoutBuilder(
                        builder: (context, c) {
                          if (c.maxWidth < 340) {
                            return const Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Plano 2D Interactivo', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF475569))),
                                SizedBox(height: 2),
                                Text('Pellizca para zoom / Arrastra', style: TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                              ],
                            );
                          }
                          return const Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Text('Plano 2D Interactivo', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF475569))),
                              ),
                              SizedBox(width: 8),
                              Text('Pellizca para zoom / Arrastra', style: TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                            ],
                          );
                        },
                      ),
                      const SizedBox(height: 8),

                      // Canvas Viewport interactivo
                      ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          width: double.infinity,
                          height: 380,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFF94A3B8), width: 1.5),
                          ),
                          child: InteractiveViewer(
                            boundaryMargin: const EdgeInsets.all(20),
                            minScale: 0.8,
                            maxScale: 2.5,
                            child: SizedBox(
                              width: 600,
                              height: 380,
                              child: Stack(
                                children: [
                                  // Fondo cuadrícula arquitectónica
                                  Positioned.fill(
                                    child: CustomPaint(
                                      painter: _GridBackgroundPainter(),
                                    ),
                                  ),

                                  // Capa de Líneas de Combinaciones autorizadas
                                  if (combinaciones.isNotEmpty)
                                    Positioned.fill(
                                      child: CustomPaint(
                                        painter: _CombinacionesLinesPainter(
                                          combinaciones: combinaciones,
                                          mesas: mesas,
                                          mesasSeleccionadasIds: _mesasSeleccionadasIds,
                                        ),
                                      ),
                                    ),

                                  // Mesas colocadas en sus coordenadas normalizadas (posicion_x, posicion_y)
                                  if (mesas.isEmpty && !_isConsulting)
                                    const Center(
                                      child: Text(
                                        'No hay mesas configuradas en este ambiente.',
                                        style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                                      ),
                                    )
                                  else
                                    ...mesas.map((mRaw) {
                                      final m = mRaw as Map<String, dynamic>;
                                      final idMesa = AppTheme.toInt(m['id_mesa']);
                                      final posX = AppTheme.toDouble(m['posicion_x'], 0.5);
                                      final posY = AppTheme.toDouble(m['posicion_y'], 0.5);
                                      final rot = AppTheme.toDouble(m['rotacion'], 0.0);
                                      final cap = AppTheme.toInt(m['capacidad'], 2);
                                      final forma = (m['forma'] ?? 'CUADRADA').toString().toUpperCase();
                                      final numero = (m['numero'] ?? m['id_mesa']).toString();
                                      final estado = (m['estado_disponibilidad'] ?? 'DISPONIBLE').toString();

                                      final isSelected = _mesasSeleccionadasIds.contains(idMesa);
                                      final isOccupied = estado == 'NO_DISPONIBLE';
                                      final isApta = cap >= _personas;
                                      final isCombApta = _esParteDeCombinacionApta(idMesa);
                                      final isIncompatible = !isApta && !isCombApta && !isOccupied;

                                      return Positioned(
                                        left: posX * 600,
                                        top: posY * 380,
                                        child: FractionalTranslation(
                                          translation: const Offset(-0.5, -0.5),
                                          child: GestureDetector(
                                            onTap: () => _toggleMesa(m),
                                            child: Transform.rotate(
                                              angle: rot * (math.pi / 180),
                                              child: Column(
                                                mainAxisSize: MainAxisSize.min,
                                                children: [
                                                  // Mesa SVG Arquitectónica
                                                  _MesaVisual(
                                                    forma: forma,
                                                    capacidad: cap,
                                                    numero: numero,
                                                    isSelected: isSelected,
                                                    isOccupied: isOccupied,
                                                    isIncompatible: isIncompatible,
                                                    isAvailable: isApta && !isOccupied,
                                                  ),
                                                  const SizedBox(height: 2),

                                                  // Badge Flotante Semáforo (Contrarrotado)
                                                  Transform.rotate(
                                                    angle: -rot * (math.pi / 180),
                                                    child: _buildMesaStatusTag(
                                                      isSelected: isSelected,
                                                      isOccupied: isOccupied,
                                                      isIncompatible: isIncompatible,
                                                      isCombApta: isCombApta && !isApta,
                                                      capacidad: cap,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ),
                                        ),
                                      );
                                    }),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Opciones de Combinaciones de Mesas (CU20, CU21)
                if (combinaciones.isNotEmpty) ...[
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: AppTheme.cardDecoration,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.link, color: AppTheme.primary, size: 18),
                            SizedBox(width: 6),
                            Expanded(
                              child: Text('Combinaciones Disponibles (Grupos Mayores)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Si su grupo supera la capacidad de una mesa individual, puede optar por combinar mesas:',
                          style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
                        ),
                        const SizedBox(height: 8),
                        ...combinaciones.map((cRaw) {
                          final c = cRaw as Map<String, dynamic>;
                          final nums = (c['numeros_mesas'] as List<dynamic>?)?.join(' + ') ?? 'Mesas';
                          final cap = c['capacidad_total'] ?? 0;
                          final bool dispComb = c['disponible'] ?? true;
                          final bool isSelectedComb = _combinacionSeleccionada != null &&
                              _combinacionSeleccionada!['id_combinacion'] == c['id_combinacion'];

                          return Container(
                            margin: const EdgeInsets.only(bottom: 6),
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                            decoration: BoxDecoration(
                              color: isSelectedComb ? const Color(0xFFEFF6FF) : Colors.white,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: isSelectedComb ? const Color(0xFF2563EB) : AppTheme.border),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text('Mesas $nums', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                                      Text('Capacidad conjunta: $cap personas', style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 8),
                                ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: isSelectedComb ? const Color(0xFF2563EB) : (dispComb ? AppTheme.primary : Colors.grey),
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  ),
                                  onPressed: dispComb ? () => _seleccionarCombinacion(c) : null,
                                  child: Text(isSelectedComb ? 'Seleccionada' : (dispComb ? 'Elegir' : 'Ocupada'), style: const TextStyle(fontSize: 11)),
                                ),
                              ],
                            ),
                          );
                        }),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Panel de Resumen y Confirmación de Reserva (Exacto a Imagen 5)
                if (_mesasSeleccionadasIds.isNotEmpty) ...[
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.primary, width: 1.5),
                      boxShadow: const [
                        BoxShadow(
                          color: Color.fromRGBO(255, 111, 0, 0.08),
                          blurRadius: 10,
                          offset: Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.receipt_long, color: AppTheme.primary, size: 20),
                            SizedBox(width: 6),
                            Expanded(
                              child: Text('Resumen de la Reserva', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.primary)),
                            ),
                          ],
                        ),
                        const Divider(height: 20),

                        // Datos clave
                        Text('Restaurante: ${widget.nombreRestaurante}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        const SizedBox(height: 4),
                        Text('Mesa(s) seleccionada(s): ${_getTextoMesasSeleccionadas()}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppTheme.primary)),
                        Text('Capacidad total: ${_getCapacidadTotalSeleccionada()} personas', style: const TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                        const SizedBox(height: 6),
                        Text('Fecha y Horario: ${_formatFechaDisplay(_fecha)} | ${_formatTimeDisplay(_horaInicio)} - ${_formatTimeDisplay(_horaFin)}', style: const TextStyle(fontSize: 12)),
                        Text('Comensales: $_personas personas', style: const TextStyle(fontSize: 12)),
                        const SizedBox(height: 12),

                        // Observaciones
                        TextField(
                          controller: _observacionesCtrl,
                          decoration: const InputDecoration(
                            labelText: 'Observaciones o peticiones especiales (opcional)',
                            hintText: 'Ej: Cumpleaños, comensal en silla de ruedas, etc.',
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Botones Limpiar y Confirmar
                        LayoutBuilder(
                          builder: (context, c) {
                            if (c.maxWidth < 280) {
                              return Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  OutlinedButton(
                                    onPressed: _limpiarSeleccion,
                                    child: const Text('Limpiar Selección'),
                                  ),
                                  const SizedBox(height: 8),
                                  ElevatedButton.icon(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.primary,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(vertical: 12),
                                    ),
                                    onPressed: _isConfirming ? null : _confirmarReserva,
                                    icon: _isConfirming
                                        ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                        : const Icon(Icons.check, size: 18),
                                    label: Text(_isConfirming ? 'Procesando...' : 'Confirmar Reserva'),
                                  ),
                                ],
                              );
                            }
                            return Row(
                              children: [
                                Expanded(
                                  child: OutlinedButton(
                                    onPressed: _limpiarSeleccion,
                                    child: const Text('Limpiar Selección'),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: ElevatedButton.icon(
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppTheme.primary,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(vertical: 12),
                                    ),
                                    onPressed: _isConfirming ? null : _confirmarReserva,
                                    icon: _isConfirming
                                        ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                        : const Icon(Icons.check, size: 18),
                                    label: Text(_isConfirming ? 'Procesando...' : 'Confirmar Reserva'),
                                  ),
                                ),
                              ],
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
    );
  }

  Widget _buildInputBox({
    required String label,
    required IconData icon,
    required String text,
    required VoidCallback onTap,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMain)),
        const SizedBox(height: 4),
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(10),
          child: Container(
            height: 44,
            padding: const EdgeInsets.symmetric(horizontal: 10),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFD8D8D8)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    alignment: Alignment.centerLeft,
                    child: Text(text, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textMain)),
                  ),
                ),
                const SizedBox(width: 4),
                Icon(icon, size: 16, color: AppTheme.textMuted),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLegendItem({
    double? maxWidth,
    required Color color,
    bool isDashed = false,
    bool isDotted = false,
    bool isSolidBox = false,
    required String label,
    required String sub,
  }) {
    return ConstrainedBox(
      constraints: BoxConstraints(
        maxWidth: maxWidth ?? double.infinity,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 2),
            width: 14,
            height: 14,
            decoration: BoxDecoration(
              color: isSolidBox ? color : Colors.white,
              borderRadius: BorderRadius.circular(3),
              border: Border.all(
                color: color,
                width: 2,
                style: (isDashed || isDotted) ? BorderStyle.solid : BorderStyle.solid,
              ),
            ),
          ),
          const SizedBox(width: 6),
          Flexible(
            child: RichText(
              softWrap: true,
              text: TextSpan(
                children: [
                  TextSpan(text: label, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.textMain)),
                  if (sub.isNotEmpty) TextSpan(text: ' $sub', style: const TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMesaStatusTag({
    required bool isSelected,
    required bool isOccupied,
    required bool isIncompatible,
    required bool isCombApta,
    required int capacidad,
  }) {
    if (isSelected) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(color: const Color(0xFF2563EB), borderRadius: BorderRadius.circular(6)),
        child: const Text('Elegida', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
      );
    }
    if (isOccupied) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(color: const Color(0xFFEF4444), borderRadius: BorderRadius.circular(6)),
        child: const Text('Ocupada', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
      );
    }
    if (isCombApta) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(color: const Color(0xFF0284C7), borderRadius: BorderRadius.circular(6)),
        child: const Text('🔗 Comb.', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
      );
    }
    if (isIncompatible) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(color: const Color(0xFFF59E0B), borderRadius: BorderRadius.circular(6)),
        child: Text('${capacidad}p', style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
      );
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(color: const Color(0xFF10B981), borderRadius: BorderRadius.circular(6)),
      child: const Text('Libre', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
    );
  }
}

// Widget Arquitectónico de Mesa y Sillas (Exacto a MesaSvgComponent en web)
class _MesaVisual extends StatelessWidget {
  final String forma;
  final int capacidad;
  final String numero;
  final bool isSelected;
  final bool isOccupied;
  final bool isIncompatible;
  final bool isAvailable;

  const _MesaVisual({
    required this.forma,
    required this.capacidad,
    required this.numero,
    required this.isSelected,
    required this.isOccupied,
    required this.isIncompatible,
    required this.isAvailable,
  });

  @override
  Widget build(BuildContext context) {
    // Colores según semáforo del plano 2D
    final Color colorBorde;
    final Color colorFondo;
    final Color colorTexto;

    if (isSelected) {
      colorBorde = const Color(0xFF2563EB);
      colorFondo = const Color(0xFFEFF6FF);
      colorTexto = const Color(0xFF1E40AF);
    } else if (isOccupied) {
      colorBorde = const Color(0xFFEF4444);
      colorFondo = const Color(0xFFFFF1F2);
      colorTexto = const Color(0xFF991B1B);
    } else if (isIncompatible) {
      colorBorde = const Color(0xFFF59E0B);
      colorFondo = const Color(0xFFFFFBEB);
      colorTexto = const Color(0xFF92400E);
    } else {
      colorBorde = const Color(0xFF10B981);
      colorFondo = Colors.white;
      colorTexto = const Color(0xFF065F46);
    }

    final double width = forma == 'RECTANGULAR' ? 76 : (forma == 'REDONDA' ? 56 : 56);
    final double height = forma == 'RECTANGULAR' ? 44 : 56;

    return CustomPaint(
      size: Size(width + 24, height + 24),
      painter: _MesaSvgPainter(
        forma: forma,
        capacidad: capacidad,
        numero: numero,
        bordeColor: colorBorde,
        fondoColor: colorFondo,
        textoColor: colorTexto,
        isOccupied: isOccupied,
      ),
    );
  }
}

// Painter que dibuja la mesa central y sus sillas alrededor
class _MesaSvgPainter extends CustomPainter {
  final String forma;
  final int capacidad;
  final String numero;
  final Color bordeColor;
  final Color fondoColor;
  final Color textoColor;
  final bool isOccupied;

  _MesaSvgPainter({
    required this.forma,
    required this.capacidad,
    required this.numero,
    required this.bordeColor,
    required this.fondoColor,
    required this.textoColor,
    required this.isOccupied,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);

    final fillPaint = Paint()
      ..color = fondoColor
      ..style = PaintingStyle.fill;

    final strokePaint = Paint()
      ..color = bordeColor
      ..strokeWidth = 2.2
      ..style = PaintingStyle.stroke;

    final chairPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    final chairStrokePaint = Paint()
      ..color = bordeColor
      ..strokeWidth = 1.8
      ..style = PaintingStyle.stroke;

    // Dimensiones de la mesa central
    final double mw = forma == 'RECTANGULAR' ? 52 : 38;
    final double mh = 38;

    // 1. Dibujar sillas alrededor
    if (forma == 'REDONDA') {
      final double rMesa = 19;
      final double rSilla = capacidad <= 2 ? 6.5 : (capacidad <= 4 ? 6.0 : 5.0);
      final double distCentro = rMesa + rSilla * 0.7;

      for (int i = 0; i < capacidad; i++) {
        final double angle = (2 * math.pi * i) / capacidad - math.pi / 2;
        final Offset cCenter = Offset(
          center.dx + distCentro * math.cos(angle),
          center.dy + distCentro * math.sin(angle),
        );
        canvas.drawCircle(cCenter, rSilla, chairPaint);
        canvas.drawCircle(cCenter, rSilla, chairStrokePaint);
      }
    } else {
      // Sillas en lados superior e inferior
      final int sillasTop = (capacidad / 2).ceil();
      final int sillasBottom = capacidad - sillasTop;
      final double rSilla = 5.0;

      for (int i = 0; i < sillasTop; i++) {
        final double cx = center.dx - mw / 2 + (mw / (sillasTop + 1)) * (i + 1);
        final double cy = center.dy - mh / 2 - rSilla * 0.7;
        canvas.drawCircle(Offset(cx, cy), rSilla, chairPaint);
        canvas.drawCircle(Offset(cx, cy), rSilla, chairStrokePaint);
      }

      for (int i = 0; i < sillasBottom; i++) {
        final double cx = center.dx - mw / 2 + (mw / (sillasBottom + 1)) * (i + 1);
        final double cy = center.dy + mh / 2 + rSilla * 0.7;
        canvas.drawCircle(Offset(cx, cy), rSilla, chairPaint);
        canvas.drawCircle(Offset(cx, cy), rSilla, chairStrokePaint);
      }
    }

    // 2. Dibujar mesa central
    if (forma == 'REDONDA') {
      canvas.drawCircle(center, 19, fillPaint);
      canvas.drawCircle(center, 19, strokePaint);
    } else {
      final rect = Rect.fromCenter(center: center, width: mw, height: mh);
      final rrect = RRect.fromRectAndRadius(rect, const Radius.circular(6));
      canvas.drawRRect(rrect, fillPaint);
      canvas.drawRRect(rrect, strokePaint);
    }

    // 3. Dibujar número en el centro
    final textSpan = TextSpan(
      text: numero,
      style: TextStyle(
        color: textoColor,
        fontSize: 13,
        fontWeight: FontWeight.bold,
      ),
    );
    final textPainter = TextPainter(
      text: textSpan,
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(center.dx - textPainter.width / 2, center.dy - textPainter.height / 2),
    );
  }

  @override
  bool shouldRepaint(covariant _MesaSvgPainter oldDelegate) {
    return oldDelegate.forma != forma ||
        oldDelegate.capacidad != capacidad ||
        oldDelegate.numero != numero ||
        oldDelegate.bordeColor != bordeColor ||
        oldDelegate.fondoColor != fondoColor;
  }
}

// Painter para el fondo cuadrícula de arquitectura
class _GridBackgroundPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final dotPaint = Paint()
      ..color = const Color(0xFFCBD5E1)
      ..style = PaintingStyle.fill;

    const double step = 24.0;
    for (double x = 0; x < size.width; x += step) {
      for (double y = 0; y < size.height; y += step) {
        canvas.drawCircle(Offset(x, y), 1.2, dotPaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// Painter para dibujar líneas de conexión entre combinaciones autorizadas
class _CombinacionesLinesPainter extends CustomPainter {
  final List<dynamic> combinaciones;
  final List<dynamic> mesas;
  final Set<int> mesasSeleccionadasIds;

  _CombinacionesLinesPainter({
    required this.combinaciones,
    required this.mesas,
    required this.mesasSeleccionadasIds,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    final mesasMap = <int, Map<String, dynamic>>{};
    for (final m in mesas) {
      mesasMap[AppTheme.toInt(m['id_mesa'])] = m as Map<String, dynamic>;
    }

    for (final c in combinaciones) {
      final mIds = (c['mesas'] as List<dynamic>?)?.map((id) => AppTheme.toInt(id)).toList() ?? [];
      if (mIds.length == 2 && mesasMap.containsKey(mIds[0]) && mesasMap.containsKey(mIds[1])) {
        final m1 = mesasMap[mIds[0]]!;
        final m2 = mesasMap[mIds[1]]!;

        final p1 = Offset(
          AppTheme.toDouble(m1['posicion_x'], 0.5) * size.width,
          AppTheme.toDouble(m1['posicion_y'], 0.5) * size.height,
        );
        final p2 = Offset(
          AppTheme.toDouble(m2['posicion_x'], 0.5) * size.width,
          AppTheme.toDouble(m2['posicion_y'], 0.5) * size.height,
        );

        final bool isSelected = mesasSeleccionadasIds.contains(mIds[0]) && mesasSeleccionadasIds.contains(mIds[1]);
        paint.color = isSelected ? const Color(0xFF2563EB) : const Color(0xFF0284C7).withValues(alpha: 0.4);

        canvas.drawLine(p1, p2, paint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant _CombinacionesLinesPainter oldDelegate) {
    return oldDelegate.mesasSeleccionadasIds != mesasSeleccionadasIds;
  }
}
