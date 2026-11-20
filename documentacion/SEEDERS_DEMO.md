# Paquetes de datos demostrativos

Los paquetes usan datos demostrativos claramente marcados, no asignan
teléfonos/correos falsos a negocios y no usan IDs fijos. El seeder separado de
cuentas solo crea `restaurante2@menuopt.com` o `cliente2@menuopt.com` si faltan;
conserva sin cambios las cuentas existentes.

## Orden de ejecución

Ejecutar cada comando primero sin `--apply`: el resumen es una vista previa y
los cambios se revierten. Revisada la salida, repetir con `--apply`. En Render
se requiere además `--allow-production`.

```sh
python -m app.database.seed_demo_cuentas_faltantes
python -m app.database.seed_demo_cuentas_faltantes --apply --allow-production

python -m app.database.seed_datos_base_demo
python -m app.database.seed_datos_base_demo --apply --allow-production

python -m app.database.seed_restaurantes_menu_demo
python -m app.database.seed_restaurantes_menu_demo --apply --allow-production

python -m app.database.seed_recetas_demo
python -m app.database.seed_recetas_demo --apply --allow-production

python -m app.database.seed_planificaciones_demo
python -m app.database.seed_planificaciones_demo --apply --allow-production

python -m app.database.seed_experiencia_cliente_demo
python -m app.database.seed_experiencia_cliente_demo --apply --allow-production
```

Los módulos se ejecutan en transacciones y son aditivos/idempotentes: una
segunda ejecución no duplica registros ni elimina cambios de usuarios. El
seeder de clientes usa `cliente1@menuopt.com` y `cliente2@menuopt.com`; el de
restaurantes usa `restaurante@menuopt.com`, `restaurante2@menuopt.com` y
`tienda@menuopt.com`. Si falta una cuenta o un catálogo requerido, el seeder de
datos se detiene sin crear cuentas ni usar IDs de respaldo.

En Render, `MENUOPT_SEED_DEMO_MODE` permite ejecutar por etapas:
`preview_accounts` muestra las cuentas que faltan y `apply_accounts` solo crea
las faltantes; `preview_restaurants` y
`apply_restaurants` manejan el paquete de restaurantes; `preview_other` y
`apply_other` manejan recetas, planes y experiencia en ese orden. Dejar la
variable en `off` al terminar cada carga.

## Contenido previsto

- **Base:** 15 tiendas demostrativas en tres ciudades; 81 ingredientes y el
  mismo catálogo en cada tienda, con precios estables y distintos para comparar
  costos de compra.
- **Restaurantes:** 12 establecimientos ficticios, 75 platos de cartas acordes
  con parrillas, pollerías, hamburgueserías y cocina boliviana; ingredientes
  por plato; categorías, una preferencia vegetariana, áreas y mesas variadas.
- **Recetas:** 49 recetas bolivianas e internacionales con instrucciones,
  porciones, dificultad, duración e ingredientes enlazados al catálogo.
- **Planes:** seis planes de cliente, tres por cuenta, con zonas, presupuestos,
  tamaños de grupo y dos preferencias vegetarianas.
- **Experiencia:** cinco reservas por cliente (10 en total), con fechas pasadas
  y futuras, estados variados, invitados sin datos de contacto y pedidos en
  distintos estados asociados a platos del restaurante.

Los nombres `DEMO |` indican registros ficticios. Las zonas son referencias
urbanas aproximadas; no representan ubicaciones comerciales reales. El seeder
de experiencias deja reservas libres de conflictos: cada reserva demostrativa
usa un restaurante distinto y una mesa con capacidad adecuada.

## Imágenes

La biblioteca de recetas ya dispone de `imagen_url`. El modelo/API de platos
todavía no ofrece un campo de imagen, por lo que este paquete no asigna fotos a
los platos del menú. Para mostrar imágenes de platos en la web y móvil primero
hay que añadir ese campo al modelo, migración, API y pantallas, y luego alojar
imágenes demostrativas con permiso de uso.

No ejecutar `seed_bloque2.py` para esta carga: ese conjunto crea cuentas de
usuario adicionales y está protegido para desarrollo/pruebas. Tampoco ejecutar
`crear_admin.py` en producción para cargar estos datos, porque restablece las
cuentas base.
