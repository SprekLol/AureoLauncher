import customtkinter as ctk
from ui.main_window import AureoLauncher

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = AureoLauncher()
    app.mainloop()
