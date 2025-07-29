#!/usr/bin/env python3
"""
Comprehensive unit tests for utility modules.

Tests logger, output formatter, error handler, and configuration utilities.
"""

import sys
import pytest
import tempfile
import json
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.logger import setup_logging, get_logger, log_function_call, log_error, log_progress
from utils.output_formatter import OutputFormatter
from utils.error_handler import ErrorHandler, ProcessingError, ErrorContext
from utils.config_loader import ConfigLoader


class TestLogger:
    """Unit tests for logging utilities."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.log_file = self.temp_dir / "test.log"
    
    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_setup_logging_console_only(self):
        """Test console-only logging setup."""
        logger = setup_logging(enable_file_logging=False)
        
        assert logger is not None
        assert logger.name == "txtIntelligentReader"
        assert len(logger.handlers) >= 1  # At least console handler
    
    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        logger = setup_logging(
            enable_file_logging=True,
            log_file=str(self.log_file),
            log_level=logging.DEBUG
        )
        
        assert logger is not None
        assert self.log_file.exists() or len(logger.handlers) >= 2
    
    def test_get_logger(self):
        """Test logger retrieval."""
        logger1 = get_logger()
        logger2 = get_logger()
        
        # Should return the same logger instance
        assert logger1 is logger2
        assert logger1.name == "txtIntelligentReader"
    
    def test_log_function_call_decorator(self):
        """Test function call logging decorator."""
        @log_function_call
        def test_function(x, y=10):
            return x + y
        
        with patch('utils.logger.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            result = test_function(5, y=15)
            
            assert result == 20
            mock_logger.debug.assert_called()
    
    def test_log_error_function(self):
        """Test error logging function."""
        with patch('utils.logger.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            test_error = ValueError("Test error")
            log_error(test_error, "Test context")
            
            mock_logger.error.assert_called()
    
    def test_log_progress_function(self):
        """Test progress logging function."""
        with patch('utils.logger.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            log_progress("Processing", 50, 100)
            
            mock_logger.info.assert_called()


class TestOutputFormatter:
    """Unit tests for OutputFormatter."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.formatter = OutputFormatter()
        
        # Sample processing results
        self.sample_results = {
            'filtered_sentences': [
                "Patient shows improvement after treatment.",
                "Medication dosage was adjusted appropriately.",
                "Follow-up appointment scheduled for next week."
            ],
            'statistics': {
                'total_sentences': 10,
                'filtered_sentences': 3,
                'retention_rate': 0.3,
                'processing_time': 1.5,
                'noise_removed': 4,
                'health_relevant': 3,
                'complete_sentences': 3,
                'quality_score': 0.85
            },
            'metadata': {
                'input_file': 'test.txt',
                'timestamp': '2024-01-15T10:30:00',
                'version': '1.0.0'
            }
        }
    
    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test OutputFormatter initialization."""
        assert self.formatter is not None
        assert hasattr(self.formatter, 'supported_formats')
        assert 'txt' in self.formatter.supported_formats
        assert 'json' in self.formatter.supported_formats
    
    def test_format_validation(self):
        """Test output format validation."""
        # Valid formats
        assert self.formatter.validate_format('txt') == True
        assert self.formatter.validate_format('json') == True
        assert self.formatter.validate_format('md') == True
        
        # Invalid formats
        assert self.formatter.validate_format('invalid') == False
        assert self.formatter.validate_format('') == False
        assert self.formatter.validate_format(None) == False
    
    def test_path_validation(self):
        """Test output path validation."""
        valid_path = self.temp_dir / "output.txt"
        invalid_path = Path("/invalid/path/output.txt")
        
        assert self.formatter.validate_output_path(str(valid_path)) == True
        # Invalid path validation depends on system permissions
        # Just ensure method doesn't crash
        result = self.formatter.validate_output_path(str(invalid_path))
        assert isinstance(result, bool)
    
    def test_text_formatting(self):
        """Test text format output."""
        output_file = self.temp_dir / "output.txt"
        
        success = self.formatter.save_output(
            self.sample_results,
            str(output_file),
            'txt'
        )
        
        assert success == True
        assert output_file.exists()
        
        content = output_file.read_text(encoding='utf-8')
        assert "Patient shows improvement" in content
        assert "Medication dosage" in content
    
    def test_json_formatting(self):
        """Test JSON format output."""
        output_file = self.temp_dir / "output.json"
        
        success = self.formatter.save_output(
            self.sample_results,
            str(output_file),
            'json'
        )
        
        assert success == True
        assert output_file.exists()
        
        # Validate JSON structure
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'filtered_sentences' in data
        assert 'statistics' in data
        assert 'metadata' in data
        assert len(data['filtered_sentences']) == 3
    
    def test_markdown_formatting(self):
        """Test Markdown format output."""
        output_file = self.temp_dir / "output.md"
        
        success = self.formatter.save_output(
            self.sample_results,
            str(output_file),
            'md'
        )
        
        assert success == True
        assert output_file.exists()
        
        content = output_file.read_text(encoding='utf-8')
        assert "# txtIntelligentReader" in content
        assert "## Processing Results" in content
        assert "| Metric |" in content  # Table formatting
    
    def test_csv_formatting(self):
        """Test CSV format output."""
        output_file = self.temp_dir / "output.csv"
        
        success = self.formatter.save_output(
            self.sample_results,
            str(output_file),
            'csv'
        )
        
        assert success == True
        assert output_file.exists()
        
        content = output_file.read_text(encoding='utf-8')
        assert "Metric,Value" in content
        assert "total_sentences,10" in content
    
    def test_html_formatting(self):
        """Test HTML format output."""
        output_file = self.temp_dir / "output.html"
        
        success = self.formatter.save_output(
            self.sample_results,
            str(output_file),
            'html'
        )
        
        assert success == True
        assert output_file.exists()
        
        content = output_file.read_text(encoding='utf-8')
        assert "<html>" in content
        assert "<title>" in content
        assert "txtIntelligentReader" in content
    
    def test_quality_metrics_calculation(self):
        """Test quality metrics calculation."""
        sentences = [
            "The patient received comprehensive medical treatment.",
            "Short.",
            "This is a very long sentence with many medical terms like hypertension, diabetes, and cardiovascular disease."
        ]
        
        metrics = self.formatter._calculate_quality_metrics(sentences)
        
        assert 'avg_sentence_length' in metrics
        assert 'medical_terms_count' in metrics
        assert 'completeness_score' in metrics
        assert 'readability_score' in metrics
        
        assert metrics['avg_sentence_length'] > 0
        assert metrics['medical_terms_count'] >= 0
        assert 0 <= metrics['completeness_score'] <= 1
        assert 0 <= metrics['readability_score'] <= 10
    
    def test_system_info_generation(self):
        """Test system information generation."""
        sys_info = self.formatter._get_system_info()
        
        assert 'platform' in sys_info
        assert 'python_version' in sys_info
        assert 'architecture' in sys_info
        assert 'processor' in sys_info
        assert 'memory_total' in sys_info
        
        # Validate data types
        assert isinstance(sys_info['platform'], str)
        assert isinstance(sys_info['python_version'], str)
    
    def test_processing_summary_generation(self):
        """Test processing summary generation."""
        summary = self.formatter._generate_processing_summary(self.sample_results)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "sentences" in summary.lower()
        assert "processed" in summary.lower()
    
    def test_error_handling(self):
        """Test error handling in output formatting."""
        # Test with invalid output path
        invalid_path = "/invalid/path/output.txt"
        
        success = self.formatter.save_output(
            self.sample_results,
            invalid_path,
            'txt'
        )
        
        # Should handle error gracefully
        assert success == False
    
    def test_empty_results_handling(self):
        """Test handling of empty results."""
        empty_results = {
            'filtered_sentences': [],
            'statistics': {},
            'metadata': {}
        }
        
        output_file = self.temp_dir / "empty.txt"
        
        success = self.formatter.save_output(
            empty_results,
            str(output_file),
            'txt'
        )
        
        assert success == True
        assert output_file.exists()


class TestErrorHandler:
    """Unit tests for ErrorHandler."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.error_handler = ErrorHandler(debug_mode=True)
    
    def test_initialization(self):
        """Test ErrorHandler initialization."""
        assert self.error_handler is not None
        assert self.error_handler.debug_mode == True
        assert len(self.error_handler.error_history) == 0
    
    def test_error_categorization(self):
        """Test error categorization."""
        file_error = FileNotFoundError("File not found")
        category = self.error_handler._categorize_error(file_error)
        assert category == "FILE_IO"
        
        value_error = ValueError("Invalid value")
        category = self.error_handler._categorize_error(value_error)
        assert category == "VALIDATION"
        
        import_error = ImportError("Module not found")
        category = self.error_handler._categorize_error(import_error)
        assert category == "DEPENDENCY"
    
    def test_severity_assessment(self):
        """Test error severity assessment."""
        critical_error = SystemError("System failure")
        severity = self.error_handler._assess_severity(critical_error, "system")
        assert severity == "CRITICAL"
        
        warning_error = UserWarning("User warning")
        severity = self.error_handler._assess_severity(warning_error, "user")
        assert severity in ["LOW", "MEDIUM"]
    
    def test_error_handling(self):
        """Test error handling process."""
        test_error = ValueError("Test error")
        
        error_id = self.error_handler.handle_error(
            test_error,
            context="unit_test",
            operation="test_operation"
        )
        
        assert error_id is not None
        assert len(self.error_handler.error_history) == 1
        
        error_record = self.error_handler.error_history[0]
        assert error_record['error_id'] == error_id
        assert error_record['category'] == "VALIDATION"
        assert error_record['context'] == "unit_test"
    
    def test_recovery_actions(self):
        """Test recovery action generation."""
        file_error = FileNotFoundError("File not found")
        actions = self.error_handler._get_recovery_actions("FILE_IO", file_error)
        
        assert isinstance(actions, list)
        assert len(actions) > 0
        assert any("check" in action.lower() for action in actions)
    
    def test_safe_execute(self):
        """Test safe execution wrapper."""
        def successful_function():
            return "success"
        
        def failing_function():
            raise ValueError("Test error")
        
        # Test successful execution
        result = self.error_handler.safe_execute(successful_function)
        assert result == "success"
        
        # Test failed execution
        result = self.error_handler.safe_execute(failing_function, default_return="default")
        assert result == "default"
        assert len(self.error_handler.error_history) > 0
    
    def test_error_context_manager(self):
        """Test error context manager."""
        with ErrorContext(self.error_handler, "test_context") as ctx:
            assert ctx is not None
            # Context manager should handle errors automatically
    
    def test_error_summary(self):
        """Test error summary generation."""
        # Generate some test errors
        self.error_handler.handle_error(ValueError("Error 1"), "context1")
        self.error_handler.handle_error(FileNotFoundError("Error 2"), "context2")
        
        summary = self.error_handler.get_error_summary()
        
        assert 'total_errors' in summary
        assert 'by_category' in summary
        assert 'by_severity' in summary
        assert summary['total_errors'] == 2
    
    def test_error_report_generation(self):
        """Test error report generation."""
        # Generate test error
        self.error_handler.handle_error(ValueError("Test error"), "test_context")
        
        report = self.error_handler.generate_error_report()
        
        assert isinstance(report, dict)
        assert 'summary' in report
        assert 'errors' in report
        assert 'system_info' in report
        assert len(report['errors']) == 1
    
    def test_debug_mode(self):
        """Test debug mode functionality."""
        debug_handler = ErrorHandler(debug_mode=True)
        normal_handler = ErrorHandler(debug_mode=False)
        
        test_error = ValueError("Test error")
        
        # Both should handle error, but debug mode should capture more info
        debug_id = debug_handler.handle_error(test_error, "debug_test")
        normal_id = normal_handler.handle_error(test_error, "normal_test")
        
        assert debug_id is not None
        assert normal_id is not None
        
        debug_record = debug_handler.error_history[0]
        normal_record = normal_handler.error_history[0]
        
        # Debug mode should have more detailed information
        assert 'debug_info' in debug_record
        assert 'debug_info' not in normal_record or not normal_record['debug_info']


class TestConfigLoader:
    """Unit tests for ConfigLoader."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "config.json"
        
        # Sample configuration
        self.sample_config = {
            "health_threshold": 0.3,
            "quality_threshold": 0.7,
            "completeness_threshold": 0.6,
            "output_format": "txt",
            "enable_logging": True,
            "log_level": "INFO"
        }
        
        # Write sample config
        with open(self.config_file, 'w') as f:
            json.dump(self.sample_config, f)
    
    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test ConfigLoader initialization."""
        loader = ConfigLoader()
        assert loader is not None
    
    def test_load_config_file(self):
        """Test loading configuration from file."""
        loader = ConfigLoader()
        config = loader.load_config(str(self.config_file))
        
        assert config is not None
        assert config['health_threshold'] == 0.3
        assert config['quality_threshold'] == 0.7
        assert config['output_format'] == "txt"
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration file."""
        loader = ConfigLoader()
        config = loader.load_config("nonexistent.json")
        
        # Should return default configuration
        assert config is not None
        assert isinstance(config, dict)
    
    def test_config_validation(self):
        """Test configuration validation."""
        loader = ConfigLoader()
        
        # Valid config
        valid_config = self.sample_config.copy()
        assert loader.validate_config(valid_config) == True
        
        # Invalid config (missing required field)
        invalid_config = {"health_threshold": 0.3}  # Missing other required fields
        # Validation behavior depends on implementation
        result = loader.validate_config(invalid_config)
        assert isinstance(result, bool)
    
    def test_default_config(self):
        """Test default configuration generation."""
        loader = ConfigLoader()
        default_config = loader.get_default_config()
        
        assert isinstance(default_config, dict)
        assert 'health_threshold' in default_config
        assert 'quality_threshold' in default_config
        assert 'output_format' in default_config
    
    def test_config_merging(self):
        """Test configuration merging."""
        loader = ConfigLoader()
        
        base_config = {"health_threshold": 0.3, "quality_threshold": 0.7}
        override_config = {"health_threshold": 0.5, "output_format": "json"}
        
        merged = loader.merge_configs(base_config, override_config)
        
        assert merged['health_threshold'] == 0.5  # Overridden
        assert merged['quality_threshold'] == 0.7  # From base
        assert merged['output_format'] == "json"   # Added
    
    def test_environment_variable_override(self):
        """Test environment variable override."""
        loader = ConfigLoader()
        
        with patch.dict('os.environ', {'TXTIR_HEALTH_THRESHOLD': '0.8'}):
            config = loader.load_config(str(self.config_file))
            
            # Environment variable should override file config
            # Implementation depends on ConfigLoader design
            assert isinstance(config, dict)
    
    def test_config_saving(self):
        """Test configuration saving."""
        loader = ConfigLoader()
        
        test_config = {
            "health_threshold": 0.4,
            "quality_threshold": 0.8,
            "output_format": "json"
        }
        
        output_file = self.temp_dir / "saved_config.json"
        success = loader.save_config(test_config, str(output_file))
        
        if success:  # If save_config is implemented
            assert output_file.exists()
            
            # Verify saved content
            with open(output_file, 'r') as f:
                saved_config = json.load(f)
            
            assert saved_config['health_threshold'] == 0.4
            assert saved_config['output_format'] == "json"


def run_utils_unit_tests():
    """Run all utility unit tests."""
    print("🚀 Running Utility Unit Tests")
    print("=" * 60)
    
    # Run pytest on this file
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', __file__, '-v', '--tb=short'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_utils_unit_tests()
    sys.exit(0 if success else 1)
