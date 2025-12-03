# Tests

Resumen
- `test/` contiene pruebas unitarias y de integración para routers y funciones centrales.

Cómo ejecutar
```powershell
pytest -q
```

Archivos importantes
- `test/test_main.py` - Verifica arranque básico de la app.
- `test/test_book_router.py` - Pruebas para endpoints de libros.
- `test/test_loan_router.py` - Pruebas para endpoints de préstamos.

Notas
- Ejecuta las pruebas en un entorno con las dependencias del `requirements.txt`.
