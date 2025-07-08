import tkinter as tk
import tkinter.ttk as ttk
from typing import Any, Dict, List

import psutil

from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame


class MemoryFrame(BaseHardwareMonitoringFrame):
    # Constants
    UPDATE_INTERVAL = 1000  # milliseconds
    PROGRESS_BAR_LENGTH = 200
    TREE_HEIGHT = 8
    MAX_PROCESS_NAME_LENGTH = 20
    TOP_PROCESS_COUNT = 10
    BYTES_TO_GB = 1024**3

    # Color thresholds
    WARNING_THRESHOLD = 50
    CRITICAL_THRESHOLD = 80

    def __init__(self, notebook: ttk.Notebook) -> None:
        self._update_interval = self.UPDATE_INTERVAL
        self._widgets: Dict[str, Any] = {}
        self.main_container: tk.Frame = tk.Frame()

        super().__init__(notebook, "Memory")
        self._start_updates()

    def setup_frame(self) -> None:
        """Setup the Memory monitoring interface with comprehensive statistics"""
        # Get the scrollable container from the base class
        self.main_container = tk.Frame(self.get_scrollable_container())
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create sections
        self._create_overall_memory_section()
        self._create_top_processes_section()
        self._create_virtual_memory_section()
        self._create_swap_memory_section()
        self._create_memory_stats_section()

        # Initial update
        self._update_memory_stats()

    def _resize_widgets(self, canvas_width: int) -> None:
        """Override base class method to handle Memory-specific widget resizing"""
        # Calculate progress bar length based on canvas width
        progress_length = max(150, min(300, canvas_width - 200))

        # Resize progress bars
        for key in ["memory_usage_bar", "swap_usage_bar"]:
            if key in self._widgets:
                self._widgets[key].config(length=progress_length)

    def _create_overall_memory_section(self) -> None:
        """Create overall memory usage section"""
        frame = tk.LabelFrame(
            self.main_container, text="Overall Memory Usage", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        # Memory usage percentage
        usage_frame = tk.Frame(frame)
        usage_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(usage_frame, text="Memory Usage:", font=("Arial", 11)).pack(
            side=tk.LEFT
        )

        self._widgets["memory_usage_label"] = tk.Label(
            usage_frame, text="0.0%", font=("Arial", 11, "bold"), fg="blue"
        )
        self._widgets["memory_usage_label"].pack(side=tk.RIGHT)

        # Progress bar for visual representation
        self._widgets["memory_usage_bar"] = ttk.Progressbar(
            frame, mode="determinate", length=300, maximum=100
        )
        self._widgets["memory_usage_bar"].pack(fill=tk.X, padx=10, pady=(0, 10))

        # Memory details
        details_frame = tk.Frame(frame)
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self._create_info_row(details_frame, "Total", "memory_total", "0 GB")
        self._create_info_row(details_frame, "Available", "memory_available", "0 GB")
        self._create_info_row(details_frame, "Used", "memory_used", "0 GB")
        self._create_info_row(details_frame, "Free", "memory_free", "0 GB")

    def _create_virtual_memory_section(self) -> None:
        """Create virtual memory details section"""
        frame = tk.LabelFrame(
            self.main_container,
            text="Virtual Memory Details",
            font=("Arial", 12, "bold"),
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        vm_frame = tk.Frame(frame)
        vm_frame.pack(fill=tk.X, padx=10, pady=10)

        # Virtual memory specific stats
        self._create_info_row(vm_frame, "Percent Used", "vm_percent", "0.0%")
        self._create_info_row(vm_frame, "Active", "vm_active", "0 GB")
        self._create_info_row(vm_frame, "Inactive", "vm_inactive", "0 GB")
        self._create_info_row(vm_frame, "Buffers", "vm_buffers", "0 GB")
        self._create_info_row(vm_frame, "Cached", "vm_cached", "0 GB")
        self._create_info_row(vm_frame, "Shared", "vm_shared", "0 GB")

    def _create_swap_memory_section(self) -> None:
        """Create swap memory section"""
        frame = tk.LabelFrame(
            self.main_container, text="Swap Memory", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        # Swap usage percentage
        usage_frame = tk.Frame(frame)
        usage_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(usage_frame, text="Swap Usage:", font=("Arial", 11)).pack(side=tk.LEFT)

        self._widgets["swap_usage_label"] = tk.Label(
            usage_frame, text="0.0%", font=("Arial", 11, "bold"), fg="orange"
        )
        self._widgets["swap_usage_label"].pack(side=tk.RIGHT)

        # Progress bar for swap
        self._widgets["swap_usage_bar"] = ttk.Progressbar(
            frame, mode="determinate", length=300, maximum=100
        )
        self._widgets["swap_usage_bar"].pack(fill=tk.X, padx=10, pady=(0, 10))

        # Swap details
        swap_frame = tk.Frame(frame)
        swap_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self._create_info_row(swap_frame, "Total", "swap_total", "0 GB")
        self._create_info_row(swap_frame, "Used", "swap_used", "0 GB")
        self._create_info_row(swap_frame, "Free", "swap_free", "0 GB")
        self._create_info_row(swap_frame, "Swap In", "swap_sin", "0")
        self._create_info_row(swap_frame, "Swap Out", "swap_sout", "0")

    def _create_memory_stats_section(self) -> None:
        """Create memory statistics section"""
        frame = tk.LabelFrame(
            self.main_container, text="Memory Statistics", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        stats_frame = tk.Frame(frame)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        # Platform-specific memory stats
        self._create_info_row(stats_frame, "Page Faults", "page_faults", "0")
        self._create_info_row(
            stats_frame, "Major Page Faults", "major_page_faults", "0"
        )

    def _create_top_processes_section(self) -> None:
        """Create top memory consuming processes section"""
        frame = tk.LabelFrame(
            self.main_container, text="Top Memory Processes", font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        tree_container = tk.Frame(frame)
        tree_container.pack(fill=tk.X, padx=10, pady=10)

        # Create treeview
        columns = ("PID", "Name", "Memory%", "Memory MB", "Status")
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

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._widgets["processes_tree"] = tree

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

    def _update_memory_stats(self) -> None:
        """Update all memory statistics"""
        try:
            self._update_overall_memory()
            self._update_virtual_memory()
            self._update_swap_memory()
            self._update_top_processes()
            self._update_memory_statistics()
        except Exception as e:
            print(f"Error updating memory stats: {e}")

    def _update_overall_memory(self) -> None:
        """Update overall memory usage"""
        try:
            memory = psutil.virtual_memory()

            # Update percentage and progress bar
            percent = memory.percent
            self._widgets["memory_usage_label"].config(
                text=f"{percent:.1f}%", fg=self._get_usage_color(percent)
            )
            self._widgets["memory_usage_bar"]["value"] = percent

            # Update memory values
            self._widgets["memory_total"].config(text=self._bytes_to_gb(memory.total))
            self._widgets["memory_available"].config(
                text=self._bytes_to_gb(memory.available)
            )
            self._widgets["memory_used"].config(text=self._bytes_to_gb(memory.used))
            self._widgets["memory_free"].config(text=self._bytes_to_gb(memory.free))

        except Exception as e:
            print(f"Error updating overall memory: {e}")

    def _update_virtual_memory(self) -> None:
        """Update virtual memory details"""
        try:
            memory = psutil.virtual_memory()

            self._widgets["vm_percent"].config(text=f"{memory.percent:.1f}%")

            # Handle platform-specific attributes safely
            self._update_memory_field(memory, "active", "vm_active")
            self._update_memory_field(memory, "inactive", "vm_inactive")
            self._update_memory_field(memory, "buffers", "vm_buffers")
            self._update_memory_field(memory, "cached", "vm_cached")
            self._update_memory_field(memory, "shared", "vm_shared")

        except Exception as e:
            print(f"Error updating virtual memory: {e}")

    def _update_swap_memory(self) -> None:
        """Update swap memory information"""
        try:
            swap = psutil.swap_memory()

            # Update percentage and progress bar
            percent = swap.percent
            self._widgets["swap_usage_label"].config(
                text=f"{percent:.1f}%", fg=self._get_usage_color(percent)
            )
            self._widgets["swap_usage_bar"]["value"] = percent

            # Update swap values
            self._widgets["swap_total"].config(text=self._bytes_to_gb(swap.total))
            self._widgets["swap_used"].config(text=self._bytes_to_gb(swap.used))
            self._widgets["swap_free"].config(text=self._bytes_to_gb(swap.free))
            self._widgets["swap_sin"].config(text=f"{swap.sin:,}")
            self._widgets["swap_sout"].config(text=f"{swap.sout:,}")

        except Exception as e:
            print(f"Error updating swap memory: {e}")

    def _update_memory_statistics(self) -> None:
        """Update memory statistics"""
        try:
            # Get system-wide memory statistics if available
            if hasattr(psutil, "virtual_memory"):
                # For basic page fault information, we'd need to track process stats
                # This is a simplified version - more detailed stats would require
                # platform-specific implementations
                total_page_faults = 0
                major_page_faults = 0

                # Sum page faults from all processes (this might be slow)
                try:
                    for proc in psutil.process_iter(["pid", "memory_info"]):
                        try:
                            if hasattr(proc.info["memory_info"], "pfaults"):
                                total_page_faults += proc.info["memory_info"].pfaults
                            if hasattr(proc.info["memory_info"], "pageins"):
                                major_page_faults += proc.info["memory_info"].pageins
                        except (
                            psutil.NoSuchProcess,
                            psutil.AccessDenied,
                            AttributeError,
                        ):
                            continue
                except Exception:
                    pass  # Skip if this takes too long or fails

                self._widgets["page_faults"].config(text=f"{total_page_faults:,}")
                self._widgets["major_page_faults"].config(text=f"{major_page_faults:,}")

        except Exception as e:
            print(f"Error updating memory statistics: {e}")

    def _update_top_processes(self) -> None:
        """Update top memory consuming processes"""
        try:
            tree = self._widgets["processes_tree"]

            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)

            # Get sorted processes by memory usage
            processes = self._get_sorted_processes()

            # Add top processes to tree
            for proc in processes[: self.TOP_PROCESS_COUNT]:
                try:
                    # Truncate process name if too long
                    name = proc["name"][: self.MAX_PROCESS_NAME_LENGTH]
                    if len(proc["name"]) > self.MAX_PROCESS_NAME_LENGTH:
                        name += "..."

                    memory_mb = proc["memory_info"].rss / (1024 * 1024)

                    tree.insert(
                        "",
                        "end",
                        values=(
                            proc["pid"],
                            name,
                            f"{proc['memory_percent']:.1f}%",
                            f"{memory_mb:.1f} MB",
                            proc["status"],
                        ),
                    )
                except Exception as e:
                    print(f"Error adding process to tree: {e}")

        except Exception as e:
            print(f"Error updating top processes: {e}")

    def _get_sorted_processes(self) -> List[Dict]:
        """Get processes sorted by memory usage"""
        processes = []
        try:
            for proc in psutil.process_iter(
                ["pid", "name", "memory_percent", "memory_info", "status"]
            ):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort by memory percentage (descending)
            processes.sort(key=lambda x: x.get("memory_percent", 0), reverse=True)

        except Exception as e:
            print(f"Error getting sorted processes: {e}")

        return processes

    def _get_usage_color(self, percentage: float) -> str:
        """Get color based on usage percentage"""
        if percentage < 50:
            return "green"
        elif percentage < 80:
            return "orange"
        else:
            return "red"

    def _bytes_to_gb(self, bytes_value: int) -> str:
        """Convert bytes to GB string"""
        return f"{bytes_value / (1024**3):.2f} GB"

    def _start_updates(self) -> None:
        """Start automatic updates"""
        self._update_memory_stats()
        self._frame.after(self._update_interval, self._start_updates)

    def _create_section_frame(self, title: str) -> tk.Frame:
        """Create a standard section frame with title"""
        frame = tk.LabelFrame(
            self.main_container, text=title, font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        content_frame = tk.Frame(frame)
        content_frame.pack(fill=tk.X, padx=10, pady=10)
        return content_frame

    def _update_memory_field(self, memory_obj, attr_name, widget_key):
        """Safely update memory field if attribute exists"""
        if hasattr(memory_obj, attr_name):
            value = getattr(memory_obj, attr_name)
            self._widgets[widget_key].config(text=self._bytes_to_gb(value))
        else:
            self._widgets[widget_key].config(text="N/A")
