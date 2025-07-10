import logging
import os
import shutil
from enum import Enum
from typing import Optional


class LogType(Enum):
    INSTALLING_LIBRARIES = "installing_libraries"
    TESTING_LIBRARIES = "testing_libraries"
    THREAD_RUNNER = "thread_runner"
    CPU_MONITORING = "cpu_monitoring"
    MEMORY_MONITORING = "memory_monitoring"
    HARDDRIVE_MONITORING = "harddrive_monitoring"
    GPU_MONITORING = "gpu_monitoring"
    FASTQC = "fastqc"
    FASTP = "fastp"
    HYBPIPER = "hybpiper"


class Logger:
    _instance: Optional["Logger"] = None
    _initialized: bool = False

    def __new__(cls) -> "Logger":
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once
        if not Logger._initialized:
            self.setup_logger()
            Logger._initialized = True

    def setup_logger(self) -> None:
        # Create log directory
        self.log_dir = os.path.expanduser(os.getenv("LOG_DIR", "~/.fast-app-logs"))
        if os.path.exists(self.log_dir):
            shutil.rmtree(self.log_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.loggers = {
            LogType.INSTALLING_LIBRARIES.value: self._create_logger(
                LogType.INSTALLING_LIBRARIES.value
            ),
            LogType.TESTING_LIBRARIES.value: self._create_logger(
                LogType.TESTING_LIBRARIES.value
            ),
            LogType.THREAD_RUNNER.value: self._create_logger(
                LogType.THREAD_RUNNER.value
            ),
            LogType.CPU_MONITORING.value: self._create_logger(
                LogType.CPU_MONITORING.value
            ),
            LogType.MEMORY_MONITORING.value: self._create_logger(
                LogType.MEMORY_MONITORING.value
            ),
            LogType.HARDDRIVE_MONITORING.value: self._create_logger(
                LogType.HARDDRIVE_MONITORING.value
            ),
            LogType.GPU_MONITORING.value: self._create_logger(
                LogType.GPU_MONITORING.value
            ),
            LogType.FASTQC.value: self._create_logger(LogType.FASTQC.value),
            LogType.FASTP.value: self._create_logger(LogType.FASTP.value),
            LogType.HYBPIPER.value: self._create_logger(LogType.HYBPIPER.value),
        }

    def _create_logger(
        self, name: str, level: int = logging.INFO, include_console: bool = True
    ) -> logging.Logger:
        log_filename = f"{name}.log"
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if logger.handlers:
            return logger

        # Create file handler
        log_file = os.path.join(self.log_dir, log_filename)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Create formatter
        # formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
        formatter = logging.Formatter("%(asctime)s %(message)s")
        file_handler.setFormatter(formatter)

        # Add file handler to logger
        logger.addHandler(file_handler)

        # Optionally add console handler
        if include_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Prevent logs from being handled by root logger
        logger.propagate = False

        return logger

    def get_logger(self, log_type: LogType) -> logging.Logger:
        logger = self.loggers.get(log_type.value)
        if logger is None:
            raise ValueError(f"Logger not found for log type: {log_type.value}")
        return logger

    def get_log_file_path(self, log_type: LogType) -> str:
        return os.path.join(self.log_dir, f"{log_type.value}.log")


def init_logger() -> None:
    Logger()
