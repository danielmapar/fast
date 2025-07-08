import tkinter as tk
import tkinter.ttk as ttk

from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame


class GPUFrame(BaseHardwareMonitoringFrame):
    def __init__(self, notebook: ttk.Notebook) -> None:
        super().__init__(notebook, "GPU")

    def setup_frame(self) -> None:
        label = tk.Label(self._frame, text="GPU", font=("Arial", 16))
        label.pack(expand=True)
        # Add GPU-specific widgets here
