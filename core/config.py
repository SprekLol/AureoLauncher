import os
import sys
import json
from pathlib import Path

APP_NAME = "AureoLauncher"
APP_VERSION = "2.0"

# 🎨 Paleta moderna: Azul oscuro profundo con acentos cian/púrpura
COL_BG      = "#0a0e27"      # Azul oscuro profundo (fondo principal)
COL_CARD    = "#141b35"      # Azul medio (tarjetas)
COL_BORDER  = "#1f2847"      # Borde sutil
COL_TEXT    = "#e8eef7"      # Blanco frío brillante
COL_MUTED   = "#7a8ab0"      # Gris azulado suave

# Accent dinámico - Cian vibrante (0, 217, 255) - MÁS MEMORABLE
DEFAULT_ACCENT = "#00d9ff"   # CIAN VIBRANTE
COL_ACCENT  = DEFAULT_ACCENT
COL_ACCENT_HOVER = "#00b8d4" # Cian más oscuro para hover

# Colores de consola mejorados
COL_LOG_ERROR = "#ff6b6b"
COL_LOG_WARN  = "#ffa500"
COL_LOG_INFO  = "#00d9ff"
COL_LOG_DEBUG = "#a0aec0"
COL_LOG_DONE  = "#52d273"

MINECRAFT_VERSIONS = [
    "1.21.5", "1.21.4", "1.21.3", "1.21.1", "1.21",
    "1.20.6", "1.20.4", "1.20.2", "1.20.1", "1.19.4", "1.19.2",
    "1.18.2", "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.12.2", "1.8.9"
]
RAM_OPTIONS = ["2GB", "4GB", "6GB", "8GB", "12GB", "16GB"]
ACCENT_COLORS = {
    "Cian":    "#00d9ff",      # ✨ Vibrante y memorable
    "Púrpura": "#9d4edd",      # Elegante y sofisticada
    "Rosa":    "#ff006e",      # Atrevida y moderna
    "Verde":   "#06d6a0",      # Fresca y natural
    "Azul":    "#5a67d8",      # Profesional y confiable
    "Naranja": "#ff9f1c",      # Energética y cálida
    "Rojo":    "#e63946",      # Impactante y llamativa
}
THEMES = {"Oscuro": "dark", "Claro": "light"}

DEFAULT_MINECRAFT_PATH = os.path.join(os.getenv("APPDATA", ""), ".minecraft")
SETTINGS_DIR  = os.path.join(os.getenv("APPDATA", "."), "AureoLauncher")
SETTINGS_PATH = os.path.join(SETTINGS_DIR, "settings.json")
LOGS_DIR      = os.path.join(SETTINGS_DIR, "logs")

MODRINTH_API = "https://api.modrinth.com/v2"
LATEST_LOADER = "Última (recomendada)"

LOADERS = (
    ("vanilla",  "Vanilla"),
    ("fabric",   "Fabric"),
    ("forge",    "Forge"),
    ("neoforge", "NeoForge"),
    ("quilt",    "Quilt"),
    ("optifine", "OptiFine"),
)
LOADER_LABELS = [b for _, b in LOADERS]
_ID_BY_LABEL  = {b: a for a, b in LOADERS}
_LABEL_BY_ID  = {a: b for a, b in LOADERS}

BASE_DIR = Path(__file__).parent
SETTINGS_FILE = BASE_DIR / "settings.json"

HUD_MOD_SLUGS = ("fabric-api", "cloth-config", "yacl", "modmenu", "veltium", "cps-plus")

from ui.colors import (
    BG_PRIMARY as COL_BG,
    BG_CARD as COL_CARD,
    TEXT_PRIMARY as COL_TEXT,
    ACCENT_BLUE as COL_ACCENT,
    ACCENT_BLUE_HOVER as COL_ACCENT_HOVER,
    LOG_ERROR as COL_LOG_ERROR,
    LOG_WARN as COL_LOG_WARN,
    LOG_INFO as COL_LOG_INFO,
    LOG_SUCCESS as COL_LOG_DONE,
)

def _load_settings() -> dict:
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

def _save_settings(data: dict) -> None:
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_default_minecraft_path_static() -> str:
    """Obtiene la ruta predeterminada de Minecraft."""
    if sys.platform == "win32":
        return os.path.join(os.getenv("APPDATA", ""), ".minecraft")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/minecraft")
    else:
        return os.path.expanduser("~/.minecraft")

DEFAULT_PROFILE = "__default__"

def _default_profile_data() -> dict:
    return {
        "name": "Default",
        "nick": "",
        "version": MINECRAFT_VERSIONS[0],
        "ram": RAM_OPTIONS[1],
        "mc_path": get_default_minecraft_path_static(),
        "loader_id": "vanilla",
        "loader_version": LATEST_LOADER,
        "hud_pack": False,
        "icon": "🟢",
        "color": DEFAULT_ACCENT,
    }