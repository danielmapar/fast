import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict

import psutil

from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame


class HardDriveFrame(BaseHardwareMonitoringFrame):
    # Constants
    UPDATE_INTERVAL = 2000  # milliseconds (slower than CPU/Memory since disk usage changes less frequently)
    PROGRESS_BAR_LENGTH = 300
    TREE_HEIGHT = 8
    BYTES_TO_GB = 1024**3
    BYTES_TO_MB = 1024**2

    # Color thresholds
    WARNING_THRESHOLD = 70
    CRITICAL_THRESHOLD = 85

    def __init__(self, notebook: ttk.Notebook) -> None:
        self._update_interval = self.UPDATE_INTERVAL
        self._widgets: Dict[str, Any] = {}
        self._partition_widgets: Dict[str, Dict[str, Any]] = {}
        self.main_container: tk.Frame = tk.Frame()

        super().__init__(notebook, "Hard Drive")
        self._start_updates()

    def setup_frame(self) -> None:
        """Setup the Hard Drive monitoring interface with comprehensive statistics"""
        # Get the scrollable container from the base class
        self.main_container = tk.Frame(self.get_scrollable_container())
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create sections
        self._create_overall_summary_section()
        self._create_partitions_overview_section()
        self._create_partition_details_section()
        self._create_disk_io_section()

        # Initial update
        self._update_disk_stats()

    def _resize_widgets(self, canvas_width: int) -> None:
        """Override base class method to handle Hard Drive-specific widget resizing"""
        # Calculate progress bar length based on canvas width
        progress_length = max(150, min(300, canvas_width - 200))

        # Resize progress bars in overall summary
        for key in ["total_usage_bar"]:
            if key in self._widgets:
                self._widgets[key].config(length=progress_length)

        # Resize partition progress bars
        for partition_widgets in self._partition_widgets.values():
            if "usage_bar" in partition_widgets:
                partition_widgets["usage_bar"].config(
                    length=max(150, progress_length - 100)
                )

    def _create_overall_summary_section(self) -> None:
        """Create overall disk space summary section"""
        frame = tk.LabelFrame(
            self.main_container,
            text="Overall Storage Summary",
            font=("Arial", 12, "bold"),
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        # Summary statistics
        summary_frame = tk.Frame(frame)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)

        self._create_info_row(
            summary_frame, "Total Partitions", "total_partitions", "0"
        )
        self._create_info_row(summary_frame, "Total Space", "total_space", "0 GB")
        self._create_info_row(summary_frame, "Total Used", "total_used", "0 GB")
        self._create_info_row(summary_frame, "Total Free", "total_free", "0 GB")

        # Overall usage percentage
        usage_frame = tk.Frame(frame)
        usage_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(usage_frame, text="Overall Usage:", font=("Arial", 11)).pack(
            side=tk.LEFT
        )

        self._widgets["total_usage_label"] = tk.Label(
            usage_frame, text="0.0%", font=("Arial", 11, "bold"), fg="blue"
        )
        self._widgets["total_usage_label"].pack(side=tk.RIGHT)

        # Progress bar for overall usage
        self._widgets["total_usage_bar"] = ttk.Progressbar(
            frame, mode="determinate", length=300, maximum=100
        )
        self._widgets["total_usage_bar"].pack(fill=tk.X, padx=10, pady=(0, 10))

    def _create_partitions_overview_section(self) -> None:
        """Create partitions overview table"""
        frame = tk.LabelFrame(
            self.main_container,
            text="Disk Partitions Overview",
            font=("Arial", 12, "bold"),
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        tree_container = tk.Frame(frame)
        tree_container.pack(fill=tk.X, padx=10, pady=10)

        # Create treeview
        columns = (
            "Device",
            "Mountpoint",
            "Filesystem",
            "Total",
            "Used",
            "Free",
            "Usage%",
        )
        tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", height=self.TREE_HEIGHT
        )

        # Configure columns
        tree.heading("Device", text="Device")
        tree.heading("Mountpoint", text="Mount Point")
        tree.heading("Filesystem", text="File System")
        tree.heading("Total", text="Total")
        tree.heading("Used", text="Used")
        tree.heading("Free", text="Free")
        tree.heading("Usage%", text="Usage %")

        # Set column widths
        tree.column("Device", width=120, minwidth=80)
        tree.column("Mountpoint", width=100, minwidth=80)
        tree.column("Filesystem", width=80, minwidth=60)
        tree.column("Total", width=80, minwidth=60)
        tree.column("Used", width=80, minwidth=60)
        tree.column("Free", width=80, minwidth=60)
        tree.column("Usage%", width=80, minwidth=60)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._widgets["partitions_tree"] = tree

    def _create_partition_details_section(self) -> None:
        """Create detailed partition information section"""
        frame = tk.LabelFrame(
            self.main_container, text="Partition Details", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        # Container for dynamic partition widgets
        self._widgets["partitions_container"] = tk.Frame(frame)
        self._widgets["partitions_container"].pack(fill=tk.X, padx=10, pady=10)

    def _create_disk_io_section(self) -> None:
        """Create disk I/O statistics section"""
        frame = tk.LabelFrame(
            self.main_container, text="Disk I/O Statistics", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        io_frame = tk.Frame(frame)
        io_frame.pack(fill=tk.X, padx=10, pady=10)

        # System-wide I/O stats
        self._create_info_row(io_frame, "Read Count", "io_read_count", "0")
        self._create_info_row(io_frame, "Write Count", "io_write_count", "0")
        self._create_info_row(io_frame, "Read Bytes", "io_read_bytes", "0 MB")
        self._create_info_row(io_frame, "Write Bytes", "io_write_bytes", "0 MB")
        self._create_info_row(io_frame, "Read Time", "io_read_time", "0 ms")
        self._create_info_row(io_frame, "Write Time", "io_write_time", "0 ms")

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

    def _update_disk_stats(self) -> None:
        """Update all disk statistics"""
        try:
            self._update_partitions_overview()
            self._update_overall_summary()
            self._update_partition_details()
            self._update_disk_io()
            # Remove this call to prevent scroll position reset
            # self.update_scroll_region()
        except Exception as e:
            print(f"Error updating disk stats: {e}")

    def _update_partitions_overview(self) -> None:
        """Update the partitions overview table"""
        try:
            tree = self._widgets.get("partitions_tree")
            if not tree:
                return

            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)

            # Get all disk partitions
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    # Get usage statistics for this partition
                    usage = psutil.disk_usage(partition.mountpoint)

                    # Calculate usage percentage
                    usage_percent = (
                        (usage.used / usage.total) * 100 if usage.total > 0 else 0
                    )

                    # Format sizes
                    total_gb = self._bytes_to_gb(usage.total)
                    used_gb = self._bytes_to_gb(usage.used)
                    free_gb = self._bytes_to_gb(usage.free)

                    # Insert into tree
                    tree.insert(
                        "",
                        "end",
                        values=(
                            partition.device,
                            partition.mountpoint,
                            partition.fstype,
                            f"{total_gb:.1f} GB",
                            f"{used_gb:.1f} GB",
                            f"{free_gb:.1f} GB",
                            f"{usage_percent:.1f}%",
                        ),
                    )

                except (OSError, psutil.AccessDenied):
                    # Some partitions may not be accessible
                    tree.insert(
                        "",
                        "end",
                        values=(
                            partition.device,
                            partition.mountpoint,
                            partition.fstype,
                            "N/A",
                            "N/A",
                            "N/A",
                            "N/A",
                        ),
                    )

        except Exception as e:
            print(f"Error updating partitions overview: {e}")

    def _update_overall_summary(self) -> None:
        """Update overall storage summary"""
        try:
            partitions = psutil.disk_partitions()
            total_space = 0
            total_used = 0
            total_free = 0
            accessible_partitions = 0

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_space += usage.total
                    total_used += usage.used
                    total_free += usage.free
                    accessible_partitions += 1
                except (OSError, psutil.AccessDenied):
                    continue

            # Update summary info
            self._widgets["total_partitions"].config(text=str(len(partitions)))
            self._widgets["total_space"].config(
                text=f"{self._bytes_to_gb(total_space):.1f} GB"
            )
            self._widgets["total_used"].config(
                text=f"{self._bytes_to_gb(total_used):.1f} GB"
            )
            self._widgets["total_free"].config(
                text=f"{self._bytes_to_gb(total_free):.1f} GB"
            )

            # Update overall usage
            if total_space > 0:
                usage_percent = (total_used / total_space) * 100
                self._widgets["total_usage_label"].config(
                    text=f"{usage_percent:.1f}%",
                    fg=self._get_usage_color(usage_percent),
                )
                self._widgets["total_usage_bar"]["value"] = usage_percent
            else:
                self._widgets["total_usage_label"].config(text="0.0%", fg="blue")
                self._widgets["total_usage_bar"]["value"] = 0

        except Exception as e:
            print(f"Error updating overall summary: {e}")

    def _update_partition_details(self) -> None:
        """Update detailed partition information"""
        try:
            container = self._widgets.get("partitions_container")
            if not container:
                return

            # Get current partitions
            partitions = psutil.disk_partitions()
            current_devices = {partition.device for partition in partitions}
            existing_devices = set(self._partition_widgets.keys())

            # Only recreate widgets if partition list changed
            if current_devices != existing_devices:
                # Clear existing partition widgets only when needed
                for widget in container.winfo_children():
                    widget.destroy()
                self._partition_widgets.clear()

                # Create new widgets for current partitions
                for i, partition in enumerate(partitions):
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        self._create_partition_widget(container, partition, usage, i)
                    except (OSError, psutil.AccessDenied):
                        self._create_inaccessible_partition_widget(
                            container, partition, i
                        )
            else:
                # Just update existing widgets
                for partition in partitions:
                    try:
                        if partition.device in self._partition_widgets:
                            usage = psutil.disk_usage(partition.mountpoint)
                            self._update_partition_widget(partition, usage)
                    except (OSError, psutil.AccessDenied):
                        # Handle inaccessible partitions
                        pass

        except Exception as e:
            print(f"Error updating partition details: {e}")

    def _create_partition_widget(
        self, parent: tk.Widget, partition, usage, index: int
    ) -> None:
        """Create a detailed widget for a single partition"""
        # Create frame for this partition
        partition_frame = tk.LabelFrame(
            parent,
            text=f"{partition.device} ({partition.mountpoint})",
            font=("Arial", 10, "bold"),
        )
        partition_frame.pack(fill=tk.X, pady=(5, 0))

        # Create widgets dictionary for this partition
        partition_widgets: Dict[str, Any] = {}
        self._partition_widgets[partition.device] = partition_widgets

        # Usage percentage and progress bar
        usage_percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0

        usage_frame = tk.Frame(partition_frame)
        usage_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(usage_frame, text="Usage:", font=("Arial", 9)).pack(side=tk.LEFT)
        partition_widgets["usage_label"] = tk.Label(
            usage_frame,
            text=f"{usage_percent:.1f}%",
            font=("Arial", 9, "bold"),
            fg=self._get_usage_color(usage_percent),
        )
        partition_widgets["usage_label"].pack(side=tk.RIGHT)

        partition_widgets["usage_bar"] = ttk.Progressbar(
            partition_frame, mode="determinate", length=200, maximum=100
        )
        partition_widgets["usage_bar"].pack(fill=tk.X, padx=10, pady=(0, 5))
        partition_widgets["usage_bar"]["value"] = usage_percent

        # Details frame
        details_frame = tk.Frame(partition_frame)
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Left column
        left_col = tk.Frame(details_frame)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._create_partition_info_row(left_col, "File System:", partition.fstype)
        self._create_partition_info_row(
            left_col, "Total Space:", f"{self._bytes_to_gb(usage.total):.2f} GB"
        )
        self._create_partition_info_row(
            left_col, "Used Space:", f"{self._bytes_to_gb(usage.used):.2f} GB"
        )

        # Right column
        right_col = tk.Frame(details_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._create_partition_info_row(
            right_col, "Free Space:", f"{self._bytes_to_gb(usage.free):.2f} GB"
        )
        self._create_partition_info_row(right_col, "Mount Point:", partition.mountpoint)
        self._create_partition_info_row(
            right_col, "Options:", getattr(partition, "opts", "N/A")
        )

    def _create_inaccessible_partition_widget(
        self, parent: tk.Widget, partition, index: int
    ) -> None:
        """Create widget for inaccessible partition"""
        partition_frame = tk.LabelFrame(
            parent,
            text=f"{partition.device} (Inaccessible)",
            font=("Arial", 10, "bold"),
        )
        partition_frame.pack(fill=tk.X, pady=(5, 0))

        info_frame = tk.Frame(partition_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            info_frame, text="Status: Access Denied", font=("Arial", 9), fg="red"
        ).pack(anchor=tk.W)
        tk.Label(
            info_frame, text=f"Device: {partition.device}", font=("Arial", 9)
        ).pack(anchor=tk.W)
        tk.Label(
            info_frame, text=f"Mount Point: {partition.mountpoint}", font=("Arial", 9)
        ).pack(anchor=tk.W)
        tk.Label(
            info_frame, text=f"File System: {partition.fstype}", font=("Arial", 9)
        ).pack(anchor=tk.W)

    def _create_partition_info_row(
        self, parent: tk.Widget, label: str, value: str
    ) -> None:
        """Create an info row for partition details"""
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=1)

        tk.Label(row, text=label, font=("Arial", 9), width=12, anchor="w").pack(
            side=tk.LEFT
        )
        tk.Label(row, text=value, font=("Arial", 9), anchor="w").pack(side=tk.LEFT)

    def _update_disk_io(self) -> None:
        """Update disk I/O statistics"""
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                self._widgets["io_read_count"].config(
                    text=f"{io_counters.read_count:,}"
                )
                self._widgets["io_write_count"].config(
                    text=f"{io_counters.write_count:,}"
                )
                self._widgets["io_read_bytes"].config(
                    text=f"{self._bytes_to_mb(io_counters.read_bytes):.1f} MB"
                )
                self._widgets["io_write_bytes"].config(
                    text=f"{self._bytes_to_mb(io_counters.write_bytes):.1f} MB"
                )

                # Some platforms may not have time information
                if hasattr(io_counters, "read_time"):
                    self._widgets["io_read_time"].config(
                        text=f"{io_counters.read_time:,} ms"
                    )
                else:
                    self._widgets["io_read_time"].config(text="N/A")

                if hasattr(io_counters, "write_time"):
                    self._widgets["io_write_time"].config(
                        text=f"{io_counters.write_time:,} ms"
                    )
                else:
                    self._widgets["io_write_time"].config(text="N/A")
            else:
                # No I/O counters available
                for key in [
                    "io_read_count",
                    "io_write_count",
                    "io_read_bytes",
                    "io_write_bytes",
                    "io_read_time",
                    "io_write_time",
                ]:
                    if key in self._widgets:
                        self._widgets[key].config(text="N/A")

        except Exception as e:
            print(f"Error updating disk I/O: {e}")

    def _update_partition_widget(self, partition, usage) -> None:
        """Update an existing partition widget without recreating it"""
        partition_widgets = self._partition_widgets.get(partition.device)
        if not partition_widgets:
            return

        # Update usage percentage and progress bar
        usage_percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0

        if "usage_label" in partition_widgets:
            partition_widgets["usage_label"].config(
                text=f"{usage_percent:.1f}%", fg=self._get_usage_color(usage_percent)
            )

        if "usage_bar" in partition_widgets:
            partition_widgets["usage_bar"]["value"] = usage_percent

    def _get_usage_color(self, percentage: float) -> str:
        """Return color based on usage percentage"""
        if percentage >= self.CRITICAL_THRESHOLD:
            return "red"
        elif percentage >= self.WARNING_THRESHOLD:
            return "orange"
        else:
            return "green"

    def _bytes_to_gb(self, bytes_value: int) -> float:
        """Convert bytes to gigabytes"""
        return bytes_value / self.BYTES_TO_GB

    def _bytes_to_mb(self, bytes_value: int) -> float:
        """Convert bytes to megabytes"""
        return bytes_value / self.BYTES_TO_MB

    def _start_updates(self) -> None:
        """Start the periodic updates"""
        self._update_disk_stats()
        if self.main_container.winfo_exists():
            self.main_container.after(self._update_interval, self._start_updates)
