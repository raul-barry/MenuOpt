# Datos de prueba del Bloque 2

El módulo `backend.app.database.seed_bloque2` crea un conjunto ficticio e identificable para probar manualmente CU05, CU06, CU07, CU08, CU09, CU17, CU18, CU19, CU20, CU21, CU22, CU23 y CU24. Usa exclusivamente modelos y tablas existentes; no necesita migraciones.

## Seguridad y repetición

- Solo corre si `APP_ENV` o `ENVIRONMENT` vale `development`, `dev`, `test` o `testing`. En desarrollo además exige un host local y una base `menuopt`, `menuopt_db`, `menuopt_dev` o `menuopt_development`; en pruebas exige que el nombre de la base incluya `test`.
- Verifica la conexión a PostgreSQL antes de escribir.
- Pide la contraseña común de las cuentas en una entrada oculta. No hay contraseñas en el código ni en este documento.
- Inserta el set en una sola transacción. Si ya existen las cuentas `b2.*@example.com`, aborta sin duplicar; limpia el conjunto antes de volver a generarlo.
- `--clean` elimina registros identificados por los usuarios, restaurantes y prefijos B2. No borra cuentas, categorías o ingredientes si conservan relaciones ajenas.
- Las operaciones inválidas se prueban enviando solicitudes inválidas sobre estos datos; el seeder no inserta datos corruptos.

## Ejecución local con Docker (PowerShell)

Desde la raíz del repositorio:

```powershell
docker compose exec -it -e APP_ENV=development backend python -m app.database.seed_bloque2
docker compose exec -it -e APP_ENV=development backend python -m app.database.seed_bloque2 --clean
```

El primer comando solicita la contraseña común de las cuentas de prueba sin mostrarla al escribir. El segundo limpia el set y no solicita contraseña. Ambos requieren una conexión funcional del backend con PostgreSQL. Si el contenedor corre con una configuración distinta, utiliza `APP_ENV=test` solo contra una base aislada de pruebas.

## Cuentas de prueba

Las cinco cuentas se crean con la misma contraseña ingresada al ejecutar el seeder:

| Rol | Correo | Uso |
|---|---|---|
| RESTAURANTE | `b2.restaurante.a@example.com` | Propietario de Sabor Cruceño |
| RESTAURANTE | `b2.restaurante.b@example.com` | Propietario de Patio Andino; prueba de acceso cruzado |
| CLIENTE | `b2.cliente.a@example.com` | Titular de reservas y pedidos del primer restaurante |
| CLIENTE | `b2.cliente.b@example.com` | Titular de reservas y pedidos del segundo restaurante |
| CLIENTE | `b2.cliente.c@example.com` | Invitado vinculado para pruebas de titularidad y pedidos |

Todas son cuentas ficticias de desarrollo. No reutilices esta contraseña en otros entornos.

## Inventario generado

- 2 restaurantes con propietarios distintos: **B2-DEMO | Sabor Cruceño** y **B2-DEMO | Patio Andino**.
- 4 áreas: Salón Principal y Terraza para cada restaurante. Incluyen elementos de plano de ejemplo.
- 20 mesas: 5 por área, con capacidades de 2, 4, 4, 6 y 8; formas variadas, ubicaciones normalizadas y una mesa fija/no combinable por área.
- 8 combinaciones válidas: dos pares combinables en cada área. La mesa fija de cada área queda como referencia para intentos inválidos por API.
- 4 categorías, 8 platos (4 por restaurante), 6 ingredientes y 16 relaciones de receta.
- 10 reservas (5 por restaurante): confirmadas, pendiente, finalizada, cancelada, individual y grupal; 10 invitados entre vinculados y sin cuenta.
- 12 pedidos (6 por restaurante), uno por estado válido de la máquina: `PENDIENTE`, `ACEPTADO`, `EN_PREPARACION`, `LISTO`, `ENTREGADO` y `CANCELADO`; incluyen líneas asignadas a invitados y precios guardados como `Decimal`.

Los datos que afectan disponibilidad están distribuidos en fechas y mesas para evitar conflictos inválidos entre filas. Para comprobar solapamientos, capacidad excedida, duplicados, acceso cruzado, transiciones no permitidas, eliminación de un invitado con pedido y conflictos HTTP 409, ejecuta solicitudes negativas contra los registros correspondientes.

## Casos cubiertos y límites

| Casos | Datos útiles |
|---|---|
| CU05-CU06 | Dos restaurantes, dos responsables y ubicaciones distintas; permite probar edición y propiedad cruzada. |
| CU07-CU09 | Categorías, platos, disponibilidad mixta, ingredientes y recetas. |
| CU17-CU19 | Áreas con plano/elementos, mesas con formas/capacidades diferentes y combinaciones válidas. |
| CU20-CU22 | Mesas reservadas y libres, fechas/horarios, estados de reserva e invitados. Una reserva confirmada ocupa una mesa en una fecha futura; conserva otras mesas libres para concurrencia. |
| CU23-CU24 | Pedidos asociados a reservas, líneas por invitado, precios históricos y distintos estados de comanda. |

El sistema no almacena un historial de cambios de precio del catálogo; el caso de precio histórico se demuestra comparando el precio copiado en `detalle_pedido` con una edición posterior del plato, y luego restaurando el catálogo. La concurrencia real debe probarse con solicitudes simultáneas durante la sesión manual. El seeder ofrece mesas libres y ocupadas, pero no lanza solicitudes concurrentes.

En la versión revisada, Angular contiene las vistas de administración de restaurantes, planos, reservas y pedidos. Flutter ofrece principalmente flujos de cliente (planificación, recomendaciones, reservas, pedidos y asistente); no se encontraron pantallas móviles para administrar restaurantes, planos o comandas. Por ello las cuentas RESTAURANTE y los casos CU05-CU09/CU17-CU19/CU22-CU24 se prueban desde Angular o la API.

## Validación automatizada aislada

El test `backend/test_seed_bloque2_isolated.py` crea el esquema en SQLite en memoria, siembra el conjunto, verifica el inventario, comprueba que una segunda ejecución no duplica y limpia las filas conservando un usuario ajeno. No se conecta al PostgreSQL local.
