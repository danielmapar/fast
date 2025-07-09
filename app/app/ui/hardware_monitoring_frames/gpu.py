import platform
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, override

import pynvml

from app.logger.config import Logger, LogType
from app.ui.hardware_monitoring_frames.base_frame import BaseHardwareMonitoringFrame


@dataclass
class GPUMetrics:
    """GPU metrics data structure"""

    gpu_util: int = 0
    memory_util: int = 0
    memory_total: int = 0
    memory_used: int = 0
    memory_free: int = 0
    temperature: int = 0
    power_usage: float = 0.0
    power_limit: float = 0.0
    gpu_clock: int = 0
    memory_clock: int = 0
    performance_state: int = 0
    fan_speed: Optional[int] = None
    pcie_bus_id: str = "N/A"
    pcie_device_id: str = "N/A"
    encoder_util: Optional[int] = None
    decoder_util: Optional[int] = None
    compute_processes: int = 0
    graphics_processes: int = 0

    @property
    def memory_percent(self) -> float:
        return (
            (self.memory_used / self.memory_total * 100)
            if self.memory_total > 0
            else 0.0
        )


class GPUFrame(BaseHardwareMonitoringFrame):
    # Constants
    UPDATE_INTERVAL = 1000
    BYTES_TO_GB = 1024**3
    TEMP_WARNING = 80
    TEMP_CRITICAL = 90

    # UI Constants
    PROGRESS_BAR_LENGTH = 300
    SECTION_PADX = 10
    SECTION_PADY = 5
    ROW_PADDING = 1

    def __init__(self, notebook: ttk.Notebook) -> None:

        self.logger = Logger().get_logger(LogType.GPU_MONITORING)

        self._nvidia_available = False
        self._gpu_count = 0
        self._fallback_info: Optional[Dict[str, Any]] = None
        self._widgets: Dict[str, tk.Label] = {}
        self._gpu_widgets: List[Dict[str, Any]] = []

        # Platform-specific optimizations
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        self.is_macos = platform.system() == "Darwin"
        self.UPDATE_INTERVAL = (
            self.UPDATE_INTERVAL * 2 if self.is_windows else self.UPDATE_INTERVAL
        )

        super().__init__(notebook, "GPU (NVIDIA)")

    @override
    def setup_frame(self) -> None:
        """Initialize the GPU monitoring interface"""
        self._initialize_nvidia()

        container = self.get_scrollable_container()
        if not container:
            return

        self.main_container = tk.Frame(container)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if self._nvidia_available:
            self._create_nvidia_interface()
        elif self._fallback_info:
            self._create_fallback_interface()
        else:
            self._create_no_gpu_interface()

        self.start_threaded_updates(self.UPDATE_INTERVAL)

    @override
    def _resize_widgets(self, canvas_width: int) -> None:
        """Resize progress bars based on canvas width"""
        progress_length = max(150, min(self.PROGRESS_BAR_LENGTH, canvas_width - 200))

        for gpu_widgets in self._gpu_widgets:
            for key, widget in gpu_widgets.items():
                if key.endswith("_bar") and hasattr(widget, "config"):
                    widget.config(length=progress_length)

    @override
    def _collect_data_threaded(self) -> Optional[Dict[str, Any]]:
        """Collect GPU data in background thread"""
        if not self._nvidia_available or self._gpu_count == 0:
            return None

        try:
            data = self._collect_driver_info()
            data["gpus"] = [
                self._collect_gpu_metrics(gpu_id) for gpu_id in range(self._gpu_count)
            ]
            return data
        except Exception as e:
            self.logger.error(f"Error collecting GPU data: {e}")
            return None

    @override
    def _update_ui_with_data(self, data: Dict[str, Any]) -> None:
        """Update UI with collected data"""
        if not data:
            return

        try:
            self._update_driver_info(data)

            if "gpus" in data:
                for gpu_id, gpu_metrics in enumerate(data["gpus"]):
                    if gpu_id < len(self._gpu_widgets) and gpu_metrics:
                        self._update_gpu_display(gpu_id, gpu_metrics)

        except Exception as e:
            self.logger.error(f"Error updating GPU UI: {e}")

    def _initialize_nvidia(self) -> None:
        """Initialize NVIDIA ML library with fallback detection"""
        try:
            pynvml.nvmlInit()
            self._gpu_count = pynvml.nvmlDeviceGetCount()
            self._nvidia_available = True
            self.logger.info(f"Detected {self._gpu_count} NVIDIA GPU(s)")
        except Exception as e:
            self.logger.error(f"NVIDIA ML initialization failed: {e}")
            self._nvidia_available = False
            self._gpu_count = 0
            self._fallback_info = self._detect_gpus_via_nvidia_smi()

    def _detect_gpus_via_nvidia_smi(self) -> Optional[Dict[str, Any]]:
        """Fallback GPU detection using nvidia-smi"""
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0 or not result.stdout.strip():
                return None

            gpus = []
            for line in result.stdout.strip().split("\n"):
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 2:
                    gpus.append(
                        {
                            "name": parts[0],
                            "memory_total": f"{parts[1]} MB",
                            "driver_version": parts[2] if len(parts) > 2 else "Unknown",
                        }
                    )

            return {"gpus": gpus} if gpus else None

        except Exception as e:
            self.logger.error(f"Fallback detection failed: {e}")
            return None

    def _create_nvidia_interface(self) -> None:
        """Create full NVIDIA GPU monitoring interface"""
        # Driver information
        self._create_info_section(
            "NVIDIA Driver Information",
            [
                ("Driver Version", "driver_version", "N/A"),
                ("CUDA Version", "cuda_version", "N/A"),
                ("GPU Count", "gpu_count", str(self._gpu_count)),
            ],
        )

        # Individual GPU sections
        for gpu_id in range(self._gpu_count):
            self._create_gpu_section(gpu_id)

    def _create_fallback_interface(self) -> None:
        """Create limited interface using fallback data"""
        self._create_warning_section()

        if self._fallback_info is not None:
            for i, gpu_info in enumerate(self._fallback_info.get("gpus", [])):
                self._create_info_section(
                    f"{gpu_info['name']} (GPU {i})",
                    [
                        ("GPU Name", f"fallback_name_{i}", gpu_info["name"]),
                        (
                            "Total Memory",
                            f"fallback_memory_{i}",
                            gpu_info["memory_total"],
                        ),
                        (
                            "Driver Version",
                            f"fallback_driver_{i}",
                            gpu_info.get("driver_version", "Unknown"),
                        ),
                    ],
                )

    def _create_no_gpu_interface(self) -> None:
        """Create interface when no GPUs are detected"""
        frame = tk.LabelFrame(
            self.main_container,
            text="GPU Monitoring - No GPU Detected",
            font=("Arial", 12, "bold"),
        )
        frame.pack(fill=tk.X, pady=10)

        message = tk.Text(
            frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 10),
            fg="red",
            bg=frame.cget("bg"),
        )
        message.pack(pady=20, padx=20, fill=tk.BOTH)

        message.insert(
            tk.END,
            "No NVIDIA GPUs detected.\n\n"
            "Possible solutions:\n"
            "• Install NVIDIA GPU drivers\n"
            "• Check if GPU is properly connected\n"
            "• Restart the application after driver installation",
        )
        message.config(state=tk.DISABLED)

    def _create_warning_section(self) -> None:
        """Create warning section for limited mode"""
        frame = tk.LabelFrame(
            self.main_container,
            text="GPU Monitoring - Limited Mode",
            font=("Arial", 12, "bold"),
        )
        frame.pack(fill=tk.X, pady=10)

        warning = tk.Label(
            frame,
            text="NVIDIA GPUs detected but real-time monitoring unavailable.\n"
            "Install nvidia-ml-py for full functionality.",
            font=("Arial", 10),
            fg="orange",
            justify=tk.LEFT,
        )
        warning.pack(pady=10, padx=10)

    def _create_info_section(self, title: str, items: List[tuple]) -> None:
        """Create a section with label-value pairs"""
        frame = tk.LabelFrame(
            self.main_container, text=title, font=("Arial", 12, "bold")
        )
        frame.pack(fill=tk.X, pady=(0, 10))

        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        for label, key, initial_value in items:
            self._create_labeled_row(info_frame, label, key, initial_value)

    def _create_labeled_row(
        self,
        parent: tk.Widget,
        label: str,
        key: str,
        initial_value: str,
        widget_dict: Optional[Dict] = None,
    ) -> None:
        """Create a label-value row"""
        row = tk.Frame(parent)
        row.pack(fill=tk.X, pady=self.ROW_PADDING)

        tk.Label(row, text=f"{label}:", font=("Arial", 10)).pack(side=tk.LEFT)

        value_label = tk.Label(row, text=initial_value, font=("Arial", 10, "bold"))
        value_label.pack(side=tk.RIGHT)

        # Store in appropriate widget dictionary
        target_dict = widget_dict or self._widgets
        target_dict[key] = value_label

    def _create_gpu_section(self, gpu_id: int) -> None:
        """Create comprehensive monitoring section for a specific GPU"""
        gpu_name = self._get_gpu_name(gpu_id)

        gpu_frame = tk.LabelFrame(
            self.main_container,
            text=f"{gpu_name} (GPU {gpu_id})",
            font=("Arial", 12, "bold"),
        )
        gpu_frame.pack(fill=tk.X, pady=(0, 15))

        gpu_widgets: Dict[str, Any] = {}
        self._gpu_widgets.append(gpu_widgets)

        # Create all sections for this GPU
        self._create_utilization_section(gpu_frame, gpu_widgets)
        self._create_temperature_power_section(gpu_frame, gpu_id, gpu_widgets)
        self._create_memory_section(gpu_frame, gpu_id, gpu_widgets)
        self._create_performance_section(gpu_frame, gpu_id, gpu_widgets)
        self._create_hardware_info_section(gpu_frame, gpu_id, gpu_widgets)

    def _create_utilization_section(
        self, parent: tk.Widget, gpu_widgets: Dict[str, Any]
    ) -> None:
        """Create utilization section with progress bars"""
        frame = tk.LabelFrame(parent, text="Utilization", font=("Arial", 10, "bold"))
        frame.pack(fill=tk.X, padx=self.SECTION_PADX, pady=self.SECTION_PADY)

        self._create_progress_bar(frame, "GPU Usage", "gpu_usage", gpu_widgets)
        self._create_progress_bar(frame, "Memory Usage", "memory_usage", gpu_widgets)
        self._create_progress_bar(frame, "Encoder Usage", "encoder_usage", gpu_widgets)
        self._create_progress_bar(frame, "Decoder Usage", "decoder_usage", gpu_widgets)

    def _create_temperature_power_section(
        self, parent: tk.Widget, gpu_id: int, gpu_widgets: Dict[str, Any]
    ) -> None:
        """Create temperature and power section"""
        frame = tk.LabelFrame(
            parent, text="Temperature & Power", font=("Arial", 10, "bold")
        )
        frame.pack(fill=tk.X, padx=self.SECTION_PADX, pady=self.SECTION_PADY)

        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        items = [
            ("Temperature", f"temp_{gpu_id}", "0°C"),
            ("Power Usage", f"power_{gpu_id}", "0W"),
            ("Power Limit", f"power_limit_{gpu_id}", "0W"),
            ("Fan Speed", f"fan_{gpu_id}", "0%"),
        ]

        for label, key, initial in items:
            self._create_labeled_row(info_frame, label, key, initial, gpu_widgets)

    def _create_memory_section(
        self, parent: tk.Widget, gpu_id: int, gpu_widgets: Dict[str, Any]
    ) -> None:
        """Create memory details section"""
        frame = tk.LabelFrame(parent, text="Memory", font=("Arial", 10, "bold"))
        frame.pack(fill=tk.X, padx=self.SECTION_PADX, pady=self.SECTION_PADY)

        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        items = [
            ("Total Memory", f"mem_total_{gpu_id}", "0 GB"),
            ("Used Memory", f"mem_used_{gpu_id}", "0 GB"),
            ("Free Memory", f"mem_free_{gpu_id}", "0 GB"),
        ]

        for label, key, initial in items:
            self._create_labeled_row(info_frame, label, key, initial, gpu_widgets)

    def _create_performance_section(
        self, parent: tk.Widget, gpu_id: int, gpu_widgets: Dict[str, Any]
    ) -> None:
        """Create performance information section"""
        frame = tk.LabelFrame(parent, text="Performance", font=("Arial", 10, "bold"))
        frame.pack(fill=tk.X, padx=self.SECTION_PADX, pady=self.SECTION_PADY)

        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        items = [
            ("GPU Clock", f"gpu_clock_{gpu_id}", "0 MHz"),
            ("Memory Clock", f"mem_clock_{gpu_id}", "0 MHz"),
            ("Performance State", f"perf_state_{gpu_id}", "P0"),
        ]

        for label, key, initial in items:
            self._create_labeled_row(info_frame, label, key, initial, gpu_widgets)

    def _create_hardware_info_section(
        self, parent: tk.Widget, gpu_id: int, gpu_widgets: Dict[str, Any]
    ) -> None:
        """Create hardware information section"""
        frame = tk.LabelFrame(parent, text="Hardware Info", font=("Arial", 10, "bold"))
        frame.pack(fill=tk.X, padx=self.SECTION_PADX, pady=self.SECTION_PADY)

        info_frame = tk.Frame(frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        items = [
            ("Bus ID", f"bus_id_{gpu_id}", "N/A"),
            ("Device ID", f"device_id_{gpu_id}", "N/A"),
            ("Compute Processes", f"compute_proc_{gpu_id}", "0"),
            ("Graphics Processes", f"graphics_proc_{gpu_id}", "0"),
        ]

        for label, key, initial in items:
            self._create_labeled_row(info_frame, label, key, initial, gpu_widgets)

    def _create_progress_bar(
        self, parent: tk.Widget, label: str, key: str, gpu_widgets: Dict[str, Any]
    ) -> None:
        """Create a progress bar with label"""
        label_frame = tk.Frame(parent)
        label_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(label_frame, text=f"{label}:", font=("Arial", 9)).pack(side=tk.LEFT)

        value_label = tk.Label(
            label_frame, text="0%", font=("Arial", 9, "bold"), fg="blue"
        )
        value_label.pack(side=tk.RIGHT)

        progress_bar = ttk.Progressbar(
            parent, mode="determinate", length=self.PROGRESS_BAR_LENGTH, maximum=100
        )
        progress_bar.pack(fill=tk.X, padx=10, pady=5)

        gpu_widgets[f"{key}_label"] = value_label
        gpu_widgets[f"{key}_bar"] = progress_bar

    def _get_gpu_name(self, gpu_id: int) -> str:
        """Get GPU name safely"""
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            name = pynvml.nvmlDeviceGetName(handle)
            return name.decode("utf-8") if isinstance(name, bytes) else str(name)
        except pynvml.NVMLError:
            return f"GPU {gpu_id}"

    def _collect_driver_info(self) -> Dict[str, Any]:
        """Collect NVIDIA driver information"""
        try:
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            driver_version = (
                driver_version.decode("utf-8")
                if isinstance(driver_version, bytes)
                else str(driver_version)
            )

            cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
            cuda_major = cuda_version // 1000
            cuda_minor = (cuda_version % 1000) // 10

            return {
                "driver_version": driver_version,
                "cuda_version": f"{cuda_major}.{cuda_minor}",
                "gpu_count": self._gpu_count,
            }
        except pynvml.NVMLError:
            return {"driver_version": "N/A", "cuda_version": "N/A", "gpu_count": 0}

    def _collect_gpu_metrics(self, gpu_id: int) -> Optional[GPUMetrics]:
        """Collect comprehensive metrics for a specific GPU"""
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)

            # Basic utilization and memory
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0

            # Additional metrics with safe fallbacks
            power_limit = self._safe_get_power_limit(handle)
            gpu_clock = self._safe_get_clock(handle, pynvml.NVML_CLOCK_GRAPHICS)
            memory_clock = self._safe_get_clock(handle, pynvml.NVML_CLOCK_MEM)
            perf_state = self._safe_get_performance_state(handle)
            fan_speed = self._safe_get_fan_speed(handle)
            pcie_info = self._safe_get_pcie_info(handle)
            encoder_util, decoder_util = self._safe_get_encoder_decoder_util(handle)
            compute_procs, graphics_procs = self._safe_get_process_counts(handle)

            return GPUMetrics(
                gpu_util=util.gpu,
                memory_util=util.memory,
                memory_total=mem_info.total,
                memory_used=mem_info.used,
                memory_free=mem_info.free,
                temperature=temp,
                power_usage=power_usage,
                power_limit=power_limit,
                gpu_clock=gpu_clock,
                memory_clock=memory_clock,
                performance_state=perf_state,
                fan_speed=fan_speed,
                pcie_bus_id=pcie_info.get("bus_id", "N/A"),
                pcie_device_id=pcie_info.get("device_id", "N/A"),
                encoder_util=encoder_util,
                decoder_util=decoder_util,
                compute_processes=compute_procs,
                graphics_processes=graphics_procs,
            )

        except Exception as e:
            self.logger.error(f"Error collecting GPU {gpu_id} metrics: {e}")
            return None

    def _safe_get_power_limit(self, handle) -> float:
        """Safely get power limit"""
        try:
            return (
                pynvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)[1] / 1000.0
            )
        except pynvml.NVMLError:
            return 0.0

    def _safe_get_clock(self, handle, clock_type) -> int:
        """Safely get clock information"""
        try:
            return pynvml.nvmlDeviceGetClockInfo(handle, clock_type)
        except pynvml.NVMLError:
            return 0

    def _safe_get_performance_state(self, handle) -> int:
        """Safely get performance state"""
        try:
            return pynvml.nvmlDeviceGetPerformanceState(handle)
        except pynvml.NVMLError:
            return 0

    def _safe_get_fan_speed(self, handle) -> Optional[int]:
        """Safely get fan speed"""
        try:
            return pynvml.nvmlDeviceGetFanSpeed(handle)
        except pynvml.NVMLError:
            return None

    def _safe_get_pcie_info(self, handle) -> Dict[str, str]:
        """Safely get PCIe information"""
        try:
            pcie_info = pynvml.nvmlDeviceGetPciInfo_v3(handle)
            return {
                "bus_id": str(pcie_info.busId),
                "device_id": f"0x{pcie_info.pciDeviceId:04X}",
            }
        except pynvml.NVMLError:
            return {"bus_id": "N/A", "device_id": "N/A"}

    def _safe_get_encoder_decoder_util(
        self, handle
    ) -> tuple[Optional[int], Optional[int]]:
        """Safely get encoder/decoder utilization"""
        try:
            encoder = pynvml.nvmlDeviceGetEncoderUtilization(handle)[0]
            decoder = pynvml.nvmlDeviceGetDecoderUtilization(handle)[0]
            return encoder, decoder
        except pynvml.NVMLError:
            return None, None

    def _safe_get_process_counts(self, handle) -> tuple[int, int]:
        """Safely get process counts"""
        try:
            compute_procs = len(pynvml.nvmlDeviceGetComputeRunningProcesses_v3(handle))
            graphics_procs = len(
                pynvml.nvmlDeviceGetGraphicsRunningProcesses_v3(handle)
            )
            return compute_procs, graphics_procs
        except pynvml.NVMLError:
            return 0, 0

    def _update_driver_info(self, data: Dict[str, Any]) -> None:
        """Update driver information widgets"""
        for key in ["driver_version", "cuda_version", "gpu_count"]:
            if key in data and key in self._widgets:
                self._widgets[key].config(text=str(data[key]))

    def _update_gpu_display(self, gpu_id: int, metrics: GPUMetrics) -> None:
        """Update display for a specific GPU"""
        gpu_widgets = self._gpu_widgets[gpu_id]

        # Update utilization bars
        self._update_progress_bar(gpu_widgets, "gpu_usage", metrics.gpu_util)
        self._update_progress_bar(gpu_widgets, "memory_usage", metrics.memory_percent)

        if metrics.encoder_util is not None:
            self._update_progress_bar(
                gpu_widgets, "encoder_usage", metrics.encoder_util
            )
        if metrics.decoder_util is not None:
            self._update_progress_bar(
                gpu_widgets, "decoder_usage", metrics.decoder_util
            )

        # Update text fields
        updates = {
            f"temp_{gpu_id}": (
                f"{metrics.temperature}°C",
                self._get_temp_color(metrics.temperature),
            ),
            f"power_{gpu_id}": f"{metrics.power_usage:.1f}W",
            f"power_limit_{gpu_id}": f"{metrics.power_limit:.1f}W",
            f"fan_{gpu_id}": f"{metrics.fan_speed}%" if metrics.fan_speed else "N/A",
            f"mem_total_{gpu_id}": f"{metrics.memory_total / self.BYTES_TO_GB:.2f} GB",
            f"mem_used_{gpu_id}": f"{metrics.memory_used / self.BYTES_TO_GB:.2f} GB",
            f"mem_free_{gpu_id}": f"{metrics.memory_free / self.BYTES_TO_GB:.2f} GB",
            f"gpu_clock_{gpu_id}": f"{metrics.gpu_clock} MHz",
            f"mem_clock_{gpu_id}": f"{metrics.memory_clock} MHz",
            f"perf_state_{gpu_id}": f"P{metrics.performance_state}",
            f"bus_id_{gpu_id}": metrics.pcie_bus_id,
            f"device_id_{gpu_id}": metrics.pcie_device_id,
            f"compute_proc_{gpu_id}": str(metrics.compute_processes),
            f"graphics_proc_{gpu_id}": str(metrics.graphics_processes),
        }

        for key, value in updates.items():
            if key in gpu_widgets:
                if isinstance(value, tuple):
                    text, color = value
                    gpu_widgets[key].config(text=text, fg=color)
                else:
                    gpu_widgets[key].config(text=value)

    def _update_progress_bar(
        self, gpu_widgets: Dict[str, Any], key: str, value: float
    ) -> None:
        """Update a progress bar and its label"""
        if f"{key}_bar" in gpu_widgets and f"{key}_label" in gpu_widgets:
            gpu_widgets[f"{key}_bar"]["value"] = value
            gpu_widgets[f"{key}_label"].config(
                text=f"{value:.1f}%", fg=self._get_percentage_color(value)
            )

    def _get_percentage_color(self, percentage: float) -> str:
        """Get color based on percentage thresholds"""
        if percentage >= 80:
            return "red"
        elif percentage >= 60:
            return "orange"
        return "green"

    def _get_temp_color(self, temperature: float) -> str:
        """Get color based on temperature thresholds"""
        if temperature >= self.TEMP_CRITICAL:
            return "red"
        elif temperature >= self.TEMP_WARNING:
            return "orange"
        return "green"
