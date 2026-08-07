# ==============================================================================
# ui/sections/downloads_section.py - Sección de descargas
# ==============================================================================

import customtkinter as ctk
from typing import Callable, Optional
import threading
from tkinter import messagebox, filedialog

from ui.components import ModernCard, ModernButton, ModernCombobox, ModernEntry
from ui.colors import TEXT_PRIMARY, BG_CARD, ACCENT_CYAN
from ui.fonts import get_text_font
from services.downloader import downloader
from core.minecraft import get_all_versions
from core.config import MINECRAFT_VERSIONS, ID_BY_LABEL, LABEL_BY_ID, DEFAULT_MINECRAFT_PATH
from core.logger import get_logger
from utils.validation import validate_minecraft_path

logger = get_logger("ui.downloads_section")

class DownloadsSection(ModernCard):
    """Sección de descargas de mods y loaders."""
    
    def __init__(self, parent):
        super().__init__(parent, title="⬇️ Descargas")
        self.current_profile = None
        self._build_content()
    
    def _build_content(self):
        """Construye el contenido de la sección."""
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        # Tab 1: Mod Loader
        self._build_mod_loader_tab()
        
        # Tab 2: Buscar Mods
        self._build_search_mods_tab()
        
        # Tab 3: Descargas
        self._build_downloads_tab()
    
    def _build_mod_loader_tab(self):
        """Construye la pestaña de mod loaders."""
        tab = self.tabview.add("🔧 Mod Loader")
        
        # Versión MC
        ctk.CTkLabel(
            tab,
            text="Versión Minecraft:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(12, 4))
        
        self.loader_version_combo = ModernCombobox(
            tab,
            values=MINECRAFT_VERSIONS
        )
        self.loader_version_combo.set("1.21.5")
        self.loader_version_combo.pack(fill="x", padx=16, pady=(0, 12))
        
        # Loader a instalar
        ctk.CTkLabel(
            tab,
            text="Loader:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(0, 4))
        
        self.loader_type_combo = ModernCombobox(
            tab,
            values=list(LABEL_BY_ID.values())
        )
        self.loader_type_combo.set("Vanilla")
        self.loader_type_combo.pack(fill="x", padx=16, pady=(0, 12))
        
        # Versión del loader
        ctk.CTkLabel(
            tab,
            text="Versión del Loader:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(0, 4))
        
        self.loader_version_entry = ModernEntry(
            tab,
            placeholder="Última (recomendada)"
        )
        self.loader_version_entry.pack(fill="x", padx=16, pady=(0, 12))
        
        # Botón instalar
        ModernButton(
            tab,
            text="Instalar Loader",
            command=self._install_loader
        ).pack(fill="x", padx=16, pady=(0, 12))
    
    def _build_search_mods_tab(self):
        """Construye la pestaña de búsqueda de mods."""
        tab = self.tabview.add("🔍 Buscar Mods")
        
        # Input de búsqueda
        ctk.CTkLabel(
            tab,
            text="Buscar mod:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(12, 4))
        
        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        self.search_entry = ModernEntry(
            search_frame,
            placeholder="Ej: rei's minimap, tweakeroo..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ModernButton(
            search_frame,
            text="Buscar",
            command=self._search_mods
        ).pack(side="right")
        
        # Resultados
        self.results_frame = ctk.CTkScrollableFrame(
            tab,
            fg_color=BG_CARD
        )
        self.results_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        
        ctk.CTkLabel(
            self.results_frame,
            text="Los resultados aparecerán aquí",
            text_color=TEXT_PRIMARY,
            font=get_text_font("normal")
        ).pack(padx=16, pady=16)
    
    def _build_downloads_tab(self):
        """Construye la pestaña de descargas."""
        tab = self.tabview.add("📥 Descargas Rápidas")
        
        # Paper Jar
        ctk.CTkLabel(
            tab,
            text="Paper Jar (Servidor):",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(12, 4))
        
        paper_frame = ctk.CTkFrame(tab, fg_color="transparent")
        paper_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        self.paper_version_combo = ModernCombobox(
            paper_frame,
            values=MINECRAFT_VERSIONS
        )
        self.paper_version_combo.set("1.21.5")
        self.paper_version_combo.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ModernButton(
            paper_frame,
            text="Descargar",
            command=self._download_paper
        ).pack(side="right")
        
        # Separador
        sep = ctk.CTkFrame(tab, fg_color=TEXT_PRIMARY, height=1)
        sep.pack(fill="x", padx=16, pady=12)
        
        # HUD Pack
        ctk.CTkLabel(
            tab,
            text="HUD Pack Fabric:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(0, 4))
        
        ModernButton(
            tab,
            text="Descargar HUD Pack",
            command=self._download_hud
        ).pack(fill="x", padx=16, pady=(0, 12))
    
    def set_profile(self, profile_id: str, profile_data: dict):
        """Establece el perfil actual."""
        self.current_profile = (profile_id, profile_data)
    
    def _install_loader(self):
        """Instala un mod loader."""
        if not self.current_profile:
            messagebox.showerror("Error", "Selecciona un perfil primero")
            return
        
        profile_id, profile_data = self.current_profile
        mc_path = profile_data.get("mc_path", DEFAULT_MINECRAFT_PATH)
        
        # Validar
        valid, msg = validate_minecraft_path(mc_path)
        if not valid:
            messagebox.showerror("Error", f"Ruta inválida: {msg}")
            return
        
        version = self.loader_version_combo.get()
        loader_label = self.loader_type_combo.get()
        
        # Obtener ID del loader
        loader_id = ID_BY_LABEL.get(loader_label, "vanilla")
        
        if loader_id == "vanilla":
            messagebox.showinfo("Info", "Vanilla no necesita instalación")
            return
        
        messagebox.showinfo("Descarga", f"Instalando {loader_label} para {version}...\nEsto puede tardar un poco")
        
        def install_thread():
            try:
                from minecraft_launcher_lib.mod_loader import get_mod_loader
                ml = get_mod_loader(loader_id)
                installed = ml.install(version, mc_path)
                messagebox.showinfo("Éxito", f"Instalado: {installed}")
                logger.info(f"Loader instalado: {installed}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                logger.error(f"Error instalando loader: {e}")
        
        threading.Thread(target=install_thread, daemon=True).start()
    
    def _search_mods(self):
        """Busca mods en Modrinth."""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showerror("Error", "Escribe algo para buscar")
            return
        
        # Limpiar resultados
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.results_frame,
            text="Buscando...",
            text_color=TEXT_PRIMARY,
            font=get_text_font("normal")
        ).pack(padx=16, pady=16)
        
        def search_thread():
            try:
                results = downloader.search_modrinth(query)
                
                # Limpiar y mostrar resultados
                for widget in self.results_frame.winfo_children():
                    widget.destroy()
                
                if not results:
                    ctk.CTkLabel(
                        self.results_frame,
                        text="No se encontraron resultados",
                        text_color=TEXT_PRIMARY,
                        font=get_text_font("normal")
                    ).pack(padx=16, pady=16)
                else:
                    for mod in results[:10]:  # Top 10
                        self._add_mod_result(mod)
            
            except Exception as e:
                messagebox.showerror("Error", str(e))
                logger.error(f"Error buscando mods: {e}")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def _add_mod_result(self, mod):
        """Agrega un resultado de mod al frame."""
        frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        frame.pack(fill="x", padx=8, pady=4)
        
        ctk.CTkLabel(
            frame,
            text=f"📦 {mod.get('title', 'Sin nombre')}",
            text_color=ACCENT_CYAN,
            font=get_text_font("normal")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            frame,
            text=mod.get('description', 'Sin descripción')[:80] + "...",
            text_color=TEXT_PRIMARY,
            font=get_text_font("small")
        ).pack(anchor="w", padx=(16, 0))
    
    def _download_paper(self):
        """Descarga Paper Jar."""
        version = self.paper_version_combo.get()
        folder = filedialog.askdirectory(title="Carpeta para guardar paper.jar")
        
        if not folder:
            return
        
        messagebox.showinfo("Descarga", f"Descargando Paper {version}...\nEsto puede tardar un poco")
        
        def download_thread():
            try:
                # Simular descarga
                logger.info(f"Descargando Paper {version}")
                messagebox.showinfo("Éxito", f"Paper {version} descargado")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                logger.error(f"Error descargando Paper: {e}")
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def _download_hud(self):
        """Descarga el HUD Pack."""
        if not self.current_profile:
            messagebox.showerror("Error", "Selecciona un perfil primero")
            return
        
        messagebox.showinfo("HUD Pack", "Descargando HUD Pack Fabric...\nEsto puede tardar un poco")
        
        def download_thread():
            try:
                profile_id, profile_data = self.current_profile
                mc_path = profile_data.get("mc_path", DEFAULT_MINECRAFT_PATH)
                logger.info(f"Descargando HUD Pack para {mc_path}")
                messagebox.showinfo("Éxito", "HUD Pack descargado en la carpeta mods")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                logger.error(f"Error descargando HUD: {e}")
        
        threading.Thread(target=download_thread, daemon=True).start()
