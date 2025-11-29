"""
Paquete principal de la aplicación Library API.
"""

from . import api
from . import domain
from . import services
from . import utils

__version__ = "1.0.0"

__all__ = [
    'api',
    'domain',
    'services',
    'utils',
    '__version__'
]