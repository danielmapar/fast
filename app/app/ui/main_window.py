import tkinter as tk
import tkinter.ttk as ttk
from typing import Optional

from app.ui.frames.base_frame import BaseFrame
from app.ui.frames.hardware_monitoring.cpu import CPUFrame
from app.ui.frames.hardware_monitoring.gpu import GPUFrame
from app.ui.frames.hardware_monitoring.harddrive import HardDriveFrame
from app.ui.frames.hardware_monitoring.memory import MemoryFrame
from app.ui.frames.tools.fastp_frame import FastPFrame
from app.ui.frames.tools.fastqc_frame import FastQCFrame
from app.ui.frames.tools.hybpiper_frame import HybPiperFrame
from app.ui.utils.utils import WindowUtils


class MainWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self._parent = parent

        # Tools UI elements
        self._tools_notebook: Optional[ttk.Notebook] = None
        # self._fastqc_frame: Optional[BaseFrame] = None
        # self._fastp_frame: Optional[BaseFrame] = None
        # self._hybpiper_frame: Optional[BaseFrame] = None

        # Hardware monitoring UI elements
        self._hardware_monitoring_window: Optional[tk.Toplevel] = None
        self._hardware_monitoring_notebook: Optional[ttk.Notebook] = None
        self._cpu_frame: Optional[BaseFrame] = None
        self._memory_frame: Optional[BaseFrame] = None
        self._gpu_frame: Optional[BaseFrame] = None
        self._hard_drive_frame: Optional[BaseFrame] = None

        # Setup window
        self._setup_window()

    def _setup_window(self) -> None:
        self._parent.title("Fast App")
        self._parent.configure(bg="#FFFFFF")

        WindowUtils.setup_logo(self._parent)

        self._create_tools_tabs()
        self._create_hardware_monitoring_button()

        WindowUtils.center_window(
            self._parent, width_percentage=1.4, height_percentage=1
        )

    def _create_tools_tabs(self) -> None:
        self._tools_notebook = ttk.Notebook(self._parent)
        self._tools_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tool frames
        FastQCFrame(self._tools_notebook)
        FastPFrame(self._tools_notebook)
        HybPiperFrame(self._tools_notebook)

    def _create_hardware_monitoring_button(self) -> None:
        """Create a button to open hardware monitoring in a separate window"""
        button_frame = tk.Frame(self._parent, bg="#FFFFFF")
        button_frame.pack(fill="x", padx=10, pady=5)

        hardware_button = tk.Button(
            button_frame,
            text="⚙ Open Hardware Monitoring",
            command=self._open_hardware_monitoring_window,
            bg="#1e3a8a",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
        )
        hardware_button.pack(side="right")

    def _open_hardware_monitoring_window(self) -> None:
        """Open hardware monitoring in a separate window"""
        # If window already exists, just bring it to front
        if (
            self._hardware_monitoring_window
            and self._hardware_monitoring_window.winfo_exists()
        ):
            self._hardware_monitoring_window.lift()
            self._hardware_monitoring_window.focus_force()
            return

        # Create new hardware monitoring window
        self._hardware_monitoring_window = tk.Toplevel(self._parent)
        self._hardware_monitoring_window.title("Fast App - Hardware Monitoring")
        self._hardware_monitoring_window.configure(bg="#FFFFFF")

        # Set window icon (same as main window if available)
        WindowUtils.setup_logo(self._hardware_monitoring_window)

        # Create notebook for hardware monitoring tabs
        self._hardware_monitoring_notebook = ttk.Notebook(
            self._hardware_monitoring_window
        )
        self._hardware_monitoring_notebook.pack(
            fill="both", expand=True, padx=10, pady=10
        )

        # Create hardware monitoring frames
        self._cpu_frame = CPUFrame(self._hardware_monitoring_notebook)
        self._memory_frame = MemoryFrame(self._hardware_monitoring_notebook)
        self._hard_drive_frame = HardDriveFrame(self._hardware_monitoring_notebook)
        self._gpu_frame = GPUFrame(self._hardware_monitoring_notebook)

        # Center the hardware monitoring window
        WindowUtils.center_window(self._hardware_monitoring_window)

        # Handle window closing to clean up resources
        self._hardware_monitoring_window.protocol(
            "WM_DELETE_WINDOW", self._on_hardware_window_close
        )

    def _on_hardware_window_close(self) -> None:
        """Clean up when hardware monitoring window is closed"""
        if self._cpu_frame:
            self._cpu_frame.stop_threaded_updates()
        if self._memory_frame:
            self._memory_frame.stop_threaded_updates()
        if self._gpu_frame:
            self._gpu_frame.stop_threaded_updates()
        if self._hard_drive_frame:
            self._hard_drive_frame.stop_threaded_updates()

        if self._hardware_monitoring_window:
            self._hardware_monitoring_window.destroy()
            self._hardware_monitoring_window = None
            self._hardware_monitoring_notebook = None
            self._cpu_frame = None
            self._memory_frame = None
            self._gpu_frame = None
            self._hard_drive_frame = None
