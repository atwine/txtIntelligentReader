#!/usr/bin/env python3
"""
Logging utilities for txtIntelligentReader

Provides comprehensive logging setup with file and console output,
error handling, and rich formatting.
"""

import logging
import os
from pathlib import Path
from typing import Optional
import sys

try:
    from rich.logging import RichHandler
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def setup_logging(verbose: bool = False, level: str = "INFO", 
                 log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup comprehensive logging for the application.
    
    Args:
        verbose: Enable verbose (DEBUG) logging
        level: Logging level string
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Determine log level
    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Console handler with rich formatting if available
    if RICH_AVAILABLE:
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_time=verbose,
            show_path=verbose
        )
        console_format = "%(message)s"
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = "%(asctime)s - %(levelname)s - %(message)s" if verbose else "%(levelname)s - %(message)s"
    
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    
    # File handler
    log_file = log_file or log_dir / "txtintelligentreader.log"
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Create application logger
    logger = logging.getLogger('txtintelligentreader')
    
    # Log startup information
    logger.info("txtIntelligentReader logging initialized")
    logger.debug(f"Log level: {logging.getLevelName(log_level)}")
    logger.debug(f"Log file: {log_file}")
    logger.debug(f"Rich formatting: {'enabled' if RICH_AVAILABLE else 'disabled'}")
    
    return logger


def get_logger(name: str = 'txtintelligentreader') -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def log_debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def log_warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def log_error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def log_exception(self, message: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, *args, **kwargs)


def log_processing_start(input_file: str, layers: list):
    """Log the start of processing."""
    logger = get_logger()
    logger.info(f"Starting processing of: {input_file}")
    logger.info(f"Applying layers: {', '.join(layers)}")


def log_processing_complete(input_file: str, input_count: int, output_count: int, 
                          processing_time: float):
    """Log processing completion."""
    logger = get_logger()
    retention_rate = (output_count / input_count * 100) if input_count > 0 else 0
    logger.info(f"Processing complete: {input_file}")
    logger.info(f"Results: {input_count} → {output_count} sentences ({retention_rate:.1f}% retained)")
    logger.info(f"Processing time: {processing_time:.3f}s")


def log_layer_result(layer_name: str, input_count: int, output_count: int, 
                    processing_time: float):
    """Log the result of applying a filtering layer."""
    logger = get_logger()
    retention_rate = (output_count / input_count * 100) if input_count > 0 else 0
    logger.debug(f"{layer_name}: {input_count} → {output_count} sentences "
                f"({retention_rate:.1f}% retained, {processing_time:.3f}s)")


def log_error_with_context(error: Exception, context: str = ""):
    """Log an error with additional context."""
    logger = get_logger()
    if context:
        logger.error(f"Error in {context}: {str(error)}")
    else:
        logger.error(f"Error: {str(error)}")
    logger.debug("Exception details:", exc_info=True)


def log_configuration(config: dict):
    """Log configuration settings."""
    logger = get_logger()
    logger.info("Configuration loaded:")
    for key, value in config.items():
        logger.debug(f"  {key}: {value}")


def log_statistics(stats: dict):
    """Log processing statistics."""
    logger = get_logger()
    logger.info("Processing statistics:")
    for key, value in stats.items():
        if isinstance(value, dict):
            logger.debug(f"  {key}:")
            for sub_key, sub_value in value.items():
                logger.debug(f"    {sub_key}: {sub_value}")
        else:
            logger.debug(f"  {key}: {value}")


# Error handling utilities
def handle_file_error(file_path: str, operation: str, error: Exception):
    """Handle file operation errors with logging."""
    logger = get_logger()
    logger.error(f"Failed to {operation} file '{file_path}': {str(error)}")
    logger.debug("File error details:", exc_info=True)


def handle_processing_error(stage: str, error: Exception, sentence: str = None):
    """Handle processing errors with context."""
    logger = get_logger()
    logger.error(f"Processing error in {stage}: {str(error)}")
    if sentence:
        logger.debug(f"Problematic sentence: '{sentence[:100]}...'")
    logger.debug("Processing error details:", exc_info=True)


def handle_configuration_error(config_file: str, error: Exception):
    """Handle configuration loading errors."""
    logger = get_logger()
    logger.error(f"Failed to load configuration from '{config_file}': {str(error)}")
    logger.debug("Configuration error details:", exc_info=True)


# Progress logging utilities
class ProgressLogger:
    """
    Utility class for logging progress during long operations.
    """
    
    def __init__(self, total_items: int, operation_name: str = "Processing"):
        self.total_items = total_items
        self.operation_name = operation_name
        self.processed_items = 0
        self.logger = get_logger()
        self.last_logged_percentage = -1
    
    def update(self, increment: int = 1):
        """Update progress and log if threshold reached."""
        self.processed_items += increment
        percentage = int((self.processed_items / self.total_items) * 100)
        
        # Log every 10% or at completion
        if (percentage >= self.last_logged_percentage + 10 or 
            self.processed_items >= self.total_items):
            self.logger.info(f"{self.operation_name}: {self.processed_items}/{self.total_items} "
                           f"({percentage}%) complete")
            self.last_logged_percentage = percentage
    
    def complete(self):
        """Log completion."""
        self.logger.info(f"{self.operation_name} completed: {self.processed_items}/{self.total_items} items")


# Decorator for automatic logging
def log_function_call(func):
    """Decorator to automatically log function calls."""
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug("Function error details:", exc_info=True)
            raise
    return wrapper
