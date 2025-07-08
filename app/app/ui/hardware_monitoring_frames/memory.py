import tkinter as tk
import tkinter.ttk as ttk

from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame


class MemoryFrame(BaseHardwareMonitoringFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        super().__init__(notebook, "Memory")

    def setup_frame(self) -> None:
        label = tk.Label(self._frame, text="Memory", font=("Arial", 16))
        label.pack(expand=True)
        # Add Memory-specific widgets here
