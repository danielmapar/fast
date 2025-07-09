import platform
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List, Optional, override

import psutil

from app.logger.config import Logger, LogType
from app.ui.frames.base_frame import BaseFrame


class HardDriveFrame(BaseFrame):
    """Hardware monitoring frame for disk/hard drive statistics."""

    # Configuration constants
    UPDATE_INTERVAL = 1000  # 1000 milliseconds = 1 second
    BYTES_TO_GB = 1024**3
    BYTES_TO_MB = 1024**2
    WARNING_THRESHOLD = 70
    CRITICAL_THRESHOLD = 85

    def __init__(self, notebook: ttk.Notebook) -> None:
        self.logger = Logger().get_logger(LogType.HARDDRIVE_MONITORING)

        self._widgets: Dict[str, Any] = {}

        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        self.is_macos = platform.system() == "Darwin"
        self.UPDATE_INTERVAL = (
            self.UPDATE_INTERVAL * 2 if self.is_windows else self.UPDATE_INTERVAL
        )

        super().__init__(notebook, "Hard Drive")

    @override
    def setup_frame(self) -> None:
        """Setup the Hard Drive monitoring interface."""
        main_frame = tk.Frame(self.get_scrollable_container())
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._create_storage_summary(main_frame)
        self._create_partitions_table(main_frame)
        self._create_disk_io_stats(main_frame)

        self.start_threaded_updates(self.UPDATE_INTERVAL)

    @override
    def _resize_widgets(self, canvas_width: int) -> None:
        """Handle widget resizing based on canvas width."""
        if "usage_bar" in self._widgets:
            new_length = max(200, min(400, canvas_width - 100))
            self._widgets["usage_bar"].config(length=new_length)

    @override
    def _collect_data_threaded(self) -> Optional[Dict[str, Any]]:
        """Collect disk data in background thread."""
        try:
            return {
                "partitions": self._get_partition_data(),
                "io_stats": self._get_io_stats(),
                "summary": self._get_summary_data(),
            }
        except Exception as e:
            self.logger.error(f"Error collecting disk data: {e}")
            return None

    @override
    def _update_ui_with_data(self, data: Dict[str, Any]) -> None:
        """Update UI with collected data."""
        if not data:
            return

        try:
            if "summary" in data:
                self._update_summary_ui(data["summary"])
            if "partitions" in data:
                self._update_partitions_ui(data["partitions"])
            if "io_stats" in data:
                self._update_io_ui(data["io_stats"])
        except Exception as e:
            self.logger.error(f"Error updating disk UI: {e}")

    def _create_storage_summary(self, parent: tk.Widget) -> None:
        """Create overall storage summary section."""
        frame = self._create_section_frame(parent, "Storage Summary")

        # Summary statistics in a grid
        stats_frame = tk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self._create_stat_row(stats_frame, "Total Space:", "total_space", row=0)
        self._create_stat_row(stats_frame, "Used Space:", "total_used", row=1)
        self._create_stat_row(stats_frame, "Free Space:", "total_free", row=2)

        # Overall usage with progress bar
        usage_frame = tk.Frame(frame)
        usage_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(usage_frame, text="Overall Usage:", font=("Arial", 11)).pack(
            side=tk.LEFT
        )
        self._widgets["usage_label"] = tk.Label(
            usage_frame, text="0%", font=("Arial", 11, "bold")
        )
        self._widgets["usage_label"].pack(side=tk.RIGHT)

        self._widgets["usage_bar"] = ttk.Progressbar(
            frame, mode="determinate", length=300, maximum=100
        )
        self._widgets["usage_bar"].pack(fill=tk.X, padx=10, pady=(0, 10))

    def _create_partitions_table(self, parent: tk.Widget) -> None:
        """Create partitions overview table."""
        frame = self._create_section_frame(parent, "Disk Partitions")

        # Create treeview with scrollbar
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Device", "Mount", "Type", "Total", "Used", "Free", "Usage%")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80, minwidth=60)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._widgets["partitions_tree"] = tree

    def _create_disk_io_stats(self, parent: tk.Widget) -> None:
        """Create disk I/O statistics section."""
        frame = self._create_section_frame(parent, "Disk I/O Statistics")

        stats_frame = tk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self._create_stat_row(stats_frame, "Read Operations:", "io_reads", row=0)
        self._create_stat_row(stats_frame, "Write Operations:", "io_writes", row=1)
        self._create_stat_row(stats_frame, "Bytes Read:", "io_read_bytes", row=2)
        self._create_stat_row(stats_frame, "Bytes Written:", "io_write_bytes", row=3)

    def _create_section_frame(self, parent: tk.Widget, title: str) -> tk.LabelFrame:
        """Create a labeled frame section."""
        frame = tk.LabelFrame(parent, text=title, font=("Arial", 12, "bold"))
        frame.pack(fill=tk.X, pady=(0, 10))
        return frame

    def _create_stat_row(
        self, parent: tk.Widget, label: str, key: str, row: int
    ) -> None:
        """Create a statistic row with label and value."""
        tk.Label(parent, text=label, font=("Arial", 10)).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=2
        )

        self._widgets[key] = tk.Label(
            parent, text="Loading...", font=("Arial", 10, "bold")
        )
        self._widgets[key].grid(row=row, column=1, sticky="e", pady=2)

    def _get_partition_data(self) -> List[Dict[str, Any]]:
        """Get data for all accessible disk partitions."""
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                usage_percent = (
                    (usage.used / usage.total * 100) if usage.total > 0 else 0
                )

                partitions.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": usage.total / self.BYTES_TO_GB,
                        "used_gb": usage.used / self.BYTES_TO_GB,
                        "free_gb": usage.free / self.BYTES_TO_GB,
                        "usage_percent": usage_percent,
                    }
                )
            except OSError:
                # Skip inaccessible partitions
                continue
        return partitions

    def _get_io_stats(self) -> Optional[Dict[str, Any]]:
        """Get disk I/O statistics."""
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                return {
                    "read_count": io_counters.read_count,
                    "write_count": io_counters.write_count,
                    "read_bytes": io_counters.read_bytes,
                    "write_bytes": io_counters.write_bytes,
                }
        except Exception:
            pass
        return None

    def _get_summary_data(self) -> Dict[str, Any]:
        """Calculate overall storage summary."""
        total_space = total_used = total_free = 0

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_space += usage.total
                total_used += usage.used
                total_free += usage.free
            except OSError:
                continue

        usage_percent = (total_used / total_space * 100) if total_space > 0 else 0

        return {
            "total_space_gb": total_space / self.BYTES_TO_GB,
            "total_used_gb": total_used / self.BYTES_TO_GB,
            "total_free_gb": total_free / self.BYTES_TO_GB,
            "usage_percent": usage_percent,
        }

    def _update_summary_ui(self, summary: Dict[str, Any]) -> None:
        """Update storage summary display."""
        self._widgets["total_space"].config(text=f"{summary['total_space_gb']:.1f} GB")
        self._widgets["total_used"].config(text=f"{summary['total_used_gb']:.1f} GB")
        self._widgets["total_free"].config(text=f"{summary['total_free_gb']:.1f} GB")

        usage_percent = summary["usage_percent"]
        color = self._get_usage_color(usage_percent)

        self._widgets["usage_label"].config(text=f"{usage_percent:.1f}%", fg=color)
        self._widgets["usage_bar"]["value"] = usage_percent

    def _update_partitions_ui(self, partitions: List[Dict[str, Any]]) -> None:
        """Update partitions table."""
        tree = self._widgets.get("partitions_tree")
        if not tree:
            return

        # Clear and repopulate
        tree.delete(*tree.get_children())

        for partition in partitions:
            tree.insert(
                "",
                "end",
                values=(
                    partition["device"],
                    partition["mountpoint"],
                    partition["fstype"],
                    f"{partition['total_gb']:.1f} GB",
                    f"{partition['used_gb']:.1f} GB",
                    f"{partition['free_gb']:.1f} GB",
                    f"{partition['usage_percent']:.1f}%",
                ),
            )

    def _update_io_ui(self, io_stats: Optional[Dict[str, Any]]) -> None:
        """Update I/O statistics display."""
        if not io_stats:
            for key in ["io_reads", "io_writes", "io_read_bytes", "io_write_bytes"]:
                if key in self._widgets:
                    self._widgets[key].config(text="N/A")
            return

        self._widgets["io_reads"].config(text=f"{io_stats['read_count']:,}")
        self._widgets["io_writes"].config(text=f"{io_stats['write_count']:,}")
        self._widgets["io_read_bytes"].config(
            text=f"{io_stats['read_bytes'] / self.BYTES_TO_MB:.1f} MB"
        )
        self._widgets["io_write_bytes"].config(
            text=f"{io_stats['write_bytes'] / self.BYTES_TO_MB:.1f} MB"
        )

    def _get_usage_color(self, percentage: float) -> str:
        """Return color based on usage percentage."""
        if percentage >= self.CRITICAL_THRESHOLD:
            return "red"
        elif percentage >= self.WARNING_THRESHOLD:
            return "orange"
        else:
            return "green"
