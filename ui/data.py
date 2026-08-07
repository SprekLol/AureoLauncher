import json
import os
from pathlib import Path

DATA_DIR = Path.home() / ".aureo"
DATA_DIR.mkdir(exist_ok=True)
PROFILES_FILE = DATA_DIR / "profiles.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
MODS_CACHE = DATA_DIR / "mods_cache.json"

# Versiones de Minecraft (1.8.9 a 1.26.2)
MC_VERSIONS = [
    "1.26.2", "1.26.1", "1.26", "1.25.2", "1.25.1", "1.25",
    "1.24.4", "1.24.3", "1.24.2", "1.24.1", "1.24",
    "1.23.2", "1.23.1", "1.23",
    "1.22.4", "1.22.3", "1.22.2", "1.22.1", "1.22",
    "1.21.4", "1.21.3", "1.21.2", "1.21.1", "1.21",
    "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
    "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19",
    "1.18.2", "1.18.1", "1.18",
    "1.17.1", "1.17",
    "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16",
    "1.15.2", "1.15.1", "1.15",
    "1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14",
    "1.13.2", "1.13.1", "1.13",
    "1.12.2", "1.12.1", "1.12",
    "1.11.2", "1.11.1", "1.11",
    "1.10.2", "1.10.1", "1.10",
    "1.9.4", "1.9.2", "1.9.1", "1.9",
    "1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2", "1.8.1", "1.8",
]

LOADERS = ["Vanilla", "Fabric", "Forge", "Quilt", "NeoForge"]

RAM_OPTIONS = ["1GB", "2GB", "3GB", "4GB", "6GB", "8GB", "10GB", "12GB", "16GB"]

MODS_POPULAR = [
    {"name": "Sodium", "description": "Mejora significativa de rendimiento", "downloads": "2.5M", "type": "optimization"},
    {"name": "Iris Shaders", "description": "Soporte de shaders compatibles", "downloads": "1.8M", "type": "graphics"},
    {"name": "Lithium", "description": "Optimización del servidor", "downloads": "1.2M", "type": "optimization"},
    {"name": "Fabric API", "description": "API base para Fabric", "downloads": "1.1M", "type": "library"},
    {"name": "Entity Culling", "description": "Optimización de entidades", "downloads": "800K", "type": "optimization"},
    {"name": "Starlight", "description": "Optimización de iluminación", "downloads": "600K", "type": "optimization"},
]

def load_profiles():
    if PROFILES_FILE.exists():
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    return {
        "default": {
            "name": "Default",
            "version": "1.20.1",
            "loader": "Fabric",
            "ram": "4GB",
        }
    }

def save_profiles(profiles):
    with open(PROFILES_FILE, 'w') as f:
        json.dump(profiles, f, indent=2)

def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        "theme": "dark",
        "minecraft_path": str(Path.home() / ".minecraft"),
    }

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)