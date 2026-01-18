"""Configuración del sistema de logging para la aplicación.

Este módulo configura el sistema de logging con salida a consola y archivo,
permitiendo diferentes niveles de detalle según el entorno (desarrollo/producción).
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    """Configura el sistema de logging para toda la aplicación.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nombre del archivo de log (si es None, usa fecha actual)
        
    Returns:
        Logger raíz configurado
        
    Ejemplo:
        >>> logger = setup_logging(log_level="DEBUG")
        >>> logger.info("Aplicación iniciada")
    """
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    if log_file is None:
        # Usar fecha actual para el nombre del archivo
        timestamp = datetime.now().strftime("%Y-%m-%d")
        log_file = f"library_{timestamp}.log"
    
    log_path = log_dir / log_file
    
    # Formato detallado para archivo
    file_format = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Formato simple para consola
    console_format = logging.Formatter(
        fmt="%(levelname)-8s | %(name)s | %(message)s"
    )
    
     
    # Handler para archivo (guarda TODO)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Siempre guarda todo en archivo
    file_handler.setFormatter(file_format)
    
    # Handler para consola (muestra según log_level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(console_format)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Nivel base para capturar todo
    
    # Limpiar handlers anteriores (evita duplicados)
    root_logger.handlers.clear()
    
    # Agregar handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    app_logger = logging.getLogger("library_api")
    app_logger.info(f"Sistema de logging inicializado: nivel={log_level}, archivo={log_path}")
    
    return app_logger


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger (usar __name__ del módulo)
        
    Returns:
        Logger configurado
        
    Ejemplo:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Mensaje de depuración")
    """
    return logging.getLogger(f"library_api.{name}")