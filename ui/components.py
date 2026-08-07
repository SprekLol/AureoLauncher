import customtkinter as ctk
from ui.colors import *
from ui.fonts import get_text_font

class ModernFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        corner_radius = kwargs.pop("corner_radius", 8)
        super().__init__(
            parent,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=corner_radius,
            **kwargs
        )

class ModernScrollFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs
        )

class ModernButton(ctk.CTkButton):
    def __init__(self, parent, text="", command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            font=get_text_font("normal"),
            corner_radius=6,
            height=35,
            fg_color=kwargs.pop("fg_color", BG_CARD),
            hover_color=kwargs.pop("hover_color", BG_CARD_HOVER),
            text_color=kwargs.pop("text_color", TEXT_PRIMARY),
            **kwargs
        )

class ModernEntry(ctk.CTkEntry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(
            parent,
            placeholder_text=placeholder,
            fg_color=BG_INPUT,
            border_color=BG_BORDER,
            border_width=1,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            font=get_text_font("normal"),
            corner_radius=6,
            height=35,
            **kwargs
        )

class ModernComboBox(ctk.CTkComboBox):
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(
            parent,
            values=values or [],
            fg_color=BG_INPUT,
            border_color=BG_BORDER,
            button_color=ACCENT_MAIN,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_PRIMARY,
            font=get_text_font("normal"),
            corner_radius=6,
            height=35,
            **kwargs
        )
