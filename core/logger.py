# ==============================================================================
# core/logger.py - Sistema de logging centralizado
# ==============================================================================

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.config import LOGS_DIR

# ==============================================================================
# Configuración del logging
# ==============================================================================
class ColoredFormatter(logging.Formatter):
    """Formateador con colores para la consola."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging(level: int = logging.DEBUG) -> logging.Logger:
    """
    Configura el sistema de logging con archivo y consola.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Crear nombre del archivo de log
    log_filename = os.path.join(
        LOGS_DIR,
        f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    # Logger raíz
    logger = logging.getLogger("aureo")
    logger.setLevel(level)
    
    # Evitar duplicados si ya hay handlers
    if logger.handlers:
        return logger
    
    # Formato para archivo
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Formato para consola
    console_formatter = ColoredFormatter(
        "[%(levelname)s] %(message)s"
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado."""
    return logging.getLogger(f"aureo.{name}")
