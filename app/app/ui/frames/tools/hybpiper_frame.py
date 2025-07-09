import tkinter as tk
import tkinter.ttk as ttk

from app.ui.frames.base_frame import BaseFrame


class HybPiperFrame(BaseFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        super().__init__(notebook, "HybPiper")

    def setup_frame(self) -> None:
        label = tk.Label(self._frame, text="HybPiper", font=("Arial", 16))
        label.pack(expand=True)
        # Add HybPiper-specific widgets here
