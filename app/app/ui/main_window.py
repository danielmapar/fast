import tkinter as tk
import tkinter.ttk as ttk
from typing import Optional

from app.ui.tool_frames import FastPFrame, FastQCFrame, HybPiperFrame
from app.ui.tool_frames.base_frame import BaseToolFrame
from app.ui.utils import WindowUtils


class MainWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self._parent = parent

        # UI elements
        self._notebook: Optional[ttk.Notebook] = None
        self._fastqc_frame: Optional[BaseToolFrame] = None
        self._fastp_frame: Optional[BaseToolFrame] = None
        self._hybpiper_frame: Optional[BaseToolFrame] = None

        # Setup window
        self._setup_window()

        WindowUtils.setup_logo(self._parent)

        self._create_tabs()

        WindowUtils.center_window(self._parent)

    def _setup_window(self) -> None:
        self._parent.title("Fast App")
        self._parent.configure(bg="#FFFFFF")

    def _create_tabs(self) -> None:
        self._notebook = ttk.Notebook(self._parent)
        self._notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tool frames
        self._fastqc_frame = FastQCFrame(self._notebook)
        self._fastp_frame = FastPFrame(self._notebook)
        self._hybpiper_frame = HybPiperFrame(self._notebook)
