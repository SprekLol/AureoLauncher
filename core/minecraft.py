import os
import re
import hashlib
import uuid as uuid_lib
import logging
from typing import List
import requests

from core.config import MINECRAFT_VERSIONS

def get_installed_versions(mc_path: str) -> list[str]:
    versions_dir = os.path.join(mc_path, "versions")
    if not os.path.isdir(versions_dir):
        return []
    
    # Palabras clave de mods/loaders que NO deben aparecer en versiones
    # (porque ya tienen su propio cargador)
    skip_keywords = ("optifine", "fabric", "forge", "neoforge", "quilt", "-fabric-", "-forge-", "-neo-")
    
    installed = []
    for name in os.listdir(versions_dir):
        # Saltar si contiene palabras clave de loaders
        if any(kw in name.lower() for kw in skip_keywords):
            continue
            
        folder    = os.path.join(versions_dir, name)
        json_file = os.path.join(folder, f"{name}.json")
        if os.path.isdir(folder) and os.path.isfile(json_file):
            installed.append(name)
    
    def sort_key(v):
        is_modded = any(x in v.lower() for x in ("optifine", "fabric", "forge", "neoforge", "quilt"))
        nums      = re.findall(r"\d+", v.split("-")[0])
        num_key   = tuple(int(n) for n in nums) if nums else (0,)
        return (0 if is_modded else 1, tuple(-n for n in num_key))
    installed.sort(key=sort_key)
    return installed

def get_all_versions(mc_path: str) -> list[str]:
    installed = get_installed_versions(mc_path)
    combined  = list(installed)
    for v in MINECRAFT_VERSIONS:
        if v not in combined:
            combined.append(v)
    return combined if combined else list(MINECRAFT_VERSIONS)

def get_optifine_installed_versions(mc_path: str) -> list[str]:
    versions_dir = os.path.join(mc_path, "versions")
    if not os.path.isdir(versions_dir):
        return []
    result = []
    for name in os.listdir(versions_dir):
        if "optifine" in name.lower() or "OptiFine" in name:
            folder    = os.path.join(versions_dir, name)
            json_file = os.path.join(folder, f"{name}.json")
            if os.path.isdir(folder) and os.path.isfile(json_file):
                result.append(name)
    result.sort(reverse=True)
    return result

def generate_uuid_from_nick(nick: str) -> str:
    hash_obj = hashlib.md5(f"OfflinePlayer:{nick}".encode())
    u        = bytearray(hash_obj.digest())
    u[6]     = (u[6] & 0x0F) | 0x30
    u[8]     = (u[8] & 0x3F) | 0x80
    return str(uuid_lib.UUID(bytes=bytes(u)))

# FIX: Requests con manejo de errores
def _safe_get(url: str, *, timeout: int = 10, **kwargs) -> requests.Response | None:
    try:
        return requests.get(url, timeout=timeout, **kwargs)
    except requests.RequestException as e:
        logging.warning("GET %s failed: %s", url, e)
        return None