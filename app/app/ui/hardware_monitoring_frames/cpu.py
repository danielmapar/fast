import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List

import psutil

from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame


class CPUFrame(BaseHardwareMonitoringFrame):
    # Constants
    UPDATE_INTERVAL = 1000  # milliseconds
    PROGRESS_BAR_LENGTH = 200
    TREE_HEIGHT = 8
    MAX_PROCESS_NAME_LENGTH = 20
    TOP_PROCESS_COUNT = 10

    def __init__(self, notebook: ttk.Notebook) -> None:
        self._update_interval = self.UPDATE_INTERVAL
        self._widgets: Dict[str, Any] = {}
        self._per_core_bars: List[ttk.Progressbar] = []
        self._per_core_labels: List[tk.Label] = []
        self.main_container: tk.Frame = tk.Frame()

        super().__init__(notebook, "CPU")
        self._start_updates()

    def setup_frame(self) -> None:
        """Setup the CPU monitoring interface with multiple statistics"""
        # Get the scrollable container from the base class
        self.main_container = tk.Frame(self.get_scrollable_container())
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        # title_label = tk.Label(
        #     self.main_container, text="CPU Monitoring", font=("Arial", 16, "bold")
        # )
        # title_label.pack(pady=(0, 15))

        # Create sections
        self._create_overall_usage_section()
        self._create_per_core_section()
        self._create_top_processes_section()
        self._create_cpu_times_section()
        self._create_cpu_info_section()
        self._create_frequency_section()
        self._create_cpu_stats_section()

        # Initial update
        self._update_cpu_stats()

    def _resize_widgets(self, canvas_width: int) -> None:
        """Override base class method to handle CPU-specific widget resizing"""
        # Calculate progress bar length based on canvas width
        progress_length = max(150, min(300, canvas_width - 200))

        # Resize main progress bar
        if "cpu_usage_bar" in self._widgets:
            self._widgets["cpu_usage_bar"].config(length=progress_length)

        # Resize per-core progress bars
        core_length = max(150, progress_length - 100)
        for progress_bar in self._per_core_bars:
            progress_bar.config(length=core_length)

    def _create_overall_usage_section(self) -> None:
        """Create overall CPU usage section"""
        frame = tk.LabelFrame(
            self.main_container, text="Overall CPU Usage", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        # CPU usage percentage
        usage_frame = tk.Frame(frame)
        usage_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(usage_frame, text="CPU Usage:", font=("Arial", 11)).pack(side=tk.LEFT)

        self._widgets["cpu_usage_label"] = tk.Label(
            usage_frame, text="0.0%", font=("Arial", 11, "bold"), fg="blue"
        )
        self._widgets["cpu_usage_label"].pack(side=tk.RIGHT)

        # Progress bar for visual representation (initial size, will be resized)
        self._widgets["cpu_usage_bar"] = ttk.Progressbar(
            frame, mode="determinate", length=300, maximum=100
        )
        self._widgets["cpu_usage_bar"].pack(fill=tk.X, padx=10, pady=(0, 10))

    def _create_info_row(
        self, parent: tk.Widget, label: str, key: str, initial_value: str = "0"
    ) -> None:
        """Helper method to create a label-value row"""
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=1)
        tk.Label(row, text=f"{label}:", font=("Arial", 10)).pack(side=tk.LEFT)
        self._widgets[key] = tk.Label(
            row, text=initial_value, font=("Arial", 10, "bold")
        )
        self._widgets[key].pack(side=tk.RIGHT)

    def _create_cpu_info_section(self) -> None:
        """Create CPU information section"""
        frame = tk.LabelFrame(
            self.main_container, text="CPU Information", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        # Use helper method for cleaner code
        self._create_info_row(info_frame, "Logical CPUs", "logical_cpus")
        self._create_info_row(info_frame, "Physical Cores", "physical_cpus")

    def _create_per_core_section(self) -> None:
        """Create per-core CPU usage section"""
        frame = tk.LabelFrame(
            self.main_container, text="Per-Core CPU Usage", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        # Container for per-core widgets
        self._widgets["per_core_container"] = tk.Frame(frame)
        self._widgets["per_core_container"].pack(fill=tk.X, padx=10, pady=10)

    def _create_cpu_times_section(self) -> None:
        """Create CPU times section"""
        frame = tk.LabelFrame(
            self.main_container, text="CPU Times", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        times_frame = tk.Frame(frame)
        times_frame.pack(fill=tk.X, padx=10, pady=10)

        # Simplified with helper method
        for time_type in ["User", "System", "Idle", "Nice", "IOWait"]:
            self._create_info_row(
                times_frame, time_type, f"cpu_time_{time_type.lower()}", "0.0%"
            )

    def _create_frequency_section(self) -> None:
        """Create CPU frequency section"""
        frame = tk.LabelFrame(
            self.main_container, text="CPU Frequency", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        freq_frame = tk.Frame(frame)
        freq_frame.pack(fill=tk.X, padx=10, pady=10)

        # Simplified with helper method
        for freq_type in [
            ("Current", "freq_current"),
            ("Min", "freq_min"),
            ("Max", "freq_max"),
        ]:
            self._create_info_row(freq_frame, freq_type[0], freq_type[1], "0 MHz")

    def _create_cpu_stats_section(self) -> None:
        """Create CPU statistics section"""
        frame = tk.LabelFrame(
            self.main_container, text="CPU Statistics", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        stats_frame = tk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        # Simplified with helper method
        stats = ["Context Switches", "Interrupts", "Soft Interrupts", "System Calls"]
        for stat in stats:
            self._create_info_row(
                stats_frame, stat, f'cpu_stat_{stat.lower().replace(" ", "_")}'
            )

    def _create_top_processes_section(self) -> None:
        """Create top CPU consuming processes section"""
        frame = tk.LabelFrame(
            self.main_container, text="Top CPU Processes", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        tree_container = tk.Frame(frame)
        tree_container.pack(fill=tk.X, padx=10, pady=10)

        # Create treeview
        columns = ("PID", "Name", "CPU%", "Memory%")
        tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", height=self.TREE_HEIGHT
        )

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, minwidth=50)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._widgets["process_tree"] = tree

    def _create_per_core_widgets(self) -> None:
        """Create widgets for per-core CPU usage display"""
        # Clear existing widgets
        for widget in self._per_core_bars + self._per_core_labels:
            widget.destroy()
        self._per_core_bars.clear()
        self._per_core_labels.clear()

        cpu_count = psutil.cpu_count(logical=True)
        container = self._widgets["per_core_container"]

        for i in range(cpu_count):
            core_frame = tk.Frame(container)
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

            self._per_core_bars.append(progress_bar)
            self._per_core_labels.append(percent_label)

        self.update_scroll_region()

    def _update_cpu_stats(self) -> None:
        """Update all CPU statistics"""
        try:
            self._update_overall_usage()
            self._update_cpu_info()
            self._update_per_core_usage()
            self._update_cpu_times()
            self._update_cpu_frequency()
            self._update_cpu_statistics()
            self._update_top_processes()
        except Exception as e:
            print(f"Error updating CPU stats: {e}")

    def _update_overall_usage(self) -> None:
        """Update overall CPU usage section"""
        cpu_percent = psutil.cpu_percent(interval=None)
        self._widgets["cpu_usage_label"].config(
            text=f"{cpu_percent:.1f}%", fg=self._get_usage_color(cpu_percent)
        )
        self._widgets["cpu_usage_bar"]["value"] = cpu_percent

    def _update_cpu_info(self) -> None:
        """Update CPU information section"""
        logical_cpus = psutil.cpu_count(logical=True)
        physical_cpus = psutil.cpu_count(logical=False)
        self._widgets["logical_cpus"].config(text=str(logical_cpus))
        self._widgets["physical_cpus"].config(text=str(physical_cpus or "N/A"))

    def _update_per_core_usage(self) -> None:
        """Update per-core CPU usage"""
        if not self._per_core_bars:
            self._create_per_core_widgets()

        per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
        for i, percent in enumerate(per_cpu_percent):
            if i < len(self._per_core_bars):
                self._per_core_bars[i]["value"] = percent
                self._per_core_labels[i].config(text=f"{percent:.1f}%")

    def _update_cpu_times(self) -> None:
        """Update CPU times section"""
        try:
            cpu_times_percent = psutil.cpu_times_percent(interval=None)
            time_attrs = ["user", "system", "idle", "nice", "iowait"]

            for attr in time_attrs:
                if hasattr(cpu_times_percent, attr):
                    value = getattr(cpu_times_percent, attr)
                    self._widgets[f"cpu_time_{attr}"].config(text=f"{value:.1f}%")
        except Exception:
            pass

    def _update_cpu_frequency(self) -> None:
        """Update CPU frequency section"""
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                freq_data = [
                    ("freq_current", cpu_freq.current),
                    ("freq_min", cpu_freq.min),
                    ("freq_max", cpu_freq.max),
                ]
                for key, value in freq_data:
                    self._widgets[key].config(text=f"{value:.0f} MHz")
            else:
                for key in ["freq_current", "freq_min", "freq_max"]:
                    self._widgets[key].config(text="N/A")
        except Exception:
            for key in ["freq_current", "freq_min", "freq_max"]:
                self._widgets[key].config(text="N/A")

    def _update_cpu_statistics(self) -> None:
        """Update CPU statistics"""
        try:
            stats = psutil.cpu_stats()
            self._widgets["cpu_stat_context_switches"].config(
                text=f"{stats.ctx_switches:,}"
            )
            self._widgets["cpu_stat_interrupts"].config(text=f"{stats.interrupts:,}")
            if hasattr(stats, "soft_interrupts"):
                self._widgets["cpu_stat_soft_interrupts"].config(
                    text=f"{stats.soft_interrupts:,}"
                )
            if hasattr(stats, "syscalls"):
                self._widgets["cpu_stat_system_calls"].config(
                    text=f"{stats.syscalls:,}"
                )
        except Exception:
            pass

    def _update_top_processes(self) -> None:
        """Update top CPU consuming processes"""
        try:
            tree = self._widgets["process_tree"]

            # Clear existing items
            tree.delete(*tree.get_children())

            # Get and sort processes
            processes = self._get_sorted_processes()

            # Insert top processes
            for proc in processes[: self.TOP_PROCESS_COUNT]:
                tree.insert(
                    "",
                    "end",
                    values=(
                        proc["pid"],
                        (proc["name"] or "N/A")[: self.MAX_PROCESS_NAME_LENGTH],
                        (
                            f"{proc['cpu_percent']:.1f}%"
                            if proc["cpu_percent"]
                            else "0.0%"
                        ),
                        (
                            f"{proc['memory_percent']:.1f}%"
                            if proc["memory_percent"]
                            else "0.0%"
                        ),
                    ),
                )
        except Exception:
            pass

    def _get_sorted_processes(self) -> List[Dict]:
        """Get processes sorted by CPU usage"""
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent"]
        ):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return sorted(processes, key=lambda x: x["cpu_percent"] or 0, reverse=True)

    def _get_usage_color(self, percentage: float) -> str:
        """Get color based on CPU usage percentage"""
        if percentage > 80:
            return "red"
        elif percentage > 60:
            return "orange"
        else:
            return "green"

    def _start_updates(self) -> None:
        """Start the periodic updates"""
        self._update_cpu_stats()
        self._frame.after(self._update_interval, self._start_updates)
