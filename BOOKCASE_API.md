## 📚 API de BookCase - Endpoints Disponibles

### Configurar BookCase
**POST** `/api/v1/loan/bookcase/configure`
```json
{
  "algorithm_type": "DEFICIENT",  // o "OPTIMOUM"
  "weight_capacity": 1.0,         // kg por estante
  "capacity_stands": 20           // número de estantes
}
```

### Ejecutar Organización (requiere admin)
**POST** `/api/v1/loan/bookcase/organize`
Headers: `Authorization: Bearer {admin_token}`

Respuesta incluye:
- Estantes creados con sus libros
- Combinaciones peligrosas detectadas
- Estadísticas de organización

### Ver Estado del BookCase
**GET** `/api/v1/loan/bookcase/status`

### Desactivar BookCase
**DELETE** `/api/v1/loan/bookcase/disable`

---

## 🧪 Scripts de Prueba Creados:

1. **test_deficient_algorithm.py** - Prueba básica con 2kg
2. **test_deficient_5kg.py** - Prueba con 5kg de capacidad
3. **test_deficient_1kg.py** - Prueba con 1kg mostrando combinaciones peligrosas

## ✅ Probado y Funcionando:
- ✅ Organización de 19 libros en 14 estantes
- ✅ Detección de 112 combinaciones peligrosas
- ✅ Estantes con múltiples libros
- ✅ Sin crashes ni timeouts
