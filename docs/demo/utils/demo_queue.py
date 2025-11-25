# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/utils/demo_queue.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
	_root = _root.parent
if (_root / "app").exists():
	sys.path.insert(0, str(_root))

"""Demostración del comportamiento de `Queue`.

Este módulo muestra operaciones comunes sobre la clase `Queue`:
- `demo_basic()`: empujar, consultar frente, sacar y comprobar longitud/estado.
- `demo_iteration()`: iterar sobre la cola y vaciarla por completo.

Se recomienda ejecutar desde la raíz del proyecto con:
	python -m docs.demo.utils.demo_queue

Los prints muestran el estado relevante tras cada operación.
"""


from app.utils import Queue


def demo_basic():
	"""Operaciones básicas: push, peek, pop, len, is_empty, to_list."""
	q = Queue()

	print("Estado inicial:", q.to_list(), "is_empty:", q.is_empty())

	# Encolar varios elementos
	q.push("alice")
	q.push("bob")
	q.push("carol")
	print("Tras push: ", q.to_list())

	# Consultar el frente sin extraer
	print("peek() ->", q.peek())

	# Extraer un elemento
	print("pop() ->", q.pop())
	print("Tras pop:", q.to_list())

	# Comprobar longitud y estado
	print("len ->", len(q))
	print("is_empty ->", q.is_empty())


def demo_iteration():
	"""Demuestra iteración FIFO y vaciado con pop."""
	q = Queue()
	for name in ("dave", "eve", "frank"):
		q.push(name)

	print("Cola inicial:", q)

	# Iteración (no consume la cola)
	print("Iterando:")
	for item in q:
		print(" -", item)

	# Vaciar la cola con pop hasta que esté vacía
	print("Vaciando con pop():")
	while not q.is_empty():
		print("pop ->", q.pop())

	print("Estado final:", q.to_list(), "is_empty:", q.is_empty())


if __name__ == "__main__":
	demo_basic()
	print()
	demo_iteration()

