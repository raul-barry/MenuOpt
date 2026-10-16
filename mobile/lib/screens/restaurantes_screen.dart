import 'package:flutter/material.dart';
import '../services/restaurante_service.dart';

class RestaurantesScreen extends StatefulWidget {
  const RestaurantesScreen({super.key});

  @override
  State<RestaurantesScreen> createState() => _RestaurantesScreenState();
}

class _RestaurantesScreenState extends State<RestaurantesScreen> {
  bool _isLoading = true;
  List<dynamic> _restaurantes = [];
  String? _error;

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
      final list = await RestauranteService.instance.getRestaurantes();
      setState(() {
        _restaurantes = list;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _verPlatos(Map<String, dynamic> resto) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _PlatosSheet(resto: resto),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.red),
              const SizedBox(height: 12),
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 12),
              ElevatedButton(onPressed: _loadData, child: const Text('Reintentar')),
            ],
          ),
        ),
      );
    }

    if (_restaurantes.isEmpty) {
      return const Center(
        child: Text('No hay restaurantes registrados actualmente.'),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _restaurantes.length,
        itemBuilder: (ctx, i) {
          final r = _restaurantes[i] as Map<String, dynamic>;
          final nombre = r['nombre'] ?? 'Sin nombre';
          final direccion = r['direccion'] ?? 'Dirección no especificada';
          final telefono = r['telefono'] ?? '';
          final estado = r['estado'] ?? 'ACTIVO';

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              leading: CircleAvatar(
                backgroundColor: const Color(0xFFD32F2F).withValues(alpha: 0.1),
                child: const Icon(Icons.storefront, color: Color(0xFFD32F2F)),
              ),
              title: Text(
                nombre,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.location_on_outlined, size: 14, color: Colors.grey),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(direccion, style: const TextStyle(fontSize: 13)),
                      ),
                    ],
                  ),
                  if (telefono.isNotEmpty) ...[
                    const SizedBox(height: 2),
                    Row(
                      children: [
                        const Icon(Icons.phone_outlined, size: 14, color: Colors.grey),
                        const SizedBox(width: 4),
                        Text(telefono, style: const TextStyle(fontSize: 13)),
                      ],
                    ),
                  ],
                ],
              ),
              trailing: Chip(
                label: Text(
                  estado,
                  style: TextStyle(
                    fontSize: 11,
                    color: estado == 'ACTIVO' ? Colors.green.shade800 : Colors.red.shade800,
                  ),
                ),
                backgroundColor: estado == 'ACTIVO' ? Colors.green.shade50 : Colors.red.shade50,
              ),
              onTap: () => _verPlatos(r),
            ),
          );
        },
      ),
    );
  }
}

class _PlatosSheet extends StatefulWidget {
  final Map<String, dynamic> resto;
  const _PlatosSheet({required this.resto});

  @override
  State<_PlatosSheet> createState() => _PlatosSheetState();
}

class _PlatosSheetState extends State<_PlatosSheet> {
  bool _isLoading = true;
  List<dynamic> _platos = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadPlatos();
  }

  Future<void> _loadPlatos() async {
    try {
      final list = await RestauranteService.instance.getPlatos(widget.resto['id_restaurante']);
      setState(() {
        _platos = list;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final nombre = widget.resto['nombre'] ?? '';

    return DraggableScrollableSheet(
      initialChildSize: 0.65,
      maxChildSize: 0.9,
      minChildSize: 0.4,
      expand: false,
      builder: (ctx, scrollCtrl) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade300,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Menú - $nombre',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            const Divider(),
            if (_isLoading)
              const Expanded(child: Center(child: CircularProgressIndicator()))
            else if (_error != null)
              Expanded(child: Center(child: Text(_error!)))
            else if (_platos.isEmpty)
              const Expanded(child: Center(child: Text('No hay platos registrados.')))
            else
              Expanded(
                child: ListView.builder(
                  controller: scrollCtrl,
                  itemCount: _platos.length,
                  itemBuilder: (c, i) {
                    final p = _platos[i] as Map<String, dynamic>;
                    final platoNombre = p['nombre'] ?? 'Plato';
                    final precio = p['precio'] ?? 0;
                    final cat = p['categoria']?['nombre'] ?? '';
                    final desc = p['descripcion'] ?? '';

                    return Card(
                      elevation: 1,
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: const Icon(Icons.fastfood, color: Color(0xFFD32F2F)),
                        title: Text(platoNombre, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (cat.isNotEmpty)
                              Text(cat, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                            if (desc.isNotEmpty)
                              Text(desc, style: const TextStyle(fontSize: 12)),
                          ],
                        ),
                        trailing: Text(
                          '$precio Bs.',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                            color: Color(0xFFD32F2F),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
