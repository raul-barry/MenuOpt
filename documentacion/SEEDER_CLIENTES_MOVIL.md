# Datos demo para probar MenuOpt móvil

El seeder `backend/app/database/seed_clientes_demo.py` prepara catálogos y datos
para el flujo del cliente: planificación, recomendaciones de restaurante y
preparación propia, ingredientes, comparación, lugares de compra, biblioteca de
recetas y contexto para el asistente de IA.

## Ejecutar o volver a ejecutar

Con Docker Compose activo:

```powershell
docker compose exec backend python -m app.database.seed_clientes_demo
```

Es aditivo e idempotente. Conserva registros existentes, reconoce por nombre
los ingredientes y platos, y crea planes demo solo si aún no están. Las
recomendaciones las calcula el motor real de MenuOpt; si un plan demo ya tiene
recomendaciones, no las reemplaza.

## Acceso de prueba

- Correo: `cliente1@menuopt.com`
- Contraseña local de demo: `Cliente1234*`

El seeder agrega tres planes etiquetados `DEMO APK`: almuerzo en Equipetrol,
cena en Centro y almuerzo vegetariano en Centro. Desde la app se puede abrir
cualquiera y consultar sus recomendaciones y detalles de preparación.

## Datos incluidos

- Catálogo de restaurantes, categorías y platos mediante el seeder existente.
- Ocho tiendas/mercados, ingredientes con precios y relaciones de disponibilidad.
- Recetas de preparación propia vinculadas a productos y precios de tiendas.
- Ingredientes de la biblioteca de recetas enlazados al catálogo cuando hay una
  correspondencia conocida.
- Recomendaciones de restaurante y preparación propia calculadas por el servicio
  normal de recomendaciones.

La consulta con IA usa la configuración ya instalada en `backend/.env`; este
seeder no imprime ni modifica credenciales del proveedor.
