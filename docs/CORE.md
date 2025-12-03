# Módulo `core`

Resumen
- `core/` recoge la configuración central y utilidades de seguridad.

Estructura relevante
- `core/config.py` - Configuración de la aplicación (variables, rutas, constantes).
- `core/security.py` - Funciones de cifrado, creación/verificación de tokens.

Qué revisar
- Revisa las variables en `core/config.py` si despliegas en otro entorno.
- Los mecanismos de autenticación usados por `app/api/v1/auth` están definidos en `core/security.py`.
