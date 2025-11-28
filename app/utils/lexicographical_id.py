"""Generador sencillo de IDs ordenables por tiempo.

Qué significa "lexicográfico" (explicación corta):
- "Lexicográfico" es el orden que usan los diccionarios: se comparan las cadenas carácter por carácter
  desde la izquierda. Por ejemplo "001" > "010" > "100".

Qué hace este módulo (resumen fácil):
- Crea IDs con formato "{timestamp_ms:13d}{sufijo:04d}".
- El prefijo de timestamp fijo (13 dígitos) hace que IDs generados en tiempos distintos
  queden en el mismo orden si los comparas como cadenas (orden lexicográfico).
- Esto facilita usar algoritmos como insertion sort y luego búsqueda binaria sobre la lista
  de IDs, porque comparar cadenas dará el mismo orden que comparar tiempos.

Por qué usamos un lock (explicación corta):
- El sufijo se incrementa protegido por un threading.Lock.
- El lock asegura que solo un hilo a la vez actualice el contador del sufijo,
  evitando generar sufijos iguales desde varios hilos al mismo tiempo.
- En otras palabras: el lock serializa esa pequeña parte para evitar IDs duplicados
  dentro del mismo proceso cuando hay concurrencia de hilos.

Nota práctica:
- Este método asegura orden y evita colisiones dentro de un mismo proceso multihilo.
- Si tiene varios procesos o servidores, use ULID/KSUID o un mecanismo central para garantizar unicidad global.
"""
import time
import threading

# para generar IDs únicos de forma segura en entornos multihilo
# el lock hace que sólo un hilo a la vez pueda modificar el contador del sufijo
_id_counter_lock = threading.Lock()
_id_counter = 0

def __next_id_suffix() -> int:
    """Devuelve un sufijo numérico de 4 dígitos; protegido por lock para evitar duplicados."""
    global _id_counter
    with _id_counter_lock:
        _id_counter += 1
        return _id_counter % 10000  # 4 dígitos, rueda cada 10000
    
def generate_id():
    """Genera un ID ordenable por tiempo: '{epoch_ms:013d}{suffix:04d}'."""
    ts_ms = int(time.time() * 1000)  # timestamp en milisegundos
    suffix = __next_id_suffix()
    return f"{ts_ms:013d}{suffix:04d}"  # 13 dígitos para timestamp + 4 dígitos para el sufijo