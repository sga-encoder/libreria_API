# Estadísticas de Contribuidores

Este proyecto incluye una utilidad para ver las estadísticas de contribuciones de cada desarrollador al repositorio.

## Uso

### Opción 1: Script Standalone

Ejecuta el script `contributor_stats.py` desde la raíz del proyecto:

```bash
python contributor_stats.py
```

### Opción 2: Módulo de Python

También puedes usar la clase `GitStats` desde el módulo `app.utils`:

```python
from app.utils import GitStats

# Obtener estadísticas de todos los contribuidores
stats = GitStats.get_all_contributor_stats()
print(stats)

# Imprimir estadísticas formateadas
GitStats.print_stats()

# Obtener estadísticas de un contribuidor específico
contributor_stats = GitStats.get_contributor_stats('nombre-del-contribuidor')
print(contributor_stats)
```

## Salida

El script muestra una tabla con las siguientes columnas:

- **Contribuidor**: Nombre del desarrollador
- **Commits**: Número de commits realizados
- **Líneas +**: Líneas de código agregadas
- **Líneas -**: Líneas de código eliminadas
- **Total**: Total de cambios (líneas agregadas + eliminadas)

### Ejemplo de salida:

```
================================================================================
ESTADÍSTICAS DE CONTRIBUCIONES AL REPOSITORIO
================================================================================
Contribuidor                      Commits     Líneas +     Líneas -        Total
--------------------------------------------------------------------------------
sga-encoder                             1         5507            0         5507
copilot-swe-agent[bot]                  2          150           25          175
--------------------------------------------------------------------------------
TOTAL                                   3         5657           25         5682
================================================================================
```

## Notas

- Las estadísticas se calculan usando el historial de Git del repositorio
- Los archivos binarios no se cuentan en las líneas agregadas/eliminadas
- El script requiere que Git esté instalado y disponible en el PATH
