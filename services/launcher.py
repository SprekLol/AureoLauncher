import subprocess
import os
import logging
import threading
import time
from typing import Optional, Callable
from queue import Queue

from core.config import (
    DEFAULT_MINECRAFT_PATH, _load_settings, _ID_BY_LABEL,
    APP_NAME, APP_VERSION
)
from core.minecraft import generate_uuid_from_nick, _safe_get
from services.downloader import (
    hud_pack_supported, install_hud_mods, _parse_loader_version_pick
)
from utils.helpers import detect_java

def launch_minecraft(
    nick: str,
    version: str,
    ram_gb: int,
    mc_path: str,
    loader_id: str,
    loader_version_pick: str,
    use_hud_pack: bool,
    progress_callback,
    log_queue: Queue,
    done_callback,
) -> None:
    try:
        from minecraft_launcher_lib import install, command, utils
        from minecraft_launcher_lib.exceptions import UnsupportedVersion, VersionNotFound
        from minecraft_launcher_lib.mod_loader import get_mod_loader

        player_uuid = generate_uuid_from_nick(nick)
        ram_mb      = ram_gb * 1024
        jvm_args    = [f"-Xmx{ram_mb}m", f"-Xms{ram_mb}m"]
        launch_version = version
        lv = _parse_loader_version_pick(loader_version_pick)

        # FIX: Validar ruta antes de continuar
        if not os.path.isdir(mc_path):
            try:
                os.makedirs(mc_path)
            except OSError as e:
                done_callback(False, f"No se pudo crear la carpeta: {e}")
                return

        progress_callback("Verificando Java…", 0.05)
        java_ok, java_msg = detect_java()
        if not java_ok:
            done_callback(False, f"Java no encontrado. Instala Java 17 o superior.\n{java_msg}")
            return

        progress_callback("Verificando versión…", 0.1)
        if loader_id == "vanilla":
            install.install_minecraft_version(version, mc_path)
        elif loader_id == "optifine":
            if not loader_version_pick or loader_version_pick.startswith("("):
                done_callback(False, "Selecciona una versión de OptiFine instalada.")
                return
            launch_version = loader_version_pick
            progress_callback("Usando OptiFine instalado…", 0.5)
        else:
            loader = get_mod_loader(loader_id)
            if not loader.is_minecraft_version_supported(version):
                done_callback(False, f"{loader.get_name()} no soporta Minecraft {version}.")
                return
            progress_callback(f"Instalando {loader.get_name()}…", 0.3)
            try:
                launch_version = loader.install(version, mc_path, loader_version=lv)
            except UnsupportedVersion as e:
                done_callback(False, str(e))
                return
            except VersionNotFound:
                done_callback(False, f"No se encontró la versión de Minecraft {version}.")
                return

            if use_hud_pack:
                if loader_id != "fabric":
                    done_callback(False, "El pack HUD solo funciona con Fabric.")
                    return
                if not hud_pack_supported(version):
                    done_callback(False, f"No hay pack HUD listo para {version}.")
                    return
                progress_callback("Descargando mods HUD…", 0.6)
                err = install_hud_mods(mc_path, version)
                if err:
                    done_callback(False, err)
                    return

        progress_callback("Preparando lanzamiento…", 0.8)
        options = {
            "username":       nick,
            "uuid":           player_uuid,
            "token":          "",
            "gameDirectory":  mc_path,
            "jvmArguments":   jvm_args,
            "launcherName":   APP_NAME,
            "launcherVersion": APP_VERSION,
            "demo":           False,
        }
        minecraft_command = command.get_minecraft_command(launch_version, mc_path, options)
        progress_callback("Iniciando Minecraft…", 0.95)
        process = subprocess.Popen(
            minecraft_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=mc_path,
            universal_newlines=True,
            bufsize=1,
        )

        def read_output():
            try:
                for line in iter(process.stdout.readline, ""):
                    if not line:
                        break
                    log_queue.put(line.rstrip())
                    logging.info("[MC] %s", line.rstrip())
            finally:
                if process.stdout:
                    process.stdout.close()
                process.wait()
                done_callback(True, "Minecraft cerrado.")

        threading.Thread(target=read_output, daemon=True).start()
        time.sleep(2)
        if process.poll() is None:
            progress_callback("¡En juego!", 1.0)

        # Monitorear hasta que Minecraft cierre
        while process.poll() is None:
            time.sleep(0.5)
        
        # Cuando el proceso termina
        done_callback(True, "Minecraft cerrado.")

    except ImportError:
        done_callback(False, "Instala dependencias: pip install minecraft-launcher-lib requests")
    except Exception as e:
        logging.exception("Error al lanzar Minecraft")
        done_callback(False, f"Error al iniciar: {e}")