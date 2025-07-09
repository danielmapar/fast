import tkinter as tk
import tkinter.ttk as ttk

from app.ui.frames.base_frame import BaseFrame


class FastPFrame(BaseFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        super().__init__(notebook, "FastP")

    def setup_frame(self) -> None:
        label = tk.Label(self._frame, text="FastP", font=("Arial", 16))
        label.pack(expand=True)
        # Add FastP-specific widgets here
