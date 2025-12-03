"""
Paquete principal de la aplicación Library API.
"""

from . import api
from . import domain
from . import services
from . import utils
from .dependencies import get_current_user


__version__ = "1.0.0"

__all__ = [
    'api',
    'domain',
    'services',
    'utils',
    'get_current_user',
    '__version__'
]