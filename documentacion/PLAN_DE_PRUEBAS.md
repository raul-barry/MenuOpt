# 📋 PLAN DE PRUEBAS DETALLADO POR CASO DE USO (CU01 A CU26) &mdash; MENUOPT

Este documento constituye la guía exhaustiva y metódica para verificar manualmente cada uno de los **26 Casos de Uso** implementados en la plataforma web **MenuOpt** ([http://localhost:4200](http://localhost:4200)).

---

## 🔑 CREDENCIALES DE ACCESO RÁPIDO

| Rol | Correo Electrónico | Contraseña | Destino Inicial |
|---|---|---|---|
| **CLIENTE 1** | `cliente1@menuopt.com` | `Cliente1234*` | `/inicio` |
| **CLIENTE 2** | `cliente2@menuopt.com` | `Cliente1234*` | `/inicio` (para pruebas de concurrencia e IDOR) |
| **RESTAURANTE** | `restaurante@menuopt.com` | `Resto1234*` | `/restaurantes` |
| **ADMINISTRADOR** | `admin@menuopt.com` | `Admin1234*` | `/admin/usuarios` |

---

# MÓDULO 1: AUTENTICACIÓN, PERFIL Y USUARIOS

### 🧪 CU01: Registrarse
- **Objetivo:** Comprobar que un visitante anónimo puede crear una cuenta de cliente con validaciones y contraseña encriptada.
- **Rol:** Público (sin sesión).
- **Ruta:** `/registro`
- **Pasos:**
  1. Si tienes una sesión abierta, haz clic en **Cerrar Sesión**.
  2. En la pantalla de login, pulsa el enlace **¿No tienes cuenta? Regístrate aquí**.
  3. Intenta enviar el formulario vacío $\rightarrow$ Verificar que los campos se marcan en rojo.
  4. Ingresa un correo ya registrado (ej. `cliente1@menuopt.com`) $\rightarrow$ Verificar mensaje de error *"El correo electrónico ya se encuentra registrado"*.
  5. Completa los campos con un correo nuevo (ej. `nuevo_cliente@test.com`), contraseña `Password123*` y pulsa **Registrarse**.
- **Resultado Esperado:** Mensaje de éxito *"Registro completado con éxito"*, redirección al login y la cuenta queda creada con rol `CLIENTE`.

---

### 🧪 CU02: Iniciar sesión
- **Objetivo:** Validar autenticación segura mediante JWT y redirección contextual según el rol.
- **Rol:** Público.
- **Ruta:** `/login`
- **Pasos:**
  1. Ingresa `cliente1@menuopt.com` con una contraseña incorrecta $\rightarrow$ Verificar mensaje *"Correo electrónico o contraseña incorrectos"*.
  2. Ingresa `cliente1@menuopt.com` con `Cliente1234*` $\rightarrow$ Verificar que ingresa y redirige a `/inicio`.
  3. Cierra sesión e ingresa como `restaurante@menuopt.com` / `Resto1234*` $\rightarrow$ Verificar que redirige a `/restaurantes`.
  4. Cierra sesión e ingresa como `admin@menuopt.com` / `Admin1234*` $\rightarrow$ Verificar que redirige a `/admin/usuarios`.
- **Resultado Esperado:** Cada rol entra correctamente, recibe su token JWT y ve el menú correspondiente en la barra lateral.

---

### 🧪 CU03: Gestionar perfil
- **Objetivo:** Consultar y modificar datos personales y contraseña del usuario autenticado.
- **Rol:** `CLIENTE` (o cualquier usuario).
- **Ruta:** `/perfil` (vía enlace **Mi Perfil** en el menú).
- **Pasos:**
  1. Entra como `cliente1@menuopt.com`.
  2. En el menú haz clic en **Mi Perfil**.
  3. Modifica tu teléfono a `77712345` y presiona **Actualizar Perfil** $\rightarrow$ Debe mostrar *"Perfil actualizado con éxito"*.
  4. En la tarjeta de cambio de clave, escribe una clave nueva menor a 8 caracteres $\rightarrow$ El botón debe bloquearse.
  5. Escribe una clave válida pero pon diferente la confirmación $\rightarrow$ Debe alertar *"Las contraseñas no coinciden"*.
- **Resultado Esperado:** Datos modificados se guardan de inmediato. Los campos sensibles (rol, ID de usuario) son de solo lectura.

---

### 🧪 CU04: Gestionar usuarios
- **Objetivo:** Permitir al administrador listar y activar/desactivar usuarios del sistema.
- **Rol:** `ADMINISTRADOR`.
- **Ruta:** `/admin/usuarios`
- **Pasos:**
  1. Inicia sesión como `admin@menuopt.com`.
  2. En el menú ve a **Usuarios**.
  3. Observa la tabla con paginación, roles (`CLIENTE`, `RESTAURANTE`, `ADMINISTRADOR`) y estados.
  4. Localiza un usuario de prueba (ej. `cliente2@menuopt.com`) y haz clic en el botón de cambiar estado a **INACTIVO**.
  5. En una ventana de incógnito intenta hacer login con ese usuario desactivado $\rightarrow$ Debe rechazar con *"Su cuenta se encuentra inactiva o suspendida"*.
  6. Vuelve a activarlo desde la cuenta admin.
- **Resultado Esperado:** Cambio de estado inmediato y bloqueo estricto de autenticación para cuentas inactivas.

---

# MÓDULO 2: GESTIÓN DE RESTAURANTES, PLATOS Y CATÁLOGO

### 🧪 CU05: Registrar restaurante
- **Objetivo:** Dar de alta un nuevo restaurante comercial.
- **Rol:** `RESTAURANTE` o `ADMINISTRADOR`.
- **Ruta:** `/restaurantes/nuevo`
- **Pasos:**
  1. Entra como `restaurante@menuopt.com`.
  2. Ve a **Mis Restaurantes** y pulsa el botón **+ Nuevo Restaurante**.
  3. Llena el nombre (ej. *"Trattoria Bella Vista"*), teléfono, horario de atención y ubicación.
  4. Haz clic en **Guardar Restaurante**.
- **Resultado Esperado:** El restaurante aparece en la lista de establecimientos del usuario.

---

### 🧪 CU06: Gestionar restaurante
- **Objetivo:** Consultar y modificar los datos de un restaurante propio.
- **Rol:** `RESTAURANTE`.
- **Ruta:** `/restaurantes`
- **Pasos:**
  1. En **Mis Restaurantes**, localiza tu restaurante y pulsa **Editar**.
  2. Modifica la descripción y pulsa **Actualizar**.
  3. Verifica que los cambios se reflejan en la ficha del restaurante.
- **Resultado Esperado:** Datos actualizados. Si un restaurante ajeno intenta entrar a la URL directa de este restaurante, recibe 403 Forbidden.

---

### 🧪 CU07: Gestionar categorías
- **Objetivo:** Administrar el catálogo de tipos de platos gastronómicos.
- **Rol:** `ADMINISTRADOR`.
- **Ruta:** `/admin/categorias`
- **Pasos:**
  1. Entra como `admin@menuopt.com` y ve a **Categorías**.
  2. Observa las categorías existentes (Pastas, Carnes, Ensaladas, etc.).
  3. Pulsa **Nueva Categoría**, ingresa *"Comida Rápida Saludable"* y guarda.
- **Resultado Esperado:** La categoría queda registrada y disponible para que los restaurantes la elijan al crear platos.

---

### 🧪 CU08: Gestionar platos
- **Objetivo:** Crear platos con precio Decimal, tipo de comida, personas cubiertas y preferencias dietarias.
- **Rol:** `RESTAURANTE`.
- **Ruta:** `/restaurantes/:id/platos` $\rightarrow$ **+ Nuevo Plato**
- **Pasos:**
  1. Entra como `restaurante@menuopt.com` $\rightarrow$ **Mis Restaurantes** $\rightarrow$ Pulsa en **Platos** de tu restaurante.
  2. Pulsa **+ Nuevo Plato**.
  3. Ingresa:
     - Nombre: *"Lasaña de Berenjenas"*
     - Precio: `45.00` Bs.
     - Personas cubiertas: `1`
     - Tipo de comida: `ALMUERZO`
     - Categoría: Selecciona una del catálogo.
     - Preferencias: Marca los checkboxes *"Vegetariano"* y *"Sin gluten"*.
  4. Guarda el plato.
- **Resultado Esperado:** El plato se crea con sus preferencias en la base de datos relacional y aparece en el menú activo.

---

### 🧪 CU09: Gestionar ingredientes
- **Objetivo:** Definir la receta estructurada de insumos por plato para costeo de preparación propia.
- **Rol:** `RESTAURANTE` o `ADMINISTRADOR`.
- **Ruta:** `/ingredientes` y ficha de plato
- **Pasos:**
  1. Como admin o restaurante ve a **Catálogo Ingredientes**.
  2. Verifica que existen ingredientes con su unidad de medida (kg, litro, unidad).
  3. En la lista de platos, entra a un plato y asocia ingredientes con su cantidad exacta para esa receta base.
- **Resultado Esperado:** La receta queda guardada en `plato_ingrediente` lista para ser usada en el escalado de preparación propia.

---

### 🧪 CU10: Gestionar disponibilidad de platos
- **Objetivo:** Conmutar rápidamente si un plato se ofrece al público o está agotado.
- **Rol:** `RESTAURANTE`.
- **Ruta:** `/restaurantes/:id/platos`
- **Pasos:**
  1. En la lista de platos, localiza cualquier plato.
  2. Cambia el interruptor de **Disponible** a **No disponible**.
  3. Cierra sesión y entra como `cliente1@menuopt.com`.
  4. En el menú público de ese restaurante comprueba que el plato marcado como no disponible no puede ser pedido ni aparece en recomendaciones.
- **Resultado Esperado:** Conmutación inmediata en base de datos (`PATCH /platos/:id/disponibilidad`).

---

# MÓDULO 3: ASISTENTE IA, PLANIFICACIÓN, RECOMENDACIÓN Y COMPARACIÓN

### 🧪 CU26: Usar asistencia con IA
- **Objetivo:** Interpretar peticiones en lenguaje natural, estructurar criterios sin inventar datos y solicitar datos faltantes.
- **Rol:** `CLIENTE`.
- **Ruta:** `/asistente`
- **Pasos:**
  1. Inicia sesión como `cliente1@menuopt.com`.
  2. En el menú haz clic en **🤖 Asistente IA**.
  3. **Prueba de datos faltantes:** Escribe: *"Quiero cenar algo sin gluten"* $\rightarrow$ Observa que el asistente detecta la comida y preferencia, pero te pide amablemente indicar el presupuesto y cuántas personas son.
  4. **Prueba de contexto continuo:** Responde a continuación: *"Somos 4 personas y tenemos 200 Bs en Equipetrol"*.
  5. Observa cómo el asistente combina ambos mensajes y llena la tarjeta estructurada de la derecha con todos los campos.
  6. **Prueba de edición directa:** Modifica el presupuesto en la cajita de la derecha si deseas.
- **Resultado Esperado:** Detección de entidades, validación de preferencias contra PostgreSQL y botón listo para crear planificación.

---

### 🧪 CU11: Registrar planificación gastronómica
- **Objetivo:** Registrar formalmente una necesidad gastronómica con presupuesto y comensales.
- **Rol:** `CLIENTE`.
- **Ruta:** `/planificaciones/nueva` (o mediante el botón del Asistente IA).
- **Pasos:**
  1. Ve a **Planificar comida** en el menú.
  2. Ingresa Presupuesto: `300` Bs.
  3. Cantidad de personas: `10`.
  4. Tipo de comida: `ALMUERZO`.
  5. Ubicación: `Equipetrol`.
  6. Preferencias: Selecciona *"Vegetariano"*.
  7. Pulsa **Guardar Planificación**.
- **Resultado Esperado:** Se crea la planificación con ID oficial en la base de datos y redirige a la vista de recomendaciones.

---

### 🧪 CU12: Definir preferencias
- **Objetivo:** Consultar y personalizar las preferencias dietarias habituales del usuario.
- **Rol:** `CLIENTE`.
- **Ruta:** `/preferencias`
- **Pasos:**
  1. En el menú ve a **Mis preferencias**.
  2. Marca o desmarca preferencias dietarias (ej. *Vegetariano*, *Sin gluten*, *Sin lactosa*).
  3. Pulsa **Guardar Preferencias**.
- **Resultado Esperado:** Mensaje de éxito; cuando crees una nueva planificación, estas preferencias aparecerán preseleccionadas como sugerencia.

---

### 🧪 CU13: Generar recomendación
- **Objetivo:** Ejecutar el algoritmo determinístico de optimización para encontrar restaurantes que cumplan presupuesto y comensales.
- **Rol:** `CLIENTE`.
- **Ruta:** `/planificaciones/:id/recomendaciones`
- **Pasos:**
  1. En la planificación creada, pulsa el botón **Generar Recomendaciones**.
  2. Observa el listado de tarjetas generadas:
     - Cada tarjeta muestra el restaurante, el plato sugerido, el costo total escalado para 10 personas y el costo por persona.
     - Ninguna opción supera los 300 Bs del presupuesto.
  3. En una de las tarjetas, pulsa el botón **🤖 ¿Por qué esta opción?**.
- **Resultado Esperado:** Modal interactivo de IA que explica con exactitud el ahorro, la satisfacción de comensales y el cumplimiento de preferencias sin inventar datos.

---

### 🧪 CU14: Comparar alternativas (Restaurante vs Preparación Propia)
- **Objetivo:** Contrastar opciones comerciales contra elaboración en casa mediante matriz de ahorro y score.
- **Rol:** `CLIENTE`.
- **Ruta:** `/planificaciones/:id/comparacion`
- **Pasos:**
  1. Desde la pantalla de recomendaciones, haz clic en **📊 Comparar Alternativas**.
  2. Observa la matriz analítica con dos secciones o tarjetas destacadas:
     - **Opción Menor Costo**
     - **Opción Mejor Puntuación**
  3. Comprueba que aparecen opciones de tipo `RESTAURANTE` y de tipo `PREPARACION_PROPIA`.
  4. Haz clic en el botón superior **🤖 Explicar Comparación**.
- **Resultado Esperado:** Resumen comparativo con los puntos clave de ahorro financiero y esfuerzo de preparación.

---

### 🧪 CU15: Consultar ingredientes para preparación propia
- **Objetivo:** Ver la lista de compras exacta con cantidades escaladas según el número de personas planificado.
- **Rol:** `CLIENTE`.
- **Ruta:** En la tarjeta de preparación propia $\rightarrow$ botón **🥗 Ingredientes**.
- **Pasos:**
  1. En la comparativa, ubica una alternativa de preparación propia y haz clic en **Ingredientes**.
  2. Verifica la tabla de compras:
     - Muestra las cantidades escaladas (ej. si la receta para 1 persona usa 0.2 kg de carne, para 10 personas muestra 2.0 kg).
     - Muestra el costo estimado por insumo y el total en Bs.
- **Resultado Esperado:** Cálculo matemático exacto de insumos para el grupo completo de comensales.

---

### 🧪 CU16: Consultar lugares de compra
- **Objetivo:** Identificar dónde adquirir los ingredientes al precio más bajo agrupados por mercado/supermercado.
- **Rol:** `CLIENTE`.
- **Ruta:** En la tarjeta de preparación propia $\rightarrow$ botón **🏪 Lugares de Compra**.
- **Pasos:**
  1. Haz clic en **Lugares de Compra**.
  2. Verifica que los ingredientes se agrupan por establecimiento (ej. *Mercado Mutualista*, *Hipermaxi*).
  3. Comprueba que el sistema seleccionó el precio unitario más económico registrado.
- **Resultado Esperado:** Agrupación clara por comercio para facilitar la logística de compra.

---

# MÓDULO 4: PLANO 2D, MESAS Y COMBINACIONES

### 🧪 CU17: Crear plano 2D del restaurante
- **Objetivo:** Diseñar y mover mesas en un lienzo gráfico interactivo en cuadrícula normalizada.
- **Rol:** `RESTAURANTE`.
- **Ruta:** `/restaurantes/:id/distribucion`
- **Pasos:**
  1. Entra como `restaurante@menuopt.com`.
  2. Ve a **Mis Restaurantes** $\rightarrow$ Haz clic en **Áreas & Plano 2D** en tu restaurante.
  3. Entra a un área (ej. *Salón Principal*) y haz clic en **🎨 Distribución 2D**.
  4. Haz clic sostenido en una mesa y arrástrala a otra posición del plano.
  5. Haz clic en el botón **Guardar Distribución**.
  6. Recarga la página del navegador (`F5`).
- **Resultado Esperado:** La mesa mantiene exactamente su nueva posición gracias a las coordenadas relativas `[posicion_x, posicion_y]`.

---

### 🧪 CU18: Gestionar mesas
- **Objetivo:** Modificar forma, capacidad, rotación y tipo fija/movible de las mesas.
- **Rol:** `RESTAURANTE`.
- **Ruta:** En el editor de distribución o en la lista de mesas del área.
- **Pasos:**
  1. En el editor 2D, haz clic sobre una mesa para seleccionarla.
  2. En el panel de propiedades lateral:
     - Cambia la capacidad de `4` a `6`.
     - Cambia la forma a `REDONDA`.
     - Haz clic en **Rotar 90°**.
  3. Guarda los cambios.
- **Resultado Esperado:** La mesa se redibuja en el lienzo reflejando la nueva forma geométrica, orientación y capacidad.

---

### 🧪 CU19: Definir combinación de mesas
- **Objetivo:** Unir dos mesas del mismo área para albergar grupos grandes con relación simétrica bidireccional.
- **Rol:** `RESTAURANTE`.
- **Ruta:** Editor 2D o sección de combinaciones.
- **Pasos:**
  1. En el área del restaurante, selecciona la Mesa 1 y pulsa **Combinar con otra mesa**.
  2. Selecciona la Mesa 2 contigua y confirma la combinación.
  3. Comprueba que la capacidad total se suma (ej. 4 + 4 = 8 personas).
- **Resultado Esperado:** La combinación queda registrada en `mesa_combinacion` y queda lista para ser reservada conjuntamente.

---

# MÓDULO 5: RESERVAS Y CONCURRENCIA

### 🧪 CU20: Consultar disponibilidad de mesas
- **Objetivo:** Calcular la disponibilidad dinámica de mesas según fecha, horario y comensales en el plano 2D.
- **Rol:** `CLIENTE`.
- **Ruta:** `/restaurantes/:id/reservar`
- **Pasos:**
  1. Inicia sesión como `cliente1@menuopt.com`.
  2. En el menú haz clic en **Inicio (Panel Cliente)** y busca *Parrilla Don Carlos*.
  3. Haz clic en **📅 Reservar Mesa**.
  4. Ingresa:
     - Fecha: Una fecha de mañana o próxima semana.
     - Horario: `19:00` a `21:00`.
     - Personas: `4`.
  5. Pulsa **Consultar Disponibilidad**:
     - Las mesas libres con capacidad óptima se iluminan en **verde** (DISPONIBLE).
     - Las mesas demasiado pequeñas o muy grandes se muestran en **amarillo** (NO_COMPATIBLE).
- **Resultado Esperado:** El mapa 2D colorea las mesas en tiempo real sin basarse en estados fijos en la base de datos.

---

### 🧪 CU21: Realizar reserva y prevenir doble reserva (Concurrencia)
- **Objetivo:** Confirmar una reserva con bloqueo `SELECT FOR UPDATE` y verificar que el sistema rechaza colisiones con HTTP 409.
- **Rol:** `CLIENTE 1` y `CLIENTE 2`.
- **Ruta:** `/restaurantes/:id/reservar`
- **Pasos:**
  1. Con los datos del CU20 anterior, selecciona una mesa verde (ej. *Mesa 2*) y pulsa **Confirmar Reserva** $\rightarrow$ Debe responder *"Reserva confirmada con éxito"*.
  2. Ve a **Mis Reservas** en el menú para comprobar que aparece con estado `CONFIRMADA`.
  3. **Prueba de doble reserva (Concurrencia):**
     - Abre una ventana en modo **Incógnito** y entra como `cliente2@menuopt.com` / `Cliente1234*`.
     - Ve al mismo restaurante y pon exactamente la misma fecha y horario (`19:00` a `21:00`).
     - Observa que esa mesa ahora aparece en **rojo/gris (NO_DISPONIBLE)**.
     - Si intentas forzar la reserva para esa mesa, el sistema responderá con **HTTP 409 Conflicto** impidiendo la doble reserva.
- **Resultado Esperado:** Transacción blindada, reserva guardada e imposibilidad de que dos clientes reserven la misma mesa en horarios que colisionen.

---

### 🧪 CU22: Gestionar reservas
- **Objetivo:** Permitir al restaurante consultar reservas recibidas y avanzar su estado (Finalizada / Cancelada).
- **Rol:** `RESTAURANTE`.
- **Ruta:** `/restaurantes/:id/reservas`
- **Pasos:**
  1. Inicia sesión como `restaurante@menuopt.com`.
  2. Ve a **Mis Restaurantes** y haz clic en **Reservas Recibidas**.
  3. Localiza la reserva recién creada por el cliente.
  4. Haz clic en **Marcar como Finalizada**.
- **Resultado Esperado:** La reserva pasa a estado `FINALIZADA` de forma controlada.

---

# MÓDULO 6: PEDIDOS Y COMANDAS

### 🧪 CU23: Enviar pedido con precios históricos
- **Objetivo:** Enviar un pedido, validar platos del mismo restaurante y verificar la inmutabilidad de precios históricos en Decimal.
- **Rol:** `CLIENTE`.
- **Ruta:** `/restaurantes/:id/pedido`
- **Pasos:**
  1. Inicia sesión como `cliente1@menuopt.com`.
  2. En **Inicio**, selecciona un restaurante y pulsa **🛍️ Hacer Pedido**.
  3. Selecciona 2 platos, ajusta cantidades (ej. 2 unidades de uno y 1 de otro).
  4. Escribe una observación: *"Por favor sin salsa picante"*.
  5. Presiona **Enviar Pedido**.
  6. Ve a **Mis Pedidos** en el menú lateral:
     - Comprueba que el pedido aparece en estado `PENDIENTE` con el total exacto en Bs.
- **Resultado Esperado:** Pedido registrado exitosamente. Si luego el restaurante sube los precios en su catálogo, este pedido mantendrá inalterado su precio histórico guardado.

---

### 🧪 CU24: Gestionar pedidos (Comanda digital)
- **Objetivo:** Gestionar el ciclo de vida de la comanda del restaurante a través de su máquina de estados.
- **Rol:** `RESTAURANTE`.
- **Ruta:** `/restaurantes/:id/pedidos`
- **Pasos:**
  1. Inicia sesión como `restaurante@menuopt.com`.
  2. Ve a **Mis Restaurantes** y pulsa **Comanda de Pedidos**.
  3. Ubica el pedido en estado `PENDIENTE` y avanza secuencialmente:
     - Haz clic en **Aceptar** $\rightarrow$ Estado cambia a `ACEPTADO`.
     - Haz clic en **Enviar a Cocina** $\rightarrow$ Estado cambia a `EN_PREPARACION`.
     - Haz clic en **Marcar Listo** $\rightarrow$ Estado cambia a `LISTO`.
     - Haz clic en **Entregar Pedido** $\rightarrow$ Estado cambia a `ENTREGADO`.
  4. En otra ventana con la sesión del cliente, recarga **Mis Pedidos** y comprueba que el estado final es `ENTREGADO`.
- **Resultado Esperado:** Flujo completo de la comanda sin permitir saltos de estado inválidos.

---

# MÓDULO 7: AUDITORÍA Y TRAZABILIDAD

### 🧪 CU25: Consultar bitácora
- **Objetivo:** Garantizar la auditoría y trazabilidad de operaciones críticas en el sistema.
- **Rol:** `ADMINISTRADOR`.
- **Ruta:** Terminal / Consola de auditoría de Docker.
- **Pasos:**
  1. Abre tu terminal en la carpeta del proyecto.
  2. Ejecuta:
     ```bash
     docker compose logs --tail=50 backend
     ```
  3. Comprueba que las operaciones transaccionales ejecutadas (login, creación de planificaciones, generación de reservas y cambios de estado de pedidos) se registraron con marcas de tiempo e identificadores de usuario sin filtrar contraseñas ni tokens.
- **Resultado Esperado:** Registro limpio de auditoría sin fugas de credenciales.
