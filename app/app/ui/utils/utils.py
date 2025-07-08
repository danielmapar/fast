import tkinter as tk
from typing import Union

from PIL import Image, ImageTk

from app.resource.manager import ResourceManager


class WindowUtils:
    @staticmethod
    def setup_logo(window: Union[tk.Tk, tk.Toplevel]) -> None:
        logo_image = ResourceManager.open_image("images/logo.png")
        # Resize logo to fit nicely in the window
        logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(window, image=logo_photo, bg="#FFFFFF")
        logo_label.pack(pady=(10, 5))

        # CRITICAL: Keep a reference to prevent garbage collection
        logo_label.image = logo_photo  # type: ignore

    @staticmethod
    def center_window(window: Union[tk.Tk, tk.Toplevel]) -> None:
        window.update_idletasks()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window_width = window.winfo_width()
        window_height = window.winfo_height()

        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)

        window.geometry(f"+{position_x}+{position_y}")

        # Bring window to front
        window.lift()
        window.focus_force()
