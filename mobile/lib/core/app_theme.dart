import 'package:flutter/material.dart';

class AppTheme {
  // Colores extraídos fielmente de frontend-web/src/styles.css
  static const Color primary = Color(0xFFFF6F00); // #ff6f00
  static const Color primaryHover = Color(0xFFE96300); // #e96300
  static const Color primaryLight = Color(0xFFFFF2E7); // #fff2e7
  static const Color secondary = Color(0xFF333333); // #333333
  static const Color secondaryHover = Color(0xFF222222);
  static const Color background = Color(0xFFF7F7F6); // #f7f7f6
  static const Color surface = Color(0xFFFFFFFF);
  static const Color textMain = Color(0xFF333333);
  static const Color textMuted = Color(0xFF737373);
  static const Color border = Color(0xFFE5E5E5);
  static const Color borderFocus = Color(0xFFFF6F00);

  // Estados
  static const Color success = Color(0xFF16845B);
  static const Color successLight = Color(0xFFEAF7F0);
  static const Color warning = Color(0xFFB76A00);
  static const Color warningLight = Color(0xFFFFF5DF);
  static const Color danger = Color(0xFFC83B36);
  static const Color dangerLight = Color(0xFFFFF0EF);
  static const Color info = Color(0xFF315B73);
  static const Color infoLight = Color(0xFFF0F6FB);

  static const double radius = 12.0;

  static ThemeData get theme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: background,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        primary: primary,
        surface: surface,
        brightness: Brightness.light,
      ),
      fontFamily: 'Roboto',
      appBarTheme: const AppBarTheme(
        backgroundColor: surface,
        foregroundColor: textMain,
        elevation: 0,
        centerTitle: false,
        scrolledUnderElevation: 1,
        titleTextStyle: TextStyle(
          color: textMain,
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
        iconTheme: IconThemeData(color: textMain),
      ),
      cardTheme: CardThemeData(
        color: surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFFECECEC)),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textMain,
          side: const BorderSide(color: border),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primary,
          textStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFFD8D8D8)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFFD8D8D8)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: danger),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: danger, width: 2),
        ),
        hintStyle: const TextStyle(color: Color(0xFFA0A0A0), fontSize: 13),
        labelStyle: const TextStyle(color: textMain, fontSize: 14),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: surface,
        side: const BorderSide(color: border),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
        labelStyle: const TextStyle(fontSize: 12, color: textMain),
        selectedColor: primaryLight,
      ),
    );
  }

  // Estilo de tarjeta con sombra suave igual a web
  static BoxDecoration cardDecoration = BoxDecoration(
    color: surface,
    borderRadius: BorderRadius.circular(16),
    border: Border.all(color: const Color(0xFFECECEC)),
    boxShadow: const [
      BoxShadow(
        color: Color.fromRGBO(35, 27, 18, 0.04),
        blurRadius: 8,
        offset: Offset(0, 2),
      ),
    ],
  );

  // Insignias / Badges iguales a web
  static Widget buildBadge(String text, {Color? bg, Color? textCol}) {
    Color bColor = bg ?? const Color(0xFFF1F1F1);
    Color tColor = textCol ?? const Color(0xFF686868);

    final upper = text.toUpperCase();
    if (upper == 'ACTIVO' || upper == 'ACTIVA' || upper == 'CONFIRMADA' || upper == 'ENTREGADO') {
      bColor = successLight;
      tColor = success;
    } else if (upper == 'PENDIENTE' || upper == 'BORRADOR') {
      bColor = warningLight;
      tColor = warning;
    } else if (upper == 'CANCELADO' || upper == 'CANCELADA' || upper == 'INACTIVO') {
      bColor = dangerLight;
      tColor = danger;
    } else if (upper == 'EN_PREPARACION' || upper == 'ACEPTADO' || upper == 'LISTO' || upper == 'COMPLETADA') {
      bColor = infoLight;
      tColor = info;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bColor,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: tColor,
          fontSize: 10,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.3,
        ),
      ),
    );
  }

  // Ayudantes de casteo numérico seguro (FastAPI / Decimal / String / int / double)
  static int toInt(dynamic v, [int fallback = 0]) {
    if (v == null) return fallback;
    if (v is int) return v;
    if (v is num) return v.toInt();
    if (v is String) {
      return int.tryParse(v) ?? double.tryParse(v)?.toInt() ?? fallback;
    }
    return fallback;
  }

  static double toDouble(dynamic v, [double fallback = 0.0]) {
    if (v == null) return fallback;
    if (v is double) return v;
    if (v is num) return v.toDouble();
    if (v is String) {
      return double.tryParse(v) ?? fallback;
    }
    return fallback;
  }

  // Logo oficial de MenuOpt
  static Widget buildBrandLogo({double? height, double? fontSize}) {
    final double computedHeight;
    if (height != null) {
      computedHeight = height;
    } else if (fontSize != null) {
      if (fontSize >= 30) {
        computedHeight = 58;
      } else if (fontSize >= 22) {
        computedHeight = 36;
      } else {
        computedHeight = 28;
      }
    } else {
      computedHeight = 32;
    }

    return Image.asset(
      'assets/branding/logo.png',
      height: computedHeight,
      fit: BoxFit.contain,
      errorBuilder: (context, error, stackTrace) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(5),
              decoration: BoxDecoration(
                color: primaryLight,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.restaurant_menu, color: primary, size: 20),
            ),
            const SizedBox(width: 8),
            RichText(
              text: TextSpan(
                children: [
                  TextSpan(
                    text: 'Menu',
                    style: TextStyle(
                      color: const Color(0xFF1E293B),
                      fontWeight: FontWeight.w800,
                      fontSize: fontSize ?? 20,
                      letterSpacing: -0.5,
                    ),
                  ),
                  TextSpan(
                    text: 'Opt',
                    style: TextStyle(
                      color: primary,
                      fontWeight: FontWeight.w900,
                      fontSize: fontSize ?? 20,
                      letterSpacing: -0.5,
                    ),
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  // Formateador amigable de fechas y horas
  static String formatDate(dynamic dt, {bool includeTime = false}) {
    if (dt == null) return '';
    DateTime? d;
    if (dt is DateTime) {
      d = dt;
    } else if (dt is String) {
      d = DateTime.tryParse(dt);
    }
    if (d == null) return dt.toString();
    const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    final m = months[d.month - 1];
    if (includeTime) {
      final hour = d.hour > 12 ? d.hour - 12 : (d.hour == 0 ? 12 : d.hour);
      final ampm = d.hour >= 12 ? 'PM' : 'AM';
      final min = d.minute.toString().padLeft(2, '0');
      final sec = d.second.toString().padLeft(2, '0');
      return '$m ${d.day}, ${d.year}, $hour:$min:$sec $ampm';
    }
    return '${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}';
  }
}

