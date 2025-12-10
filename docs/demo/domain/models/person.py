# Esto solo es necesario para poder ejecutar el script directamente
# desde el árbol del proyecto (por ejemplo: `python docs/demo/models/demo_models.py`).
from pathlib import Path
import sys

_here = Path(__file__).resolve()
_root = _here
while not (_root / "app").exists() and _root.parent != _root:
    _root = _root.parent
if (_root / "app").exists():
    sys.path.insert(0, str(_root))

"""Demo de modelos: instancia `Person` y muestra ejemplos de uso.

Este script se usa solo como demo para desarrolladores: crea instancias,
convierte a diccionario con `to_dict()`, compara por `id`, y prueba
la verificación y cambio de contraseña.

Ejecución (desde la raíz del proyecto) en PowerShell:
; python -m docs.demo.domain.models.person

Nota: el archivo se mantiene en español en los mensajes para facilitar
la comprensión del demo por parte del autor original.
"""

from app.domain.models import Person
from app.domain.models.enums import PersonRole
from json import dumps


def _print_header(title: str):
    """Imprime un encabezado visible para separar secciones del demo."""
    print('\n' + '=' * 40)
    print(f'{title}')
    print('=' * 40)


def run_demo():
    """Ejecuta el demo mostrando varias operaciones del modelo `Person`."""
    person_default = Person.default()

    _print_header('person_default')
    print(person_default)

    ice_king = Person(
        fullName='Ice King',
        email='iceKing.aventure@time.cartoon',
        password='adventuretime',
        role=PersonRole.USER,
    )

    _print_header('ice_king Instance')
    print(ice_king)

    ice_king_dict = ice_king.to_dict()
    _print_header('ice_king Method to_dict')
    print(dumps(ice_king_dict, indent=2, ensure_ascii=False))

    ice_king_from_dict = Person.from_dict(ice_king_dict, password_is_hashed=True)
    ice_king_from_dict.set_fullName('Ice King from dict modified')

    _print_header('ice_king_from_dict Instance')
    print(ice_king_from_dict)

    _print_header('Comparaciones (solo se compara el id)')
    print(f'ice_king == ice_king_from_dict ? {ice_king == ice_king_from_dict}')

    user_to_search = Person.from_search_api(ice_king.get_id())
    _print_header('user_to_search Instance from search_api')
    print(dumps(user_to_search.to_dict(), indent=2, ensure_ascii=False))
    print(f'ice_king == user_to_search ? {ice_king == user_to_search}')

    _print_header('Actualizar ice_king desde dict (update_from_dict)')
    ice_king.update_from_dict({
        "fullName": "Ice King Updated",
        "new_password": "contraseña_correcta",
        "password": "adventuretime",
    })
    print(dumps(ice_king.to_dict(), indent=2, ensure_ascii=False))

    _print_header('Verificación de contraseñas')
    print('contraseña incorrecta:', ice_king.verify_password('contraseña_incorrecta'))
    print('contraseña correcta:', ice_king.verify_password('contraseña_correcta'))

    _print_header('Intento de cambio de contraseña (válido)')
    result = ice_king.change_password('contraseña_correcta', 'adventuretime')
    print('cambio realizado:', result)
    print('verificación nueva contraseña:', ice_king.verify_password('adventuretime'))

    _print_header('Intento de cambio de contraseña (inválido)')
    result2 = ice_king.change_password('contraseña_correcta', 'new_password')
    print('cambio realizado:', result2)
    print('verificación contraseña new_password:', ice_king.verify_password('new_password'))


if __name__ == '__main__':
    run_demo()
