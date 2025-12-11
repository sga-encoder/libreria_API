# GUÍA DE EJECUCIÓN Y TESTING

## Requisitos Previos

```bash
# Instalar dependencias (si no lo has hecho)
pip install -r requirements.txt
pip install python-jose passlib
```

## Ejecutar Tests

### Opción 1: Tests Simples (Recomendado)
```bash
# Cambiar al directorio del proyecto
cd "c:\Tecnias de Prog Juan\Biblioteca\libreria_API"

# Ejecutar tests
python -m pytest test/test_loan_service_simple.py -v

# Versión concisa
python -m pytest test/test_loan_service_simple.py -q
```

**Resultado esperado:**
```
10 passed in 0.05s ✅
```

### Opción 2: Tests con Salida Detallada
```bash
python -m pytest test/test_loan_service_simple.py -v -s
```

### Opción 3: Un Test Específico
```bash
# Solo test de BookCase
python -m pytest test/test_loan_service_simple.py::test_bookcase_creation -v

# Solo test de DeficientOrganizer
python -m pytest test/test_loan_service_simple.py::test_deficient_organizer -v
```

## Verificar Compilación

```bash
# Compilar a bytecode (sin ejecutar)
python -m py_compile app/domain/services/loan_service.py

# Si no hay error: ✅ Compilación exitosa
```

## Importar en tu Código

```python
from app.domain.services.loan_service import LoanService
from app.domain.models import BookCase, BookShelf
from app.domain.models.enums import TypeOrdering

# Sin bookcase (compatible)
loan_service = LoanService(url, queue, users, inventory)

# Con bookcase
bookcase = BookCase(
    stands=BookShelf(books=[]),
    TypeOrdering=TypeOrdering.DEFICIENT,
    weighCapacity=10.0,
    capacityStands=5,
    store=[]
)
loan_service = LoanService(url, queue, users, inventory, bookcase=bookcase)

# Cambiar bookcase después
loan_service.set_bookcase(new_bookcase)
```

## Documentación Generada

1. **RESUMEN_FINAL.md** - Resumen completo de implementación
2. **CAMBIOS_LOAN_SERVICE.md** - Detalles de cambios realizados
3. **RESULTADOS_TESTS.md** - Resultados detallados de tests
4. **GUIA_EJECUCION.md** - Este archivo

## Estructura de Archivos

```
libreria_API/
├── app/
│   └── domain/
│       └── services/
│           └── loan_service.py (✅ MODIFICADO)
├── test/
│   ├── test_loan_service_simple.py (✅ CREADO)
│   ├── test_loan_service_bookshelf.py (Creado)
│   ├── test_loan_service_unit.py (Creado)
│   └── ...
├── CAMBIOS_LOAN_SERVICE.md (✅ CREADO)
├── RESULTADOS_TESTS.md (✅ CREADO)
├── RESUMEN_FINAL.md (✅ CREADO)
└── GUIA_EJECUCION.md (Este archivo)
```

## Flujo de Uso Típico

### 1. Inicialización
```python
from app.domain.services.loan_service import LoanService
from app.domain.models import BookCase, BookShelf
from app.domain.models.enums import TypeOrdering

# Crear BookCase con algoritmo DEFICIENT
bookcase = BookCase(
    stands=BookShelf(books=[]),
    TypeOrdering=TypeOrdering.DEFICIENT,
    weighCapacity=10.0,  # 10 kg máximo
    capacityStands=3,
    store=[]
)

# Inicializar servicio
loan_service = LoanService(
    url="loans.json",
    reservations_queue=queue,
    users=users_list,
    inventory_service=inventory_service,
    bookcase=bookcase  # ← Con BookCase
)
```

### 2. Crear Préstamo
```python
# Automáticamente:
# 1. Marca libro como prestado
# 2. Remueve de inventario
# 3. Agrega a usuario
# 4. Aplica algoritmo DEFICIENT (organiza libros disponibles)
loan = loan_service.create_loan(usuario, libro)
```

### 3. Actualizar Préstamo
```python
# Automáticamente:
# 1. Libera libro antiguo + aplica algoritmo
# 2. Valida nuevo libro
# 3. Marca como prestado + aplica algoritmo
# 4. Crea nuevo préstamo
loan = loan_service.update_loan(prestamo_id, nuevo_libro)
```

### 4. Eliminar Préstamo
```python
# Automáticamente:
# 1. Reintegra libro + aplica algoritmo
# 2. Procesa cola de reservas
# 3. Elimina del sistema
resultado = loan_service.delete_loan(prestamo_id)
```

## Troubleshooting

### Error: "No module named 'app'"
**Solución**: Ejecutar desde el directorio raíz del proyecto con `python -m pytest`

### Error: "ModuleNotFoundError: No module named 'jose'"
**Solución**: `pip install python-jose`

### Error: "UnicodeEncodeError"
**Solución**: Es un warning, no afecta los tests

## Salida Esperada

```bash
C:\...\libreria_API> python -m pytest test/test_loan_service_simple.py -q

..........                                                            [100%]
10 passed in 0.05s
```

## Próximos Pasos

1. ✅ Implementación completada
2. ✅ Tests ejecutados exitosamente  
3. 🔄 Integrar en API endpoints (opcional)
4. 🔄 Testing con datos reales (opcional)
5. 🔄 Documentación en Swagger (opcional)

---

**¿Necesitas ayuda adicional?**
- Revisa RESUMEN_FINAL.md para detalles completos
- Revisa CAMBIOS_LOAN_SERVICE.md para cambios específicos
- Ejecuta los tests para verificar funcionamiento
