# Auditoría funcional ejecutable de MenuOpt

Fecha: 2026-10-08
Rama revisada: `codex-funcionalidades`

## Alcance y método

La especificación oficial disponible es `README.md` (tabla de CU01–CU26). Se contrastó con `documentacion/trazabilidad.md`, routers, servicios, modelos, migraciones, componentes y servicios Angular. La matriz informa presencia localizada; esa presencia por sí sola no acredita el flujo de punta a punta. No se encontró código Flutter en este repositorio. La matriz de trazabilidad afirma pruebas para varios casos, pero los archivos `backend/test_part*_backend.py` son scripts HTTP que requieren API y datos ya levantados, no tests descubribles por pytest/unittest.

En la auditoría inicial pytest no encontró pruebas y Angular no tenía paquetes instalados. `email-validator` ya estaba declarado en `backend/requirements.txt`, aunque faltaba en el intérprete global. Los resultados posteriores de estabilización y sus comandos están registrados en la sección de evidencia siguiente.

## Evidencia de la fase de estabilización (2026-10-08)

Se inspeccionaron los archivos de dependencias: no hay `backend/pyproject.toml` ni lockfile Angular inicial. `email-validator` ya estaba declarado en `backend/requirements.txt`; estaba ausente solo del entorno local. Se agregaron `backend/requirements-test.txt` y `backend/requirements-test.lock` (versiones fijadas desde la imagen probada), `frontend-web/package-lock.json`, `backend/Dockerfile.test` y `docker-compose.test.yml`. El entorno usa PostgreSQL 16 aislado con proyecto Docker `menuopt-codex-test`, contenedor `menuopt_codex_test_postgres`, puerto `55432` y volumen exclusivo `menuopt_codex_test_postgres_data`. `backend/tests/conftest.py` rechaza truncar si el nombre de la base no es `menuopt_test_db`.

**Probado correctamente:**

- `alembic upgrade head` sobre la base vacía exclusiva. Se aplicaron las siete revisiones hasta `24a8f9850af4`; `alembic current` confirmó `24a8f9850af4 (head)`. No se requirieron cambios a migraciones.
- `pytest -q -p no:cacheprovider` en la imagen Linux reconstruida desde el lock: **6 passed**. Incluye autenticación por login, permisos ADMIN/CLIENTE/propietario, creación de restaurante/categoría/área/menú, combinación de mesas, disponibilidad, reserva individual y combinada, capacidad, solapamiento, límites adyacentes, concurrencia (exactamente una solicitud obtiene 201 y la otra 409), pedidos individuales de dos cuentas e historial propio.
- `pytest -q -p no:cacheprovider tests/test_reserva_capacity.py`: **2 passed**. También está incluida en el total de seis.
- `npm.cmd ci --ignore-scripts --no-audit --no-fund`: instalación exacta desde el nuevo lock, 846 paquetes instalados. `npm.cmd run build`: compilación Angular de producción completada. El build informa dos advertencias preexistentes de presupuesto CSS; no se modificaron estilos.

**Probado con errores durante la preparación, luego corregidos:** los primeros intentos de pytest usaron un dominio reservado y helpers mal ubicados; el intento inicial de build no podía descargar Google Fonts bajo el bloqueo de red. Se corrigieron los datos/helpers de prueba y se repitió build con acceso de red autorizado. La única advertencia restante de pytest es una deprecación de `starlette.testclient` con `httpx`.

**No ejecutado:** los scripts heredados `backend/test_part*_backend.py` requieren una API y datos seed con otros endpoints; la suite nueva probó las rutas relevantes mediante FastAPI TestClient y PostgreSQL real. No se probó el flujo completo de CU01 (registro), cambios de contraseña, cambios de estado ni todos los filtros/transiciones de pedidos y reservas. Tampoco se probaron llamadas a un proveedor externo de IA.

**Pendiente de implementación:** CU25 sigue ausente (ver matriz). No hay app Flutter en el árbol móvil (`mobile` contiene solo `.gitkeep`).

La corrida Windows local de Alembic tampoco fue usable: Windows bloqueó la DLL de `psycopg-binary`; se migró y verificó la base desde la imagen Linux. No se conectó ni se ejecutó ninguna migración en una base compartida.

## Actualización de microtarea 1.1 — invitados de reserva

Se agregó la entidad `reserva_invitado` mediante la revisión Alembic `74c12e89a531`, con vinculación opcional a `usuario` y snapshots de nombre/correo. Los endpoints `GET` y `POST /reservas/{id}/invitados`, y `DELETE /reservas/{id}/invitados/{id_invitado}`, validan la reserva y permisos de titular/restaurante responsable/administrador. Se serializan altas con bloqueo de la fila de reserva, limitan la cantidad a `cantidad_personas` y evitan repetición por cuenta, correo o nombre sin correo.

Al quitar un invitado vinculado se comprueba si existe un pedido del mismo usuario asociado a esa reserva; si existe, se devuelve `409` y se conserva el invitado. Los tests de integración ejercitan este caso.

La suite completa de esta iteración terminó con **9 passed**; `tests/test_reserva_invitados.py` terminó con **3 passed**. `alembic current` confirmó `74c12e89a531 (head)` y `alembic check` no detectó diferencias entre modelos y migración.

## Actualización de microtarea 1.2 — autorización de pedidos por invitados

`POST /pedidos` autoriza una reserva vinculada para su titular, un invitado con cuenta vinculado a esa reserva o un administrador (regla preexistente). La identidad del pedido sigue derivándose exclusivamente del token autenticado. `PedidoCrear` ahora rechaza campos adicionales (`extra=forbid`), incluido un `id_usuario` enviado para suplantar a otra persona. Se conserva el permiso existente del endpoint (CLIENTE/ADMINISTRADOR); no se amplió a RESTAURANTE. La asociación a otra reserva-restaurante sigue devolviendo `400`.

**Probado correctamente:** `docker compose -f docker-compose.test.yml -p menuopt-codex-test run --rm backend-test pytest -q -p no:cacheprovider` terminó con **9 passed, 1 warning** (PostgreSQL aislado). El test de regresión cubre titular `201`, invitado vinculado `201` con identidad propia, cliente no vinculado `403`, intento de enviar `id_usuario` ajeno `422`, reserva de otro restaurante `400` y pedidos sin reserva `201` para ambos usuarios. Historial propio incluye correctamente pedidos vinculados y separados.

**Probado con errores, luego corregido:** la primera ejecución detectó una expectativa antigua en el test de historial (solo pedidos independientes); se actualizó para contemplar el pedido asociado del propio usuario y se repitió la suite completa.

## Actualización de microtarea 1.3 — asignación de platos a invitados

Se amplió `POST /pedidos` para aceptar `detalles[].id_invitado` cuando el pedido tiene reserva. El titular y el administrador existente pueden asignar a cualquier invitado de esa reserva, incluyendo invitados sin cuenta; un invitado registrado que omite el campo queda asignado a su propia ficha y no puede asignar a otra. La respuesta del detalle incluye `id_invitado` y `nombre_invitado`. Los detalles mantienen precio/subtotal calculado por el backend y ahora se consolidan por plato e invitado.

La migración compatible `b317d4a82e19` agrega un vínculo nullable con FK restrictiva, y cambia la unicidad del detalle para permitir el mismo plato destinado a distintos invitados; detalles históricos conservan `id_invitado=NULL`. La eliminación de invitado devuelve `409` si hay detalles asignados, incluidos los invitados sin cuenta.

**Probado correctamente:** suite pytest PostgreSQL aislado: **11 passed, 1 warning**. Incluye varios platos/invitados, repetición del plato para un invitado y el mismo plato para dos invitados, invitado anónimo asignado por titular, autoasignación/aislamiento del invitado registrado, usuario no autorizado, invitado de otra reserva, plato de otro restaurante, montos, integridad al eliminar y pedido independiente. `alembic current`: `b317d4a82e19 (head)`; `alembic check`: `No new upgrade operations detected`.

**Probado con error de colección, luego corregido:** la primera ejecución no encontró un helper importado del módulo vecino de tests; se hizo autocontenido el test y la suite completa pasó en la repetición.

## Matriz de trazabilidad funcional

| Caso de uso | Funcionalidad esperada | Estado real | Implementación localizada | Prueba ejecutada | Error o ausencia detectada | Prioridad |
|---|---|---|---|---|---|---|
| CU01 Registrarse | Crear cuenta pública de cliente validada y con clave protegida | Parcial: código localizado, runtime no verificado | `routers/autenticacion.py`, `services/autenticacion_service.py`, modelos Usuario/Rol, Angular `registro` | No; scripts Parte 2 requieren API | Suite funcional no ejecutable en el entorno actual; revisar integración y validación end-to-end | P2 |
| CU02 Iniciar sesión | Autenticar credenciales y emitir JWT | Probado correctamente (login por roles) | Router/servicio autenticación, JWT | TestClient/PostgreSQL en suite pytest | El login funciona; expiración y otros casos siguen sin ejecutar | P2 |
| CU03 Gestionar perfil | Leer/actualizar perfil y cambiar contraseña autenticado | Parcial: código localizado, runtime no verificado | `routers/usuarios.py`, `services/usuario_service.py`, Angular perfil | No | No se pudo validar control de propiedad ni flujo completo en ejecución | P2 |
| CU04 Gestionar usuarios | Operaciones administrativas y cambio de estado | Parcial; permisos básicos probados | Router usuarios, servicio usuarios, guard Angular | pytest: ADMIN puede acceder; CLIENTE recibe 403 | Listado y bloqueo de rol verificados; cambio de estado no ejecutado | P2 |
| CU05 Registrar restaurante | Crear restaurante asociado al usuario responsable | Probado correctamente | Router/servicio restaurantes, modelos Restaurante/Ubicacion | pytest: creación real HTTP y PostgreSQL | Se probó el flujo básico; edición y permisos cruzados no completos | P2 |
| CU06 Gestionar restaurante | Consultar/editar establecimiento con control de titularidad | Parcial: código localizado, runtime no verificado | Router/servicio restaurantes, `security/propiedad.py`, Angular restaurantes | No | Falta prueba de autorización entre titulares en ejecución | P2 |
| CU07 Gestionar categorías | CRUD administrativo de categorías | Parcial; creación probada | Router/servicio/modelo categoría | pytest: creación con ADMIN en preparación de cada caso | Edición y denegación CRUD completa no probadas | P2 |
| CU08 Gestionar platos | Administrar catálogo, preferencias, estado y disponibilidad | Parcial; alta/listado y control de propietario probados | Router, servicio/repositorio/modelos de platos | pytest: alta, listado de cliente y 403 a otro restaurante | Preferencias, estado y disponibilidad no probados en esta fase | P2 |
| CU09 Gestionar ingredientes y recetas | Mantener ingredientes y composición de platos | Parcial: código localizado, runtime no verificado | `routers/ingredientes.py`, servicios/repositorios y modelos ingrediente/receta | No | Falta validar unidades, propiedad del plato y persistencia integrada | P2 |
| CU10 Gestionar disponibilidad | Cambiar disponibilidad de platos por el restaurante | Parcial: código localizado, runtime no verificado | Endpoint en `routers/platos.py`, servicio plato, Angular platos | No | Falta comprobar titularidad y efecto en recomendaciones/pedidos | P2 |
| CU11 Registrar planificación | Crear/editar planificación con presupuesto y comensales válidos | Parcial: código localizado, runtime no verificado | `routers/planificaciones.py`, servicio/modelos, Angular planificaciones | No | No se ejecutaron pruebas de validación/propiedad | P2 |
| CU12 Definir preferencias | Gestionar catálogo y preferencias personales | Parcial: código localizado, runtime no verificado | `routers/preferencias.py`, servicio/modelos, Angular preferencias | No | Sin comprobación integrada de permisos ni filtrado de recomendaciones | P2 |
| CU13 Generar recomendación | Calcular y guardar opciones ordenadas según planificación | Parcial: algoritmo y rutas localizados, salida no verificada | `services/recomendacion_algoritmo.py`, `recomendacion_service.py`, router y Angular | No | Afirmaciones de trazabilidad no reproducibles en esta ejecución | P1 |
| CU14 Comparar alternativas | Comparar coste y cobertura entre restaurante y preparación propia | Parcial: código localizado, cálculo no verificado | Servicio de recomendación/preparación, schema comparación, Angular comparativa | No | Falta verificar totales y casos sin alternativas/precios | P1 |
| CU15 Consultar ingredientes para preparación | Escalar receta y calcular costes por comensales | Parcial: código localizado, cálculo no verificado | `services/preparacion_service.py`, modelos preparación/ingredientes, Angular preparación | No | No se pudo verificar cálculo con datos reales | P2 |
| CU16 Consultar lugares de compra | Agrupar insumos y comparar precios registrados | Parcial: código localizado, cálculo no verificado | Router/servicio/repositories de lugares de compra, Angular lugares | No | Falta probar precio mínimo, ausencia de proveedor y asociación de ingrediente | P2 |
| CU17 Crear plano 2D | Mantener áreas y distribución persistida de mesas | Parcial: código localizado, runtime no verificado | `routers/areas.py`, servicios distribución/área, Angular editor | No | No se pudo validar guardado/recarga ni build visual | P2 |
| CU18 Gestionar mesas | Crear/editar/desactivar mesas con geometría y capacidad | Parcial: código localizado, runtime no verificado | `routers/mesas.py`, `mesa_service.py`, modelo Mesa | No | Falta comprobar restricciones con reservas activas | P1 |
| CU19 Combinar mesas | Registrar solo pares compatibles, activos, móviles y de la misma área | Parcial; creación de par y reserva combinada probadas | Router mesas, `mesa_combinacion_service.py`, repositorio/modelo | pytest PostgreSQL: crear combinación y reservar dos mesas | Reglas negativas de pares inválidos no cubiertas aquí | P1 |
| CU20 Consultar disponibilidad | Filtrar por fecha/horario, solapamiento y capacidad, incluyendo combinaciones | Probado correctamente (reglas cubiertas) | Router reservas, servicio disponibilidad y repositorios | pytest PostgreSQL: una mesa sobredimensionada se marca NO_COMPATIBLE/no seleccionable | El límite concuerda con el rechazo de CU21 | P1 |
| CU21 Reservar, gestionar invitados y cancelar | Invitados sin cuenta/cuenta vinculada, permisos, duplicados, límite y protección de pedidos | Probado correctamente para CRUD y preservación de invitados con detalles asignados | `reserva_invitado.py`, servicio/repositorio, schemas, router y migración `74c12e89a531` | pytest PostgreSQL: CRUD, reglas y eliminación `409` tras asignar detalle | La atribución de pedidos conserva la ficha del invitado; sin defecto observado en alcance | P1 |
| CU22 Gestionar reservas | Listar/filtrar y transicionar estados con permisos del restaurante | Parcial: código localizado, runtime no verificado | Router/servicio/repositorio reservas, Angular gestión | No | No se pudo ejecutar prueba de titularidad y transiciones | P1 |
| CU23 Enviar pedido | Crear pedidos por usuario, asignar detalles a invitados de una reserva y calcular precio histórico | Probado correctamente para titular, invitado registrado, invitado sin cuenta e independiente | `routers/pedidos.py`, `services/pedido_service.py`, `repositories/reserva_invitado_repository.py`, modelo y schema de detalle | pytest PostgreSQL aislado: asignación múltiple, autorizaciones, pertenencia a reserva/restaurante, subtotales, totales e independiente | No se aceptan invitados de otra reserva ni platos de otro restaurante; precios se originan en catálogo backend | P1 |
| CU24 Gestionar pedidos | Consultar, cancelar y avanzar comanda con control de rol/estado | Parcial; aislamiento de historial probado | Router/servicio/repositorio pedidos | pytest: historial independiente por dos cuentas | Máquina de estados y comanda del restaurante no ejecutadas aquí | P1 |
| CU25 Consultar bitácora | Consultar auditoría de eventos para administrador | No implementado en el árbol revisado | README/trazabilidad mencionan `/bitacora`; no hay router, servicio, modelo ni migración de bitácora | No | Endpoint y persistencia ausentes; la trazabilidad afirma implementación sin correspondencia en código | P1 |
| CU26 Asistencia IA | Interpretar solicitudes y explicar recomendaciones/comparaciones sin reemplazar cálculo determinista | Parcial: módulos localizados, proveedor externo no verificado | `routers/asistente_ia.py`, `services/asistente_ia_service.py`, `app/ai`, Angular asistente | No | La suite Parte 13 requiere API; no se verificaron timeout, configuración ni proveedor remoto | P2 |

## Defectos y dependencias priorizados

1. **P1 — Coherencia de reservas CU20/CU21 (corregido en esta iteración):** `DisponibilidadMesasService` imponía el límite superior de capacidad configurado, pero `ReservaService.crear_reserva` solo rechazaba capacidades insuficientes. Una llamada directa a `POST /reservas` podía aceptar una mesa que la disponibilidad declaraba no seleccionable. La creación ahora valida también `capacidad <= comensales + MAX_EXCESO_CAPACIDAD_MESA`, para mesas individuales y pares.
2. **P1 — CU25 no existe:** el README y la matriz de trazabilidad documentan `/bitacora`, pero no se encontró implementación asociada. Bloquea cumplimiento de auditoría y hace incorrecta la declaración de entrega completa.
3. **P1 — Evidencia de integración reproducible:** las suites de partes dependen de servicios externos levantados y datos seed, y pytest descubre cero tests antes de esta corrección. Falta una suite aislada/automatizada para reglas críticas y un entorno de integración repetible.
4. **P1 — Reservas y pedidos:** concurrencia, autorización por propietario y transiciones son dependencias de operaciones posteriores; priorizar pruebas API con PostgreSQL antes de confiar en los reclamos de trazabilidad.
5. **P2 — Entorno frontend incompleto:** no hay paquetes Angular instalados, así que las rutas y servicios TypeScript no pudieron compilarse.
6. **P2 — Flutter ausente:** no hay aplicación ni manifest Flutter en la copia inspeccionada, pese a que el encargo describe la plataforma como web y móvil.

No se ejecutaron migraciones ni se conectó a una base de datos compartida.
