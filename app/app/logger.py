import logging
import os
import sys
from typing import Optional


class Logger:
    """
    Singleton class for centralized logging configuration.
    Logs to both file and stdout with proper formatting.
    """
    _instance: Optional['Logger'] = None
    _initialized: bool = False

    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_file: str = "app.log", log_level: int = logging.INFO):
        """
        Initialize the logger singleton.
        
        Args:
            log_file: Name of the log file (default: "app.log")
            log_level: Logging level (default: logging.INFO)
        """
        if Logger._initialized:
            return
        
        self.log_file = log_file
        self.log_level = log_level
        self.logger = logging.getLogger()
        
        # Avoid duplicate handlers if logger is reconfigured
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self._setup_logger()
        Logger._initialized = True

    def _setup_logger(self) -> None:
        """Configure the logger with file and console handlers."""
        # Set the overall logger level
        self.logger.setLevel(self.log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            logging.Logger: The configured logger
        """
        return self.logger
    
    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log a critical message."""
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """Log an exception with traceback."""
        self.logger.exception(message)

    @classmethod
    def configure(cls, log_file: str = "app.log", log_level: int = logging.INFO) -> 'Logger':
        """
        Configure the logger singleton (can be called before first instantiation).
        
        Args:
            log_file: Name of the log file
            log_level: Logging level
            
        Returns:
            Logger: The singleton instance
        """
        if cls._instance is not None and cls._initialized:
            # Logger already exists, reconfigure it
            cls._instance.log_file = log_file
            cls._instance.log_level = log_level
            cls._instance.logger.handlers.clear()
            cls._instance._setup_logger()
        else:
            # Create new instance with configuration
            cls._instance = cls.__new__(cls)
            cls._instance.__init__(log_file, log_level)
        
        return cls._instance


# Convenience function for easy access
def get_logger() -> Logger:
    """
    Get the logger singleton instance.
    
    Returns:
        Logger: The singleton logger instance
    """
    return Logger()