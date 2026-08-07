import subprocess
import os
import re
from typing import Tuple
import sys

def detect_java() -> tuple[bool, str]:
    """Detecta si Java está instalado y devuelve (ok, mensaje)."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True, text=True, timeout=5
        )
        output = result.stderr or result.stdout
        version_match = re.search(r'version "([^"]+)"', output)
        version = version_match.group(1) if version_match else "desconocida"
        return True, f"Java {version}"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "Java no encontrado"
    except Exception as e:
        return False, f"Error: {e}"