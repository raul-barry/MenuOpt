import 'package:flutter/material.dart';

import '../core/app_theme.dart';
import '../services/pedido_service.dart';
import '../services/restaurante_service.dart';

class PedidosScreen extends StatefulWidget {
  const PedidosScreen({super.key, this.initialResourceId});

  final int? initialResourceId;

  @override
  State<PedidosScreen> createState() => _PedidosScreenState();
}

class _PedidosScreenState extends State<PedidosScreen> {
  bool _notificacionAbierta = false;
  bool _isLoading = true;
  List<dynamic> _pedidos = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadPedidos();
  }

  Future<void> _loadPedidos() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final list = await PedidoService.instance.getMisPedidos();
      if (mounted) {
        setState(() {
          _pedidos = list;
          _isLoading = false;
        });
        final id = widget.initialResourceId;
        if (!_notificacionAbierta && id != null) {
          _notificacionAbierta = true;
          await _abrirPedidoNotificado(id);
        }
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

  Future<void> _abrirPedidoNotificado(int idPedido) async {
    try {
      // El detalle se obtiene con el JWT actual y el backend valida la titularidad.
      final pedido = await PedidoService.instance.getDetallePedido(idPedido);
      if (mounted) _verDetallePedido(pedido);
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'No tienes permiso para consultar este pedido o ya no está disponible.',
            ),
          ),
        );
      }
    }
  }

  Future<void> _cancelarPedido(int idPedido) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancelar Pedido'),
        content: Text('¿Está seguro de cancelar el pedido #$idPedido?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Volver'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.danger,
              foregroundColor: Colors.white,
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Sí, Cancelar'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await PedidoService.instance.cancelarPedido(idPedido);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Pedido cancelado correctamente'),
          backgroundColor: AppTheme.success,
        ),
      );
      _loadPedidos();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al cancelar pedido: $e'),
          backgroundColor: AppTheme.danger,
        ),
      );
    }
  }

  void _abrirNuevoPedidoModal() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => const Center(
        child: CircularProgressIndicator(color: AppTheme.primary),
      ),
    );

    List<dynamic> restaurantes = [];
    try {
      restaurantes = await RestauranteService.instance.getRestaurantes();
    } catch (_) {}

    if (!mounted) return;
    Navigator.pop(context); // cerrar loader

    if (restaurantes.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No hay restaurantes disponibles'),
          backgroundColor: AppTheme.warning,
        ),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _NuevoPedidoSheet(
        restaurantes: restaurantes,
        onCreated: () {
          Navigator.pop(ctx);
          _loadPedidos();
        },
      ),
    );
  }

  void _verDetallePedido(Map<String, dynamic> pedido) {
    final idPedido = pedido['id_pedido'];
    final resto =
        pedido['nombre_restaurante'] ??
        pedido['restaurante']?['nombre'] ??
        'Restaurante';
    final estado = pedido['estado'] ?? 'PENDIENTE';
    final total = pedido['total'] ?? 0;
    final items = (pedido['detalles'] as List<dynamic>?) ?? [];
    final fecha = pedido['fecha_pedido'] ?? '';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Pedido #$idPedido',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      resto,
                      style: const TextStyle(
                        color: AppTheme.textMuted,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
                AppTheme.buildBadge(estado),
              ],
            ),
            const Divider(height: 20),
            Text(
              'Platos incluidos (${items.length}):',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
            ),
            const SizedBox(height: 10),
            if (items.isEmpty)
              const Text('No se registraron platos en el detalle.')
            else
              ...items.map((it) {
                final nom = it['nombre_plato'] ?? 'Plato';
                final cant = it['cantidad'] ?? 1;
                final sub = it['subtotal'] ?? 0;
                final pu = it['precio_unitario'] ?? 0;
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '$cant x $nom (Bs $pu)',
                        style: const TextStyle(fontSize: 13),
                      ),
                      Text(
                        'Bs $sub',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                );
              }),
            const Divider(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Total Pagado/Por pagar:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                Text(
                  'Bs $total',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.primary,
                  ),
                ),
              ],
            ),
            if (fecha.toString().isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(
                'Fecha: ${fecha.toString().split('T').first}',
                style: const TextStyle(color: AppTheme.textMuted, fontSize: 12),
              ),
            ],
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cerrar'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        onPressed: _abrirNuevoPedidoModal,
        icon: const Icon(Icons.add),
        label: const Text('Hacer Pedido'),
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
                      Text(
                        'Mis Pedidos',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textMain,
                        ),
                      ),
                      Text(
                        'Historial de pedidos y compras',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppTheme.textMuted,
                        ),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.refresh),
                    tooltip: 'Recargar',
                    onPressed: _loadPedidos,
                  ),
                ],
              ),
            ),
            Expanded(
              child: _isLoading
                  ? const Center(
                      child: CircularProgressIndicator(color: AppTheme.primary),
                    )
                  : _error != null
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.error_outline,
                              size: 40,
                              color: AppTheme.danger,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              _error!,
                              textAlign: TextAlign.center,
                              style: const TextStyle(fontSize: 13),
                            ),
                            const SizedBox(height: 12),
                            ElevatedButton(
                              onPressed: _loadPedidos,
                              child: const Text('Reintentar'),
                            ),
                          ],
                        ),
                      ),
                    )
                  : _pedidos.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.receipt_long_outlined,
                            size: 48,
                            color: AppTheme.textMuted,
                          ),
                          const SizedBox(height: 10),
                          const Text(
                            'No tienes pedidos registrados actualmente.',
                            style: TextStyle(
                              fontSize: 14,
                              color: AppTheme.textMuted,
                            ),
                          ),
                          const SizedBox(height: 14),
                          ElevatedButton(
                            onPressed: _abrirNuevoPedidoModal,
                            child: const Text('Hacer un Pedido Ahora'),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadPedidos,
                      color: AppTheme.primary,
                      child: ListView.builder(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        itemCount: _pedidos.length,
                        itemBuilder: (ctx, i) {
                          final p = _pedidos[i] as Map<String, dynamic>;
                          final idPedido = p['id_pedido'];
                          final resto =
                              p['nombre_restaurante'] ??
                              p['restaurante']?['nombre'] ??
                              'Restaurante';
                          final total = p['total'] ?? 0;
                          final estado = (p['estado'] ?? 'PENDIENTE')
                              .toString();
                          final items = (p['detalles'] as List<dynamic>?) ?? [];
                          final fecha = p['fecha_pedido'] ?? '';

                          return Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            decoration: AppTheme.cardDecoration,
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.all(6),
                                            decoration: BoxDecoration(
                                              color: AppTheme.primaryLight,
                                              borderRadius:
                                                  BorderRadius.circular(8),
                                            ),
                                            child: const Icon(
                                              Icons.receipt_long,
                                              color: AppTheme.primary,
                                              size: 18,
                                            ),
                                          ),
                                          const SizedBox(width: 8),
                                          Text(
                                            'Pedido #$idPedido',
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                              fontSize: 15,
                                              color: AppTheme.textMain,
                                            ),
                                          ),
                                        ],
                                      ),
                                      AppTheme.buildBadge(estado),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    resto,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 14,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Wrap(
                                    spacing: 14,
                                    runSpacing: 4,
                                    crossAxisAlignment:
                                        WrapCrossAlignment.center,
                                    children: [
                                      Text(
                                        'Total: Bs $total',
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          color: AppTheme.primary,
                                          fontSize: 14,
                                        ),
                                      ),
                                      Text(
                                        '${items.length} producto(s)',
                                        style: const TextStyle(
                                          color: AppTheme.textMuted,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ],
                                  ),
                                  if (fecha.toString().isNotEmpty) ...[
                                    const SizedBox(height: 4),
                                    Text(
                                      'Fecha: ${fecha.toString().split('T').first}',
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: AppTheme.textMuted,
                                      ),
                                    ),
                                  ],
                                  const Divider(height: 20),
                                  Wrap(
                                    alignment: WrapAlignment.end,
                                    crossAxisAlignment:
                                        WrapCrossAlignment.center,
                                    spacing: 6,
                                    runSpacing: 4,
                                    children: [
                                      TextButton.icon(
                                        onPressed: () => _verDetallePedido(p),
                                        icon: const Icon(
                                          Icons.list_alt,
                                          size: 16,
                                        ),
                                        label: const Text(
                                          'Ver Platos',
                                          style: TextStyle(fontSize: 12),
                                        ),
                                      ),
                                      if (estado == 'PENDIENTE') ...[
                                        TextButton.icon(
                                          style: TextButton.styleFrom(
                                            foregroundColor: AppTheme.danger,
                                          ),
                                          onPressed: () =>
                                              _cancelarPedido(idPedido),
                                          icon: const Icon(
                                            Icons.cancel_outlined,
                                            size: 16,
                                          ),
                                          label: const Text(
                                            'Cancelar',
                                            style: TextStyle(fontSize: 12),
                                          ),
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

class _NuevoPedidoSheet extends StatefulWidget {
  final List<dynamic> restaurantes;
  final VoidCallback onCreated;

  const _NuevoPedidoSheet({
    required this.restaurantes,
    required this.onCreated,
  });

  @override
  State<_NuevoPedidoSheet> createState() => _NuevoPedidoSheetState();
}

class _NuevoPedidoSheetState extends State<_NuevoPedidoSheet> {
  int? _idRestaurante;
  List<dynamic> _platos = [];
  final Map<int, int> _carrito = {}; // id_plato -> cantidad
  bool _isLoadingPlatos = false;
  bool _isSaving = false;
  String? _error;
  final _obsCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    if (widget.restaurantes.isNotEmpty) {
      _idRestaurante = AppTheme.toInt(
        widget.restaurantes.first['id_restaurante'],
      );
      _cargarPlatos(_idRestaurante!);
    }
  }

  @override
  void dispose() {
    _obsCtrl.dispose();
    super.dispose();
  }

  Future<void> _cargarPlatos(int idResto) async {
    setState(() {
      _isLoadingPlatos = true;
      _platos.clear();
      _carrito.clear();
      _error = null;
    });

    try {
      final platos = await RestauranteService.instance.getPlatos(idResto);
      if (mounted) {
        setState(() {
          _platos = platos;
          _isLoadingPlatos = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Error al cargar platos del restaurante: $e';
          _isLoadingPlatos = false;
        });
      }
    }
  }

  double get _totalCalculado {
    double sum = 0.0;
    for (final plato in _platos) {
      final id = AppTheme.toInt(plato['id_plato']);
      final cant = _carrito[id] ?? 0;
      if (cant > 0) {
        final p = AppTheme.toDouble(plato['precio']);
        sum += p * cant;
      }
    }
    return sum;
  }

  Future<void> _enviarPedido() async {
    if (_idRestaurante == null) return;
    if (_carrito.isEmpty || _totalCalculado <= 0) {
      setState(() => _error = 'Debes añadir al menos 1 plato al pedido.');
      return;
    }

    setState(() {
      _isSaving = true;
      _error = null;
    });

    final detalles = <Map<String, dynamic>>[];
    _carrito.forEach((idPlato, cant) {
      if (cant > 0) {
        detalles.add({'id_plato': idPlato, 'cantidad': cant});
      }
    });

    final payload = {
      'id_restaurante': _idRestaurante,
      'detalles': detalles,
      if (_obsCtrl.text.trim().isNotEmpty)
        'observaciones': _obsCtrl.text.trim(),
    };

    try {
      await PedidoService.instance.crearPedido(payload);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('¡Pedido enviado exitosamente!'),
          backgroundColor: AppTheme.success,
        ),
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
    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      expand: false,
      builder: (ctx, scroll) => Container(
        padding: const EdgeInsets.all(20),
        child: ListView(
          controller: scroll,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Hacer Pedido Gastronómico',
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const Divider(),
            if (_error != null)
              Container(
                padding: const EdgeInsets.all(10),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: AppTheme.dangerLight,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _error!,
                  style: const TextStyle(color: AppTheme.danger, fontSize: 12),
                ),
              ),
            const Text(
              'Selecciona el Restaurante *',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
            ),
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
                  _cargarPlatos(val);
                }
              },
            ),
            const SizedBox(height: 14),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Menú y Platos Disponibles:',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Total: Bs ${_totalCalculado.toStringAsFixed(2)}',
                  style: const TextStyle(
                    color: AppTheme.primary,
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),

            if (_isLoadingPlatos)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(color: AppTheme.primary),
                ),
              )
            else if (_platos.isEmpty)
              const Padding(
                padding: EdgeInsets.all(20),
                child: Text(
                  'No hay platos activos en este restaurante.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppTheme.textMuted),
                ),
              )
            else
              ..._platos.map((plato) {
                final id = AppTheme.toInt(plato['id_plato']);
                final nom = plato['nombre'] ?? '';
                final precio = AppTheme.toDouble(plato['precio'])
                    .toStringAsFixed(2);
                final desc = plato['descripcion'] ?? '';
                final cant = _carrito[id] ?? 0;

                return Container(
                  margin: const EdgeInsets.only(bottom: 10),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: cant > 0
                        ? AppTheme.primaryLight.withValues(alpha: 0.25)
                        : AppTheme.surface,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: cant > 0 ? AppTheme.primary : AppTheme.border,
                    ),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              nom,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            Text(
                              'Bs $precio',
                              style: const TextStyle(
                                color: AppTheme.primary,
                                fontWeight: FontWeight.w600,
                                fontSize: 13,
                              ),
                            ),
                            if (desc.toString().isNotEmpty)
                              Text(
                                desc.toString(),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 11,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                          ],
                        ),
                      ),
                      Row(
                        children: [
                          if (cant > 0)
                            IconButton(
                              icon: const Icon(
                                Icons.remove_circle_outline,
                                color: AppTheme.danger,
                                size: 22,
                              ),
                              onPressed: () {
                                setState(() {
                                  if (cant > 1) {
                                    _carrito[id] = cant - 1;
                                  } else {
                                    _carrito.remove(id);
                                  }
                                });
                              },
                            ),
                          if (cant > 0)
                            Text(
                              '$cant',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                          IconButton(
                            icon: const Icon(
                              Icons.add_circle,
                              color: AppTheme.primary,
                              size: 24,
                            ),
                            onPressed: () {
                              setState(() {
                                _carrito[id] = cant + 1;
                              });
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              }),

            const SizedBox(height: 12),
            TextField(
              controller: _obsCtrl,
              decoration: const InputDecoration(
                labelText: 'Observaciones / Instrucciones de entrega',
              ),
            ),
            const SizedBox(height: 16),

            ElevatedButton(
              onPressed: _isSaving ? null : _enviarPedido,
              child: Text(
                _isSaving
                    ? 'Enviando Pedido...'
                    : 'Confirmar Pedido (Total Bs ${_totalCalculado.toStringAsFixed(2)})',
              ),
            ),
          ],
        ),
      ),
    );
  }
}
