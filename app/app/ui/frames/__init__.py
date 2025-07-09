from app.ui.frames.base_frame import BaseFrame
from app.ui.frames.hardware_monitoring.cpu import CPUFrame
from app.ui.frames.hardware_monitoring.gpu import GPUFrame
from app.ui.frames.hardware_monitoring.harddrive import HardDriveFrame
from app.ui.frames.hardware_monitoring.memory import MemoryFrame
from app.ui.frames.tools.fastp_frame import FastPFrame
from app.ui.frames.tools.fastqc_frame import FastQCFrame
from app.ui.frames.tools.hybpiper_frame import HybPiperFrame

__all__ = [
    "CPUFrame",
    "GPUFrame",
    "HardDriveFrame",
    "MemoryFrame",
    "FastPFrame",
    "FastQCFrame",
    "HybPiperFrame",
    "BaseFrame",
]
