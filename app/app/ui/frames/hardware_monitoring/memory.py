import platform
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, override

import psutil

from app.logger.config import Logger, LogType
from app.ui.frames.base_frame import BaseFrame


@dataclass
class MemoryStats:
    """Data container for memory statistics."""

    total: float
    available: float
    used: float
    free: float
    percent: float


@dataclass
class ProcessInfo:
    """Data container for process information."""

    pid: int
    name: str
    memory_percent: float
    memory_mb: float
    status: str


class MemoryFrame(BaseFrame):
    """Memory monitoring frame with comprehensive memory statistics display."""

    # Configuration constants
    UPDATE_INTERVAL = 1000
    PROGRESS_BAR_LENGTH = 200
    MAX_PROCESS_NAME_LENGTH = 20
    TOP_PROCESS_COUNT = 10
    BYTES_TO_GB = 1024**3

    # UI color thresholds
    USAGE_COLORS = {
        "low": "green",  # < 50%
        "medium": "orange",  # 50-80%
        "high": "red",  # > 80%
    }

    def __init__(self, notebook: ttk.Notebook) -> None:
        self.logger = Logger().get_logger(LogType.MEMORY_MONITORING)
        self._widgets: Dict[str, Any] = {}
        self._previous_values: Dict[str, Any] = {}
        self._swap_available = False

        # Platform-specific optimizations
        self._is_windows = platform.system() == "Windows"
        self._is_linux = platform.system() == "Linux"
        self._is_macos = platform.system() == "Darwin"
        self.UPDATE_INTERVAL = (
            self.UPDATE_INTERVAL * 2 if self._is_windows else self.UPDATE_INTERVAL
        )

        super().__init__(notebook, "Memory")

    @override
    def setup_frame(self) -> None:
        """Initialize the memory monitoring interface."""
        self.main_container = tk.Frame(self.get_scrollable_container())
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._check_swap_availability()
        self._create_memory_overview_section()
        self._create_virtual_memory_section()
        self._create_swap_memory_section()

        self.start_threaded_updates(self.UPDATE_INTERVAL)

    @override
    def _update_ui_with_data(self, data: Dict[str, Any]) -> None:
        """Update UI with collected memory data."""
        if not data:
            return

        try:
            self._update_memory_stats(data.get("virtual_memory"))
            self._update_swap_stats(data.get("swap_memory"))
        except Exception as e:
            self.logger.error(f"Error updating memory UI: {e}")

    @override
    def _resize_widgets(self, canvas_width: int) -> None:
        """Resize progress bars based on available width."""
        progress_length = max(150, min(300, canvas_width - 200))

        for bar_key in ["memory_usage_bar", "swap_usage_bar"]:
            if bar_key in self._widgets:
                self._widgets[bar_key].config(length=progress_length)

    @override
    def _collect_data_threaded(self) -> Optional[Dict[str, Any]]:
        """Collect memory data in background thread."""
        try:
            data = {
                "virtual_memory": psutil.virtual_memory(),
                "top_processes": self._get_top_processes(),
            }

            # Always try to collect swap data
            try:
                data["swap_memory"] = psutil.swap_memory()
            except Exception as e:
                self.logger.warning(f"Warning: Could not collect swap data: {e}")
                data["swap_memory"] = None

            return data
        except Exception as e:
            self.logger.error(f"Error collecting memory data: {e}")
            return None

    def _check_swap_availability(self) -> None:
        """Check swap availability at startup."""
        try:
            swap_info = psutil.swap_memory()
            self._swap_available = swap_info.total > 0
        except Exception:
            self._swap_available = False

    def _create_memory_overview_section(self) -> None:
        """Create the main memory usage overview section."""
        frame = self._create_section("Overall Memory Usage")

        # Usage percentage with progress bar
        self._create_usage_display(
            frame, "Memory Usage:", "memory_usage_label", "memory_usage_bar"
        )

        # Memory breakdown
        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        memory_fields = [
            ("Total", "memory_total"),
            ("Available", "memory_available"),
            ("Used", "memory_used"),
            ("Free", "memory_free"),
        ]

        for label, key in memory_fields:
            self._create_info_row(info_frame, label, key, "0 GB")

    def _create_virtual_memory_section(self) -> None:
        """Create virtual memory details section - platform aware."""
        frame = self._create_section("Virtual Memory Details")

        # Get a sample of virtual memory to check available attributes
        vm_sample = psutil.virtual_memory()
        # Remove unused variable
        # available_attributes = [
        #     attr for attr in dir(vm_sample) if not attr.startswith("_")
        # ]

        # Define platform-specific fields
        if self._is_windows:
            # Windows-specific virtual memory fields
            vm_fields = [
                ("Percent Used", "vm_percent", "%"),
                ("Total", "vm_total", "GB"),
                ("Available", "vm_available", "GB"),
                ("Used", "vm_used", "GB"),
                ("Free", "vm_free", "GB"),
            ]
        elif self._is_linux:
            # Linux-specific virtual memory fields
            vm_fields = [
                ("Percent Used", "vm_percent", "%"),
                ("Active", "vm_active", "GB"),
                ("Inactive", "vm_inactive", "GB"),
                ("Buffers", "vm_buffers", "GB"),
                ("Cached", "vm_cached", "GB"),
                ("Shared", "vm_shared", "GB"),
                ("Available", "vm_available", "GB"),
            ]
        elif self._is_macos:
            # macOS-specific virtual memory fields
            vm_fields = [
                ("Percent Used", "vm_percent", "%"),
                ("Active", "vm_active", "GB"),
                ("Inactive", "vm_inactive", "GB"),
                ("Wired", "vm_wired", "GB"),
                ("Available", "vm_available", "GB"),
            ]
        else:
            # Generic fallback for other platforms
            vm_fields = [
                ("Percent Used", "vm_percent", "%"),
                ("Available", "vm_available", "GB"),
            ]

        # Only create widgets for attributes that actually exist
        for label, key, unit in vm_fields:
            attr_name = key.replace("vm_", "") if key != "vm_percent" else "percent"
            if hasattr(vm_sample, attr_name):
                default_value = "0%" if unit == "%" else "0 GB"
                self._create_info_row(frame, label, key, default_value)

    def _create_swap_memory_section(self) -> None:
        """Create swap memory monitoring section - always create widgets."""
        frame = self._create_section("Swap Memory")

        # Add status indicator
        status_frame = tk.Frame(frame)
        status_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        tk.Label(status_frame, text="Status:", font=("Arial", 10)).pack(side=tk.LEFT)
        status_text = "Available" if self._swap_available else "Not Configured"
        status_color = "green" if self._swap_available else "orange"
        self._widgets["swap_status"] = tk.Label(
            status_frame, text=status_text, font=("Arial", 10, "bold"), fg=status_color
        )
        self._widgets["swap_status"].pack(side=tk.RIGHT)

        # Always create swap usage display (will show 0% if no swap)
        self._create_usage_display(
            frame, "Swap Usage:", "swap_usage_label", "swap_usage_bar"
        )

        # Swap details - always create these widgets
        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        swap_fields = [
            ("Total", "swap_total"),
            ("Used", "swap_used"),
            ("Free", "swap_free"),
            ("Swap In", "swap_sin"),
            ("Swap Out", "swap_sout"),
        ]

        for label, key in swap_fields:
            default_value = (
                "0 GB"
                if key.startswith("swap_") and not key.endswith(("sin", "sout"))
                else "0"
            )
            self._create_info_row(info_frame, label, key, default_value)

    def _create_section(self, title: str) -> tk.LabelFrame:
        """Create a labeled frame section."""
        frame = tk.LabelFrame(
            self.main_container, text=title, font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))
        return frame

    def _create_usage_display(
        self,
        parent: Union[tk.Frame, tk.LabelFrame],
        label: str,
        label_key: str,
        bar_key: str,
    ) -> None:
        """Create a usage percentage display with label and progress bar."""
        # Usage percentage row
        usage_frame = tk.Frame(parent)
        usage_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(usage_frame, text=label, font=("Arial", 11)).pack(side=tk.LEFT)
        self._widgets[label_key] = tk.Label(
            usage_frame, text="0.0%", font=("Arial", 11, "bold")
        )
        self._widgets[label_key].pack(side=tk.RIGHT)

        # Progress bar
        self._widgets[bar_key] = ttk.Progressbar(
            parent, mode="determinate", length=300, maximum=100
        )
        self._widgets[bar_key].pack(fill=tk.X, padx=10, pady=(0, 10))

    def _create_info_row(
        self,
        parent: Union[tk.Frame, tk.LabelFrame],
        label: str,
        key: str,
        initial_value: str,
    ) -> None:
        """Create a label-value information row."""
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=1)

        tk.Label(row, text=f"{label}:", font=("Arial", 10)).pack(side=tk.LEFT)
        self._widgets[key] = tk.Label(
            row, text=initial_value, font=("Arial", 10, "bold")
        )
        self._widgets[key].pack(side=tk.RIGHT)

    def _get_top_processes(self) -> List[ProcessInfo]:
        """Get top memory consuming processes."""
        processes = []

        try:
            for proc in psutil.process_iter(
                ["pid", "name", "memory_percent", "memory_info", "status"]
            ):
                try:
                    info = proc.info
                    if not info or info.get("memory_percent") is None:
                        continue

                    memory_mb = 0
                    if info.get("memory_info"):
                        memory_mb = info["memory_info"].rss / (1024 * 1024)

                    process_info = ProcessInfo(
                        pid=info.get("pid", 0),
                        name=(info.get("name") or "Unknown")[
                            : self.MAX_PROCESS_NAME_LENGTH
                        ],
                        memory_percent=info.get("memory_percent", 0) or 0,
                        memory_mb=memory_mb,
                        status=(info.get("status", "Unknown"))[:10],
                    )
                    processes.append(process_info)

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

                # Performance limit
                if len(processes) > 200:
                    break

        except Exception as e:
            self.logger.error(f"Error getting processes: {e}")

        return sorted(processes, key=lambda x: x.memory_percent, reverse=True)[
            : self.TOP_PROCESS_COUNT
        ]

    def _update_memory_stats(self, vm_data) -> None:
        """Update virtual memory statistics with platform awareness."""
        if not vm_data:
            return

        # Main memory usage - simplified progress bar update
        memory_percent = vm_data.percent
        self._widgets["memory_usage_label"].config(
            text=f"{memory_percent:.1f}%", fg=self._get_usage_color(memory_percent)
        )
        self._widgets["memory_usage_bar"]["value"] = memory_percent

        # Memory amounts
        self._widgets["memory_total"].config(
            text=self._format_bytes_to_gb(vm_data.total)
        )
        self._widgets["memory_available"].config(
            text=self._format_bytes_to_gb(vm_data.available)
        )
        self._widgets["memory_used"].config(text=self._format_bytes_to_gb(vm_data.used))
        self._widgets["memory_free"].config(text=self._format_bytes_to_gb(vm_data.free))

        # Platform-specific virtual memory details
        self._update_platform_specific_vm_stats(vm_data)

    def _update_platform_specific_vm_stats(self, vm_data) -> None:
        """Update platform-specific virtual memory statistics."""
        # Always update percent if widget exists
        if "vm_percent" in self._widgets:
            self._widgets["vm_percent"].config(text=f"{vm_data.percent:.1f}%")

        # Platform-specific attributes
        platform_attributes = {
            "Windows": ["total", "available", "used", "free"],
            "Linux": ["active", "inactive", "buffers", "cached", "shared", "available"],
            "Darwin": ["active", "inactive", "wired", "available"],  # macOS
        }

        current_platform = platform.system()
        attributes_to_update = platform_attributes.get(current_platform, ["available"])

        for attr_name in attributes_to_update:
            widget_key = f"vm_{attr_name}"
            if widget_key in self._widgets and hasattr(vm_data, attr_name):
                value = getattr(vm_data, attr_name)
                self._widgets[widget_key].config(text=self._format_bytes_to_gb(value))

    def _update_swap_stats(self, swap_data) -> None:
        """Update swap memory statistics - always safe to call."""
        if swap_data and swap_data.total > 0:
            # Update swap availability status
            if not self._swap_available:
                self._swap_available = True
                if "swap_status" in self._widgets:
                    self._widgets["swap_status"].config(text="Available", fg="green")

            # Update swap usage
            swap_percent = swap_data.percent
            self._widgets["swap_usage_label"].config(
                text=f"{swap_percent:.1f}%", fg=self._get_usage_color(swap_percent)
            )
            self._widgets["swap_usage_bar"]["value"] = swap_percent

            # Update swap amounts
            self._widgets["swap_total"].config(
                text=self._format_bytes_to_gb(swap_data.total)
            )
            self._widgets["swap_used"].config(
                text=self._format_bytes_to_gb(swap_data.used)
            )
            self._widgets["swap_free"].config(
                text=self._format_bytes_to_gb(swap_data.free)
            )
            self._widgets["swap_sin"].config(text=f"{swap_data.sin:,}")
            self._widgets["swap_sout"].config(text=f"{swap_data.sout:,}")

        else:
            # No swap available - show zeros
            self._widgets["swap_usage_label"].config(text="0.0%", fg="gray")
            self._widgets["swap_usage_bar"]["value"] = 0

            # Set all swap values to appropriate defaults
            self._widgets["swap_total"].config(text="0 GB")
            self._widgets["swap_used"].config(text="0 GB")
            self._widgets["swap_free"].config(text="0 GB")
            self._widgets["swap_sin"].config(text="0")
            self._widgets["swap_sout"].config(text="0")

            # Update status if needed
            if self._swap_available:
                self._swap_available = False
                if "swap_status" in self._widgets:
                    self._widgets["swap_status"].config(
                        text="Not Configured", fg="orange"
                    )

    def _get_usage_color(self, percentage: float) -> str:
        """Get color based on memory usage percentage."""
        if percentage < 50:
            return self.USAGE_COLORS["low"]
        elif percentage < 80:
            return self.USAGE_COLORS["medium"]
        else:
            return self.USAGE_COLORS["high"]

    def _format_bytes_to_gb(self, bytes_value: int) -> str:
        """Convert bytes to readable GB format."""
        return f"{bytes_value / self.BYTES_TO_GB:.2f} GB"
