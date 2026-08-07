# ==============================================================================
# ui/sections/settings_section.py - Sección de configuración
# ==============================================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox

from ui.components import ModernCard, ModernButton, ModernCombobox, ModernEntry
from ui.colors import TEXT_PRIMARY, BG_CARD, ACCENT_COLORS_MAP
from ui.fonts import get_text_font
from core.config import load_config, save_config, THEMES, DEFAULT_MINECRAFT_PATH
from core.logger import get_logger

logger = get_logger("ui.settings_section")

class SettingsSection(ModernCard):
    """Sección de configuración de la aplicación."""
    
    def __init__(self, parent):
        super().__init__(parent, title="⚙️ Configuración")
        self._build_content()
    
    def _build_content(self):
        """Construye el contenido de la sección."""
        
        # Cargar configuración actual
        config = load_config()
        
        # Tema
        ctk.CTkLabel(
            self,
            text="Tema:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(12, 4))
        
        self.theme_combo = ModernCombobox(
            self,
            values=list(THEMES.keys())
        )
        self.theme_combo.set(config.get("theme", "Oscuro"))
        self.theme_combo.pack(fill="x", padx=16, pady=(0, 12))
        
        # Color de acento
        ctk.CTkLabel(
            self,
            text="Color de acento:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(0, 4))
        
        self.accent_combo = ModernCombobox(
            self,
            values=list(ACCENT_COLORS_MAP.keys())
        )
        
        # Obtener color actual
        accent_color = config.get("accent_color", "#00d9ff")
        for name, color in ACCENT_COLORS_MAP.items():
            if color == accent_color:
                self.accent_combo.set(name)
                break
        
        self.accent_combo.pack(fill="x", padx=16, pady=(0, 12))
        
        # Separador
        sep = ctk.CTkFrame(self, fg_color=TEXT_PRIMARY, height=1)
        sep.pack(fill="x", padx=16, pady=12)
        
        # Ruta de Minecraft
        ctk.CTkLabel(
            self,
            text="Ruta de Minecraft:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(0, 4))
        
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        self.mc_path_entry = ModernEntry(
            path_frame,
            placeholder=DEFAULT_MINECRAFT_PATH
        )
        self.mc_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.mc_path_entry.insert(0, config.get("minecraft_path", DEFAULT_MINECRAFT_PATH))
        
        ModernButton(
            path_frame,
            text="Seleccionar",
            command=self._select_mc_path,
            is_primary=False
        ).pack(side="right")
        
        # Frame de botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        ModernButton(
            btn_frame,
            text="Guardar Cambios",
            command=self._save_settings
        ).pack(side="left", padx=(0, 8))
        
        ModernButton(
            btn_frame,
            text="Restaurar Predeterminados",
            command=self._reset_settings,
            is_primary=False
        ).pack(side="left")
    
    def _select_mc_path(self):
        """Selecciona la carpeta de Minecraft."""
        folder = filedialog.askdirectory(
            title="Selecciona la carpeta .minecraft"
        )
        if folder:
            self.mc_path_entry.delete(0, "end")
            self.mc_path_entry.insert(0, folder)
    
    def _save_settings(self):
        """Guarda la configuración."""
        config = load_config()
        
        config["theme"] = self.theme_combo.get()
        
        # Guardar color
        accent_name = self.accent_combo.get()
        config["accent_color"] = ACCENT_COLORS_MAP.get(accent_name, "#00d9ff")
        
        config["minecraft_path"] = self.mc_path_entry.get()
        
        save_config(config)
        logger.info("Configuración guardada")
        messagebox.showinfo("Éxito", "Configuración guardada correctamente")
    
    def _reset_settings(self):
        """Restaura la configuración predeterminada."""
        if messagebox.askyesno("Confirmar", "¿Restaurar configuración predeterminada?"):
            config = {
                "theme": "Oscuro",
                "accent_color": "#00d9ff",
                "minecraft_path": DEFAULT_MINECRAFT_PATH,
            }
            save_config(config)
            
            self.theme_combo.set("Oscuro")
            self.accent_combo.set("Cian")
            self.mc_path_entry.delete(0, "end")
            self.mc_path_entry.insert(0, DEFAULT_MINECRAFT_PATH)
            
            logger.info("Configuración restaurada")
            messagebox.showinfo("Éxito", "Configuración restaurada")
