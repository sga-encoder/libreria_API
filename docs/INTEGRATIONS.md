# Integraciones

Resumen
- `integrations/` contiene adaptadores a servicios externos.

Ejemplo
- `app/integrations/google_book_api.py` - Integración con Google Books API para buscar metadatos de libros.

Notas
- Añade claves y configuración en `core/config.py` cuando sea necesario.
- Las integraciones deberían devolver datos normalizados para que los servicios del dominio los consuman.
