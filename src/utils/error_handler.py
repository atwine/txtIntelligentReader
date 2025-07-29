#!/usr/bin/env python3
"""
Comprehensive Error Handling Framework for txtIntelligentReader

Provides structured error handling, recovery mechanisms, and detailed
error reporting with context preservation.
"""

import sys
import traceback
from typing import Dict, Any, Optional, Callable, List, Union
from pathlib import Path
from datetime import datetime
import json
import logging

from .logger import LoggerMixin, get_logger


class ErrorSeverity:
    """Error severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory:
    """Error categories for classification."""
    FILE_IO = "FILE_IO"
    PROCESSING = "PROCESSING"
    CONFIGURATION = "CONFIGURATION"
    VALIDATION = "VALIDATION"
    NETWORK = "NETWORK"
    DEPENDENCY = "DEPENDENCY"
    USER_INPUT = "USER_INPUT"
    SYSTEM = "SYSTEM"


class ProcessingError(Exception):
    """Custom exception for processing errors."""
    
    def __init__(self, message: str, category: str = ErrorCategory.PROCESSING,
                 severity: str = ErrorSeverity.MEDIUM, context: Dict[str, Any] = None):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.timestamp = datetime.now()


class ErrorHandler(LoggerMixin):
    """
    Comprehensive error handling framework.
    
    Provides structured error handling, recovery mechanisms,
    and detailed error reporting with context preservation.
    """
    
    def __init__(self, debug_mode: bool = False, error_log_file: str = None):
        """
        Initialize the error handler.
        
        Args:
            debug_mode: Enable debug mode for detailed error information
            error_log_file: Optional specific error log file
        """
        self.debug_mode = debug_mode
        self.error_log_file = error_log_file or "logs/errors.log"
        self.error_count = 0
        self.error_history = []
        
        # Create error log directory
        Path(self.error_log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Setup error-specific logger
        self.error_logger = logging.getLogger('error_handler')
        if not self.error_logger.handlers:
            error_handler = logging.FileHandler(self.error_log_file)
            error_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            self.error_logger.addHandler(error_handler)
            self.error_logger.setLevel(logging.ERROR)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None,
                    recovery_action: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Handle an error with comprehensive logging and optional recovery.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            recovery_action: Optional recovery function to attempt
            
        Returns:
            Dictionary with error handling results
        """
        self.error_count += 1
        context = context or {}
        
        # Determine error details
        error_info = self._analyze_error(error, context)
        
        # Log the error
        self._log_error(error_info)
        
        # Store in history
        self.error_history.append(error_info)
        
        # Attempt recovery if provided
        recovery_result = None
        if recovery_action:
            try:
                recovery_result = recovery_action()
                self.log_info(f"Recovery action successful for {error_info['category']} error")
            except Exception as recovery_error:
                self.log_error(f"Recovery action failed: {str(recovery_error)}")
                recovery_result = None
        
        # Return error handling result
        return {
            'error_handled': True,
            'error_id': error_info['error_id'],
            'severity': error_info['severity'],
            'category': error_info['category'],
            'recovery_attempted': recovery_action is not None,
            'recovery_successful': recovery_result is not None,
            'recovery_result': recovery_result
        }
    
    def _analyze_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an error to determine its characteristics."""
        error_id = f"ERR_{self.error_count:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine category and severity
        if isinstance(error, ProcessingError):
            category = error.category
            severity = error.severity
        else:
            category = self._categorize_error(error)
            severity = self._assess_severity(error, category)
        
        # Get traceback information
        tb_info = traceback.format_exception(type(error), error, error.__traceback__)
        
        return {
            'error_id': error_id,
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category,
            'severity': severity,
            'context': context,
            'traceback': tb_info,
            'system_info': self._get_system_context()
        }
    
    def _categorize_error(self, error: Exception) -> str:
        """Categorize an error based on its type and message."""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        if error_type in ['FileNotFoundError', 'PermissionError', 'IOError']:
            return ErrorCategory.FILE_IO
        elif error_type in ['ValueError', 'TypeError']:
            if 'config' in error_message:
                return ErrorCategory.CONFIGURATION
            else:
                return ErrorCategory.VALIDATION
        elif error_type in ['ImportError', 'ModuleNotFoundError']:
            return ErrorCategory.DEPENDENCY
        elif error_type in ['ConnectionError', 'TimeoutError']:
            return ErrorCategory.NETWORK
        elif 'input' in error_message or 'argument' in error_message:
            return ErrorCategory.USER_INPUT
        elif error_type in ['MemoryError', 'SystemError']:
            return ErrorCategory.SYSTEM
        else:
            return ErrorCategory.PROCESSING
    
    def _assess_severity(self, error: Exception, category: str) -> str:
        """Assess the severity of an error."""
        error_type = type(error).__name__
        
        # Critical errors that stop processing
        if error_type in ['MemoryError', 'SystemError', 'KeyboardInterrupt']:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category == ErrorCategory.FILE_IO and error_type == 'PermissionError':
            return ErrorSeverity.HIGH
        if category == ErrorCategory.DEPENDENCY:
            return ErrorSeverity.HIGH
        if category == ErrorCategory.CONFIGURATION:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.PROCESSING, ErrorCategory.VALIDATION]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    def _log_error(self, error_info: Dict[str, Any]):
        """Log error information with appropriate detail level."""
        error_id = error_info['error_id']
        severity = error_info['severity']
        category = error_info['category']
        message = error_info['error_message']
        
        # Console logging
        log_message = f"[{error_id}] {severity} {category} Error: {message}"
        
        if severity == ErrorSeverity.CRITICAL:
            self.log_error(f"🚨 CRITICAL: {log_message}")
        elif severity == ErrorSeverity.HIGH:
            self.log_error(f"🔴 HIGH: {log_message}")
        elif severity == ErrorSeverity.MEDIUM:
            self.log_warning(f"🟡 MEDIUM: {log_message}")
        else:
            self.log_info(f"🟢 LOW: {log_message}")
        
        # Detailed file logging
        detailed_log = {
            'error_info': error_info,
            'debug_mode': self.debug_mode
        }
        
        self.error_logger.error(json.dumps(detailed_log, indent=2, default=str))
        
        # Debug mode: print full traceback
        if self.debug_mode:
            self.log_debug("Full traceback:")
            for line in error_info['traceback']:
                self.log_debug(line.strip())
    
    def _get_system_context(self) -> Dict[str, Any]:
        """Get system context information."""
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': str(Path.cwd()),
            'memory_usage': self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information if available."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'available': False, 'reason': 'psutil not installed'}
    
    def create_recovery_action(self, action_type: str, **kwargs) -> Callable:
        """
        Create a recovery action for common error scenarios.
        
        Args:
            action_type: Type of recovery action
            **kwargs: Additional parameters for the recovery action
            
        Returns:
            Recovery function
        """
        if action_type == 'retry_with_backoff':
            return self._create_retry_action(kwargs.get('max_retries', 3), 
                                           kwargs.get('backoff_factor', 2))
        elif action_type == 'fallback_value':
            return lambda: kwargs.get('fallback_value')
        elif action_type == 'skip_and_continue':
            return lambda: {'action': 'skip', 'reason': 'error_recovery'}
        elif action_type == 'use_default_config':
            return lambda: kwargs.get('default_config', {})
        else:
            return None
    
    def _create_retry_action(self, max_retries: int, backoff_factor: float) -> Callable:
        """Create a retry action with exponential backoff."""
        def retry_action():
            import time
            for attempt in range(max_retries):
                try:
                    # This would need to be customized for specific operations
                    self.log_info(f"Retry attempt {attempt + 1}/{max_retries}")
                    time.sleep(backoff_factor ** attempt)
                    return {'retry_attempt': attempt + 1, 'success': True}
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    continue
            return None
        return retry_action
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all handled errors."""
        if not self.error_history:
            return {'total_errors': 0, 'summary': 'No errors recorded'}
        
        # Count by category and severity
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            category = error['category']
            severity = error['severity']
            
            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'by_category': category_counts,
            'by_severity': severity_counts,
            'most_recent': self.error_history[-1]['timestamp'],
            'critical_errors': severity_counts.get(ErrorSeverity.CRITICAL, 0)
        }
    
    def export_error_report(self, output_file: str = None) -> str:
        """
        Export a comprehensive error report.
        
        Args:
            output_file: Optional output file path
            
        Returns:
            Path to the generated report
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"logs/error_report_{timestamp}.json"
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'summary': self.get_error_summary(),
            'detailed_errors': self.error_history,
            'system_info': self._get_system_context()
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.log_info(f"Error report exported to: {output_path}")
        return str(output_path)
    
    def reset_error_history(self):
        """Reset the error history and counter."""
        self.error_history.clear()
        self.error_count = 0
        self.log_info("Error history reset")


class DebugMode:
    """Debug mode utilities for enhanced error reporting."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.debug_info = {}
    
    def capture_state(self, name: str, data: Any):
        """Capture state information for debugging."""
        if self.enabled:
            self.debug_info[name] = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'type': type(data).__name__
            }
    
    def get_debug_context(self) -> Dict[str, Any]:
        """Get all captured debug information."""
        return self.debug_info.copy() if self.enabled else {}
    
    def clear_debug_info(self):
        """Clear all debug information."""
        self.debug_info.clear()


# Global error handler instance
_global_error_handler = None


def get_error_handler(debug_mode: bool = False) -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler(debug_mode=debug_mode)
    return _global_error_handler


def handle_error(error: Exception, context: Dict[str, Any] = None,
                recovery_action: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Convenience function to handle errors using the global error handler.
    
    Args:
        error: The exception that occurred
        context: Additional context information
        recovery_action: Optional recovery function
        
    Returns:
        Error handling result
    """
    handler = get_error_handler()
    return handler.handle_error(error, context, recovery_action)


def safe_execute(func: Callable, *args, context: Dict[str, Any] = None,
                recovery_action: Optional[Callable] = None, **kwargs) -> Dict[str, Any]:
    """
    Safely execute a function with comprehensive error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        context: Error context information
        recovery_action: Optional recovery function
        **kwargs: Function keyword arguments
        
    Returns:
        Execution result with error handling information
    """
    try:
        result = func(*args, **kwargs)
        return {
            'success': True,
            'result': result,
            'error': None
        }
    except Exception as e:
        error_result = handle_error(e, context, recovery_action)
        return {
            'success': False,
            'result': error_result.get('recovery_result'),
            'error': error_result
        }


# Context manager for error handling
class ErrorContext:
    """Context manager for handling errors in a specific context."""
    
    def __init__(self, context_name: str, recovery_action: Optional[Callable] = None):
        self.context_name = context_name
        self.recovery_action = recovery_action
        self.error_handler = get_error_handler()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            context = {'context_name': self.context_name}
            self.error_handler.handle_error(exc_val, context, self.recovery_action)
            return True  # Suppress the exception
        return False
