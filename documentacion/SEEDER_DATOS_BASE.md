# Seeder de datos base demostrativos

El módulo `backend.app.database.seed_datos_base_demo` prepara 15 establecimientos
de compra ficticios en zonas de Santa Cruz de la Sierra, La Paz y Cochabamba,
81 ingredientes y sus precios de referencia en bolivianos. Cada tienda ofrece
el mismo catálogo y compara precios, con diferencias estables por ciudad y tipo
de tienda. Los nombres de los
locales llevan `DEMO`, y no se inventan teléfonos ni direcciones comerciales.

El seeder no crea usuarios. Requiere que exista `tienda@menuopt.com`; aborta si
no lo encuentra y no usa IDs de respaldo. Las filas nuevas se reconocen por
nombre y las relaciones existentes no se sobrescriben. Se puede volver a
ejecutar sin duplicar el conjunto.

## Vista previa y aplicación

La imagen del backend admite el modo temporal `MENUOPT_SEED_BASE_MODE`. En
Render, definirlo como `preview` ejecuta el seeder en una transacción que se
revierte y deja el resumen en los logs. Cambiarlo a `apply` confirma las
inserciones en la base del servicio. Al terminar, volver a `off` para que una
reinicialización futura no vuelva a ejecutar el seeder.

El modo `apply` solo se debe usar cuando la vista previa confirme las
cantidades esperadas y que el backend está conectado a la base correcta.

En un entorno local configurado contra una base de desarrollo:

```sh
python -m app.database.seed_datos_base_demo
python -m app.database.seed_datos_base_demo --apply
```

La opción `--allow-production` es obligatoria para aplicar a una base remota o
un entorno marcado `production`/`prod`; el modo Render `apply` la proporciona
explícitamente.
