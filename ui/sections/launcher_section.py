# ==============================================================================
# ui/sections/launcher_section.py - Sección de lanzamiento
# ==============================================================================

import customtkinter as ctk
from typing import Callable, Optional
import threading
from tkinter import messagebox
from queue import Queue, Empty

from ui.components import ModernCard, ModernButton, ModernCombobox, ModernLabel
from ui.colors import TEXT_PRIMARY, BG_PRIMARY, ACCENT_CYAN, LOG_ERROR, LOG_INFO, LOG_SUCCESS
from ui.fonts import get_text_font, get_title_font
from services.profile_manager import profile_manager
from services.launcher import minecraft_launcher
from core.minecraft import get_all_versions
from core.config import RAM_OPTIONS, ID_BY_LABEL, LABEL_BY_ID, DEFAULT_MINECRAFT_PATH
from core.logger import get_logger
from utils.validation import validate_nick, validate_minecraft_path

logger = get_logger("ui.launcher_section")

class LauncherSection(ModernCard):
    """Sección de lanzamiento de Minecraft."""
    
    def __init__(self, parent, on_profile_changed: Optional[Callable] = None):
        super().__init__(parent, title="🎮 Lanzador")
        self.on_profile_changed = on_profile_changed
        self.current_profile = None
        self.log_queue = Queue()
        
        self._build_content()
    
    def _build_content(self):
        """Construye el contenido de la sección."""
        
        # Frame superior: opciones
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        # Nick
        ctk.CTkLabel(
            top_frame,
            text="Nick:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY,
            width=50
        ).pack(side="left", padx=(0, 8))
        
        self.nick_entry = ctk.CTkEntry(
            top_frame,
            placeholder_text="Tu nick",
            font=get_text_font("normal"),
            width=120
        )
        self.nick_entry.pack(side="left", padx=(0, 16))
        
        # RAM
        ctk.CTkLabel(
            top_frame,
            text="RAM:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY,
            width=50
        ).pack(side="left", padx=(0, 8))
        
        self.ram_combo = ModernCombobox(
            top_frame,
            values=RAM_OPTIONS
        )
        self.ram_combo.set("4GB")
        self.ram_combo.pack(side="left", padx=(0, 16), fill="x", expand=True)
        
        # Botón lanzar
        ModernButton(
            top_frame,
            text="🚀 LANZAR",
            command=self._launch_minecraft,
            is_primary=True
        ).pack(side="right")
        
        # Separador
        sep = ctk.CTkFrame(self, fg_color=TEXT_PRIMARY, height=1)
        sep.pack(fill="x", padx=16, pady=12)
        
        # Frame de consola
        console_label = ctk.CTkLabel(
            self,
            text="📋 Consola",
            font=get_text_font("header"),
            text_color=TEXT_PRIMARY
        )
        console_label.pack(anchor="w", padx=16, pady=(0, 8))
        
        # Textbox de logs
        self.console_text = ctk.CTkTextbox(
            self,
            fg_color="#0a0a0c",
            text_color=TEXT_PRIMARY,
            font=("Consolas", 9),
            height=150
        )
        self.console_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        # Configurar tags de color
        self.console_text.tag_config("error", foreground=LOG_ERROR)
        self.console_text.tag_config("warn", foreground="#ffa500")
        self.console_text.tag_config("info", foreground=LOG_INFO)
        self.console_text.tag_config("done", foreground=LOG_SUCCESS)
        
        # Frame de botones de consola
        console_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        console_btn_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        ModernButton(
            console_btn_frame,
            text="Limpiar",
            command=self._clear_console,
            is_primary=False
        ).pack(side="left", padx=(0, 8))
        
        ModernButton(
            console_btn_frame,
            text="Guardar log",
            command=self._save_log,
            is_primary=False
        ).pack(side="left")
    
    def set_profile(self, profile_id: str, profile_data: dict):
        """Establece el perfil actual."""
        self.current_profile = (profile_id, profile_data)
        self.nick_entry.delete(0, "end")
        self.nick_entry.insert(0, profile_data.get("nick", ""))
        self.ram_combo.set(profile_data.get("ram", "4GB"))
        self._log(f"Perfil cargado: {profile_data.get('name')}\n", "info")
    
    def _launch_minecraft(self):
        """Lanza Minecraft."""
        if not self.current_profile:
            messagebox.showerror("Error", "Selecciona un perfil primero")
            return
        
        profile_id, profile_data = self.current_profile
        nick = self.nick_entry.get().strip()
        ram = self.ram_combo.get()
        
        # Validar nick
        valid, msg = validate_nick(nick)
        if not valid:
            messagebox.showerror("Error", f"Nick inválido: {msg}")
            return
        
        # Validar ruta
        mc_path = profile_data.get("mc_path", DEFAULT_MINECRAFT_PATH)
        valid, msg = validate_minecraft_path(mc_path)
        if not valid:
            messagebox.showerror("Error", f"Ruta inválida: {msg}")
            return
        
        # Extraer RAM en GB
        ram_gb = int(ram.replace("GB", ""))
        
        # Log
        self._log(f"Lanzando Minecraft...\n", "info")
        self._log(f"Nick: {nick}, Versión: {profile_data['version']}, RAM: {ram}\n", "info")
        
        # Lanzar en thread
        def launch_thread():
            minecraft_launcher.launch(
                nick=nick,
                version=profile_data.get("version", "1.21.5"),
                ram_gb=ram_gb,
                mc_path=mc_path,
                loader_id=profile_data.get("loader_id", "vanilla"),
                log_queue=self.log_queue,
                on_complete=self._on_launch_complete
            )
        
        threading.Thread(target=launch_thread, daemon=True).start()
        
        # Iniciar lector de queue
        self._read_log_queue()
    
    def _read_log_queue(self):
        """Lee logs de la queue."""
        try:
            while True:
                level, msg = self.log_queue.get_nowait()
                self._log(msg, level)
        except Empty:
            pass
        
        # Reintentar después de 100ms
        self.after(100, self._read_log_queue)
    
    def _log(self, message: str, level: str = "info"):
        """Agrega un mensaje al log."""
        self.console_text.insert("end", message, level)
        self.console_text.see("end")
    
    def _clear_console(self):
        """Limpia la consola."""
        self.console_text.delete("1.0", "end")
        logger.info("Consola limpiada")
    
    def _save_log(self):
        """Guarda el log a un archivo."""
        from tkinter import filedialog
        from datetime import datetime
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt")]
        )
        
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.console_text.get("1.0", "end"))
                messagebox.showinfo("Éxito", f"Log guardado en:\n{filename}")
                logger.info(f"Log guardado: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
    
    def _on_launch_complete(self, success: bool, message: str):
        """Callback cuando se completa el lanzamiento."""
        if success:
            self._log(f"✅ {message}\n", "done")
        else:
            self._log(f"❌ {message}\n", "error")
        logger.info(f"Lanzamiento completado: {message}")
