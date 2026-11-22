import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../core/app_theme.dart';
import '../services/asistente_service.dart';

class AgenteGuiaFlotante extends StatefulWidget {
  const AgenteGuiaFlotante({
    super.key,
    required this.paginaActual,
    required this.onNavigate,
  });

  final String paginaActual;
  final ValueChanged<int> onNavigate;

  @override
  State<AgenteGuiaFlotante> createState() => _AgenteGuiaFlotanteState();
}

class _GuiaMessage {
  const _GuiaMessage({
    required this.text,
    required this.fromUser,
    this.destination,
    this.mobileSection,
  });

  final String text;
  final bool fromUser;
  final String? destination;
  final int? mobileSection;
}

class _AgenteGuiaFlotanteState extends State<AgenteGuiaFlotante> {
  final _input = TextEditingController();
  final List<_GuiaMessage> _messages = [];
  List<dynamic> _actions = [];
  bool _open = false;
  bool _loading = false;

  @override
  void dispose() {
    _input.dispose();
    super.dispose();
  }

  Future<void> _toggle() async {
    setState(() => _open = !_open);
    if (_open && _messages.isEmpty) {
      await _send('¿Qué funciones puedo realizar con mi rol?');
    }
  }

  Future<void> _selectAction(Map<String, dynamic> action) async {
    await _send(action['nombre']?.toString() ?? 'Ayúdame con esta función',
        actionId: action['id']?.toString());
  }

  Future<void> _send(String raw, {String? actionId}) async {
    final text = raw.trim();
    if (text.isEmpty || _loading) return;
    _input.clear();
    final history = _messages
        .take(10)
        .map((item) => <String, String>{
              'emisor': item.fromUser ? 'user' : 'assistant',
              'contenido': item.text,
            })
        .toList();
    setState(() {
      _messages.add(_GuiaMessage(text: text, fromUser: true));
      _actions = [];
      _loading = true;
    });
    try {
      final result = await AsistenteService.instance.guiarUsuario(
        mensaje: text,
        accionId: actionId,
        paginaActual: widget.paginaActual,
        historial: history,
      );
      if (!mounted) return;
      final sectionValue = result['seccion_movil'];
      setState(() {
        _messages.add(_GuiaMessage(
          text: result['respuesta']?.toString() ?? 'No recibí una respuesta.',
          fromUser: false,
          destination: result['destino']?.toString(),
          mobileSection: sectionValue is num ? sectionValue.toInt() : null,
        ));
        _actions = result['acciones'] is List ? result['acciones'] as List : [];
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _messages.add(const _GuiaMessage(
          text: 'No pude conectar con el agente guía. Inténtalo de nuevo en un momento.',
          fromUser: false,
        ));
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final width = (MediaQuery.sizeOf(context).width - 24)
        .clamp(280.0, 360.0)
        .toDouble();
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        if (_open) ...[
          Container(
            width: width,
            height: (MediaQuery.sizeOf(context).height - 150)
                .clamp(300.0, 510.0)
                .toDouble(),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppTheme.border),
              boxShadow: const [BoxShadow(color: Color(0x33241306), blurRadius: 28, offset: Offset(0, 8))],
            ),
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                Container(
                  color: AppTheme.primary,
                  padding: const EdgeInsets.fromLTRB(14, 12, 8, 12),
                  child: Row(
                    children: [
                      const CircleAvatar(
                        radius: 17,
                        backgroundColor: Color(0x33FFFFFF),
                        child: Icon(Icons.auto_awesome, color: Colors.white, size: 19),
                      ),
                      const SizedBox(width: 9),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Agente guía', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                            Text('Ayuda para usar MenuOpt', style: TextStyle(color: Colors.white70, fontSize: 11)),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: () => setState(() => _open = false),
                        icon: const Icon(Icons.close, color: Colors.white),
                        tooltip: 'Cerrar chat',
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.all(12),
                    children: [
                      for (final message in _messages) ...[
                        Align(
                          alignment: message.fromUser ? Alignment.centerRight : Alignment.centerLeft,
                          child: Container(
                            constraints: BoxConstraints(maxWidth: width * .88),
                            margin: const EdgeInsets.only(bottom: 8),
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                            decoration: BoxDecoration(
                              color: message.fromUser ? AppTheme.primaryLight : const Color(0xFFFAF8F6),
                              border: Border.all(color: AppTheme.border),
                              borderRadius: BorderRadius.circular(13),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(message.text, style: const TextStyle(fontSize: 12, height: 1.45)),
                                if (message.mobileSection != null)
                                  TextButton.icon(
                                    onPressed: () {
                                      widget.onNavigate(message.mobileSection!);
                                      setState(() => _open = false);
                                    },
                                    icon: const Icon(Icons.open_in_new, size: 15),
                                    label: const Text('Abrir esta función'),
                                    style: TextButton.styleFrom(foregroundColor: AppTheme.primary, padding: EdgeInsets.zero),
                                  ),
                              ],
                            ),
                          ),
                        ),
                      ],
                      for (final item in _actions)
                        if (item is Map)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 6),
                            child: OutlinedButton(
                              onPressed: _loading ? null : () => _selectAction(Map<String, dynamic>.from(item)),
                              style: OutlinedButton.styleFrom(
                                alignment: Alignment.centerLeft,
                                foregroundColor: AppTheme.primary,
                                side: const BorderSide(color: AppTheme.border),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 10),
                              ),
                              child: Text(item['nombre']?.toString() ?? '', style: const TextStyle(fontSize: 12)),
                            ),
                          ),
                      if (_loading)
                        const Padding(
                          padding: EdgeInsets.all(8),
                          child: Align(alignment: Alignment.centerLeft, child: Text('El agente está escribiendo…', style: TextStyle(fontSize: 12, color: AppTheme.textMuted))),
                        ),
                    ],
                  ),
                ),
                SafeArea(
                  top: false,
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(10, 8, 10, 10),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _input,
                            enabled: !_loading,
                            maxLength: 1000,
                            minLines: 1,
                            maxLines: 3,
                            decoration: const InputDecoration(
                              counterText: '',
                              hintText: '¿Qué quieres hacer?',
                              isDense: true,
                              border: OutlineInputBorder(borderRadius: BorderRadius.all(Radius.circular(22))),
                              contentPadding: EdgeInsets.symmetric(horizontal: 13, vertical: 10),
                            ),
                          onSubmitted: _send,
                          ),
                        ),
                        const SizedBox(width: 7),
                        IconButton.filled(
                          onPressed: _loading ? null : () => _send(_input.text),
                          style: IconButton.styleFrom(backgroundColor: AppTheme.primary, foregroundColor: Colors.white),
                          icon: const Icon(Icons.send_rounded, size: 18),
                          tooltip: 'Enviar',
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
        ],
        FloatingActionButton.extended(
          heroTag: 'menuopt_agent_guide',
          onPressed: _toggle,
          backgroundColor: AppTheme.primary,
          foregroundColor: Colors.white,
          icon: Icon(_open ? Icons.close : Icons.auto_awesome),
          label: Text(_open ? 'Cerrar' : '¿Necesitas ayuda?'),
        ),
      ],
    );
  }
}
