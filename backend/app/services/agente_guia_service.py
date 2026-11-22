from typing import Any, Dict, List, Optional

from app.ai.proveedor import obtener_proveedor_ia
from app.schemas.agente_guia import MensajeGuia, RespuestaGuia


def _accion(
    id_accion: str,
    nombre: str,
    ruta: str,
    pasos: List[str],
    seccion_movil: Optional[int] = None,
) -> Dict[str, Any]:
    return {
        "id": id_accion,
        "nombre": nombre,
        "ruta": ruta,
        "seccion_movil": seccion_movil,
        "pasos": pasos,
    }


ACCIONES_POR_ROL: Dict[str, List[Dict[str, Any]]] = {
    "CLIENTE": [
        _accion("planificar", "Crear una planificación de comida", "/planificaciones/nueva", ["Abre «Planificar comida» desde el menú.", "Indica presupuesto, cantidad de personas, tipo de comida y zona.", "Guarda la planificación para consultar las recomendaciones."], 1),
        _accion("planes", "Consultar mis planificaciones y recomendaciones", "/planificaciones", ["Abre «Mis planificaciones».", "Selecciona una planificación guardada.", "Revisa sus recomendaciones y abre la opción que te interese."], 2),
        _accion("preferencias", "Configurar mis preferencias", "/preferencias", ["Abre «Mis preferencias».", "Marca las preferencias alimentarias que quieras aplicar.", "Guarda los cambios."], 3),
        _accion("recetas", "Consultar recetas y el asistente culinario", "/recetas", ["Abre «Biblioteca de Recetas».", "Busca o filtra una receta; también puedes indicar ingredientes al asistente culinario.", "Abre una receta para revisar sus detalles."], 8),
        _accion("reservar", "Reservar una mesa", "/inicio", ["Abre el restaurante que te interesa.", "Elige «Reservar», indica fecha, horario y número de personas.", "Selecciona una mesa disponible y confirma la reserva."], 4),
        _accion("reservas", "Revisar mis reservas", "/mis-reservas", ["Abre «Mis Reservas».", "Selecciona una reserva para revisar su estado y detalles."], 4),
        _accion("pedir", "Realizar un pedido", "/inicio", ["Abre el restaurante y entra a su menú.", "Selecciona los platos y cantidades.", "Revisa el resumen y confirma el pedido."], 5),
        _accion("pedidos", "Consultar mis pedidos", "/mis-pedidos", ["Abre «Mis Pedidos».", "Selecciona un pedido para ver su detalle y estado."], 5),
        _accion("perfil", "Actualizar mi perfil", "/perfil", ["Abre «Mi Perfil» desde el menú.", "Edita los datos disponibles.", "Guarda los cambios."], 6),
    ],
    "RESTAURANTE": [
        _accion("restaurantes", "Administrar mi restaurante", "/restaurantes", ["Abre «Mis Restaurantes».", "Selecciona el restaurante que quieres gestionar.", "Usa sus opciones para revisar o editar sus datos." ]),
        _accion("platos", "Gestionar platos y disponibilidad", "/restaurantes", ["Abre «Mis Restaurantes» y selecciona un restaurante.", "Entra a «Platos».", "Crea o edita platos y ajusta su disponibilidad." ]),
        _accion("mesas", "Configurar áreas y distribución de mesas", "/restaurantes", ["Abre «Mis Restaurantes» y selecciona un restaurante.", "Entra a la gestión de áreas o distribución.", "Edita el área, coloca mesas y guarda la distribución." ]),
        _accion("reservas", "Gestionar reservas recibidas", "/restaurantes", ["Abre «Mis Restaurantes» y selecciona un restaurante.", "Entra a «Reservas».", "Revisa cada solicitud y actualiza su estado según corresponda." ]),
        _accion("pedidos", "Gestionar pedidos y comandas", "/restaurantes", ["Abre «Mis Restaurantes» y selecciona un restaurante.", "Entra a «Pedidos» o «Comanda».", "Abre un pedido y actualiza su estado durante la preparación." ]),
        _accion("ingredientes", "Consultar el catálogo de ingredientes", "/ingredientes", ["Abre «Catálogo Ingredientes».", "Busca el ingrediente que necesitas y consulta sus datos." ]),
        _accion("perfil", "Actualizar mi perfil", "/perfil", ["Abre «Mi Perfil» desde el menú.", "Edita los datos disponibles y guarda los cambios." ], 6),
    ],
    "ADMINISTRADOR": [
        _accion("usuarios", "Administrar usuarios", "/admin/usuarios", ["Abre «Usuarios» en Administración.", "Busca o selecciona un usuario.", "Usa las acciones disponibles para gestionar su cuenta." ]),
        _accion("restaurantes", "Gestionar restaurantes", "/restaurantes", ["Abre «Restaurantes».", "Selecciona un restaurante o crea uno nuevo.", "Edita los datos o entra a sus opciones de gestión." ]),
        _accion("categorias", "Administrar categorías", "/admin/categorias", ["Abre «Categorías».", "Crea, edita o administra las categorías disponibles." ]),
        _accion("catalogo", "Gestionar ingredientes y proveedores", "/ingredientes", ["Abre «Ingredientes» o «Proveedores & Precios».", "Selecciona el catálogo que quieres administrar.", "Busca y utiliza las opciones disponibles para mantener sus datos." ]),
        _accion("bitacora", "Consultar la bitácora del sistema", "/admin/bitacora", ["Abre «Bitácora» en Administración.", "Usa filtros para localizar los eventos que necesitas revisar." ]),
        _accion("planificaciones", "Consultar planificación y recomendaciones", "/inicio", ["Abre «Panel Cliente» o «Planificaciones».", "Selecciona la planificación que quieres consultar." ]),
        _accion("perfil", "Actualizar mi perfil", "/perfil", ["Abre «Mi Perfil» desde el menú.", "Edita los datos disponibles y guarda los cambios." ], 6),
    ],
    "ADMINISTRADOR_TIENDA": [
        _accion("proveedores", "Gestionar tiendas y proveedores", "/proveedores", ["Abre «Mis Tiendas & Precios».", "Selecciona una tienda o proveedor.", "Usa las opciones disponibles para gestionar sus datos." ]),
        _accion("ingredientes", "Consultar el catálogo de ingredientes", "/ingredientes", ["Abre «Catálogo Ingredientes».", "Busca el ingrediente que quieres revisar." ]),
        _accion("perfil", "Actualizar mi perfil", "/perfil", ["Abre «Mi Perfil» desde el menú.", "Edita los datos disponibles y guarda los cambios." ]),
    ],
}


class AgenteGuiaService:
    @staticmethod
    def responder(solicitud: MensajeGuia, rol: str) -> RespuestaGuia:
        rol_normalizado = (rol or "").strip().upper()
        acciones = ACCIONES_POR_ROL.get(rol_normalizado, [])

        if solicitud.accion_id:
            seleccionada = next((a for a in acciones if a["id"] == solicitud.accion_id), None)
            if seleccionada:
                pasos = "\n".join(f"{i}. {paso}" for i, paso in enumerate(seleccionada["pasos"], 1))
                respuesta = f"Para {seleccionada['nombre'].lower()}:\n{pasos}"
                if solicitud.plataforma == "mobile" and seleccionada["seccion_movil"] is None:
                    respuesta += f"\n\nEsta función no tiene una pantalla móvil disponible actualmente; puedes gestionarla desde la web en «{seleccionada['ruta']}»."
                return RespuestaGuia(
                    respuesta=respuesta,
                    destino=seleccionada["ruta"],
                    seccion_movil=seleccionada["seccion_movil"],
                )

        contexto = {
            "rol": rol_normalizado,
            "acciones": [{"id": a["id"], "nombre": a["nombre"], "ruta": a["ruta"], "pasos": a["pasos"]} for a in acciones],
            "pagina_actual": solicitud.pagina_actual or "",
            "plataforma": solicitud.plataforma or "web",
            "historial": solicitud.historial[-10:],
        }
        respuesta = obtener_proveedor_ia().responder_guia_plataforma(solicitud.mensaje, contexto)
        return RespuestaGuia(respuesta=respuesta, acciones=acciones)
