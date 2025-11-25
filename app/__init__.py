"""
Paquete principal de la aplicación Library API.
"""

from . import crud
from . import models
from . import schemas
from . import routers
from . import services
from . import utils

__version__ = "1.0.0"

__all__ = [
    'crud',
    'models',
    'schemas',
    'routers',
    'services',
    'utils',
    '__version__'
]