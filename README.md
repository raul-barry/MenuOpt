# MenuOpt - Plataforma de Planificación Gastronómica

Proyecto universitario para la asignatura **Ingeniería de Software 1**.  
Metodología de trabajo: **Scrum**.

---

## 📌 Descripción General

**MenuOpt** es una plataforma web y móvil orientada a la planificación gastronómica, optimización de presupuesto, recomendaciones personalizadas y conexión entre consumidores y establecimientos gastronómicos.

Esta versión integra **PARTE 1, PARTE 2, PARTE 3, PARTE 4, PARTE 5, PARTE 6, PARTE 7, PARTE 8, PARTE 9, PARTE 10, PARTE 11, PARTE 12 y PARTE 13 DEL DESARROLLO**:
- **Parte 1:** Base técnica, infraestructura Docker, PostgreSQL 16, SQLAlchemy 2.0 y migraciones con Alembic.
- **Parte 2:** Autenticación JWT, seguridad con Bcrypt, CU01 (Registro), CU02 (Login), CU03 (Perfil) y CU04 (Usuarios).
- **Parte 3:** Gestión de negocio gastronómico: CU05 (Registrar restaurante), CU06 (Gestionar restaurante), CU07 (Categorías), CU08 (Platos), CU09 (Ingredientes) y CU10 (Disponibilidad).
- **Parte 4:** Frontend web modular y responsive en **Angular 18**, conectado al backend FastAPI mediante Docker y Nginx (CU01 a CU10).
- **Parte 5:** Planificación gastronómica y preferencias del consumidor: CU11 (Registrar planificación gastronómica) y CU12 (Definir preferencias).
- **Parte 6:** Recomendaciones inteligentes y comparación de alternativas gastronómicas en restaurantes: CU13 (Generar recomendación) y CU14 (Comparar alternativas - etapa inicial).
- **Parte 7:** Preparación propia, lugares de compra y optimización comparativa completa: CU15 (Consultar ingredientes para preparación propia), CU16 (Consultar lugares de compra) y finalización completa de CU14 (Comparar alternativas: RESTAURANTE vs PREPARACION_PROPIA).
- **Parte 8:** Frontend Web Angular integral para los casos de uso CU11, CU12, CU13, CU14, CU15 y CU16 con flujos de usuario completos y reactivos.
- **Parte 9:** Gestión de distribución física y mesas de restaurantes: CU17 (Crear plano 2D del restaurante y distribución en cuadrícula determinística con coordenadas normalizadas), CU18 (Gestionar mesas: formas, capacidades, rotación, fijas/movibles) y CU19 (Definir combinación de mesas: relaciones simétricas bidireccionales con validación de misma área).
- **Parte 10:** Sistema transaccional de reservas y disponibilidad de mesas: CU20 (Consultar disponibilidad según fecha, horario, solapamiento y capacidad), CU21 (Realizar y cancelar reservas con control estricto de concurrencia SELECT FOR UPDATE y HTTP 409) y CU22 (Gestionar reservas de restaurante con filtros y transiciones de estado controladas).
- **Parte 11:** Sistema de pedidos gastronómicos y comandas: CU23 (Enviar pedido con validación de platos del mismo restaurante, precios históricos copiados en backend con Decimal, reserva opcional) y CU24 (Gestionar pedidos con historial de cliente, comanda de restaurante, filtros y máquina de estados controlada: PENDIENTE -> ACEPTADO -> EN_PREPARACION -> LISTO -> ENTREGADO).
- **Parte 12:** Historial y bitácora del sistema: CU25 (Consultar bitácora del sistema y auditoría de eventos de dominio).
- **Parte 13:** Asistencia de lenguaje natural con Inteligencia Artificial: CU26 (Usar asistencia con IA para interpretación de solicitudes gastronómicas, extracción de entidades y explicación pedagógica de recomendaciones y comparaciones sin reemplazar algoritmos deterministas ni el modelo de datos relacional).

---

## 🛠️ Tecnologías y Stack Técnico

- **Backend:** Python 3.11+, FastAPI, Pydantic 2.x, PyJWT, Passlib con Bcrypt.
- **Asistente IA (CU26):** Arquitectura desacoplada mediante interfaz abstracta `ProveedorIA` (`MockProveedorIA`, `GeminiProveedorIA`), configuración por variables de entorno (`AI_ENABLED`, `AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`, `AI_TIMEOUT_SECONDS`), resiliencia y modo seguro sin IA.
- **Frontend Web:** Angular 18 (Standalone Components, Signals, Reactive Forms, Guards e Interceptors JWT), servido con Nginx en Docker.
- **Base de Datos:** PostgreSQL 16.
- **ORM & Migraciones:** SQLAlchemy 2.0 (driver `psycopg 3`), Alembic (`0001_sprint_1`, `485e7aad0736`, `4d154d153551`, `c928d00a309a`, `ee09d72ff584`, `3f88887b2251`).
- **Contenerización y Red:** Docker Compose con red bridge dedicada (`menuopt_network`).

---

## 🏛️ Casos de Uso Implementados

| Caso de Uso | Nombre | Rol Permitido | Endpoint Backend |
|---|---|---|---|
| **CU01** | Registrarse | Público | `POST /autenticacion/registro` |
| **CU02** | Iniciar sesión | Público | `POST /autenticacion/login` |
| **CU03** | Gestionar perfil | Autenticado | `GET /usuarios/perfil`, `PUT /usuarios/perfil`, `PUT /usuarios/perfil/contrasena` |
| **CU04** | Gestionar usuarios | ADMINISTRADOR | `GET /usuarios`, `GET /usuarios/{id}`, `PATCH /usuarios/{id}/estado` |
| **CU05** | Gestionar restaurantes | RESTAURANTE / ADMIN | `POST /restaurantes`, `GET /restaurantes/mis-restaurantes`, `GET /restaurantes/{id}`, `PUT /restaurantes/{id}` |
| **CU06** | Gestionar área física del restaurante | RESTAURANTE / ADMIN | `GET /restaurantes/{id}/areas`, `POST /restaurantes/{id}/areas`, `PUT /areas/{id}` |
| **CU07** | Gestionar categorías | ADMINISTRADOR | `GET /categorias`, `POST /categorias`, `PUT /categorias/{id}` |
| **CU08** | Gestionar platos y preferencias | RESTAURANTE / ADMIN | `GET /restaurantes/{id}/platos`, `POST /restaurantes/{id}/platos`, `GET /platos/{id}`, `PUT /platos/{id}`, `PATCH /platos/{id}/estado`, `GET /platos/{id}/preferencias`, `PUT /platos/{id}/preferencias` |
| **CU09** | Gestionar proveedores | ADMINISTRADOR_TIENDA / ADMIN | `GET /lugares-compra`, `POST /lugares-compra`, `GET /lugares-compra/mis-tiendas`, `PUT /lugares-compra/{id}`, `POST /lugares-compra/{id}/ingredientes`, `PUT /lugares-compra/{id}/ingredientes/{id_ing}`, `DELETE /lugares-compra/{id}/ingredientes/{id_ing}` |
| **CU10** | Gestionar disponibilidad | RESTAURANTE / ADMIN | `PATCH /platos/{id}/disponibilidad` |
| **CU11** | Registrar planificación | CLIENTE / ADMIN | `POST /planificaciones`, `GET /planificaciones/mis-planificaciones`, `GET /planificaciones/{id}`, `PUT /planificaciones/{id}`, `PATCH /planificaciones/{id}/estado` |
| **CU12** | Definir preferencias | Autenticado / ADMIN | `GET /preferencias`, `GET /usuarios/preferencias`, `PUT /usuarios/preferencias`, `POST /preferencias`, `PUT /preferencias/{id}`, `PATCH /preferencias/{id}/estado` |
| **CU13** | Generar recomendación | CLIENTE (Titular) / ADMIN | `POST /planificaciones/{id}/recomendaciones/generar`, `GET /planificaciones/{id}/recomendaciones`, `GET /recomendaciones/{id}` |
| **CU14** | Comparar alternativas (Completo) | CLIENTE (Titular) / ADMIN | `GET /planificaciones/{id}/comparacion` |
| **CU15** | Ingredientes preparación propia | CLIENTE (Titular) / ADMIN | `GET /recomendaciones/{id}/preparacion` |
| **CU16** | Consultar lugares de compra | Autenticado / ADMIN | `GET /lugares-compra`, `POST /lugares-compra`, `GET /lugares-compra/{id}`, `PUT /lugares-compra/{id}`, `GET /ingredientes/{id}/lugares-compra`, `POST /lugares-compra/{id}/ingredientes`, `PUT /lugares-compra/{id}/ingredientes/{id_ing}`, `GET /recomendaciones/{id}/lugares-compra` |
| **CU17** | Crear plano 2D del restaurante | RESTAURANTE / ADMIN | `GET /restaurantes/{id}/areas`, `POST /restaurantes/{id}/areas`, `PUT /areas/{id}`, `POST /areas/{id}/distribucion/generar`, `PUT /areas/{id}/distribucion`, `POST /areas/{id}/distribucion/restablecer` |
| **CU18** | Gestionar mesas | RESTAURANTE / ADMIN | `GET /areas/{id}/mesas`, `POST /areas/{id}/mesas`, `GET /mesas/{id}`, `PUT /mesas/{id}`, `DELETE /mesas/{id}`, `PATCH /mesas/{id}/estado` |
| **CU19** | Definir combinación de mesas | RESTAURANTE / ADMIN | `GET /areas/{id}/combinaciones`, `POST /combinaciones`, `DELETE /combinaciones/{id}` |
| **CU20** | Consultar disponibilidad mesas | Autenticado / ADMIN | `GET /restaurantes/{id}/mesas-disponibles` |
| **CU21** | Realizar y cancelar reserva; gestionar invitados | CLIENTE / RESTAURANTE propietario / ADMIN | `POST /reservas`, `GET /reservas/mis-reservas`, `GET /reservas/{id}`, `PATCH /reservas/{id}/cancelar`, `GET /reservas/{id}/invitados`, `POST /reservas/{id}/invitados`, `DELETE /reservas/{id}/invitados/{id_invitado}` |
| **CU22** | Gestionar reservas | RESTAURANTE / ADMIN | `GET /restaurantes/{id}/reservas`, `PATCH /reservas/{id}/estado` |
| **CU23** | Enviar pedido | CLIENTE / ADMIN | `POST /pedidos` |
| **CU24** | Gestionar pedidos | CLIENTE / RESTAURANTE / ADMIN | `GET /pedidos/mis-pedidos`, `GET /pedidos/{id}`, `PATCH /pedidos/{id}/cancelar`, `GET /restaurantes/{id}/pedidos`, `PATCH /pedidos/{id}/estado` |
| **CU25** | Consultar bitácora del sistema | ADMINISTRADOR | `GET /bitacora` |
| **CU26** | Usar asistencia con IA | CLIENTE / ADMIN | `POST /asistente/interpretar`, `POST /asistente/explicar-recomendacion`, `POST /asistente/explicar-comparacion` |

### Gestión de invitados de una reserva

El titular, el restaurante responsable y un administrador pueden consultar, agregar y eliminar invitados. Para un invitado sin cuenta, `POST /reservas/{id}/invitados` recibe `{"nombre":"Ana Pérez","correo":"ana@example.com"}`; el correo es opcional. Para vincular una cuenta existente recibe `{"id_usuario":42}` y la cuenta debe estar activa y tener rol `CLIENTE`. El invitado vinculado conserva una copia de su nombre y correo al momento de registrarlo.

La cantidad de invitados no puede superar la cantidad de personas de la reserva. Se rechazan duplicados por cuenta, correo (sin distinguir mayúsculas) y nombre cuando no hay correo para identificar a la persona. El borrado responde `409 Conflict` si el invitado vinculado tiene un pedido asociado a esa reserva. Los endpoints devuelven `404` para una reserva inexistente y `403` cuando el usuario autenticado no tiene acceso.

---

## 🚀 Despliegue y Puesta en Marcha con Docker

Toda la plataforma se levanta de forma automatizada mediante Docker Compose.

### 1. Levantar los 3 Servicios
```bash
docker compose up -d --build
```

### 2. Verificar el Estado de los Contenedores
```bash
docker compose ps
```
Deberá observar 3 contenedores activos:
- `menuopt_postgres`: Puerto `5432` (healthy)
- `menuopt_backend`: Puerto `8000` (running)
- `menuopt_frontend`: Puerto `4200` (running)

### 3. Cargar o restaurar las cuentas de prueba y el catálogo de preferencias
```bash
docker compose exec backend python -m app.database.crear_admin
```
Este comando crea las cinco cuentas de la tabla siguiente. También restaura sus contraseñas y estado activo si fueron modificados durante pruebas; ejecútalo nuevamente si alguna credencial no funciona.

---

## 🔑 Credenciales de Acceso para Pruebas

| Rol | Correo Electrónico | Contraseña | Destino Inicial Post-Login |
|---|---|---|---|
| **ADMINISTRADOR** | `admin@menuopt.com` | `Admin1234*` | `/admin/usuarios` |
| **ADMINISTRADOR_TIENDA** | `tienda@menuopt.com` | `Tienda1234*` | `/proveedores` |
| **RESTAURANTE** | `restaurante@menuopt.com` | `Resto1234*` | `/restaurantes` |
| **RESTAURANTE 2** | `restaurante2@menuopt.com` | `Resto1234*` | `/restaurantes` |
| **CLIENTE 1** | `cliente1@menuopt.com` | `Cliente1234*` | `/inicio` |
| **CLIENTE 2** | `cliente2@menuopt.com` | `Cliente1234*` | `/inicio` |

---

## 🌐 URLs de Acceso

- **Frontend Web Angular:** [http://localhost:4200](http://localhost:4200)
- **Documentación Backend (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación Backend (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **API Health Check:** [http://localhost:8000/salud/base-datos](http://localhost:8000/salud/base-datos)
