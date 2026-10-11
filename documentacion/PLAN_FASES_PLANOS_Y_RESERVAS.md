# 🗺️ Plan de Desarrollo por Fases: Planos 2D, Mesas y Reservas (CU17 a CU22)

Este plan establece una metodología de desarrollo **incremental y validada por caso de uso**. Trabajaremos fase por fase de forma individual:
1. Se ajusta y perfecciona el caso de uso correspondiente.
2. Tú realizas las pruebas funcionales guiadas en tu navegador.
3. Tras tu confirmación y visto bueno (*"Aprobado"*), avanzamos al siguiente.

---

## 📌 Resumen de Fases

| Fase | Caso de Uso | Enfoque Principal | Actor Responsable | Estado |
| :---: | :---: | :--- | :--- | :---: |
| **Fase 1** | **CU17** | Gestión de Áreas Físicas y Lienzo 2D con pestañas estilo Excel | `RESTAURANTE` | 🟢 **Completado** |
| **Fase 2** | **CU18** | Gestión de Mesas (13 modelos SVG arquitectónicos, drag & drop) | `RESTAURANTE` | 🟢 **Completado** |
| **Fase 3** | **CU19** | Combinaciones de Mesas contiguas con conectores visuales en plano | `RESTAURANTE` | 🟡 **Completado (En Validación)** |
| **Fase 4** | **CU20** | Consulta dinámica de disponibilidad en tiempo real sobre el plano 2D | `CLIENTE` | ⚪ Siguiente |
| **Fase 5** | **CU21** | Elección interactiva de mesas y confirmación con blindaje anti-colisión | `CLIENTE` | ⚪ Pendiente |
| **Fase 6** | **CU22** | Gestión operativa de reservas y asignación de mesas en servicio | `RESTAURANTE` | ⚪ Pendiente |

---

## 🧱 Desglose Detallado de Cada Fase

### 📍 FASE 1: CU17 — Gestión de Áreas Físicas y Creación del Plano 2D
* **Objetivo:** Permitir al restaurante estructurar sus ambientes físicos independientes (Salón Principal, Terraza, Jardín, etc.) y visualizar el plano 2D mediante navegación fluida por pestañas tipo Excel.
* **Componentes clave:**
  - Creación automática del área "Salón Principal" al registrar el restaurante.
  - Barra de navegación interactiva por pestañas (hojas de cálculo) con botón rápido `[ + ]`.
  - Creación, edición de nombre, dimensiones del lienzo (`ancho_mapa x alto_mapa`) y baja lógica de áreas.
  - Coordenadas relativas normalizadas `[0.0 a 1.0]` para garantizar adaptabilidad responsive en cualquier pantalla.
* **Criterio de Validación del Usuario:**
  1. Entrar como restaurante a *Áreas & Plano 2D*.
  2. Ver la pestaña "Salón Principal" ya lista.
  3. Pulsar `[ + ]` y crear una nueva área física (ej. *"Terraza Exterior"*).
  4. Alternar entre pestañas y verificar que cada área abre su propio lienzo 2D independiente.

---

### 📍 FASE 2: CU18 — Gestión de Mesas en el Plano 2D
* **Objetivo:** Dotar a cada área física de su inventario de mesas personalizadas con ubicación espacial arrastrable.
* **Componentes clave:**
  - Agregar mesas al área seleccionada (código/número, capacidad mínima y máxima).
  - Configuración geométrica: `CUADRADA`, `RECTANGULAR`, `REDONDA`.
  - Rotación en ángulos (0°, 90°, 180°, 270°) y clasificación (Fija o Movible).
  - Arrastrar y soltar (*drag & drop*) fluido dentro del lienzo con guardado persistente en base de datos.
* **Criterio de Validación del Usuario:**
  1. En el área deseada, crear una mesa de 4 personas (cuadrada) y otra de 6 personas (redonda).
  2. Moverlas a distintos puntos del plano y pulsar *Guardar Distribución*.
  3. Recargar la página (`F5`) y comprobar que las mesas conservan su ubicación exacta.

---

### 📍 FASE 3: CU19 — Definir Combinación de Mesas
* **Objetivo:** Permitir la unión física de dos o más mesas contiguas para acoger grupos grandes.
* **Componentes clave:**
  - Regla de negocio estricta: Sólo se pueden combinar mesas **pertenecientes a la misma área física**.
  - Relación simétrica bidireccional en la base de datos (Mesa A con Mesa B implica Mesa B con Mesa A).
  - Cálculo automático de la capacidad resultante combinada.
  - Indicador visual en el plano que dibuja la unión entre las mesas combinables.
* **Criterio de Validación del Usuario:**
  1. Seleccionar la Mesa 1 y pulsar *Combinar*.
  2. Elegir la Mesa 2 vecina.
  3. Verificar que el sistema muestra el enlace entre ambas y la capacidad sumada (ej. 4 + 4 = 8 personas).

---

### ✅ FASE 4: CU20 — Consulta de Disponibilidad de Mesas en Vivo (COMPLETADA)
* **Objetivo:** Mostrar al comensal el plano 2D coloreado en vivo según fecha, horario y comensales deseados.
* **Componentes clave:**
  - Pestañas estilo Excel en la vista del cliente para cambiar de ambiente (*Salón* vs *Terraza*).
  - Cálculo dinámico cruzando reservas existentes sin estados fijos en la base de datos.
  - Renderizado con SVG arquitectónico (`MesaSvgComponent`) con semáforo visual en el plano:
    - 🟢 **Verde (`DISPONIBLE`):** Libre y capacidad adecuada para el grupo.
    - 🟡 **Amarillo (`NO_COMPATIBLE`):** Libre de reservas pero capacidad insuficiente o excesiva.
    - 🔴 **Rojo (`NO_DISPONIBLE`):** Ocupada por otra reserva en ese intervalo horario.
    - 🔵 **Naranja (`SELECCIONADA`):** Mesa elegida por el comensal.
  - Visualización de combinaciones de mesas en el plano del comensal con conectores SVG y chips de capacidad.
* **Criterio de Validación del Usuario:**
  1. Como cliente, entrar a *Reservar Mesa* (`/restaurantes/:id/reservar`), poner fecha y hora.
  2. Cambiar entre las pestañas de área (estilo Excel) y verificar que el plano 2D se colorea en vivo con el semáforo y se dibujan las sillas arquitectónicas.

---

### 📍 FASE 5: CU21 — Elección de Mesa y Confirmación de Reserva
* **Objetivo:** El cliente hace clic sobre la mesa verde favorita (o combinación de mesas) y asegura su reserva sin riesgo de doble reserva.
* **Componentes clave:**
  - Selección interactiva directa sobre el dibujo de la mesa en el mapa 2D.
  - Transacción segura en PostgreSQL con bloqueo pesimista `SELECT ... FOR UPDATE`.
  - Prevención de concurrencia: si dos clientes intentan reservar la misma mesa a la vez, el segundo recibe **HTTP 409 Conflicto**.
* **Criterio de Validación del Usuario:**
  1. Hacer clic en una mesa verde, confirmar la reserva y ver el comprobante.
  2. Abrir otra ventana (o incógnito con otro cliente) y comprobar que esa misma mesa ahora sale en rojo (no disponible).

---

### 📍 FASE 6: CU22 — Gestión de Reservas por el Restaurante
* **Objetivo:** El personal del restaurante visualiza las mesas reservadas en el plano del día y administra su flujo.
* **Componentes clave:**
  - Tablero de control y plano operativo del restaurante.
  - Transiciones de estado: `CONFIRMADA` $\rightarrow$ `EN_CURSO` $\rightarrow$ `FINALIZADA` (o `CANCELADA`).
  - Consulta de comensales e invitados asignados a cada mesa.
* **Criterio de Validación del Usuario:**
  1. Entrar como restaurante a *Gestión de Reservas*.
  2. Identificar la reserva realizada en la Fase 5 y avanzar su estado.
