# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/utils/demo_filemanager.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))

"""Demostración del comportamiento de `FileManager`.

Este módulo contiene dos demos pequeñas:
- `demo_json()`: muestra cómo `FileManager` normaliza y persiste datos JSON.
- `demo_csv()`: muestra escritura de cabeceras CSV y append de filas.

Se recomienda ejecutar desde la raíz del proyecto con:
    python -m docs.demo.utils.demo_filemanager

Los prints en las funciones muestran el contenido resultado de operaciones
relevantes (por ejemplo, llamadas a `read()` o datos añadidos). Los mensajes
meramente informativos fueron eliminados para simplificar la salida.
"""


from app.utils import FileManager, FileType


def demo_json():
    """Demuestra operaciones JSON con `FileManager`.

    Pasos:
    1. Escribe un dict (se normaliza internamente a lista de dicts).
    2. Lee y muestra el contenido.
    3. Añade otro dict con `append()` y vuelve a mostrar el contenido.
    """
    fm = FileManager("docs/demo/result_demos/demo.json", FileType.JSON)

    # write: normaliza dict -> [dict]
    fm.write({"sample": "value"})
    print("read() ->", fm.read())

    # append: añade otra entrada (se normaliza todo a lista)
    fm.append({"another": "entry"})
    print("read() ->", fm.read())

def demo_csv():
    """Demuestra operaciones CSV con `FileManager`.

    Pasos:
    1. Escribe cabeceras CSV (lista de strings).
    2. Lee y muestra el contenido tras la escritura.
    3. Añade una fila como dict y muestra el contenido.
    4. Añade varias filas a la vez y muestra el contenido final.
    """
    fm = FileManager("docs/demo/result_demos/demo.csv", FileType.CSV, ["id", "user", "action", "timestamp"])


    # append: añadir fila como dict
    row = {"id": "1", "user": "alice", "action": "borrow", "timestamp": "2025-11-24T12:00:00"}
    fm.write([row])
    print("Contenido tras append(row):", fm.read())

    # append varias filas
    more = [
        {"id": "2", "user": "bob", "action": "return", "timestamp": "2025-11-24T13:00:00"},
        {"id": "3", "user": "carol", "action": "borrow", "timestamp": "2025-11-24T14:00:00"},
    ]
    print("Append lista de filas ->", more)
    fm.append(more)
    print("Contenido tras append(more):", fm.read())

if __name__ == "__main__":
    demo_json()
    demo_csv()
