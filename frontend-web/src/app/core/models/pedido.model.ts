// CASO DE USO: CU23, CU24 - Modelos de Pedido

export type EstadoPedido = 'PENDIENTE' | 'ACEPTADO' | 'EN_PREPARACION' | 'LISTO' | 'ENTREGADO' | 'CANCELADO';

export interface DetallePedidoItemCrear {
  id_plato: number;
  cantidad: number;
}

export interface PedidoCrear {
  id_restaurante: number;
  detalles: DetallePedidoItemCrear[];
  id_reserva?: number | null;
  observaciones?: string | null;
}

export interface DetallePedidoRespuesta {
  id_detalle_pedido: number;
  id_plato: number;
  nombre_plato: string;
  cantidad: number;
  precio_unitario: number | string;
  subtotal: number | string;
}

export interface PedidoRespuesta {
  id_pedido: number;
  id_restaurante: number;
  nombre_restaurante: string;
  id_usuario: number;
  nombre_cliente?: string | null;
  correo_cliente?: string | null;
  telefono_cliente?: string | null;
  id_reserva?: number | null;
  estado: EstadoPedido;
  total: number | string;
  observaciones?: string | null;
  fecha_pedido: string;
  detalles: DetallePedidoRespuesta[];
}

export interface PedidoResumen {
  id_pedido: number;
  id_restaurante: number;
  nombre_restaurante: string;
  id_usuario: number;
  nombre_cliente?: string | null;
  id_reserva?: number | null;
  estado: EstadoPedido;
  total: number | string;
  fecha_pedido: string;
  cantidad_items: number;
}

export interface PedidoEstadoActualizar {
  estado: EstadoPedido;
}

export interface CartItem {
  id_plato: number;
  nombre: string;
  precio: number;
  cantidad: number;
  subtotal: number;
}
