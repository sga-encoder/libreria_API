# Carpeta `data`

Resumen
- `data/` contiene archivos persistidos en formatos JSON y CSV usados por el proyecto.

Contenido principal
- `data/json/` - Archivos JSON: `books.json`, `users.json`, `inventary.json`, `loans_records.json`, `admin.json`.
- `data/csv/` - Historial en `history.csv`.

Uso
- Los repositorios de `domain/repositories` y `app/services` leen/escriben estos ficheros.
- Si migras a una base de datos, estos ficheros pueden usarse como fuente de datos inicial.

Formato
- JSONs: arrays de objetos con las propiedades de los modelos (ver `domain/models`).
