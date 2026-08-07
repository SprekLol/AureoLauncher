# ==============================================================================
# utils/validation.py - Validaciones
# ==============================================================================

import os
from typing import Tuple

from core.logger import get_logger

logger = get_logger("utils.validation")

# ==============================================================================
# Validaciones de Minecraft
# ==============================================================================
def validate_minecraft_path(path: str) -> Tuple[bool, str]:
    """
    Valida una ruta de Minecraft.
    
    Args:
        path: Ruta a validar
    
    Returns:
        Tupla (válido, mensaje)
    """
    if not path:
        return False, "La ruta no puede estar vacía"
    
    if not os.path.isdir(path):
        return False, f"La ruta no existe: {path}"
    
    # Verificar si parece una carpeta de Minecraft válida
    has_versions = os.path.isdir(os.path.join(path, "versions"))
    has_profiles = os.path.isfile(os.path.join(path, "launcher_profiles.json"))
    
    if not (has_versions or has_profiles):
        return False, "Esta no parece ser una carpeta válida de Minecraft"
    
    logger.info(f"Ruta de Minecraft válida: {path}")
    return True, "Ruta válida"

def validate_version(mc_path: str, version: str) -> Tuple[bool, str]:
    """
    Valida si una versión está instalada.
    
    Args:
        mc_path: Ruta de Minecraft
        version: Versión a validar
    
    Returns:
        Tupla (válido, mensaje)
    """
    version_path = os.path.join(mc_path, "versions", version)
    json_file = os.path.join(version_path, f"{version}.json")
    
    if not os.path.isdir(version_path):
        return False, f"Versión no instalada: {version}"
    
    if not os.path.isfile(json_file):
        return False, f"Archivo de versión corrupto: {json_file}"
    
    return True, "Versión válida"

def validate_nick(nick: str) -> Tuple[bool, str]:
    """
    Valida un nick de Minecraft.
    
    Args:
        nick: Nick a validar
    
    Returns:
        Tupla (válido, mensaje)
    """
    if not nick:
        return False, "El nick no puede estar vacío"
    
    if len(nick) < 3:
        return False, "El nick debe tener al menos 3 caracteres"
    
    if len(nick) > 16:
        return False, "El nick no puede tener más de 16 caracteres"
    
    if not all(c.isalnum() or c == '_' for c in nick):
        return False, "El nick solo puede contener letras, números y guiones bajos"
    
    return True, "Nick válido"

def validate_ram(ram_gb: int) -> Tuple[bool, str]:
    """
    Valida la cantidad de RAM.
    
    Args:
        ram_gb: RAM en GB
    
    Returns:
        Tupla (válido, mensaje)
    """
    if ram_gb < 1:
        return False, "La RAM debe ser mínimo 1GB"
    
    if ram_gb > 128:
        return False, "La RAM no puede superar 128GB"
    
    return True, "RAM válida"

# ==============================================================================
# Validaciones de archivo
# ==============================================================================
def validate_file_exists(path: str) -> Tuple[bool, str]:
    """
    Valida que un archivo existe.
    
    Args:
        path: Ruta del archivo
    
    Returns:
        Tupla (existe, mensaje)
    """
    if os.path.isfile(path):
        return True, "Archivo existe"
    return False, f"Archivo no encontrado: {path}"

def validate_directory_exists(path: str) -> Tuple[bool, str]:
    """
    Valida que un directorio existe.
    
    Args:
        path: Ruta del directorio
    
    Returns:
        Tupla (existe, mensaje)
    """
    if os.path.isdir(path):
        return True, "Directorio existe"
    return False, f"Directorio no encontrado: {path}"

# ==============================================================================
# Validaciones de entrada
# ==============================================================================
def validate_string(value: str, min_length: int = 1, max_length: int = 255) -> Tuple[bool, str]:
    """
    Valida un string genérico.
    
    Args:
        value: String a validar
        min_length: Longitud mínima
        max_length: Longitud máxima
    
    Returns:
        Tupla (válido, mensaje)
    """
    if not isinstance(value, str):
        return False, "Debe ser un texto"
    
    if len(value) < min_length:
        return False, f"Mínimo {min_length} caracteres"
    
    if len(value) > max_length:
        return False, f"Máximo {max_length} caracteres"
    
    return True, "Texto válido"

def validate_integer(value, min_val: int = None, max_val: int = None) -> Tuple[bool, str]:
    """
    Valida un entero.
    
    Args:
        value: Valor a validar
        min_val: Valor mínimo
        max_val: Valor máximo
    
    Returns:
        Tupla (válido, mensaje)
    """
    try:
        val = int(value)
        
        if min_val is not None and val < min_val:
            return False, f"Valor mínimo: {min_val}"
        
        if max_val is not None and val > max_val:
            return False, f"Valor máximo: {max_val}"
        
        return True, "Valor válido"
    
    except (ValueError, TypeError):
        return False, "Debe ser un número entero"
