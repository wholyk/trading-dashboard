"""
Logging system for ShortsFactory with timestamps and structured output.
"""

import logging
import os
from datetime import datetime
from typing import Optional
import colorlog


class ShortsFactoryLogger:
    """Centralized logging system with file and console output"""
    
    def __init__(self, log_dir: str = "logs", name: str = "shortsfactory"):
        """Initialize logger with file and console handlers"""
        self.log_dir = log_dir
        self.name = name
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        # File handler - main log
        log_file = os.path.join(log_dir, f"{name}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # File handler - daily log
        today = datetime.now().strftime('%Y-%m-%d')
        daily_log_file = os.path.join(log_dir, f"{name}_{today}.log")
        daily_handler = logging.FileHandler(daily_log_file, encoding='utf-8')
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(file_formatter)
        self.logger.addHandler(daily_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message"""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        self.logger.critical(message, exc_info=exc_info)
    
    def job_event(self, job_id: int, event: str, details: Optional[str] = None):
        """Log a job-related event"""
        message = f"JOB {job_id}: {event}"
        if details:
            message += f" - {details}"
        self.logger.info(message)
    
    def worker_event(self, worker_name: str, event: str, details: Optional[str] = None):
        """Log a worker-related event"""
        message = f"WORKER {worker_name}: {event}"
        if details:
            message += f" - {details}"
        self.logger.info(message)


# Global logger instance
_global_logger = None


def get_logger(name: str = "shortsfactory") -> ShortsFactoryLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ShortsFactoryLogger(name=name)
    return _global_logger
