import tkinter as tk
import tkinter.ttk as ttk
from typing import Optional

from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame
from app.ui.hardware_monitoring_frames.cpu import CPUFrame
from app.ui.hardware_monitoring_frames.gpu import GPUFrame
from app.ui.hardware_monitoring_frames.harddrive import HardDriveFrame
from app.ui.hardware_monitoring_frames.memory import MemoryFrame
from app.ui.tool_frames import FastPFrame, FastQCFrame, HybPiperFrame
from app.ui.tool_frames.base_frame import BaseToolFrame
from app.ui.utils.utils import WindowUtils


class MainWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self._parent = parent

        # Tools UI elements
        self._tools_notebook: Optional[ttk.Notebook] = None
        self._fastqc_frame: Optional[BaseToolFrame] = None
        self._fastp_frame: Optional[BaseToolFrame] = None
        self._hybpiper_frame: Optional[BaseToolFrame] = None

        # Hardware monitoring UI elements
        self._hardware_monitoring_notebook: Optional[ttk.Notebook] = None
        self._cpu_frame: Optional[BaseHardwareMonitoringFrame] = None
        self._memory_frame: Optional[BaseHardwareMonitoringFrame] = None
        self._gpu_frame: Optional[BaseHardwareMonitoringFrame] = None
        self._hard_drive_frame: Optional[BaseHardwareMonitoringFrame] = None

        # Setup window
        self._setup_window()

        WindowUtils.setup_logo(self._parent)

        self._create_tools_tabs()
        self._create_hardware_monitoring_tabs()

        WindowUtils.center_window(self._parent)

    def _setup_window(self) -> None:
        self._parent.title("Fast App")
        self._parent.configure(bg="#FFFFFF")

    def _create_tools_tabs(self) -> None:
        self._tools_notebook = ttk.Notebook(self._parent)
        self._tools_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tool frames
        self._fastqc_frame = FastQCFrame(self._tools_notebook)
        self._fastp_frame = FastPFrame(self._tools_notebook)
        self._hybpiper_frame = HybPiperFrame(self._tools_notebook)

    def _create_hardware_monitoring_tabs(self) -> None:
        self._hardware_monitoring_notebook = ttk.Notebook(self._parent)
        self._hardware_monitoring_notebook.pack(
            fill="both", expand=True, padx=10, pady=10
        )

        # Create hardware monitoring frames
        self._cpu_frame = CPUFrame(self._hardware_monitoring_notebook)
        self._memory_frame = MemoryFrame(self._hardware_monitoring_notebook)
        self._hard_drive_frame = HardDriveFrame(self._hardware_monitoring_notebook)
        self._gpu_frame = GPUFrame(self._hardware_monitoring_notebook)
