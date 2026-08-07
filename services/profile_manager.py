# ==============================================================================
# services/profile_manager.py - Gestor de perfiles de Minecraft
# ==============================================================================

import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.config import (
    load_config, save_config, MINECRAFT_VERSIONS, RAM_OPTIONS,
    DEFAULT_MINECRAFT_PATH, DEFAULT_ACCENT
)
from core.logger import get_logger

logger = get_logger("services.profiles")

# ==============================================================================
# Constantes
# ==============================================================================
DEFAULT_PROFILE = "__default__"

# ==============================================================================
# Clase ProfileManager
# ==============================================================================
class ProfileManager:
    """Gestor centralizado de perfiles."""
    
    def __init__(self):
        """Inicializa el gestor de perfiles."""
        self.logger = get_logger("profile_manager")
    
    @staticmethod
    def get_default_profile_data() -> Dict[str, Any]:
        """Obtiene los datos por defecto de un perfil."""
        return {
            "name": "Default",
            "nick": "",
            "version": MINECRAFT_VERSIONS[0],
            "ram": RAM_OPTIONS[1],
            "mc_path": DEFAULT_MINECRAFT_PATH,
            "loader_id": "vanilla",
            "loader_version": "Última (recomendada)",
            "hud_pack": False,
            "icon": "🟢",
            "color": DEFAULT_ACCENT,
        }
    
    def get_profile(self, profile_id: str = DEFAULT_PROFILE) -> Dict[str, Any]:
        """
        Obtiene un perfil específico.
        
        Args:
            profile_id: ID del perfil
        
        Returns:
            Diccionario con los datos del perfil
        """
        config = load_config()
        profiles = config.get("profiles", {})
        
        if profile_id not in profiles:
            logger.warning(f"Perfil no encontrado: {profile_id}")
            return self.get_default_profile_data()
        
        return profiles[profile_id]
    
    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene todos los perfiles.
        
        Returns:
            Diccionario de perfiles
        """
        config = load_config()
        profiles = config.get("profiles", {})
        
        if not profiles:
            logger.debug("No hay perfiles, creando perfil default")
            profiles[DEFAULT_PROFILE] = self.get_default_profile_data()
        
        return profiles
    
    def save_profile(self, profile_id: str, data: Dict[str, Any]) -> None:
        """
        Guarda un perfil.
        
        Args:
            profile_id: ID del perfil
            data: Datos del perfil
        """
        config = load_config()
        if "profiles" not in config:
            config["profiles"] = {}
        
        config["profiles"][profile_id] = data
        save_config(config)
        logger.info(f"Perfil guardado: {profile_id}")
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Elimina un perfil.
        
        Args:
            profile_id: ID del perfil
        
        Returns:
            True si se eliminó, False si no existe
        """
        if profile_id == DEFAULT_PROFILE:
            logger.warning("No se puede eliminar el perfil default")
            return False
        
        config = load_config()
        profiles = config.get("profiles", {})
        
        if profile_id not in profiles:
            logger.warning(f"Perfil no encontrado: {profile_id}")
            return False
        
        del profiles[profile_id]
        config["profiles"] = profiles
        save_config(config)
        logger.info(f"Perfil eliminado: {profile_id}")
        return True
    
    def create_profile(self, profile_id: str, data: Dict[str, Any]) -> None:
        """
        Crea un nuevo perfil.
        
        Args:
            profile_id: ID del perfil
            data: Datos del perfil
        """
        profiles = self.get_all_profiles()
        
        if profile_id in profiles:
            logger.warning(f"Perfil ya existe: {profile_id}")
            return
        
        self.save_profile(profile_id, data)
        logger.info(f"Perfil creado: {profile_id}")
    
    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> None:
        """
        Actualiza un perfil existente.
        
        Args:
            profile_id: ID del perfil
            updates: Diccionario con los cambios
        """
        data = self.get_profile(profile_id)
        data.update(updates)
        self.save_profile(profile_id, data)
        logger.info(f"Perfil actualizado: {profile_id}")

# ==============================================================================
# Instancia global
# ==============================================================================
profile_manager = ProfileManager()
