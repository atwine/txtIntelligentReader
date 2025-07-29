"""
Utilities module for txtIntelligentReader

Contains helper functions and utilities for text processing, 
file operations, and output formatting.
"""

from .file_handler import FileHandler
from .logger import setup_logging
from .output_formatter import OutputFormatter
from .error_handler import ErrorHandler, handle_error, safe_execute, ErrorContext

__all__ = [
    'FileHandler',
    'setup_logging',
    'OutputFormatter',
    'ErrorHandler',
    'handle_error',
    'safe_execute',
    'ErrorContext'
]
