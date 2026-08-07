import requests
import os
import json
import logging
from typing import Optional, List, Tuple

from core.config import (
    MODRINTH_API, HUD_MOD_SLUGS, get_default_minecraft_path_static,
    LATEST_LOADER,
    MINECRAFT_VERSIONS
)
from core.minecraft import (
    get_optifine_installed_versions, _safe_get
)

def modrinth_list_versions(slug: str, game_version: str, loader: str = "fabric") -> list:
    url    = f"{MODRINTH_API}/project/{slug}/version"
    params = {"loaders": json.dumps([loader]), "game_versions": json.dumps([game_version])}
    resp   = _safe_get(url, timeout=45, params=params)
    if resp is None:
        return []
    try:
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list):
            return []
        return data
    except (requests.RequestException, ValueError) as e:
        logging.warning("Error parsing Modrinth response for %s: %s", slug, e)
        return []

def hud_pack_supported(game_version: str) -> bool:
    try:
        v = modrinth_list_versions("veltium",  game_version)
        c = modrinth_list_versions("cps-plus", game_version)
        return len(v) > 0 and len(c) > 0
    except Exception:
        return False

def install_hud_mods(mc_path: str, game_version: str) -> str | None:
    mods_dir = os.path.join(mc_path, "mods")
    os.makedirs(mods_dir, exist_ok=True)
    session = requests.Session()
    try:
        for slug in HUD_MOD_SLUGS:
            try:
                versions = modrinth_list_versions(slug, game_version)
            except requests.RequestException as e:
                return f"No se pudo consultar Modrinth ({slug}): {e}"
            if not versions:
                return f"No hay versión de «{slug}» para Minecraft {game_version} con Fabric."
            
            first_version = versions[0]
            if not isinstance(first_version, dict):
                return f"Formato de respuesta inválido para «{slug}»."
            
            files = first_version.get("files") or []
            if not files:
                return f"No hay archivos disponibles para «{slug}»."
            
            primary = next((f for f in files if isinstance(f, dict) and f.get("primary")), 
                          files[0] if files else None)
            if not primary or not isinstance(primary, dict) or not primary.get("url"):
                return f"Archivo principal no encontrado para «{slug}»."
            
            dest = os.path.join(mods_dir, primary["filename"])
            try:
                r = session.get(primary["url"], timeout=120)
                r.raise_for_status()
                with open(dest, "wb") as f:
                    f.write(r.content)
            except requests.RequestException as e:
                return f"Error descargando {slug}: {e}"
        return None
    finally:
        session.close()

def paper_latest_jar_url(mc_version: str) -> tuple[str | None, str | None]:
    url  = f"https://api.papermc.io/v2/projects/paper/versions/{mc_version}/builds"
    resp = _safe_get(url, timeout=45)
    if resp is None:
        return None, "Sin conexión a internet."
    if resp.status_code == 404:
        return None, f"No hay builds de Paper para Minecraft {mc_version}."
    try:
        resp.raise_for_status()
        builds = resp.json().get("builds") or []
        if not builds:
            return None, "Paper no devolvió ningún build."
        b   = builds[-1]
        bid = b["build"]
        app = b.get("downloads", {}).get("application")
        if not app:
            return None, "El último build no tiene descarga."
        name = app["name"]
        jar  = f"https://api.papermc.io/v2/projects/paper/versions/{mc_version}/builds/{bid}/downloads/{name}"
        return jar, None
    except (KeyError, ValueError, requests.RequestException) as e:
        return None, f"Error procesando respuesta de Paper: {e}"

def download_paper_jar(mc_version: str, dest_folder: str) -> tuple[str | None, str | None]:
    try:
        jar_url, err = paper_latest_jar_url(mc_version)
        if err:
            return None, err
        resp = _safe_get(jar_url, timeout=180)
        if resp is None:
            return None, "Error de conexión descargando Paper."
        resp.raise_for_status()
        fn   = jar_url.rsplit("/", 1)[-1]
        os.makedirs(dest_folder, exist_ok=True)
        dest = os.path.join(dest_folder, fn)
        with open(dest, "wb") as f:
            f.write(resp.content)
        return dest, None
    except requests.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, f"Error inesperado: {e}"

def fetch_loader_version_rows(loader_id: str, mc_version: str, mc_path: str = "") -> list[str]:
    if loader_id == "vanilla":
        return ["—"]
    if loader_id == "optifine":
        path      = mc_path or get_default_minecraft_path_static()
        installed = get_optifine_installed_versions(path)
        if not installed:
            return ["(no hay versiones OptiFine instaladas)"]
        return installed
    try:
        from minecraft_launcher_lib.mod_loader import get_mod_loader
        ml = get_mod_loader(loader_id)
        if not ml.is_minecraft_version_supported(mc_version):
            return ["(no compatible con esta versión de Minecraft)"]
        rows = ml.get_loader_versions(mc_version, True)
        if not rows:
            rows = ml.get_loader_versions(mc_version, False)
        if not isinstance(rows, list):
            return ["(error al obtener versiones)"]
        tail = rows[:45]
        return [LATEST_LOADER] + tail
    except ImportError:
        return ["(no instalado minecraft-launcher-lib)"]
    except Exception as e:
        logging.exception("Error in fetch_loader_version_rows")
        return [f"Error: {str(e)[:50]}"]

def fetch_loader_minecraft_versions(loader_id: str, stable_only: bool) -> list[str]:
    if loader_id == "vanilla":
        return MINECRAFT_VERSIONS
    try:
        from minecraft_launcher_lib.mod_loader import get_mod_loader
        ml       = get_mod_loader(loader_id)
        versions = ml.get_minecraft_versions(stable_only)
        return list(versions)
    except Exception:
        return []

def _parse_loader_version_pick(pick: str) -> str | None:
    if not pick or not isinstance(pick, str):
        return None
    pick = pick.strip()
    if pick in ("—", LATEST_LOADER) or pick.startswith("(") or pick.startswith("Error"):
        return None
    return pick