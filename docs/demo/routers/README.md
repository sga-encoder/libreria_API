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
