import 'package:flutter/material.dart';
import '../core/app_theme.dart';
import '../services/asistente_service.dart';
import '../services/planificacion_service.dart';

class AsistenteScreen extends StatefulWidget {
  const AsistenteScreen({super.key});

  @override
  State<AsistenteScreen> createState() => _AsistenteScreenState();
}

class _AsistenteScreenState extends State<AsistenteScreen> {
  final _textCtrl = TextEditingController();
  final List<_ChatMessage> _messages = [];
  bool _isLoading = false;
  bool _isCreatingPlan = false;

  final List<String> _sugerencias = [
    'Quiero almorzar silpancho para 1 persona con presupuesto de 150 bs en 16 de julio',
    'Cena para 2 personas con presupuesto de 110 bs en Chacos',
    'Recomiéndame platos con presupuesto de 120 bs para 1 persona',
  ];

  @override
  void initState() {
    super.initState();
    _messages.add(
      _ChatMessage(
        text: '¡Hola! Soy el asistente inteligente de MenuOpt. ¿Qué tipo de comida, dieta o presupuesto estás buscando hoy?',
        isUser: false,
      ),
    );
  }

  @override
  void dispose() {
    _textCtrl.dispose();
    super.dispose();
  }

  Future<void> _sendMessage([String? prefilledText]) async {
    final text = (prefilledText ?? _textCtrl.text).trim();
    if (text.isEmpty) return;

    if (prefilledText == null) {
      _textCtrl.clear();
    }

    setState(() {
      _messages.add(_ChatMessage(text: text, isUser: true));
      _isLoading = true;
    });

    try {
      final res = await AsistenteService.instance.interpretar(text);
      final botMsg = res['mensaje_asistente'] ?? res['explicacion'] ?? res['respuesta'] ?? 'Solicitud procesada con éxito.';
      final prefs = (res['preferencias_detectadas'] as List?)?.map((e) => e.toString()).toList() ?? [];
      final tipoComida = res['tipo_comida'];
      final personas = res['cantidad_personas'];
      final presupuesto = res['presupuesto'];
      final ubicacion = res['ubicacion_referencia'] ?? res['ubicacion'];
      final listoParaCrear = res['listo_para_crear'] == true;

      String botResponse = botMsg.toString();
      final List<String> criterios = [];
      if (tipoComida != null) criterios.add('Tipo de comida: $tipoComida');
      if (personas != null) criterios.add('Personas: $personas');
      if (presupuesto != null) criterios.add('Presupuesto: \$$presupuesto Bs');
      if (ubicacion != null) criterios.add('Ubicación: $ubicacion');
      if (prefs.isNotEmpty) criterios.add('Preferencias: ${prefs.join(", ")}');

      if (criterios.isNotEmpty) {
        botResponse += '\n\n📌 Criterios detectados:\n• ${criterios.join("\n• ")}';
      }

      Map<String, dynamic>? planData;
      if (listoParaCrear && presupuesto != null && personas != null && tipoComida != null) {
        planData = {
          'presupuesto': double.tryParse(presupuesto.toString()) ?? 0.0,
          'cantidad_personas': int.tryParse(personas.toString()) ?? 1,
          'tipo_comida': tipoComida.toString(),
          'ubicacion_referencia': (ubicacion?.toString().trim().isNotEmpty == true) ? ubicacion.toString() : 'Centro',
        };
      }

      setState(() {
        _messages.add(_ChatMessage(
          text: botResponse,
          isUser: false,
          extra: listoParaCrear ? 'Listo para crear planificación' : null,
          planData: planData,
        ));
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _messages.add(_ChatMessage(text: 'Error: ${e.toString()}', isUser: false, isError: true));
        _isLoading = false;
      });
    }
  }

  Future<void> _crearPlanificacion(Map<String, dynamic> data) async {
    setState(() => _isCreatingPlan = true);
    try {
      final resPlan = await PlanificacionService.instance.crearPlanificacion(
        presupuesto: AppTheme.toDouble(data['presupuesto']),
        cantidadPersonas: AppTheme.toInt(data['cantidad_personas']),
        tipoComida: data['tipo_comida'].toString(),
        ubicacionReferencia: data['ubicacion_referencia'].toString(),
      );

      final idPlan = AppTheme.toInt(resPlan['id_planificacion']);

      // Generar recomendaciones de MenuOpt
      final recs = await PlanificacionService.instance.generarRecomendaciones(idPlan);

      if (!mounted) return;
      setState(() => _isCreatingPlan = false);

      _mostrarDialogoRecomendaciones(idPlan, recs);

      setState(() {
        _messages.add(_ChatMessage(
          text: '🎉 ¡Planificación #$idPlan creada exitosamente!\n\n'
              'Se generaron ${recs.length} alternativas recomendadas para tu comida.',
          isUser: false,
        ));
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _isCreatingPlan = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al crear planificación: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _mostrarDialogoRecomendaciones(int idPlan, List<dynamic> recs) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.65,
        maxChildSize: 0.9,
        minChildSize: 0.4,
        expand: false,
        builder: (_, scrollCtrl) => Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              Row(
                children: [
                  const Icon(Icons.stars, color: AppTheme.primary, size: 24),
                  const SizedBox(width: 8),
                  Text(
                    'Recomendaciones (#$idPlan)',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                'Opciones optimizadas según tu presupuesto:',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
              ),
              const SizedBox(height: 16),
              Expanded(
                child: recs.isEmpty
                    ? Center(
                        child: Text(
                          'No se encontraron recomendaciones automáticas para estos criterios exactos.',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey.shade600),
                        ),
                      )
                    : ListView.builder(
                        controller: scrollCtrl,
                        itemCount: recs.length,
                        itemBuilder: (c, idx) {
                          final r = recs[idx] as Map<String, dynamic>;
                          final nombreResto = r['nombre_restaurante'] ?? r['nombre'] ?? 'Alternativa Gastronómica';
                          final tipo = r['tipo_recomendacion'] ?? '';
                          final costo = r['costo_total'] ?? '0.00';
                          final platos = r['platos'] as List? ?? [];

                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            elevation: 2,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            child: Padding(
                              padding: const EdgeInsets.all(14),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          nombreResto.toString(),
                                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: AppTheme.primaryLight,
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: Text(
                                          '$costo Bs',
                                          style: const TextStyle(
                                            color: AppTheme.primary,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    tipo == 'RESTAURANTE' ? 'Opción en Restaurante' : 'Preparación Propia',
                                    style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                                  ),
                                  if (platos.isNotEmpty) ...[
                                    const Divider(height: 16),
                                    ...platos.map((p) => Padding(
                                      padding: const EdgeInsets.only(bottom: 4),
                                      child: Row(
                                        children: [
                                          const Icon(Icons.check, size: 14, color: Colors.green),
                                          const SizedBox(width: 4),
                                          Text(
                                            '${p['nombre_plato'] ?? 'Plato'} - ${p['precio_unitario'] ?? p['subtotal']} Bs',
                                            style: const TextStyle(fontSize: 13),
                                          ),
                                        ],
                                      ),
                                    )),
                                  ],
                                ],
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    const primaryColor = AppTheme.primary;

    return Column(
      children: [
        // Lista de mensajes
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length,
            itemBuilder: (ctx, i) {
              final m = _messages[i];
              return Align(
                alignment: m.isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.82),
                  decoration: BoxDecoration(
                    color: m.isUser
                        ? primaryColor
                        : m.isError
                            ? AppTheme.dangerLight
                            : Colors.white,
                    borderRadius: BorderRadius.circular(16).copyWith(
                      bottomRight: m.isUser ? const Radius.circular(0) : const Radius.circular(16),
                      bottomLeft: !m.isUser ? const Radius.circular(0) : const Radius.circular(16),
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.04),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        m.text,
                        style: TextStyle(
                          color: m.isUser
                              ? Colors.white
                              : m.isError
                                  ? AppTheme.danger
                                  : Colors.black87,
                          fontSize: 14,
                        ),
                      ),
                      if (m.extra != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          m.extra!,
                          style: TextStyle(
                            fontSize: 11,
                            color: m.isUser ? Colors.white70 : Colors.grey.shade600,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ],
                      // Botón para crear planificación cuando los datos están completos
                      if (m.planData != null) ...[
                        const SizedBox(height: 12),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryLight,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppTheme.primary.withValues(alpha: 0.3)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.restaurant_menu, color: primaryColor, size: 18),
                                  const SizedBox(width: 6),
                                  const Text(
                                    'Planificación detectada',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color: AppTheme.primaryHover,
                                      fontSize: 13,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              Text(
                                '• ${m.planData!['tipo_comida']} para ${m.planData!['cantidad_personas']} personas\n'
                                '• Presupuesto: ${m.planData!['presupuesto']} Bs\n'
                                '• Zona: ${m.planData!['ubicacion_referencia']}',
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade800),
                              ),
                              const SizedBox(height: 10),
                              ElevatedButton.icon(
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: primaryColor,
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(vertical: 10),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                ),
                                icon: _isCreatingPlan
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                      )
                                    : const Icon(Icons.check_circle, size: 18),
                                label: Text(
                                  _isCreatingPlan ? 'Creando...' : 'Crear Planificación',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                                onPressed: _isCreatingPlan ? null : () => _crearPlanificacion(m.planData!),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              );
            },
          ),
        ),

        // Sugerencias
        if (_messages.length <= 2)
          SizedBox(
            height: 40,
            child: ListView.separated(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              scrollDirection: Axis.horizontal,
              itemCount: _sugerencias.length,
              separatorBuilder: (ctx, index) => const SizedBox(width: 8),
              itemBuilder: (ctx, i) {
                final s = _sugerencias[i];
                return ActionChip(
                  label: Text(s, style: const TextStyle(fontSize: 12)),
                  backgroundColor: Colors.white,
                  side: BorderSide(color: Colors.grey.shade300),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                  onPressed: () => _sendMessage(s),
                );
              },
            ),
          ),

        // Input
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 6,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _textCtrl,
                  decoration: InputDecoration(
                    hintText: 'Pregunta sobre comidas, platos, dietas...',
                    hintStyle: TextStyle(color: Colors.grey.shade500, fontSize: 13),
                    filled: true,
                    fillColor: Colors.grey.shade100,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                      borderSide: BorderSide(color: Colors.grey.shade300),
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 8),
              IconButton.filled(
                style: IconButton.styleFrom(backgroundColor: primaryColor),
                icon: const Icon(Icons.send, color: Colors.white),
                onPressed: _isLoading ? null : () => _sendMessage(),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ChatMessage {
  final String text;
  final bool isUser;
  final bool isError;
  final String? extra;
  final Map<String, dynamic>? planData;

  _ChatMessage({
    required this.text,
    required this.isUser,
    this.isError = false,
    this.extra,
    this.planData,
  });
}
