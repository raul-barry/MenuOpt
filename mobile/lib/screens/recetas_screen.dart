import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/receta_service.dart';

class RecetasScreen extends StatefulWidget {
  const RecetasScreen({super.key});

  @override
  State<RecetasScreen> createState() => _RecetasScreenState();
}

class _RecetasScreenState extends State<RecetasScreen> {
  final _recetaService = RecetaService.instance;
  final _iaTextController = TextEditingController();
  final _searchController = TextEditingController();

  bool _isLoading = true;
  String? _error;
  List<dynamic> _recetas = [];

  // Filtros
  String _filtroCategoria = 'TODAS';
  String _busqueda = '';

  // Asistente IA
  int _comensalesIA = 2;
  bool _consultandoIA = false;
  Map<String, dynamic>? _resultadoIA;
  String? _errorIA;

  final List<String> _sugerenciasIA = [
    'Pollo, arroz, tomate y cebolla',
    'Carne de res, papas y ensalada',
    'Pescado, arroz y plátano',
    'Huevos, queso y jamón',
  ];

  @override
  void initState() {
    super.initState();
    _cargarRecetas();
  }

  @override
  void dispose() {
    _iaTextController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _cargarRecetas() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await _recetaService.getRecetas(
        tipoComida: _filtroCategoria,
        busqueda: _busqueda,
      );
      setState(() {
        _recetas = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _ejecutarConsultaIA() async {
    final texto = _iaTextController.text.trim();
    if (texto.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor escribe los ingredientes que tienes en casa')),
      );
      return;
    }

    setState(() {
      _consultandoIA = true;
      _errorIA = null;
    });

    try {
      final respuesta = await _recetaService.consultarIA(
        mensaje: texto,
        comensales: _comensalesIA,
      );
      setState(() {
        _resultadoIA = respuesta;
        _consultandoIA = false;
      });
    } catch (e) {
      setState(() {
        _errorIA = e.toString();
        _consultandoIA = false;
      });
    }
  }

  void _verDetalleReceta(Map<String, dynamic> receta) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _DetalleRecetaModal(receta: receta),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Biblioteca de Recetas'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Actualizar',
            onPressed: _cargarRecetas,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _cargarRecetas,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _buildIACard(),
              const SizedBox(height: 20),
              _buildFiltrosYBusqueda(),
              const SizedBox(height: 16),
              _buildCatalogoRecetas(),
            ],
          ),
        ),
      ),
    );
  }

  // --- TARJETA ASISTENTE CULINARIO IA ---
  Widget _buildIACard() {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFFF7ED), Color(0xFFFFFFFF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFFFEDD5), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primary.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.psychology, color: AppTheme.primary, size: 26),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Asistente Culinario IA',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.secondary,
                      ),
                    ),
                    Text(
                      '¿Qué tienes en casa? La IA te dice qué cocinar y dónde comprar lo que falte.',
                      style: TextStyle(fontSize: 12, color: AppTheme.textMuted),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),

          // Chips rápidos
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _sugerenciasIA.map((sug) {
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ActionChip(
                    label: Text(sug, style: const TextStyle(fontSize: 11, color: AppTheme.secondary)),
                    backgroundColor: Colors.white,
                    side: const BorderSide(color: Color(0xFFFED7AA)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    onPressed: () {
                      _iaTextController.text = sug;
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 12),

          // Input de ingredientes
          TextField(
            controller: _iaTextController,
            maxLines: 2,
            decoration: InputDecoration(
              hintText: 'Ej. Tengo 500g de pechuga de pollo, 2 tazas de arroz, tomate...',
              hintStyle: const TextStyle(fontSize: 13, color: AppTheme.textMuted),
              filled: true,
              fillColor: Colors.white,
              contentPadding: const EdgeInsets.all(12),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppTheme.border),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFFED7AA)),
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Selector de comensales y botón
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppTheme.border),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.people_outline, size: 18, color: AppTheme.textMuted),
                    const SizedBox(width: 6),
                    IconButton(
                      icon: const Icon(Icons.remove, size: 16),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                      onPressed: _comensalesIA > 1 ? () => setState(() => _comensalesIA--) : null,
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      child: Text(
                        '$_comensalesIA',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.add, size: 16),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                      onPressed: _comensalesIA < 20 ? () => setState(() => _comensalesIA++) : null,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _consultandoIA ? null : _ejecutarConsultaIA,
                  icon: _consultandoIA
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.auto_awesome, size: 18),
                  label: Text(_consultandoIA ? 'Pensando...' : 'Consultar IA'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primary,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                ),
              ),
            ],
          ),

          if (_errorIA != null) ...[
            const SizedBox(height: 10),
            Text(
              _errorIA!,
              style: const TextStyle(color: Colors.red, fontSize: 12),
            ),
          ],

          // Resultado del Asistente IA
          if (_resultadoIA != null) ...[
            const SizedBox(height: 16),
            const Divider(color: Color(0xFFFED7AA)),
            const SizedBox(height: 8),
            _buildResultadoIACard(),
          ],
        ],
      ),
    );
  }

  Widget _buildResultadoIACard() {
    final res = _resultadoIA!;
    final mensaje = res['mensaje'] as String? ?? '';
    final receta = res['receta_sugerida'] as Map<String, dynamic>?;
    final faltantes = (res['ingredientes_faltantes'] as List<dynamic>?) ?? [];
    final tiendas = (res['tiendas_recomendadas'] as List<dynamic>?) ?? [];
    final comensalesCalculados = res['personas_estimadas'] ?? _comensalesIA;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFFDBA74)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.verified, color: AppTheme.primary, size: 20),
              const SizedBox(width: 8),
              const Text(
                'Sugerencia Culinaria',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: AppTheme.secondary),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.primaryLight,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  'Para $comensalesCalculados personas',
                  style: const TextStyle(color: AppTheme.primary, fontSize: 11, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(mensaje, style: const TextStyle(fontSize: 13, height: 1.4, color: AppTheme.textMain)),
          
          if (receta != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Row(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: receta['imagen_url'] != null && (receta['imagen_url'] as String).isNotEmpty
                        ? Image.network(
                            receta['imagen_url'],
                            width: 60,
                            height: 60,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => _placeholderIcon(),
                          )
                        : _placeholderIcon(),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          receta['nombre'] ?? '',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${receta['tiempo_preparacion_min'] ?? 0} min • ${receta['tipo_comida'] ?? 'PLATO'}',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
                        ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () => _verDetalleReceta(receta),
                    child: const Text('Ver Ficha', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ),
          ],

          // Ingredientes faltantes
          if (faltantes.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text(
              '⚠️ Ingredientes que te faltan:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFFB45309)),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: faltantes.map((f) {
                final nombre = f['ingrediente'] ?? '';
                final cant = f['cantidad'] ?? '';
                final unidad = f['unidad_medida'] ?? '';
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF3C7),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: const Color(0xFFFDE68A)),
                  ),
                  child: Text(
                    '$nombre ($cant $unidad)',
                    style: const TextStyle(fontSize: 11, color: Color(0xFF92400E), fontWeight: FontWeight.w500),
                  ),
                );
              }).toList(),
            ),
          ],

          // Tiendas recomendadas en Santa Cruz (CU16)
          if (tiendas.isNotEmpty) ...[
            const SizedBox(height: 14),
            Row(
              children: const [
                Icon(Icons.storefront, size: 16, color: AppTheme.primary),
                SizedBox(width: 6),
                Text(
                  'Dónde comprar al mejor precio (Santa Cruz):',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppTheme.secondary),
                ),
              ],
            ),
            const SizedBox(height: 6),
            ...tiendas.map((t) {
              final nombreTienda = t['lugar_nombre'] ?? '';
              final direccion = t['direccion'] ?? 'Santa Cruz';
              final ingrediente = t['ingrediente'] ?? '';
              final precio = t['precio_unitario'];
              final unidad = t['unidad_medida'] ?? 'ud';
              final precioTexto = precio != null ? 'Bs. $precio / $unidad' : '';

              return Container(
                margin: const EdgeInsets.only(top: 4),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0FDF4),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFBBF7D0)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            nombreTienda,
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFF166534)),
                          ),
                          Text(
                            '$ingrediente • $direccion',
                            style: const TextStyle(fontSize: 11, color: Color(0xFF15803D)),
                          ),
                        ],
                      ),
                    ),
                    if (precioTexto.isNotEmpty)
                      Text(
                        precioTexto,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xFF166534)),
                      ),
                  ],
                ),
              );
            }),
          ],
        ],
      ),
    );
  }

  // --- FILTROS Y BÚSQUEDA ---
  Widget _buildFiltrosYBusqueda() {
    final categorias = ['TODAS', 'ALMUERZO', 'CENA', 'DESAYUNO'];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Buscador
        TextField(
          controller: _searchController,
          onSubmitted: (val) {
            _busqueda = val;
            _cargarRecetas();
          },
          decoration: InputDecoration(
            hintText: 'Buscar receta por nombre...',
            prefixIcon: const Icon(Icons.search, size: 20),
            suffixIcon: _searchController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear, size: 18),
                    onPressed: () {
                      _searchController.clear();
                      _busqueda = '';
                      _cargarRecetas();
                    },
                  )
                : null,
            filled: true,
            fillColor: Colors.white,
            contentPadding: const EdgeInsets.symmetric(vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppTheme.border),
            ),
          ),
        ),
        const SizedBox(height: 10),

        // Filtro categorías
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: categorias.map((cat) {
              final activa = _filtroCategoria == cat;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(
                    cat == 'TODAS' ? 'Todas' : cat[0] + cat.substring(1).toLowerCase(),
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: activa ? FontWeight.bold : FontWeight.normal,
                      color: activa ? Colors.white : AppTheme.secondary,
                    ),
                  ),
                  selected: activa,
                  selectedColor: AppTheme.primary,
                  backgroundColor: Colors.white,
                  side: BorderSide(color: activa ? AppTheme.primary : AppTheme.border),
                  onSelected: (selected) {
                    if (selected) {
                      setState(() => _filtroCategoria = cat);
                      _cargarRecetas();
                    }
                  },
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  // --- CATÁLOGO DE RECETAS ---
  Widget _buildCatalogoRecetas() {
    if (_isLoading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(40),
          child: CircularProgressIndicator(color: AppTheme.primary),
        ),
      );
    }

    if (_error != null) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            const Icon(Icons.error_outline, size: 40, color: Colors.red),
            const SizedBox(height: 8),
            Text(_error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 13)),
            const SizedBox(height: 12),
            ElevatedButton(onPressed: _cargarRecetas, child: const Text('Reintentar')),
          ],
        ),
      );
    }

    if (_recetas.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(32),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Column(
          children: [
            Icon(Icons.menu_book, size: 44, color: AppTheme.textMuted),
            SizedBox(height: 10),
            Text('No se encontraron recetas', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            SizedBox(height: 4),
            Text('Intenta con otro filtro o término de búsqueda', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
          ],
        ),
      );
    }

    return Column(
      children: _recetas.map((r) {
        final receta = r as Map<String, dynamic>;
        return _buildRecetaCard(receta);
      }).toList(),
    );
  }

  Widget _buildRecetaCard(Map<String, dynamic> receta) {
    final nombre = receta['nombre'] ?? '';
    final descripcion = receta['descripcion'] ?? '';
    final tipoComida = receta['tipo_comida'] ?? 'ALMUERZO';
    final porciones = receta['porciones_base'] ?? 2;
    final tiempo = receta['tiempo_preparacion_min'] ?? 30;
    final dificultad = receta['dificultad'] ?? 'MEDIO';
    final imagenUrl = receta['imagen_url'] as String?;

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () => _verDetalleReceta(receta),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Imagen de cabecera con Badge de categoría
            Stack(
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(14)),
                  child: imagenUrl != null && imagenUrl.isNotEmpty
                      ? Image.network(
                          imagenUrl,
                          height: 150,
                          width: double.infinity,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => _cardPlaceholderImage(),
                        )
                      : _cardPlaceholderImage(),
                ),
                Positioned(
                  top: 10,
                  right: 10,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.65),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      tipoComida,
                      style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),

            Padding(
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    nombre,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.secondary),
                  ),
                  if (descripcion.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      descripcion,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 12, color: AppTheme.textMuted, height: 1.3),
                    ),
                  ],
                  const SizedBox(height: 12),

                  // Fila de metadatos rápidos
                  Row(
                    children: [
                      _buildMetaChip(Icons.timer_outlined, '$tiempo min'),
                      const SizedBox(width: 8),
                      _buildMetaChip(Icons.group_outlined, '$porciones pers.'),
                      const SizedBox(width: 8),
                      _buildMetaChip(Icons.signal_cellular_alt, dificultad),
                      const Spacer(),
                      const Text(
                        'Ver receta →',
                        style: TextStyle(
                          color: AppTheme.primary,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetaChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: AppTheme.textMuted),
          const SizedBox(width: 4),
          Text(label, style: const TextStyle(fontSize: 11, color: AppTheme.secondary, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _placeholderIcon() {
    return Container(
      width: 60,
      height: 60,
      color: AppTheme.primaryLight,
      child: const Icon(Icons.restaurant, color: AppTheme.primary),
    );
  }

  Widget _cardPlaceholderImage() {
    return Container(
      height: 150,
      width: double.infinity,
      color: AppTheme.primaryLight,
      child: const Center(
        child: Icon(Icons.restaurant_menu, size: 48, color: AppTheme.primary),
      ),
    );
  }
}

// --- MODAL DE DETALLE COMPLETO DE RECETA ---
class _DetalleRecetaModal extends StatelessWidget {
  final Map<String, dynamic> receta;

  const _DetalleRecetaModal({required this.receta});

  @override
  Widget build(BuildContext context) {
    final nombre = receta['nombre'] ?? '';
    final descripcion = receta['descripcion'] ?? '';
    final tipoComida = receta['tipo_comida'] ?? 'ALMUERZO';
    final porciones = receta['porciones_base'] ?? 2;
    final tiempo = receta['tiempo_preparacion_min'] ?? 30;
    final dificultad = receta['dificultad'] ?? 'MEDIO';
    final imagenUrl = receta['imagen_url'] as String?;
    final ingredientes = (receta['ingredientes'] as List<dynamic>?) ?? [];
    final instrucciones = receta['instrucciones'] as String? ?? 'Preparar y sazonar a gusto.';

    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.88,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // Barra de arrastre
          Container(
            margin: const EdgeInsets.symmetric(vertical: 8),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.grey.shade300,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Imagen grande
                  if (imagenUrl != null && imagenUrl.isNotEmpty) ...[
                    ClipRRect(
                      borderRadius: BorderRadius.circular(14),
                      child: Image.network(
                        imagenUrl,
                        height: 200,
                        width: double.infinity,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryLight,
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          tipoComida,
                          style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 11),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          'Dificultad $dificultad',
                          style: const TextStyle(color: AppTheme.secondary, fontSize: 11),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  Text(
                    nombre,
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.secondary),
                  ),

                  if (descripcion.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      descripcion,
                      style: const TextStyle(fontSize: 13, color: AppTheme.textMuted, height: 1.4),
                    ),
                  ],

                  const SizedBox(height: 14),
                  Row(
                    children: [
                      _buildInfoBox(Icons.timer_outlined, '$tiempo min', 'Tiempo'),
                      const SizedBox(width: 10),
                      _buildInfoBox(Icons.people_alt_outlined, '$porciones personas', 'Porciones'),
                    ],
                  ),

                  const SizedBox(height: 20),
                  const Text(
                    'Ingredientes necesarios',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.secondary),
                  ),
                  const SizedBox(height: 10),

                  if (ingredientes.isEmpty)
                    const Text('No hay ingredientes registrados.', style: TextStyle(color: AppTheme.textMuted, fontSize: 13))
                  else
                    ...ingredientes.map((ing) {
                      final item = ing as Map<String, dynamic>;
                      final ingObj = item['ingrediente'] as Map<String, dynamic>?;
                      final nombreIng = ingObj?['nombre'] ?? item['nombre'] ?? 'Ingrediente';
                      final cant = item['cantidad_base'] ?? item['cantidad'] ?? '';
                      final unidad = ingObj?['unidad_medida'] ?? item['unidad_medida'] ?? '';

                      return Container(
                        margin: const EdgeInsets.only(bottom: 6),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.check_circle_outline, size: 16, color: AppTheme.primary),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                nombreIng,
                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                              ),
                            ),
                            Text(
                              '$cant $unidad',
                              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.textMuted),
                            ),
                          ],
                        ),
                      );
                    }),

                  const SizedBox(height: 20),
                  const Text(
                    'Instrucciones paso a paso',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.secondary),
                  ),
                  const SizedBox(height: 10),

                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFFBEB),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFFDE68A)),
                    ),
                    child: Text(
                      instrucciones,
                      style: const TextStyle(fontSize: 13, height: 1.5, color: Color(0xFF78350F)),
                    ),
                  ),

                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.secondary,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                      child: const Text('Cerrar'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoBox(IconData icon, String value, String title) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Row(
          children: [
            Icon(icon, size: 20, color: AppTheme.primary),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 10, color: AppTheme.textMuted)),
                Text(value, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.secondary)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
