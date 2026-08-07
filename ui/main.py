# ==============================================================================
# AUREO LAUNCHER - Versión 3.0 (Refactorizada con arquitectura modular)
# ==============================================================================
# Dependencias: pip install -r requirements.txt
# Uso: python main.py
# ==============================================================================

import sys
from pathlib import Path

# Agregar la raíz del proyecto al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import setup_logging
from ui.main_window import AureoLauncher
from core.config import load_config

def main():
    """Punto de entrada principal de la aplicación."""
    # Configurar logging
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("Iniciando Aureo Launcher v3.0")
    logger.info("=" * 80)
    
    try:
        # Cargar configuración
        config = load_config()
        logger.info(f"Configuración cargada: {config}")
        
        # Crear y ejecutar la aplicación
        app = AureoLauncher()
        app.mainloop()
        
    except Exception as e:
        logger.critical(f"Error fatal: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
