import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/reserva_service.dart';
import '../services/restaurante_service.dart';
import 'reservar_mesa_plano_screen.dart';

class ReservasScreen extends StatefulWidget {
  const ReservasScreen({super.key});

  @override
  State<ReservasScreen> createState() => _ReservasScreenState();
}

class _ReservasScreenState extends State<ReservasScreen> {
  bool _isLoading = true;
  List<dynamic> _reservas = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadReservas();
  }

  Future<void> _loadReservas() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final list = await ReservaService.instance.getMisReservas();
      if (mounted) {
        setState(() {
          _reservas = list;
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

  Future<void> _cancelarReserva(int idReserva) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancelar Reserva'),
        content: Text('¿Está seguro de que desea cancelar la reserva #$idReserva?'),
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
      await ReservaService.instance.cancelarReserva(idReserva);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Reserva cancelada exitosamente'), backgroundColor: AppTheme.success),
      );
      _loadReservas();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cancelar: $e'), backgroundColor: AppTheme.danger),
      );
    }
  }

  void _abrirNuevaReservaModal() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(child: CircularProgressIndicator(color: AppTheme.primary)),
    );

    List<dynamic> restaurantes = [];
    try {
      restaurantes = await RestauranteService.instance.getRestaurantes();
    } catch (_) {}

    if (!mounted) return;
    Navigator.pop(context); // cerrar loader

    if (restaurantes.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No hay restaurantes disponibles actualmente'), backgroundColor: AppTheme.warning),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Seleccionar Restaurante', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            const Text('Elige el establecimiento para consultar el plano 2D y reservar tu mesa:', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
            const Divider(height: 24),
            Flexible(
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: restaurantes.length,
                itemBuilder: (ctx, idx) {
                  final r = restaurantes[idx] as Map<String, dynamic>;
                  final idR = AppTheme.toInt(r['id_restaurante']);
                  final nom = r['nombre'] ?? 'Restaurante #$idR';
                  final dir = r['direccion'] ?? r['ubicacion'] ?? '';
                  return ListTile(
                    leading: const CircleAvatar(backgroundColor: AppTheme.primaryLight, child: Icon(Icons.restaurant, color: AppTheme.primary, size: 20)),
                    title: Text(nom, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    subtitle: dir.toString().isNotEmpty ? Text(dir.toString(), style: const TextStyle(fontSize: 12)) : null,
                    trailing: const Icon(Icons.arrow_forward_ios, size: 14, color: AppTheme.textMuted),
                    onTap: () {
                      Navigator.pop(ctx);
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ReservarMesaPlanoScreen(
                            idRestaurante: idR,
                            nombreRestaurante: nom,
                          ),
                        ),
                      ).then((_) => _loadReservas());
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }


  void _verInvitados(Map<String, dynamic> res) async {
    final idReserva = res['id_reserva'];
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => _InvitadosSheet(idReserva: idReserva),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        onPressed: _abrirNuevaReservaModal,
        icon: const Icon(Icons.add),
        label: const Text('Nueva Reserva'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Mis Reservas', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textMain)),
                      Text('Gestiona tus mesas y reservas', style: TextStyle(fontSize: 12, color: AppTheme.textMuted)),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh),
                    tooltip: 'Recargar',
                    onPressed: _loadReservas,
                  ),
                ],
              ),
            ),
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
                                ElevatedButton(onPressed: _loadReservas, child: const Text('Reintentar')),
                              ],
                            ),
                          ),
                        )
                      : _reservas.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(Icons.event_seat_outlined, size: 48, color: AppTheme.textMuted),
                                  const SizedBox(height: 10),
                                  const Text('No tienes reservas registradas.', style: TextStyle(fontSize: 14, color: AppTheme.textMuted)),
                                  const SizedBox(height: 14),
                                  ElevatedButton(
                                    onPressed: _abrirNuevaReservaModal,
                                    child: const Text('Hacer una Reserva'),
                                  ),
                                ],
                              ),
                            )
                          : RefreshIndicator(
                              onRefresh: _loadReservas,
                              color: AppTheme.primary,
                              child: ListView.builder(
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                itemCount: _reservas.length,
                                itemBuilder: (ctx, i) {
                                  final res = _reservas[i] as Map<String, dynamic>;
                                  final idReserva = res['id_reserva'];
                                  final restoNombre = res['restaurante']?['nombre'] ?? res['nombre_restaurante'] ?? 'Restaurante';
                                  final fecha = res['fecha_reserva'] ?? '';
                                  final horaInicio = res['hora_inicio'] ?? '';
                                  final horaFin = res['hora_fin'] ?? '';
                                  final personas = res['cantidad_personas'] ?? 0;
                                  final estado = (res['estado'] ?? 'PENDIENTE').toString();
                                  final mesas = (res['mesas'] as List<dynamic>?) ?? [];

                                  return Container(
                                    margin: const EdgeInsets.only(bottom: 12),
                                    decoration: AppTheme.cardDecoration,
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
                                                      child: const Icon(Icons.event_seat, color: AppTheme.primary, size: 18),
                                                    ),
                                                    const SizedBox(width: 8),
                                                    Expanded(
                                                      child: Text(
                                                        restoNombre,
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
                                              Row(
                                                mainAxisSize: MainAxisSize.min,
                                                children: [
                                                  const Icon(Icons.calendar_today, size: 14, color: AppTheme.textMuted),
                                                  const SizedBox(width: 6),
                                                  Text(fecha, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                                                ],
                                              ),
                                              Row(
                                                mainAxisSize: MainAxisSize.min,
                                                children: [
                                                  const Icon(Icons.access_time, size: 14, color: AppTheme.textMuted),
                                                  const SizedBox(width: 6),
                                                  Text('$horaInicio - $horaFin', style: const TextStyle(fontSize: 13, color: AppTheme.textMuted)),
                                                ],
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 6),
                                          Wrap(
                                            spacing: 14,
                                            runSpacing: 4,
                                            crossAxisAlignment: WrapCrossAlignment.center,
                                            children: [
                                              Row(
                                                mainAxisSize: MainAxisSize.min,
                                                children: [
                                                  const Icon(Icons.people_outline, size: 14, color: AppTheme.textMuted),
                                                  const SizedBox(width: 6),
                                                  Text('$personas personas', style: const TextStyle(fontSize: 13, color: AppTheme.textMuted)),
                                                ],
                                              ),
                                              if (mesas.isNotEmpty) ...[
                                                Text('Mesa(s): ${mesas.map((m) => m['numero'] ?? m['id_mesa']).join(', ')}', style: const TextStyle(fontSize: 12, color: AppTheme.primary, fontWeight: FontWeight.bold)),
                                              ],
                                            ],
                                          ),
                                          const Divider(height: 20),
                                          Wrap(
                                            alignment: WrapAlignment.end,
                                            crossAxisAlignment: WrapCrossAlignment.center,
                                            spacing: 6,
                                            runSpacing: 4,
                                            children: [
                                              TextButton.icon(
                                                onPressed: () => _verInvitados(res),
                                                icon: const Icon(Icons.person_add_outlined, size: 16),
                                                label: const Text('Invitados', style: TextStyle(fontSize: 12)),
                                              ),
                                              if (estado != 'CANCELADA' && estado != 'COMPLETADA') ...[
                                                TextButton.icon(
                                                  style: TextButton.styleFrom(foregroundColor: AppTheme.danger),
                                                  onPressed: () => _cancelarReserva(idReserva),
                                                  icon: const Icon(Icons.cancel_outlined, size: 16),
                                                  label: const Text('Cancelar', style: TextStyle(fontSize: 12)),
                                                ),
                                              ],
                                            ],
                                          ),
                                        ],
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

class _NuevaReservaSheet extends StatefulWidget {
  final List<dynamic> restaurantes;
  final VoidCallback onCreated;

  const _NuevaReservaSheet({required this.restaurantes, required this.onCreated});

  @override
  State<_NuevaReservaSheet> createState() => _NuevaReservaSheetState();
}

class _NuevaReservaSheetState extends State<_NuevaReservaSheet> {
  int? _idRestaurante;
  int? _idArea;
  DateTime _fecha = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _horaInicio = const TimeOfDay(hour: 12, minute: 30);
  TimeOfDay _horaFin = const TimeOfDay(hour: 14, minute: 0);
  int _personas = 2;

  List<dynamic> _areas = [];
  List<dynamic> _mesasDisponibles = [];
  final Set<int> _mesasSeleccionadas = {};

  bool _isCheckingAvailability = false;
  bool _isSaving = false;
  bool _hasChecked = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.restaurantes.isNotEmpty) {
      _idRestaurante = AppTheme.toInt(widget.restaurantes.first['id_restaurante']);
      _cargarAreas(_idRestaurante!);
    }
  }

  Future<void> _cargarAreas(int idResto) async {
    final areas = await ReservaService.instance.getAreasRestaurante(idResto);
    if (mounted) {
      setState(() {
        _areas = areas;
        _idArea = areas.isNotEmpty ? AppTheme.toInt(areas.first['id_area']) : null;
        _mesasDisponibles.clear();
        _mesasSeleccionadas.clear();
        _hasChecked = false;
      });
    }
  }

  String _formatTime(TimeOfDay t) {
    final h = t.hour.toString().padLeft(2, '0');
    final m = t.minute.toString().padLeft(2, '0');
    return '$h:$m:00';
  }

  Future<void> _consultarDisponibilidad() async {
    if (_idRestaurante == null) return;
    if (_idArea == null && _areas.isNotEmpty) {
      _idArea = AppTheme.toInt(_areas.first['id_area']);
    }

    setState(() {
      _isCheckingAvailability = true;
      _error = null;
      _mesasDisponibles.clear();
      _mesasSeleccionadas.clear();
      _hasChecked = true;
    });

    final fechaStr = _fecha.toIso8601String().split('T').first;
    final hi = _formatTime(_horaInicio);
    final hf = _formatTime(_horaFin);

    try {
      final mesas = await ReservaService.instance.getMesasDisponibles(
        _idRestaurante!,
        fechaStr,
        hi,
        hf,
        _personas,
        idArea: _idArea,
      );

      if (mounted) {
        setState(() {
          _mesasDisponibles = mesas;
          _isCheckingAvailability = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isCheckingAvailability = false;
        });
      }
    }
  }

  Future<void> _confirmarReserva() async {
    if (_idRestaurante == null) return;
    if (_idArea == null && _areas.isNotEmpty) {
      _idArea = AppTheme.toInt(_areas.first['id_area']);
    }
    if (_mesasSeleccionadas.isEmpty && _mesasDisponibles.isNotEmpty) {
      // Auto seleccionar la primera si no seleccionó manualmente
      _mesasSeleccionadas.add(AppTheme.toInt(_mesasDisponibles.first['id_mesa']));
    }

    if (_mesasSeleccionadas.isEmpty) {
      setState(() => _error = 'Debes consultar y seleccionar al menos una mesa disponible.');
      return;
    }

    setState(() {
      _isSaving = true;
      _error = null;
    });

    final fechaStr = _fecha.toIso8601String().split('T').first;
    final payload = {
      'id_restaurante': _idRestaurante,
      'id_area': _idArea ?? 1,
      'fecha_reserva': fechaStr,
      'hora_inicio': _formatTime(_horaInicio),
      'hora_fin': _formatTime(_horaFin),
      'cantidad_personas': _personas,
      'mesas': _mesasSeleccionadas.toList(),
    };

    try {
      await ReservaService.instance.crearReserva(payload);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('¡Reserva creada exitosamente!'), backgroundColor: AppTheme.success),
      );
      widget.onCreated();
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
    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Nueva Reserva de Mesa', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(context)),
              ],
            ),
            const Divider(),
            if (_error != null)
              Container(
                padding: const EdgeInsets.all(10),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(color: AppTheme.dangerLight, borderRadius: BorderRadius.circular(8)),
                child: Text(_error!, style: const TextStyle(color: AppTheme.danger, fontSize: 12)),
              ),
            // Restaurante
            const Text('Restaurante *', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            DropdownButtonFormField<int>(
              initialValue: _idRestaurante,
              decoration: const InputDecoration(),
              items: widget.restaurantes.map((r) {
                return DropdownMenuItem<int>(
                  value: AppTheme.toInt(r['id_restaurante']),
                  child: Text(r['nombre'] ?? 'Restaurante'),
                );
              }).toList(),
              onChanged: (val) {
                if (val != null) {
                  setState(() => _idRestaurante = val);
                  _cargarAreas(val);
                }
              },
            ),
            const SizedBox(height: 12),

            if (_areas.isNotEmpty) ...[
              const Text('Área / Ambiente *', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
              const SizedBox(height: 6),
              DropdownButtonFormField<int>(
                initialValue: _idArea,
                decoration: const InputDecoration(),
                items: _areas.map((a) {
                  return DropdownMenuItem<int>(
                    value: AppTheme.toInt(a['id_area']),
                    child: Text(a['nombre'] ?? 'Área'),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val != null) {
                    setState(() {
                      _idArea = val;
                      _mesasDisponibles.clear();
                      _mesasSeleccionadas.clear();
                      _hasChecked = false;
                    });
                  }
                },
              ),
              const SizedBox(height: 12),
            ],

            // Personas y Fecha
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Personas *', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 6),
                      DropdownButtonFormField<int>(
                        initialValue: _personas,
                        decoration: const InputDecoration(),
                        items: List.generate(20, (i) => i + 1).map((n) {
                          return DropdownMenuItem<int>(value: n, child: Text('$n'));
                        }).toList(),
                        onChanged: (v) {
                          if (v != null) setState(() => _personas = v);
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Fecha *', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 6),
                      OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
                        ),
                        onPressed: () async {
                          final picked = await showDatePicker(
                            context: context,
                            initialDate: _fecha,
                            firstDate: DateTime.now(),
                            lastDate: DateTime.now().add(const Duration(days: 90)),
                          );
                          if (picked != null) setState(() => _fecha = picked);
                        },
                        icon: const Icon(Icons.calendar_today, size: 16),
                        label: Text(_fecha.toIso8601String().split('T').first, style: const TextStyle(fontSize: 12)),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Horario
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Hora Inicio', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 6),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final picked = await showTimePicker(context: context, initialTime: _horaInicio);
                          if (picked != null) setState(() => _horaInicio = picked);
                        },
                        icon: const Icon(Icons.access_time, size: 16),
                        label: Text(_horaInicio.format(context), style: const TextStyle(fontSize: 12)),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Hora Fin', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 6),
                      OutlinedButton.icon(
                        onPressed: () async {
                          final picked = await showTimePicker(context: context, initialTime: _horaFin);
                          if (picked != null) setState(() => _horaFin = picked);
                        },
                        icon: const Icon(Icons.access_time, size: 16),
                        label: Text(_horaFin.format(context), style: const TextStyle(fontSize: 12)),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Botón consultar disponibilidad
            OutlinedButton.icon(
              onPressed: _isCheckingAvailability ? null : _consultarDisponibilidad,
              icon: _isCheckingAvailability
                  ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.primary))
                  : const Icon(Icons.search, size: 18),
              label: Text(_isCheckingAvailability ? 'Consultando mesas...' : 'Consultar Disponibilidad de Mesas (CU20)'),
            ),
            const SizedBox(height: 12),

            // Mesas disponibles
            if (_mesasDisponibles.isNotEmpty) ...[
              const Text('Mesas Disponibles (selecciona una o varias):', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _mesasDisponibles.map((m) {
                  final idMesa = AppTheme.toInt(m['id_mesa']);
                  final numMesa = m['numero'] ?? '#$idMesa';
                  final cap = m['capacidad'] ?? '';
                  final isSel = _mesasSeleccionadas.contains(idMesa);
                  final isDisponible = m['seleccionable'] == true || m['estado_disponibilidad'] == 'DISPONIBLE';

                  return ChoiceChip(
                    label: Text(isDisponible ? 'Mesa $numMesa (cap. $cap)' : 'Mesa $numMesa (Ocupada)'),
                    selected: isSel,
                    selectedColor: AppTheme.primaryLight,
                    onSelected: isDisponible
                        ? (val) {
                            setState(() {
                              if (val) {
                                _mesasSeleccionadas.add(idMesa);
                              } else {
                                _mesasSeleccionadas.remove(idMesa);
                              }
                            });
                          }
                        : null,
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
            ] else if (_hasChecked && !_isCheckingAvailability) ...[
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.amber.shade300),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.orange, size: 20),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'No hay mesas disponibles en esta área para el horario y personas indicadas. Intente con otro horario o área.',
                        style: TextStyle(fontSize: 12, color: Colors.black87),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            ElevatedButton(
              onPressed: _isSaving ? null : _confirmarReserva,
              child: Text(_isSaving ? 'Guardando Reserva...' : 'Confirmar Reserva (CU21)'),
            ),
          ],
        ),
      ),
    );
  }
}

class _InvitadosSheet extends StatefulWidget {
  final int idReserva;

  const _InvitadosSheet({required this.idReserva});

  @override
  State<_InvitadosSheet> createState() => _InvitadosSheetState();
}

class _InvitadosSheetState extends State<_InvitadosSheet> {
  bool _isLoading = true;
  List<dynamic> _invitados = [];
  final _nombreCtrl = TextEditingController();
  final _correoCtrl = TextEditingController();
  bool _isAdding = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadInvitados();
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _correoCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadInvitados() async {
    setState(() => _isLoading = true);
    try {
      final list = await ReservaService.instance.getInvitados(widget.idReserva);
      if (mounted) {
        setState(() {
          _invitados = list;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _agregarInvitado() async {
    final nom = _nombreCtrl.text.trim();
    final cor = _correoCtrl.text.trim();
    if (nom.isEmpty) {
      setState(() => _error = 'Ingrese el nombre del invitado');
      return;
    }

    setState(() {
      _isAdding = true;
      _error = null;
    });

    try {
      await ReservaService.instance.agregarInvitado(widget.idReserva, {
        'nombre': nom,
        if (cor.isNotEmpty) 'correo': cor,
      });
      _nombreCtrl.clear();
      _correoCtrl.clear();
      if (!mounted) return;
      setState(() => _isAdding = false);
      _loadInvitados();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isAdding = false;
        _error = e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Invitados Reserva #${widget.idReserva}', style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
              IconButton(icon: const Icon(Icons.close), onPressed: () => Navigator.pop(context)),
            ],
          ),
          const Divider(),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(_error!, style: const TextStyle(color: AppTheme.danger, fontSize: 12)),
            ),
          Row(
            children: [
              Expanded(
                child: TextField(controller: _nombreCtrl, decoration: const InputDecoration(labelText: 'Nombre *')),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextField(controller: _correoCtrl, decoration: const InputDecoration(labelText: 'Correo')),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14)),
                onPressed: _isAdding ? null : _agregarInvitado,
                child: const Icon(Icons.add, size: 20),
              ),
            ],
          ),
          const SizedBox(height: 14),
          if (_isLoading)
            const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator(color: AppTheme.primary)))
          else if (_invitados.isEmpty)
            const Padding(padding: EdgeInsets.all(20), child: Text('No hay invitados registrados aún.', textAlign: TextAlign.center, style: TextStyle(color: AppTheme.textMuted)))
          else
            ..._invitados.map((inv) {
              return ListTile(
                dense: true,
                leading: const CircleAvatar(radius: 14, backgroundColor: AppTheme.primaryLight, child: Icon(Icons.person, size: 16, color: AppTheme.primary)),
                title: Text(inv['nombre'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text(inv['correo'] ?? 'Sin correo'),
              );
            }),
        ],
      ),
    );
  }
}
