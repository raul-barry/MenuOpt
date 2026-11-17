# INFORME DE ENTREGA FINAL &mdash; SISTEMA MENUOPT (SISTEMA COMPLETO)

**Asignatura:** Ingeniería de Software 1  
**Metodología:** Scrum  
**Versión del Sistema:** 1.0.0 (Consolidación Final)  
**Alcance:** Casos de Uso CU01 al CU26  

---

## 1. ESTADO GENERAL DEL PROYECTO
La plataforma **MenuOpt** se encuentra 100% operativa, integrada y estabilizada en sus tres capas (Base de datos PostgreSQL 16, Backend FastAPI y Frontend Web Angular 18 con Docker Nginx).
Todos los flujos clave (autenticación JWT, gestión de negocio gastronómico, planificación con presupuesto y comensales, optimización algorítmica de recomendaciones, matriz comparativa de restaurante vs preparación propia, plano 2D interactivo con coordenadas relativas, reservas con control estricto de concurrencia y pedidos con precios históricos) han sido validados de forma integral mediante suites de pruebas automatizadas y compilaciones de producción libres de errores.

---

## 2. ARQUITECTURA DEL SISTEMA
El sistema implementa una arquitectura modular multicapa con alta cohesión y bajo acoplamiento:
- **Capa de Presentación (Frontend):** Angular 18 en modo Standalone Components, programación reactiva con Signals, Angular Router con Guards de autenticación y roles, Interceptor HTTP para inyección de token JWT, y servidor Nginx para producción en Docker.
- **Capa de Controladores / Endpoints (Backend API):** FastAPI con enrutadores modulares organizados por entidad (`/autenticacion`, `/usuarios`, `/restaurantes`, `/categorias`, `/platos`, `/ingredientes`, `/preferencias`, `/planificaciones`, `/recomendaciones`, `/lugares-compra`, `/areas`, `/mesas`, `/reservas`, `/pedidos`, `/asistente`).
- **Capa de Reglas de Negocio (Services):** Servicios puros de dominio encargados del cálculo presupuestario, algoritmos determinísticos de optimización y scoring, validaciones cruzadas de capacidad y horarios de reserva, transiciones de estado de comandas y orquestación con proveedores de IA.
- **Capa de Acceso a Datos (Repositories):** Abstracción desacoplada de SQLAlchemy 2.0 que aísla las consultas, uniones (`joinedload`), filtros e índices del modelo relacional.
- **Capa de Persistencia (Base de Datos):** PostgreSQL 16 con migraciones versionadas y lineales mediante Alembic (`0001_crear_tablas_iniciales_sprint_1` hasta `24a8f9850af4_crear_tablas_pedido_y_detalle_pedido`).
- **Capa Periférica de IA (Opcional & Defensiva):** Módulo `app.ai` con interfaz abstracta `ProveedorIA`, implementación determinística `MockProveedorIA` y cliente `GeminiProveedorIA`. La IA no accede a PostgreSQL, no calcula precios y no reemplaza algoritmos de optimización.

---

## 3. RESUMEN DE LOS 26 CASOS DE USO IMPLEMENTADOS

| Caso de Uso | Nombre | Rol Permitido | Estado | Cobertura de Verificación |
|---|---|---|---|---|
| **CU01** | Registrarse | Público | COMPLETO | Hash bcrypt, validación de correo único, asignación de rol CLIENTE |
| **CU02** | Iniciar sesión | Público | COMPLETO | Generación de JWT (HS256) con expiración y respuesta tipada |
| **CU03** | Gestionar perfil | Autenticado | COMPLETO | Actualización de datos personales y cambio seguro de contraseña |
| **CU04** | Gestionar usuarios | ADMINISTRADOR | COMPLETO | Listado de usuarios, detalle y desactivación lógica (403 a otros roles) |
| **CU05** | Gestionar restaurantes | RESTAURANTE / ADMIN | COMPLETO | Ciclo de vida completo del restaurante (alta, consulta, edición y estado) |
| **CU06** | Gestionar área física del restaurante | RESTAURANTE / ADMIN | COMPLETO | Ambientes, dimensiones y planos del establecimiento |
| **CU07** | Gestionar categorías | ADMINISTRADOR | COMPLETO | Catálogo clasificado de comidas para los menús |
| **CU08** | Gestionar platos | RESTAURANTE / ADMIN | COMPLETO | Alta de platos, asignación de tipo de comida, comensales y preferencias |
| **CU09** | Gestionar proveedores | ADMINISTRADOR_TIENDA / ADMIN | COMPLETO | Gestión de comercios proveedores, insumos y actualización de precios unitarios para recetas y recomendaciones de IA |
| **CU10** | Gestionar disponibilidad | RESTAURANTE / ADMIN | COMPLETO | Conmutador rápido de plato disponible / no disponible |
| **CU11** | Registrar planificación gastronómica | CLIENTE / ADMIN | COMPLETO | Presupuesto > 0, comensales > 0, preferencias y titularidad |
| **CU12** | Definir preferencias | Autenticado / ADMIN | COMPLETO | Catálogo de preferencias (vegetariano, sin gluten, etc.) y asignación |
| **CU13** | Generar recomendación | CLIENTE / ADMIN | COMPLETO | Algoritmo determinístico de cobertura y presupuesto para restaurantes |
| **CU14** | Comparar alternativas gastronómicas | CLIENTE / ADMIN | COMPLETO | Matriz analítica de costo, score y ahorro en restaurantes |
| **CU15** | Biblioteca de recetas gastronómicas | CLIENTE / ADMIN | COMPLETO | Catálogo autónomo de recetas con fotos, Asistente Culinario IA con escalado y gestión administrativa de recetas |
| **CU16** | Consultar lugares de compra | Autenticado / ADMIN | COMPLETO | Búsqueda del menor precio disponible y agrupación por establecimiento |
| **CU17** | Crear plano 2D del restaurante | RESTAURANTE / ADMIN | COMPLETO | Editor de distribución con coordenadas relativas [0, 1] y rotación |
| **CU18** | Gestionar mesas | RESTAURANTE / ADMIN | COMPLETO | Formas geométricas (cuadrada, redonda, rectangular), capacidades y fijas |
| **CU19** | Definir combinación de mesas | RESTAURANTE / ADMIN | COMPLETO | Relaciones simétricas bidireccionales validadas dentro de la misma área |
| **CU20** | Consultar disponibilidad de mesas | Autenticado / ADMIN | COMPLETO | Cálculo dinámico sin flags estáticas: fecha, horario, solape y capacidad |
| **CU21** | Realizar reserva | CLIENTE / ADMIN | COMPLETO | Transacción segura `SELECT FOR UPDATE`, rechazo de doble reserva (409) |
| **CU22** | Gestionar reservas | RESTAURANTE / ADMIN | COMPLETO | Máquina de estados: CONFIRMADA -> FINALIZADA / CANCELADA |
| **CU23** | Enviar pedido | CLIENTE / ADMIN | COMPLETO | Validación de platos del mismo restaurante, precios históricos copiados en Decimal |
| **CU24** | Gestionar pedidos | CLIENTE / RESTO / ADMIN | COMPLETO | Comanda digital, máquina de estados: PENDIENTE -> ACEPTADO -> EN_PREPARACION -> LISTO -> ENTREGADO |
| **CU25** | Consultar bitácora | ADMINISTRADOR | COMPLETO | Registro y auditoría de eventos de dominio estructurados |
| **CU26** | Usar asistencia con IA | CLIENTE / ADMIN | COMPLETO | Lenguaje natural defensivo, extracción de entidades y explicación pedagógica |

---

## 4. INVENTARIO DE PRUEBAS AUTOMATIZADAS
Todas las suites de prueba ejecutadas dentro del contenedor `menuopt_backend` arrojan un 100% de éxito:
1. `test_part6.py`: 30/30 PASS (Recomendaciones algorítmicas, presupuesto, titularidad y comparativa inicial).
2. `test_part7.py`: 23/23 PASS (Preparación propia, lugares de compra, menor precio, escalado y CU14 completo).
3. `test_part9_backend.py`: 22/22 PASS (Plano 2D, áreas, coordenadas normalizadas, mesas y combinaciones simétricas).
4. `test_part10_backend.py`: 34/34 PASS (Disponibilidad dinámica, reservas transaccionales, 409 conflicto, solapes y estados).
5. `test_part11_backend.py`: 35/35 PASS (Pedidos, consolidación, inmutabilidad de precios históricos Decimal, comanda y transiciones).
6. `test_part13_backend.py`: 30/30 PASS (Asistente IA, prompts defensivos, cruce con BD relacional, contexto previo, modo sin IA).

**Total de Pruebas Automatizadas Verificadas:** 174 pruebas PASS (0 fallos).

---

## 5. REPORTE DE CALIDAD Y COMPILACIÓN FRONTEND (ANGULAR 18)
- El frontend web compila en modo estricto de producción mediante `docker compose build frontend`:
  - `Application bundle generation complete.`
  - `0 errores de TypeScript (TS2305, TS2345 y tipados 'any' resueltos con interfaces oficiales).`
- El contenedor `menuopt_frontend` sirve la aplicación en el puerto `4200` mediante un servidor Nginx optimizado con compresión gzip y fallback para Angular SPA (`try_files $uri $uri/ /index.html`).

---

## 6. COMANDOS PARA EJECUCIÓN LIMPIA Y DESPLIEGUE
```bash
# 1. Clonar el repositorio y posicionarse en la carpeta raíz
cd "d:/carlo rodrigoD/Escritorio/proyecto grupal sw1"

# 2. Levantar los 3 contenedores (PostgreSQL, Backend FastAPI y Frontend Angular)
docker compose up -d --build

# 3. Comprobar que los servicios se encuentren en estado Up / healthy
docker compose ps

# 4. En caso de base de datos vacía, aplicar migraciones lineales de Alembic
docker compose exec backend alembic upgrade head

# 5. Cargar usuarios y catálogos de prueba iniciales
docker compose exec backend python -m app.database.crear_admin
```

---

## 7. URLS DE ACCESO
- **Frontend Web Angular:** [http://localhost:4200](http://localhost:4200)
- **Documentación Interactiva Backend (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check API / Base de Datos:** [http://localhost:8000/salud/base-datos](http://localhost:8000/salud/base-datos)

---

## 8. LIMITACIONES DEL ALCANCE ACADÉMICO
Siguiendo las restricciones formales del proyecto de Ingeniería de Software 1:
1. **Sin pasarelas de pago externas:** Los pedidos calculan y congelan subtotales y totales con precisión monetaria `Decimal`, pero el cobro se realiza contra entrega o en el restaurante físico.
2. **Sin GPS ni geocodificación externa:** Las ubicaciones y distancias se basan en referencias espaciales y zonas (ej. Equipetrol, Centro).
3. **Sin editor arquitectónico CAD:** El plano 2D utiliza un lienzo interactivo con cuadrícula normalizada y coordenadas porcentuales `[0, 1]`, sin requerir planos arquitectónicos a escala ni medidas en milímetros.
4. **Flutter como plataforma futura:** El alcance funcional completo se encuentra validado y operativo en Angular Web Responsive; el cliente móvil Flutter permanece previsto para fases posteriores.
5. **Inteligencia Artificial opcional:** La plataforma opera al 100% de sus capacidades con `AI_ENABLED=false` o sin conexión externa a APIs comerciales.
