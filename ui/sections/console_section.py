# ==============================================================================
# ui/sections/console_section.py - Sección de consola integrada
# ==============================================================================

import customtkinter as ctk
from typing import Optional

from ui.components import ModernCard, ModernButton
from ui.colors import TEXT_PRIMARY, LOG_ERROR, LOG_INFO, LOG_SUCCESS
from ui.fonts import get_text_font
from core.logger import get_logger

logger = get_logger("ui.console_section")

class ConsoleSection(ModernCard):
    """Sección de consola para ver logs en tiempo real."""
    
    def __init__(self, parent):
        super().__init__(parent, title="📋 Consola del Sistema")
        self._build_content()
    
    def _build_content(self):
        """Construye el contenido de la sección."""
        
        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=16, pady=(0, 8))
        
        # Leyenda
        ctk.CTkLabel(
            toolbar,
            text="Leyenda:",
            font=get_text_font("small"),
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))
        
        for text, color in [("● ERROR", LOG_ERROR), ("● WARN", "#ffa500"), 
                            ("● INFO", LOG_INFO), ("● SUCCESS", LOG_SUCCESS)]:
            ctk.CTkLabel(
                toolbar,
                text=text,
                font=get_text_font("small"),
                text_color=color
            ).pack(side="left", padx=4)
        
        # Espaciador
        ctk.CTkFrame(toolbar, fg_color="transparent").pack(side="left", expand=True)
        
        # Botones
        ModernButton(
            toolbar,
            text="Limpiar",
            command=self._clear,
            is_primary=False
        ).pack(side="right", padx=(0, 4))
        
        # Consola
        self.console = ctk.CTkTextbox(
            self,
            fg_color="#0a0a0c",
            text_color=TEXT_PRIMARY,
            font=("Consolas", 9)
        )
        self.console.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        # Configurar tags
        self.console.tag_config("error", foreground=LOG_ERROR)
        self.console.tag_config("warn", foreground="#ffa500")
        self.console.tag_config("info", foreground=LOG_INFO)
        self.console.tag_config("done", foreground=LOG_SUCCESS)
        self.console.tag_config("debug", foreground="#a0aec0")
        
        # Mensaje inicial
        self.log("Consola del sistema lista\n", "info")
    
    def log(self, message: str, level: str = "info"):
        """Agrega un mensaje al log."""
        self.console.insert("end", message, level)
        self.console.see("end")
    
    def _clear(self):
        """Limpia la consola."""
        self.console.delete("1.0", "end")
        self.log("Consola limpiada\n", "info")
