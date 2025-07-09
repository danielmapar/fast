import platform
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List, Optional, override

import psutil

from app.logger.config import Logger, LogType
from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame


class CPUFrame(BaseHardwareMonitoringFrame):

    UPDATE_INTERVAL = 1000
    TOP_PROCESS_COUNT = 10
    MAX_PROCESS_NAME_LENGTH = 20

    def __init__(self, notebook: ttk.Notebook) -> None:
        self.logger = Logger().get_logger(LogType.CPU_MONITORING)

        # UI components
        self.cpu_usage_label: tk.Label
        self.cpu_usage_bar: ttk.Progressbar
        self.per_core_container: tk.Frame
        self.per_core_bars: List[ttk.Progressbar] = []
        self.per_core_labels: List[tk.Label] = []
        self.process_tree: ttk.Treeview

        # Info labels for various metrics
        self.logical_cpus_label: tk.Label
        self.physical_cpus_label: tk.Label
        self.freq_current_label: tk.Label
        self.freq_min_label: tk.Label
        self.freq_max_label: tk.Label

        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        self.is_macos = platform.system() == "Darwin"
        self.UPDATE_INTERVAL = (
            self.UPDATE_INTERVAL * 2 if self.is_windows else self.UPDATE_INTERVAL
        )

        # Initialize baseline CPU measurements for immediate data availability
        self._initialize_cpu_baseline()

        super().__init__(notebook, "CPU")

    def _initialize_cpu_baseline(self) -> None:
        """Initialize CPU baseline measurements so first data collection shows real values."""
        try:
            # Call cpu_percent to establish baseline - this first call will return 0.0 but sets up future calls
            psutil.cpu_percent(interval=None)
            psutil.cpu_percent(interval=None, percpu=True)
            self.logger.debug("CPU baseline measurements initialized")
        except Exception as e:
            self.logger.error(f"Error initializing CPU baseline: {e}")

    @override
    def setup_frame(self) -> None:
        """Setup the CPU monitoring interface."""
        self.main_container = tk.Frame(self.get_scrollable_container())
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._setup_overall_usage()
        self._setup_per_core_usage()
        self._setup_top_processes()
        self._setup_cpu_info()
        self._setup_frequency_info()

        self.start_threaded_updates(self.UPDATE_INTERVAL)

    @override
    def _collect_data_threaded(self) -> Optional[Dict[str, Any]]:
        """Collect all CPU data in background thread."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "per_cpu_percent": psutil.cpu_percent(interval=None, percpu=True),
                "logical_cpus": psutil.cpu_count(logical=True),
                "physical_cpus": psutil.cpu_count(logical=False),
                "cpu_freq": self._safe_get_cpu_freq(),
                "top_processes": self._get_top_processes(),
            }
        except Exception as e:
            self.logger.error(f"Error collecting CPU data: {e}")
            return None

    @override
    def _update_ui_with_data(self, data: Dict[str, Any]) -> None:
        """Update UI with collected data."""
        if not data:
            return

        try:
            self._update_overall_usage(data.get("cpu_percent", 0))
            self._update_cpu_info(data)
            self._update_per_core_usage(data.get("per_cpu_percent", []))
            self._update_frequency(data.get("cpu_freq"))
            self._update_top_processes(data.get("top_processes", []))
        except Exception as e:
            self.logger.error(f"Error updating CPU UI: {e}")

    @override
    def _resize_widgets(self, canvas_width: int) -> None:
        """Handle widget resizing based on canvas width."""
        progress_length = max(150, min(300, canvas_width - 200))

        # Resize main progress bar
        self.cpu_usage_bar.config(length=progress_length)

        # Resize per-core progress bars
        core_length = max(150, progress_length - 100)
        for progress_bar in self.per_core_bars:
            progress_bar.config(length=core_length)

    def _setup_overall_usage(self) -> None:
        """Create overall CPU usage section."""
        frame = self._create_section("Overall CPU Usage")

        # CPU usage display
        usage_row = tk.Frame(frame)
        usage_row.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(usage_row, text="CPU Usage:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.cpu_usage_label = tk.Label(
            usage_row, text="0.0%", font=("Arial", 11, "bold"), fg="blue"
        )
        self.cpu_usage_label.pack(side=tk.RIGHT)

        # Progress bar
        self.cpu_usage_bar = ttk.Progressbar(
            frame, mode="determinate", length=300, maximum=100
        )
        self.cpu_usage_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

    def _setup_per_core_usage(self) -> None:
        """Create per-core CPU usage section."""
        frame = self._create_section("Per-Core CPU Usage")
        self.per_core_container = tk.Frame(frame)
        self.per_core_container.pack(fill=tk.X, padx=10, pady=10)

    def _setup_top_processes(self) -> None:
        """Create top CPU consuming processes section."""
        frame = self._create_section("Top CPU Processes")
        tree_container = tk.Frame(frame)
        tree_container.pack(fill=tk.X, padx=10, pady=10)

        # Process tree with scrollbar
        columns = ("PID", "Name", "CPU%", "Memory%")
        self.process_tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", height=8
        )

        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100, minwidth=50)

        scrollbar = ttk.Scrollbar(
            tree_container, orient="vertical", command=self.process_tree.yview
        )
        self.process_tree.configure(yscrollcommand=scrollbar.set)

        self.process_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _setup_cpu_info(self) -> None:
        """Create CPU information section."""
        frame = self._create_section("CPU Information")
        info_container = tk.Frame(frame)
        info_container.pack(fill=tk.X, padx=10, pady=10)

        self.logical_cpus_label = self._create_info_row(info_container, "Logical CPUs")
        self.physical_cpus_label = self._create_info_row(
            info_container, "Physical Cores"
        )

    def _setup_frequency_info(self) -> None:
        """Create CPU frequency section."""
        frame = self._create_section("CPU Frequency")
        freq_container = tk.Frame(frame)
        freq_container.pack(fill=tk.X, padx=10, pady=10)

        self.freq_current_label = self._create_info_row(
            freq_container, "Current", "0 MHz"
        )
        self.freq_min_label = self._create_info_row(freq_container, "Min", "0 MHz")
        self.freq_max_label = self._create_info_row(freq_container, "Max", "0 MHz")

    def _create_section(self, title: str) -> tk.LabelFrame:
        """Create a labeled section frame."""
        frame = tk.LabelFrame(
            self.main_container, text=title, font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))
        return frame

    def _create_info_row(
        self, parent: tk.Widget, label: str, initial_value: str = "0"
    ) -> tk.Label:
        """Create a label-value row and return the value label."""
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=1)

        tk.Label(row, text=f"{label}:", font=("Arial", 10)).pack(side=tk.LEFT)
        value_label = tk.Label(row, text=initial_value, font=("Arial", 10, "bold"))
        value_label.pack(side=tk.RIGHT)
        return value_label

    def _create_per_core_widgets(self) -> None:
        """Create widgets for per-core CPU usage display."""
        # Clear existing widgets
        for widget in self.per_core_bars + self.per_core_labels:
            widget.destroy()
        self.per_core_bars.clear()
        self.per_core_labels.clear()

        cpu_count = psutil.cpu_count(logical=True)

        for i in range(cpu_count):
            core_frame = tk.Frame(self.per_core_container)
            core_frame.pack(fill=tk.X, pady=2)

            tk.Label(
                core_frame,
                text=f"Core {i + 1}:",
                font=("Arial", 9),
                width=8,
                anchor="w",
            ).pack(side=tk.LEFT)

            progress_bar = ttk.Progressbar(
                core_frame, mode="determinate", length=200, maximum=100
            )
            progress_bar.pack(side=tk.LEFT, padx=(5, 10))

            percent_label = tk.Label(
                core_frame, text="0.0%", font=("Arial", 9), width=6, anchor="e"
            )
            percent_label.pack(side=tk.RIGHT)

            self.per_core_bars.append(progress_bar)
            self.per_core_labels.append(percent_label)

        self.update_scroll_region()

    def _safe_get_cpu_freq(self) -> Optional[Any]:
        """Safely get CPU frequency, returning None if not available."""
        try:
            return psutil.cpu_freq()
        except Exception:
            return None

    def _get_top_processes(self) -> List[Dict]:
        """Get top processes sorted by CPU usage."""
        processes = []
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent"]
            ):
                try:
                    info = proc.info
                    if info and info.get("cpu_percent") is not None:
                        processes.append(info)
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

                # Limit for performance
                if len(processes) > 100:
                    break

        except Exception as e:
            self.logger.error(f"Error getting processes: {e}")

        return sorted(
            processes, key=lambda x: x.get("cpu_percent", 0) or 0, reverse=True
        )

    def _update_overall_usage(self, cpu_percent: float) -> None:
        """Update overall CPU usage display."""
        color = self._get_usage_color(cpu_percent)
        self.cpu_usage_label.config(text=f"{cpu_percent:.1f}%", fg=color)
        self.cpu_usage_bar["value"] = cpu_percent

    def _update_cpu_info(self, data: Dict[str, Any]) -> None:
        """Update CPU information display."""
        self.logical_cpus_label.config(text=str(data.get("logical_cpus", "N/A")))
        physical_cpus = data.get("physical_cpus") or "N/A"
        self.physical_cpus_label.config(text=str(physical_cpus))

    def _update_per_core_usage(self, per_cpu_percent: List[float]) -> None:
        """Update per-core CPU usage display."""
        if not per_cpu_percent:
            return

        # Create widgets if they don't exist
        if not self.per_core_bars:
            self._create_per_core_widgets()

        for i, percent in enumerate(per_cpu_percent):
            if i < len(self.per_core_bars):
                self.per_core_bars[i]["value"] = percent
                self.per_core_labels[i].config(text=f"{percent:.1f}%")

    def _update_frequency(self, cpu_freq: Optional[Any]) -> None:
        """Update CPU frequency display."""
        if cpu_freq:
            self.freq_current_label.config(text=f"{cpu_freq.current:.0f} MHz")
            self.freq_min_label.config(text=f"{cpu_freq.min:.0f} MHz")
            self.freq_max_label.config(text=f"{cpu_freq.max:.0f} MHz")
        else:
            for label in [
                self.freq_current_label,
                self.freq_min_label,
                self.freq_max_label,
            ]:
                label.config(text="N/A")

    def _update_top_processes(self, processes: List[Dict]) -> None:
        """Update top processes display."""
        # Clear and repopulate tree
        self.process_tree.delete(*self.process_tree.get_children())

        for proc in processes[: self.TOP_PROCESS_COUNT]:
            self.process_tree.insert(
                "",
                "end",
                values=(
                    proc.get("pid", "N/A"),
                    (proc.get("name") or "N/A")[: self.MAX_PROCESS_NAME_LENGTH],
                    f"{proc.get('cpu_percent', 0) or 0:.1f}%",
                    f"{proc.get('memory_percent', 0) or 0:.1f}%",
                ),
            )

    def _get_usage_color(self, percentage: float) -> str:
        """Get color based on CPU usage percentage."""
        if percentage > 80:
            return "red"
        elif percentage > 60:
            return "orange"
        else:
            return "green"
