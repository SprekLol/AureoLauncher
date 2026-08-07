# ==============================================================================
# ui/sections/profiles_section.py - Gestión de perfiles
# ==============================================================================

import customtkinter as ctk
from typing import Callable, Optional
import uuid as uuid_lib
import json
from tkinter import simpledialog, messagebox

from ui.components import ModernCard, ModernButton, ModernCombobox, ModernEntry, ModernLabel
from ui.colors import TEXT_PRIMARY, BG_CARD, ACCENT_CYAN
from ui.fonts import get_text_font, get_title_font
from services.profile_manager import profile_manager
from core.minecraft import get_all_versions
from core.config import RAM_OPTIONS, ID_BY_LABEL, LABEL_BY_ID, DEFAULT_MINECRAFT_PATH, DEFAULT_ACCENT, ACCENT_COLORS_MAP
from core.logger import get_logger

logger = get_logger("ui.profiles_section")

class ProfilesSection(ModernCard):
    """Sección de gestión de perfiles."""
    
    def __init__(self, parent, on_profile_changed: Optional[Callable] = None):
        super().__init__(parent, title="👤 Perfiles")
        self.on_profile_changed = on_profile_changed
        
        self._build_content()
        self._update_profiles_list()
    
    def _build_content(self):
        """Construye el contenido de la sección."""
        
        # Frame superior: Dropdown y botones
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        # Dropdown de perfiles
        ctk.CTkLabel(
            top_frame,
            text="Perfil activo:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))
        
        self.profile_combo = ModernCombobox(
            top_frame,
            values=["Default"]
        )
        self.profile_combo.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.profile_combo.bind("<<ComboboxChanged>>", lambda e: self._on_profile_selected())
        
        # Frame de botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        ModernButton(
            btn_frame,
            text="➕ Nuevo",
            command=self._create_profile,
            is_primary=True
        ).pack(side="left", padx=(0, 6))
        
        ModernButton(
            btn_frame,
            text="✏️ Editar",
            command=self._edit_profile,
            is_primary=False
        ).pack(side="left", padx=(0, 6))
        
        ModernButton(
            btn_frame,
            text="🗑️ Eliminar",
            command=self._delete_profile,
            is_primary=False
        ).pack(side="left", padx=(0, 6))
        
        # Panel de información del perfil
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        # Scrollable para la info
        self.info_scroll = ctk.CTkScrollableFrame(
            self.info_frame,
            fg_color=BG_CARD
        )
        self.info_scroll.pack(fill="both", expand=True)
    
    def _update_profiles_list(self):
        """Actualiza la lista de perfiles en el combo."""
        profiles = profile_manager.get_all_profiles()
        names = [profile["name"] for profile in profiles.values()]
        self.profile_combo.configure(values=names)
        
        if names:
            self.profile_combo.set(names[0])
            self._on_profile_selected()
    
    def _on_profile_selected(self):
        """Callback cuando se selecciona un perfil."""
        selected_name = self.profile_combo.get()
        profiles = profile_manager.get_all_profiles()
        
        # Buscar el perfil por nombre
        for profile_id, profile_data in profiles.items():
            if profile_data["name"] == selected_name:
                self._display_profile_info(profile_data)
                
                if self.on_profile_changed:
                    self.on_profile_changed(profile_id, profile_data)
                
                logger.info(f"Perfil seleccionado: {selected_name}")
                break
    
    def _display_profile_info(self, profile_data):
        """Muestra la información del perfil seleccionado."""
        # Limpiar frame anterior
        for widget in self.info_scroll.winfo_children():
            widget.destroy()
        
        # Información del perfil
        info = [
            ("Nick:", profile_data.get("nick", "N/A")),
            ("Versión:", profile_data.get("version", "N/A")),
            ("RAM:", profile_data.get("ram", "N/A")),
            ("Loader:", LABEL_BY_ID.get(profile_data.get("loader_id", "vanilla"), "Vanilla")),
            ("Ruta MC:", profile_data.get("mc_path", "N/A")[:50] + "..."),
            ("HUD Pack:", "✅" if profile_data.get("hud_pack") else "❌"),
        ]
        
        for label, value in info:
            frame = ctk.CTkFrame(self.info_scroll, fg_color="transparent")
            frame.pack(fill="x", padx=8, pady=4)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=get_text_font("small"),
                text_color=TEXT_PRIMARY,
                width=100
            ).pack(side="left")
            
            ctk.CTkLabel(
                frame,
                text=value,
                font=get_text_font("small"),
                text_color=TEXT_PRIMARY
            ).pack(side="left", padx=(8, 0))
    
    def _create_profile(self):
        """Crea un nuevo perfil."""
        dialog = ProfileDialog(self, "Crear perfil", {})
        if dialog.result:
            profile_id = str(uuid_lib.uuid4())
            profile_manager.save_profile(profile_id, dialog.result)
            self._update_profiles_list()
            logger.info(f"Perfil creado: {dialog.result['name']}")
            messagebox.showinfo("Éxito", f"Perfil '{dialog.result['name']}' creado")
    
    def _edit_profile(self):
        """Edita el perfil seleccionado."""
        selected_name = self.profile_combo.get()
        profiles = profile_manager.get_all_profiles()
        
        for profile_id, profile_data in profiles.items():
            if profile_data["name"] == selected_name:
                dialog = ProfileDialog(self, "Editar perfil", profile_data)
                if dialog.result:
                    profile_manager.save_profile(profile_id, dialog.result)
                    self._update_profiles_list()
                    logger.info(f"Perfil editado: {dialog.result['name']}")
                    messagebox.showinfo("Éxito", "Perfil actualizado")
                break
    
    def _delete_profile(self):
        """Elimina el perfil seleccionado."""
        selected_name = self.profile_combo.get()
        
        if selected_name == "Default":
            messagebox.showerror("Error", "No puedes eliminar el perfil Default")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar perfil '{selected_name}'?"):
            profiles = profile_manager.get_all_profiles()
            for profile_id, profile_data in profiles.items():
                if profile_data["name"] == selected_name:
                    profile_manager.delete_profile(profile_id)
                    self._update_profiles_list()
                    logger.info(f"Perfil eliminado: {selected_name}")
                    messagebox.showinfo("Éxito", "Perfil eliminado")
                    break


class ProfileDialog(ctk.CTkToplevel):
    """Diálogo para crear/editar perfiles."""
    
    def __init__(self, parent, title: str, profile_data: dict):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x600")
        self.result = None
        
        self.profile_data = profile_data or {
            "name": "",
            "nick": "",
            "version": "1.21.5",
            "ram": "4GB",
            "mc_path": DEFAULT_MINECRAFT_PATH,
            "loader_id": "vanilla",
            "loader_version": "Última (recomendada)",
            "hud_pack": False,
            "icon": "🟢",
            "color": DEFAULT_ACCENT,
        }
        
        self._build_ui()
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        self.focus()
    
    def _build_ui(self):
        """Construye la interfaz del diálogo."""
        
        # Frame de contenido
        frame = ctk.CTkScrollableFrame(self)
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Nombre
        ctk.CTkLabel(frame, text="Nombre:", font=get_text_font("normal")).pack(anchor="w", pady=(0, 4))
        self.name_entry = ModernEntry(frame, placeholder="Nombre del perfil")
        self.name_entry.pack(fill="x", pady=(0, 12))
        self.name_entry.insert(0, self.profile_data.get("name", ""))
        
        # Nick
        ctk.CTkLabel(frame, text="Nick:", font=get_text_font("normal")).pack(anchor="w", pady=(0, 4))
        self.nick_entry = ModernEntry(frame, placeholder="Tu nick de Minecraft")
        self.nick_entry.pack(fill="x", pady=(0, 12))
        self.nick_entry.insert(0, self.profile_data.get("nick", ""))
        
        # Versión
        ctk.CTkLabel(frame, text="Versión:", font=get_text_font("normal")).pack(anchor="w", pady=(0, 4))
        mc_path = self.profile_data.get("mc_path", DEFAULT_MINECRAFT_PATH)
        versions = get_all_versions(mc_path)
        self.version_combo = ModernCombobox(frame, values=versions)
        self.version_combo.set(self.profile_data.get("version", "1.21.5"))
        self.version_combo.pack(fill="x", pady=(0, 12))
        
        # RAM
        ctk.CTkLabel(frame, text="RAM:", font=get_text_font("normal")).pack(anchor="w", pady=(0, 4))
        self.ram_combo = ModernCombobox(frame, values=RAM_OPTIONS)
        self.ram_combo.set(self.profile_data.get("ram", "4GB"))
        self.ram_combo.pack(fill="x", pady=(0, 12))
        
        # Loader
        ctk.CTkLabel(frame, text="Loader:", font=get_text_font("normal")).pack(anchor="w", pady=(0, 4))
        self.loader_combo = ModernCombobox(frame, values=list(LABEL_BY_ID.values()))
        self.loader_combo.set(LABEL_BY_ID.get(self.profile_data.get("loader_id", "vanilla"), "Vanilla"))
        self.loader_combo.pack(fill="x", pady=(0, 12))
        
        # HUD Pack
        self.hud_var = ctk.BooleanVar(value=self.profile_data.get("hud_pack", False))
        ctk.CTkCheckBox(
            frame,
            text="Descargar HUD Pack",
            variable=self.hud_var,
            font=get_text_font("normal")
        ).pack(anchor="w", pady=(0, 12))
        
        # Color
        ctk.CTkLabel(frame, text="Color:", font=get_text_font("normal")).pack(anchor="w", pady=(0, 4))
        self.color_combo = ModernCombobox(frame, values=list(ACCENT_COLORS_MAP.keys()))
        current_color = self.profile_data.get("color", DEFAULT_ACCENT)
        for name, color in ACCENT_COLORS_MAP.items():
            if color == current_color:
                self.color_combo.set(name)
                break
        self.color_combo.pack(fill="x", pady=(0, 12))
        
        # Botones
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        ModernButton(btn_frame, text="Guardar", command=self._save).pack(side="left", padx=(0, 8))
        ModernButton(btn_frame, text="Cancelar", command=self.destroy, is_primary=False).pack(side="left")
    
    def _save(self):
        """Guarda los cambios y cierra el diálogo."""
        if not self.name_entry.get():
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        
        if not self.nick_entry.get():
            messagebox.showerror("Error", "El nick no puede estar vacío")
            return
        
        loader_label = self.loader_combo.get()
        loader_id = None
        for id_, label in LABEL_BY_ID.items():
            if label == loader_label:
                loader_id = id_
                break
        
        color_name = self.color_combo.get()
        color = ACCENT_COLORS_MAP.get(color_name, DEFAULT_ACCENT)
        
        self.result = {
            "name": self.name_entry.get(),
            "nick": self.nick_entry.get(),
            "version": self.version_combo.get(),
            "ram": self.ram_combo.get(),
            "mc_path": self.profile_data.get("mc_path", DEFAULT_MINECRAFT_PATH),
            "loader_id": loader_id or "vanilla",
            "loader_version": "Última (recomendada)",
            "hud_pack": self.hud_var.get(),
            "icon": "🟢",
            "color": color,
        }
        
        self.destroy()
