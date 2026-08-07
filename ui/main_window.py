import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from ui.colors import *
from ui.fonts import get_text_font
from ui.data import (
    load_profiles, save_profiles, load_settings, save_settings,
    MC_VERSIONS, LOADERS, RAM_OPTIONS, MODS_POPULAR
)
from ui.components import (
    ModernButton, ModernEntry, ModernComboBox, 
    ModernFrame, ModernScrollFrame
)

class AureoLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Aureo Launcher")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        self.configure(fg_color=BG_PRIMARY)
        
        self.profiles = load_profiles()
        self.settings = load_settings()
        self.current_profile = "default"
        self.search_results = []
        
        # Layout principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Contenido
        self.content_frame = ctk.CTkFrame(main_container, fg_color=BG_PRIMARY)
        self.content_frame.pack(side="left", fill="both", expand=True)
        
        # Header
        self.create_header()
        
        # Secciones
        self.sections_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.sections_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mostrar launcher por defecto
        self.show_launcher()
    
    def create_sidebar(self, parent):
        sidebar = ModernFrame(parent, corner_radius=0)
        sidebar.configure(width=200, fg_color=BG_SIDEBAR)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo
        title = ctk.CTkLabel(
            sidebar,
            text="AUREO",
            font=("Segoe UI", 16, "bold"),
            text_color=ACCENT_MAIN
        )
        title.pack(pady=20)
        
        # Navegación
        nav_items = [
            ("Lanzador", self.show_launcher),
            ("Perfiles", self.show_profiles),
            ("Descargas", self.show_downloads),
            ("Configuración", self.show_settings),
        ]
        
        self.nav_buttons = {}
        
        for label, command in nav_items:
            btn = ModernButton(
                sidebar,
                text=label,
                command=command,
                width=180
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[label] = btn
        
        # Highlight inicial
        self.nav_buttons["Lanzador"].configure(fg_color=ACCENT_MAIN, text_color="white")
    
    def create_header(self):
        header = ModernFrame(self.content_frame, corner_radius=8)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.configure(height=50)
        
        self.header_label = ctk.CTkLabel(
            header,
            text="Lanzador",
            font=get_text_font("title"),
            text_color=TEXT_PRIMARY
        )
        self.header_label.pack(pady=15)
    
    def highlight_nav(self, name):
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=ACCENT_MAIN, text_color="white")
            else:
                btn.configure(fg_color=BG_CARD, text_color=TEXT_PRIMARY)
    
    def clear_section(self):
        for widget in self.sections_container.winfo_children():
            widget.destroy()
    
    def show_launcher(self):
        self.clear_section()
        self.header_label.configure(text="Lanzador")
        self.highlight_nav("Lanzador")
        
        scroll = ModernScrollFrame(self.sections_container)
        scroll.pack(fill="both", expand=True)
        
        # Perfil actual
        self.create_section_title(scroll, "Perfil Actual")
        profile_info = ModernFrame(scroll)
        profile_info.pack(fill="x", pady=(0, 15))
        
        self.profile_label = ctk.CTkLabel(
            profile_info,
            text=f"Perfil: {self.profiles[self.current_profile]['name']}",
            font=get_text_font("section_title"),
            text_color=ACCENT_MAIN
        )
        self.profile_label.pack(anchor="w", padx=15, pady=10)
        
        # Información de versión
        profile = self.profiles[self.current_profile]
        info_text = f"Versión: {profile['version']} | Loader: {profile['loader']} | RAM: {profile['ram']}"
        info_label = ctk.CTkLabel(
            profile_info,
            text=info_text,
            font=get_text_font("small"),
            text_color=TEXT_SECONDARY
        )
        info_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Selector de versión
        self.create_section_title(scroll, "Versión de Minecraft")
        combo_frame = ModernFrame(scroll)
        combo_frame.pack(fill="x", pady=(0, 15))
        
        self.version_combo = ModernComboBox(combo_frame, MC_VERSIONS, width=200)
        self.version_combo.set(profile['version'])
        self.version_combo.pack(fill="x", padx=15, pady=10)
        
        # Loader
        self.create_section_title(scroll, "Modloader")
        loader_frame = ModernFrame(scroll)
        loader_frame.pack(fill="x", pady=(0, 15))
        
        self.loader_combo = ModernComboBox(loader_frame, LOADERS, width=200)
        self.loader_combo.set(profile['loader'])
        self.loader_combo.pack(fill="x", padx=15, pady=10)
        
        # RAM
        self.create_section_title(scroll, "Memoria Asignada")
        ram_frame = ModernFrame(scroll)
        ram_frame.pack(fill="x", pady=(0, 15))
        
        self.ram_combo = ModernComboBox(ram_frame, RAM_OPTIONS, width=200)
        self.ram_combo.set(profile['ram'])
        self.ram_combo.pack(fill="x", padx=15, pady=10)
        
        # Botones finales
        button_frame = ctk.CTkFrame(self.sections_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0), padx=20)
        
        play_btn = ModernButton(
            button_frame,
            text="JUGAR",
            command=self.play_game,
            fg_color=ACCENT_SUCCESS,
            width=150
        )
        play_btn.pack(side="left", padx=(0, 10))
        
        save_btn = ModernButton(
            button_frame,
            text="Guardar Cambios",
            command=self.save_launcher_changes,
            width=150
        )
        save_btn.pack(side="left")
    
    def show_profiles(self):
        self.clear_section()
        self.header_label.configure(text="Perfiles")
        self.highlight_nav("Perfiles")
        
        scroll = ModernScrollFrame(self.sections_container)
        scroll.pack(fill="both", expand=True)
        
        # Crear nuevo perfil
        self.create_section_title(scroll, "Crear Nuevo Perfil")
        new_profile_frame = ModernFrame(scroll)
        new_profile_frame.pack(fill="x", pady=(0, 20))
        
        name_label = ctk.CTkLabel(
            new_profile_frame,
            text="Nombre:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        )
        name_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.new_profile_entry = ModernEntry(new_profile_frame, placeholder="Mi Perfil")
        self.new_profile_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        version_label = ctk.CTkLabel(
            new_profile_frame,
            text="Versión:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        )
        version_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.new_version_combo = ModernComboBox(new_profile_frame, MC_VERSIONS)
        self.new_version_combo.set("1.20.1")
        self.new_version_combo.pack(fill="x", padx=15, pady=(0, 10))
        
        loader_label = ctk.CTkLabel(
            new_profile_frame,
            text="Loader:",
            font=get_text_font("normal"),
            text_color=TEXT_PRIMARY
        )
        loader_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.new_loader_combo = ModernComboBox(new_profile_frame, LOADERS)
        self.new_loader_combo.set("Fabric")
        self.new_loader_combo.pack(fill="x", padx=15, pady=(0, 10))
        
        create_btn = ModernButton(
            new_profile_frame,
            text="Crear Perfil",
            command=self.create_profile,
            width=150
        )
        create_btn.pack(padx=15, pady=(10, 0))
        
        # Lista de perfiles existentes
        self.create_section_title(scroll, "Perfiles Existentes")
        
        for profile_id, profile_data in self.profiles.items():
            profile_card = ModernFrame(scroll)
            profile_card.pack(fill="x", pady=8)
            
            name = ctk.CTkLabel(
                profile_card,
                text=profile_data['name'],
                font=get_text_font("section_title"),
                text_color=TEXT_PRIMARY
            )
            name.pack(anchor="w", padx=15, pady=(10, 5))
            
            info = ctk.CTkLabel(
                profile_card,
                text=f"{profile_data['version']} - {profile_data['loader']}",
                font=get_text_font("small"),
                text_color=TEXT_SECONDARY
            )
            info.pack(anchor="w", padx=15, pady=(0, 10))
            
            btn_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            select_btn = ModernButton(
                btn_frame,
                text="Seleccionar",
                command=lambda pid=profile_id: self.select_profile(pid),
                width=100
            )
            select_btn.pack(side="left", padx=(0, 5))
            
            delete_btn = ModernButton(
                btn_frame,
                text="Eliminar",
                command=lambda pid=profile_id: self.delete_profile(pid),
                fg_color=ACCENT_ERROR,
                width=100
            )
            delete_btn.pack(side="left")
    
    def show_downloads(self):
        self.clear_section()
        self.header_label.configure(text="Descargas y Mods")
        self.highlight_nav("Descargas")
        
        scroll = ModernScrollFrame(self.sections_container)
        scroll.pack(fill="both", expand=True)
        
        # Búsqueda
        self.create_section_title(scroll, "Buscar Mods")
        search_frame = ModernFrame(scroll)
        search_frame.pack(fill="x", pady=(0, 15))
        
        self.search_entry = ModernEntry(search_frame, placeholder="Buscar mods, shaders, texturas...")
        self.search_entry.pack(fill="x", padx=15, pady=(10, 10))
        
        search_btn = ModernButton(
            search_frame,
            text="Buscar",
            command=self.search_mods,
            width=100
        )
        search_btn.pack(padx=15, pady=(0, 10))
        
        # Resultados
        self.create_section_title(scroll, "Mods Populares")
        
        self.mods_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.mods_container.pack(fill="both", expand=True)
        
        for mod in MODS_POPULAR:
            self.create_mod_item(self.mods_container, mod)
    
    def show_settings(self):
        self.clear_section()
        self.header_label.configure(text="Configuración")
        self.highlight_nav("Configuración")
        
        scroll = ModernScrollFrame(self.sections_container)
        scroll.pack(fill="both", expand=True)
        
        # Tema
        self.create_section_title(scroll, "Tema")
        theme_frame = ModernFrame(scroll)
        theme_frame.pack(fill="x", pady=(0, 15))
        
        self.theme_combo = ModernComboBox(
            theme_frame,
            ["light", "dark", "oled"],
            width=150
        )
        self.theme_combo.set(self.settings['theme'])
        self.theme_combo.pack(fill="x", padx=15, pady=10)
        
        # Ruta Minecraft
        self.create_section_title(scroll, "Ruta Minecraft")
        path_frame = ModernFrame(scroll)
        path_frame.pack(fill="x", pady=(0, 15))
        
        self.path_entry = ModernEntry(
            path_frame,
            placeholder="Selecciona la ruta de .minecraft"
        )
        self.path_entry.insert(0, self.settings['minecraft_path'])
        self.path_entry.pack(fill="x", padx=15, pady=(10, 10))
        
        browse_btn = ModernButton(
            path_frame,
            text="Examinar",
            command=self.browse_path,
            width=100
        )
        browse_btn.pack(padx=15, pady=(0, 10))
        
        # Guardar
        save_btn = ModernButton(
            path_frame,
            text="Guardar Configuración",
            command=self.save_settings_data,
            width=150
        )
        save_btn.pack(padx=15, pady=(10, 0))
    
    def create_section_title(self, parent, text):
        title = ctk.CTkLabel(
            parent,
            text=text,
            font=get_text_font("section_title"),
            text_color=TEXT_PRIMARY
        )
        title.pack(anchor="w", pady=(20, 10))
    
    def create_mod_item(self, parent, mod):
        item = ModernFrame(parent)
        item.pack(fill="x", pady=8)
        
        name = ctk.CTkLabel(
            item,
            text=mod['name'],
            font=get_text_font("normal"),
            text_color=ACCENT_MAIN
        )
        name.pack(anchor="w", padx=15, pady=(10, 5))
        
        desc = ctk.CTkLabel(
            item,
            text=mod['description'],
            font=get_text_font("small"),
            text_color=TEXT_SECONDARY,
            wraplength=500
        )
        desc.pack(anchor="w", padx=15, pady=(0, 5))
        
        downloads = ctk.CTkLabel(
            item,
            text=f"Descargas: {mod['downloads']}",
            font=get_text_font("small"),
            text_color=TEXT_MUTED
        )
        downloads.pack(anchor="w", padx=15, pady=(0, 10))
        
        install_btn = ModernButton(
            item,
            text="Instalar",
            command=lambda: self.install_mod(mod['name']),
            width=100,
            fg_color=ACCENT_SUCCESS
        )
        install_btn.pack(padx=15, pady=(0, 10))
    
    # Funciones de perfil
    def create_profile(self):
        name = self.new_profile_entry.get()
        if not name:
            messagebox.showerror("Error", "Ingresa un nombre para el perfil")
            return
        
        profile_id = name.lower().replace(" ", "_")
        self.profiles[profile_id] = {
            "name": name,
            "version": self.new_version_combo.get(),
            "loader": self.new_loader_combo.get(),
            "ram": "4GB",
        }
        save_profiles(self.profiles)
        messagebox.showinfo("Éxito", f"Perfil '{name}' creado correctamente")
        self.show_profiles()
    
    def select_profile(self, profile_id):
        self.current_profile = profile_id
        messagebox.showinfo("Perfil", f"Perfil '{self.profiles[profile_id]['name']}' seleccionado")
        self.show_launcher()
    
    def delete_profile(self, profile_id):
        if profile_id == "default":
            messagebox.showerror("Error", "No puedes eliminar el perfil por defecto")
            return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar este perfil?"):
            del self.profiles[profile_id]
            save_profiles(self.profiles)
            self.show_profiles()
    
    def save_launcher_changes(self):
        profile = self.profiles[self.current_profile]
        profile['version'] = self.version_combo.get()
        profile['loader'] = self.loader_combo.get()
        profile['ram'] = self.ram_combo.get()
        save_profiles(self.profiles)
        messagebox.showinfo("Éxito", "Cambios guardados correctamente")
    
    def search_mods(self):
        query = self.search_entry.get().lower()
        self.search_results = [m for m in MODS_POPULAR if query in m['name'].lower()]
        
        for widget in self.mods_container.winfo_children():
            widget.destroy()
        
        if self.search_results:
            for mod in self.search_results:
                self.create_mod_item(self.mods_container, mod)
        else:
            no_results = ctk.CTkLabel(
                self.mods_container,
                text="No se encontraron resultados",
                font=get_text_font("normal"),
                text_color=TEXT_MUTED
            )
            no_results.pack(pady=20)
    
    def install_mod(self, mod_name):
        messagebox.showinfo("Instalación", f"Instalando {mod_name}...")
    
    def browse_path(self):
        path = filedialog.askdirectory(title="Selecciona la ruta de .minecraft")
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
    
    def save_settings_data(self):
        self.settings['theme'] = self.theme_combo.get()
        self.settings['minecraft_path'] = self.path_entry.get()
        save_settings(self.settings)
        messagebox.showinfo("Éxito", "Configuración guardada")
    
    def play_game(self):
        profile = self.profiles[self.current_profile]
        messagebox.showinfo(
            "Iniciando",
            f"Iniciando {profile['name']} con {profile['version']} {profile['loader']}"
        )

if __name__ == "__main__":
    app = AureoLauncher()
    app.mainloop()
