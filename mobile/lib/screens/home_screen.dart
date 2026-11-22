import 'package:flutter/material.dart';

import '../core/app_theme.dart';
import '../core/api_client.dart';
import '../services/auth_service.dart';
import '../services/planificacion_service.dart';
import '../services/reserva_service.dart';
import '../services/pedido_service.dart';
import 'login_screen.dart';
import 'planificar_screen.dart';
import 'planificaciones_screen.dart';
import 'preferencias_screen.dart';
import 'reservas_screen.dart';
import 'pedidos_screen.dart';
import 'perfil_screen.dart';
import 'asistente_screen.dart';
import 'recetas_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    this.initialSection = 0,
    this.initialResourceType,
    this.initialResourceId,
  });

  final int initialSection;
  final String? initialResourceType;
  final int? initialResourceId;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // Índice actual de la vista
  // 0: Inicio, 1: Planificar comida, 2: Mis planificaciones, 3: Mis preferencias,
  // 4: Mis Reservas, 5: Mis Pedidos, 6: Mi Perfil, 7: Asistente IA, 8: Biblioteca de Recetas
  late int _currentSection;
  late String? _pendingResourceType;
  late int? _pendingResourceId;

  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  void initState() {
    super.initState();
    _currentSection = widget.initialSection.clamp(0, 8).toInt();
    _pendingResourceType = widget.initialResourceType;
    _pendingResourceId = widget.initialResourceId;
  }

  void _navigateToSection(int sectionIndex) {
    if (sectionIndex != _currentSection) {
      _pendingResourceType = null;
      _pendingResourceId = null;
    }
    setState(() => _currentSection = sectionIndex);
    if (_scaffoldKey.currentState?.isDrawerOpen ?? false) {
      Navigator.pop(context); // cerrar drawer si estaba abierto
    }
  }

  // Mapeo entre bottom navigation bar y sectionIndex
  int get _bottomNavIndex {
    switch (_currentSection) {
      case 0:
        return 0; // Inicio
      case 1:
        return 1; // Planificar
      case 4:
        return 2; // Reservas
      case 5:
        return 3; // Pedidos
      case 6:
        return 4; // Perfil
      default:
        return 0;
    }
  }

  void _onBottomNavTapped(int index) {
    switch (index) {
      case 0:
        _navigateToSection(0); // Inicio
        break;
      case 1:
        _navigateToSection(1); // Planificar
        break;
      case 2:
        _navigateToSection(4); // Reservas
        break;
      case 3:
        _navigateToSection(5); // Pedidos
        break;
      case 4:
        _navigateToSection(6); // Perfil
        break;
    }
  }

  Future<void> _logout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text(
          'Cerrar Sesión',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        content: const Text('¿Estás seguro de que deseas salir de tu cuenta?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.danger,
              foregroundColor: Colors.white,
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Salir'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await AuthService.instance.logout();
      if (!mounted) return;
      Navigator.of(
        context,
      ).pushReplacement(MaterialPageRoute(builder: (_) => const LoginScreen()));
    }
  }

  Widget _buildBody() {
    switch (_currentSection) {
      case 0:
        return _InicioTab(onNavigate: _navigateToSection);
      case 1:
        return PlanificarScreen(onPlanCreated: () => _navigateToSection(2));
      case 2:
        return PlanificacionesScreen(
          onNavigateToNueva: () => _navigateToSection(1),
        );
      case 3:
        return const PreferenciasScreen();
      case 4:
        return ReservasScreen(
          initialResourceId: _pendingResourceType == 'reserva'
              ? _pendingResourceId
              : null,
        );
      case 5:
        return PedidosScreen(
          initialResourceId: _pendingResourceType == 'pedido'
              ? _pendingResourceId
              : null,
        );
      case 6:
        return const PerfilScreen();
      case 7:
        return const AsistenteScreen();
      case 8:
        return const RecetasScreen();
      default:
        return _InicioTab(onNavigate: _navigateToSection);
    }
  }

  @override
  Widget build(BuildContext context) {
    final userName = ApiClient.instance.userName;
    final userRole = ApiClient.instance.userRole.isNotEmpty
        ? ApiClient.instance.userRole
        : 'CLIENTE';

    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.menu, color: AppTheme.textMain),
          onPressed: () => _scaffoldKey.currentState?.openDrawer(),
        ),
        title: AppTheme.buildBrandLogo(fontSize: 19),
        actions: [
          // Badge del usuario y rol como en la Web (en pantallas con espacio suficiente)
          if (MediaQuery.of(context).size.width >= 370)
            Container(
              margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 4),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: AppTheme.border),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 90),
                    child: Text(
                      userName,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textMain,
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 6,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Text(
                      userRole.toUpperCase(),
                      style: const TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textMuted,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          IconButton(
            icon: const Icon(
              Icons.smart_toy_outlined,
              size: 20,
              color: AppTheme.primary,
            ),
            tooltip: 'Asistente IA',
            onPressed: () => _navigateToSection(7),
          ),
          IconButton(
            icon: const Icon(Icons.logout, size: 20, color: AppTheme.textMuted),
            tooltip: 'Salir',
            onPressed: _logout,
          ),
        ],
      ),
      drawer: _WebStyleDrawer(
        currentSection: _currentSection,
        onSelectSection: _navigateToSection,
        onLogout: _logout,
      ),
      body: _buildBody(),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(top: BorderSide(color: AppTheme.border, width: 1)),
        ),
        child: NavigationBar(
          backgroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
          indicatorColor: AppTheme.primaryLight,
          selectedIndex: _bottomNavIndex,
          onDestinationSelected: _onBottomNavTapped,
          destinations: const [
            NavigationDestination(
              icon: Icon(Icons.home_outlined),
              selectedIcon: Icon(Icons.home, color: AppTheme.primary),
              label: 'Inicio',
            ),
            NavigationDestination(
              icon: Icon(Icons.restaurant_outlined),
              selectedIcon: Icon(Icons.restaurant, color: AppTheme.primary),
              label: 'Planificar',
            ),
            NavigationDestination(
              icon: Icon(Icons.event_seat_outlined),
              selectedIcon: Icon(Icons.event_seat, color: AppTheme.primary),
              label: 'Reservas',
            ),
            NavigationDestination(
              icon: Icon(Icons.receipt_long_outlined),
              selectedIcon: Icon(Icons.receipt_long, color: AppTheme.primary),
              label: 'Pedidos',
            ),
            NavigationDestination(
              icon: Icon(Icons.person_outline),
              selectedIcon: Icon(Icons.person, color: AppTheme.primary),
              label: 'Perfil',
            ),
          ],
        ),
      ),
    );
  }
}

// Drawer idéntico a la barra lateral de la Web
class _WebStyleDrawer extends StatelessWidget {
  final int currentSection;
  final void Function(int) onSelectSection;
  final VoidCallback onLogout;

  const _WebStyleDrawer({
    required this.currentSection,
    required this.onSelectSection,
    required this.onLogout,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: Colors.white,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Encabezado Drawer
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
              child: AppTheme.buildBrandLogo(fontSize: 24),
            ),
            const Divider(height: 1, color: AppTheme.border),

            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(vertical: 12),
                children: [
                  // ASISTENTE VIRTUAL
                  _buildSectionHeader('ASISTENTE VIRTUAL'),
                  _buildDrawerItem(
                    index: 7,
                    title: 'Asistente IA',
                    icon: Icons.smart_toy_outlined,
                    activeIcon: Icons.smart_toy,
                  ),

                  const SizedBox(height: 12),
                  // PLANIFICACIÓN
                  _buildSectionHeader('PLANIFICACIÓN'),
                  _buildDrawerItem(
                    index: 0,
                    title: 'Inicio',
                    icon: Icons.home_outlined,
                    activeIcon: Icons.home,
                  ),
                  _buildDrawerItem(
                    index: 1,
                    title: 'Planificar comida',
                    icon: Icons.restaurant_menu_outlined,
                    activeIcon: Icons.restaurant_menu,
                  ),
                  _buildDrawerItem(
                    index: 2,
                    title: 'Mis planificaciones',
                    icon: Icons.assignment_outlined,
                    activeIcon: Icons.assignment,
                  ),
                  _buildDrawerItem(
                    index: 3,
                    title: 'Mis preferencias',
                    icon: Icons.tune_outlined,
                    activeIcon: Icons.tune,
                  ),
                  _buildDrawerItem(
                    index: 8,
                    title: 'Biblioteca de Recetas',
                    icon: Icons.menu_book_outlined,
                    activeIcon: Icons.menu_book,
                  ),

                  const SizedBox(height: 12),
                  // PEDIDOS & RESERVAS
                  _buildSectionHeader('PEDIDOS & RESERVAS'),
                  _buildDrawerItem(
                    index: 4,
                    title: 'Mis Reservas',
                    icon: Icons.event_seat_outlined,
                    activeIcon: Icons.event_seat,
                  ),
                  _buildDrawerItem(
                    index: 5,
                    title: 'Mis Pedidos',
                    icon: Icons.receipt_long_outlined,
                    activeIcon: Icons.receipt_long,
                  ),

                  const SizedBox(height: 12),
                  // CUENTA
                  _buildSectionHeader('CUENTA'),
                  _buildDrawerItem(
                    index: 6,
                    title: 'Mi Perfil',
                    icon: Icons.person_outline,
                    activeIcon: Icons.person,
                  ),
                ],
              ),
            ),

            const Divider(height: 1, color: AppTheme.border),
            ListTile(
              leading: const Icon(
                Icons.logout,
                color: AppTheme.danger,
                size: 20,
              ),
              title: const Text(
                'Salir',
                style: TextStyle(
                  color: AppTheme.danger,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
              onTap: onLogout,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 6),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: AppTheme.textMuted,
          letterSpacing: 0.8,
        ),
      ),
    );
  }

  Widget _buildDrawerItem({
    required int index,
    required String title,
    required IconData icon,
    required IconData activeIcon,
  }) {
    final isSelected = currentSection == index;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      decoration: BoxDecoration(
        color: isSelected ? AppTheme.primaryLight : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
        border: isSelected
            ? Border.all(color: AppTheme.primary.withValues(alpha: 0.3))
            : null,
      ),
      child: ListTile(
        dense: true,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        leading: Icon(
          isSelected ? activeIcon : icon,
          color: isSelected ? AppTheme.primary : AppTheme.textMain,
          size: 20,
        ),
        title: Text(
          title,
          style: TextStyle(
            fontSize: 13.5,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            color: isSelected ? AppTheme.primary : AppTheme.textMain,
          ),
        ),
        onTap: () => onSelectSection(index),
      ),
    );
  }
}

// Pantalla / Tab de Inicio
class _InicioTab extends StatefulWidget {
  final void Function(int) onNavigate;

  const _InicioTab({required this.onNavigate});

  @override
  State<_InicioTab> createState() => _InicioTabState();
}

class _InicioTabState extends State<_InicioTab> {
  int _totalPlanificaciones = 0;
  int _totalReservas = 0;
  int _totalPedidos = 0;
  bool _isLoadingKpis = true;

  @override
  void initState() {
    super.initState();
    _loadMetrics();
  }

  Future<void> _loadMetrics() async {
    try {
      final plans = await PlanificacionService.instance
          .listarMisPlanificaciones();
      final reservas = await ReservaService.instance.getMisReservas();
      final pedidos = await PedidoService.instance.getMisPedidos();

      if (mounted) {
        setState(() {
          final totalFromApi = AppTheme.toInt(plans['total'], -1);
          _totalPlanificaciones = totalFromApi >= 0
              ? totalFromApi
              : ((plans['planificaciones'] as List?)?.length ?? 0);
          _totalReservas = reservas.length;
          _totalPedidos = pedidos.length;
          _isLoadingKpis = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoadingKpis = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final name = ApiClient.instance.userName;
    final email = ApiClient.instance.userEmail;
    final role = ApiClient.instance.userRole.isNotEmpty
        ? ApiClient.instance.userRole
        : 'CLIENTE';

    return RefreshIndicator(
      onRefresh: _loadMetrics,
      color: AppTheme.primary,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Banner de bienvenida naranja vibrante
            Container(
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.primary, AppTheme.primaryHover],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: const [
                  BoxShadow(
                    color: Color.fromRGBO(255, 111, 0, 0.25),
                    blurRadius: 12,
                    offset: Offset(0, 4),
                  ),
                ],
              ),
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(3),
                        decoration: const BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                        ),
                        child: const CircleAvatar(
                          radius: 22,
                          backgroundColor: AppTheme.primaryLight,
                          child: Icon(
                            Icons.person,
                            color: AppTheme.primary,
                            size: 26,
                          ),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              '¡Hola, $name!',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 18,
                              ),
                            ),
                            Text(
                              email,
                              style: const TextStyle(
                                color: Colors.white70,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          role.toUpperCase(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 10,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 18),
                  const Text(
                    'Planifica tu comida optimizando presupuesto, ingredientes y reservas en un solo lugar.',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      height: 1.3,
                    ),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: AppTheme.primary,
                        elevation: 0,
                      ),
                      onPressed: () => widget.onNavigate(1),
                      icon: const Icon(Icons.bolt, size: 18),
                      label: const FittedBox(
                        fit: BoxFit.scaleDown,
                        child: Text('Planificar Comida Ahora'),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),

            // Métricas / KPIs rápidos
            Row(
              children: [
                Expanded(
                  child: _MetricCard(
                    title: 'Planificaciones',
                    value: _isLoadingKpis ? '...' : '$_totalPlanificaciones',
                    icon: Icons.assignment_outlined,
                    onTap: () => widget.onNavigate(2),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _MetricCard(
                    title: 'Reservas',
                    value: _isLoadingKpis ? '...' : '$_totalReservas',
                    icon: Icons.event_seat_outlined,
                    onTap: () => widget.onNavigate(4),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _MetricCard(
                    title: 'Pedidos',
                    value: _isLoadingKpis ? '...' : '$_totalPedidos',
                    icon: Icons.receipt_long_outlined,
                    onTap: () => widget.onNavigate(5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Accesos principales a los módulos
            const Text(
              'Módulos del Cliente',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppTheme.textMain,
              ),
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _ModuleCard(
                    title: 'Planificar comida',
                    desc: 'Optimiza por presupuesto y dieta',
                    icon: Icons.restaurant_menu,
                    color: AppTheme.primary,
                    onTap: () => widget.onNavigate(1),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _ModuleCard(
                    title: 'Mis Preferencias',
                    desc: 'Define restricciones y gustos',
                    icon: Icons.tune,
                    color: const Color(0xFF2563EB),
                    onTap: () => widget.onNavigate(3),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _ModuleCard(
                    title: 'Mis Reservas',
                    desc: 'Mesa y comensales en vivo',
                    icon: Icons.event_seat,
                    color: const Color(0xFF059669),
                    onTap: () => widget.onNavigate(4),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _ModuleCard(
                    title: 'Hacer Pedido',
                    desc: 'Comandas y platos del menú',
                    icon: Icons.receipt_long,
                    color: const Color(0xFFD97706),
                    onTap: () => widget.onNavigate(5),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _ModuleCard(
                    title: 'Asistente IA',
                    desc: 'Consulta en lenguaje natural',
                    icon: Icons.smart_toy,
                    color: const Color(0xFF7C3AED),
                    onTap: () => widget.onNavigate(7),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _ModuleCard(
                    title: 'Biblioteca de Recetas',
                    desc: '16 recetas y Asistente Culinario IA',
                    icon: Icons.menu_book,
                    color: const Color(0xFFEA580C),
                    onTap: () => widget.onNavigate(8),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _ModuleCard(
                    title: 'Mi Perfil',
                    desc: 'Datos personales y clave',
                    icon: Icons.manage_accounts,
                    color: const Color(0xFF475569),
                    onTap: () => widget.onNavigate(6),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final VoidCallback onTap;

  const _MetricCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: AppTheme.cardDecoration,
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
        child: Column(
          children: [
            Icon(icon, color: AppTheme.primary, size: 20),
            const SizedBox(height: 6),
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(
                value,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: AppTheme.textMain,
                ),
              ),
            ),
            Text(
              title,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 10.5, color: AppTheme.textMuted),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModuleCard extends StatelessWidget {
  final String title;
  final String desc;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _ModuleCard({
    required this.title,
    required this.desc,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        decoration: AppTheme.cardDecoration,
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(height: 10),
            Text(
              title,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: AppTheme.textMain,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              desc,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 11, color: AppTheme.textMuted),
            ),
          ],
        ),
      ),
    );
  }
}
