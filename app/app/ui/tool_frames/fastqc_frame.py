import tkinter as tk
import tkinter.ttk as ttk

from app.ui.tool_frames.base_frame import BaseToolFrame


class FastQCFrame(BaseToolFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        super().__init__(notebook, "FastQC")

    def setup_frame(self) -> None:
        label = tk.Label(self._frame, text="FastQC", font=("Arial", 16))
        label.pack(expand=True)
        # Add FastQC-specific widgets here
