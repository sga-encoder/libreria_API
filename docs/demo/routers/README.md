# Demo de peticiones HTTP (routers)

Este README sirve como guía rápida para usar `docs/demo/routers/demo_requests.http`.

Pasos rápidos
1. Inicia la aplicación:
```powershell
python -m uvicorn main:app --reload
```
2. Abre `docs/demo/routers/demo_requests.http` en VSCode.
3. Usa la extensión REST Client para enviar peticiones.

Variables útiles dentro del archivo de peticiones
- `@host = http://localhost:8000`
- `@token` - Se rellena tras hacer login y obtener el token.

Endpoints de ejemplo incluidos
- Crear usuario, login, crear libro, crear préstamo, listar préstamos.

Si alguna petición falla, comprueba que las rutas/params coincidan con `app/api/v1`.
Demo: Peticiones para los routers usando REST Client (VS Code)

Cómo usar

1. Instala la extensión REST Client en VS Code (`humao.rest-client`).
2. Inicia la aplicación localmente:

```powershell
; uvicorn main:app --reload
```

3. Abre `docs/demo/routers/demo_requests.http` en VS Code.
4. Haz clic en `Send Request` sobre la petición que quieras ejecutar.

Notas

- El archivo define `@host = http://localhost:8000`. Cámbialo si tu servidor
  corre en otro puerto o host.
- Estas peticiones son ejemplos y pueden necesitar IDs reales dependiendo de
  los datos que tengas en memoria (por ejemplo, usuarios o libros creados).
