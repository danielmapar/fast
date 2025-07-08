import tkinter as tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk

from app.resource.manager import open_image
from app.ui.styles import AppStyles
from app.ui.tool_frames import FastPFrame, FastQCFrame, HybPiperFrame


class MainWindow:
    def __init__(self, parent):
        self.parent = parent

        # Setup window
        self.setup_window()

        # Setup styling
        self.setup_styling()

        # Setup logo
        self.setup_logo()

        # Create tabs
        self.create_tabs()

        # Center window
        self.center_window()

    def setup_logo(self):
        logo_image = open_image("images/logo.png")
        # Resize logo to fit nicely in the window
        logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo_image)

        logo_label = tk.Label(self.parent, image=self.logo_photo, bg="#FFFFFF")
        logo_label.pack(pady=(10, 5))

    def setup_window(self):
        self.parent.title("Fast App")
        self.parent.configure(bg="#FFFFFF")

    def setup_styling(self):
        self.style = AppStyles.setup_notebook_style()

    def create_tabs(self):
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tool frames
        self.fastqc_frame = FastQCFrame(self.notebook)
        self.fastp_frame = FastPFrame(self.notebook)
        self.hybpiper_frame = HybPiperFrame(self.notebook)

    def center_window(self):
        self.parent.update_idletasks()

        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        window_width = self.parent.winfo_width()
        window_height = self.parent.winfo_height()

        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)

        self.parent.geometry(f"+{position_x}+{position_y}")
