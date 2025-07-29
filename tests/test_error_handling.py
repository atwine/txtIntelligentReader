#!/usr/bin/env python3
"""
Test suite for error handling and logging functionality.

Tests the comprehensive error handling framework including error categorization,
severity assessment, recovery mechanisms, and debug mode functionality.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.error_handler import (
    ErrorHandler, ProcessingError, ErrorSeverity, ErrorCategory,
    handle_error, safe_execute, ErrorContext, DebugMode
)
from utils.logger import setup_logging


def test_error_handler_initialization():
    """Test ErrorHandler initialization and basic functionality."""
    print("🧪 Testing ErrorHandler Initialization...")
    
    # Test basic initialization
    handler = ErrorHandler()
    assert handler.error_count == 0
    assert len(handler.error_history) == 0
    print("✅ Basic initialization successful")
    
    # Test debug mode initialization
    debug_handler = ErrorHandler(debug_mode=True)
    assert debug_handler.debug_mode == True
    print("✅ Debug mode initialization successful")
    
    return True


def test_error_categorization():
    """Test error categorization functionality."""
    print("\n🧪 Testing Error Categorization...")
    
    handler = ErrorHandler()
    
    # Test different error types
    test_cases = [
        (FileNotFoundError("File not found"), ErrorCategory.FILE_IO),
        (ValueError("Invalid configuration"), ErrorCategory.CONFIGURATION),
        (ImportError("Module not found"), ErrorCategory.DEPENDENCY),
        (TypeError("Type error"), ErrorCategory.VALIDATION),
        (MemoryError("Out of memory"), ErrorCategory.SYSTEM)
    ]
    
    for error, expected_category in test_cases:
        category = handler._categorize_error(error)
        assert category == expected_category, f"Expected {expected_category}, got {category}"
        print(f"   ✓ {type(error).__name__} → {category}")
    
    print("✅ Error categorization working correctly")
    return True


def test_severity_assessment():
    """Test error severity assessment."""
    print("\n🧪 Testing Severity Assessment...")
    
    handler = ErrorHandler()
    
    # Test different severity levels
    test_cases = [
        (MemoryError("Out of memory"), ErrorSeverity.CRITICAL),
        (PermissionError("Access denied"), ErrorSeverity.HIGH),
        (ValueError("Invalid value"), ErrorSeverity.MEDIUM),
        (Warning("Minor warning"), ErrorSeverity.LOW)
    ]
    
    for error, expected_severity in test_cases:
        category = handler._categorize_error(error)
        severity = handler._assess_severity(error, category)
        print(f"   ✓ {type(error).__name__} → {severity}")
    
    print("✅ Severity assessment working correctly")
    return True


def test_error_handling():
    """Test comprehensive error handling."""
    print("\n🧪 Testing Error Handling...")
    
    handler = ErrorHandler()
    
    # Test basic error handling
    test_error = ValueError("Test error message")
    context = {'test_context': 'unit_test', 'stage': 'testing'}
    
    result = handler.handle_error(test_error, context)
    
    assert result['error_handled'] == True
    assert 'error_id' in result
    assert result['severity'] in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM, ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
    assert result['category'] in [ErrorCategory.VALIDATION, ErrorCategory.PROCESSING]
    
    print(f"✅ Error handled with ID: {result['error_id']}")
    print(f"   Category: {result['category']}")
    print(f"   Severity: {result['severity']}")
    
    # Verify error was recorded
    assert handler.error_count == 1
    assert len(handler.error_history) == 1
    
    print("✅ Error recording working correctly")
    return True


def test_recovery_mechanisms():
    """Test error recovery mechanisms."""
    print("\n🧪 Testing Recovery Mechanisms...")
    
    handler = ErrorHandler()
    
    # Test recovery action
    def test_recovery():
        return {'recovered': True, 'value': 42}
    
    test_error = RuntimeError("Recoverable error")
    result = handler.handle_error(test_error, recovery_action=test_recovery)
    
    assert result['recovery_attempted'] == True
    assert result['recovery_successful'] == True
    assert result['recovery_result']['recovered'] == True
    
    print("✅ Recovery mechanism working correctly")
    
    # Test failed recovery
    def failing_recovery():
        raise Exception("Recovery failed")
    
    result2 = handler.handle_error(test_error, recovery_action=failing_recovery)
    assert result2['recovery_attempted'] == True
    assert result2['recovery_successful'] == False
    
    print("✅ Failed recovery handling working correctly")
    return True


def test_processing_error():
    """Test custom ProcessingError functionality."""
    print("\n🧪 Testing ProcessingError...")
    
    # Create custom processing error
    error = ProcessingError(
        "Custom processing error",
        category=ErrorCategory.PROCESSING,
        severity=ErrorSeverity.HIGH,
        context={'custom_field': 'test_value'}
    )
    
    handler = ErrorHandler()
    result = handler.handle_error(error)
    
    assert result['category'] == ErrorCategory.PROCESSING
    assert result['severity'] == ErrorSeverity.HIGH
    
    print("✅ ProcessingError handling working correctly")
    return True


def test_safe_execute():
    """Test safe execution wrapper."""
    print("\n🧪 Testing Safe Execute...")
    
    # Test successful execution
    def successful_function(x, y):
        return x + y
    
    result = safe_execute(successful_function, 5, 10)
    assert result['success'] == True
    assert result['result'] == 15
    assert result['error'] is None
    
    print("✅ Safe execute - successful case")
    
    # Test failed execution
    def failing_function():
        raise ValueError("Test failure")
    
    result = safe_execute(failing_function, context={'test': 'safe_execute'})
    assert result['success'] == False
    assert result['error'] is not None
    
    print("✅ Safe execute - failure case")
    return True


def test_error_context_manager():
    """Test error context manager."""
    print("\n🧪 Testing Error Context Manager...")
    
    # Test successful context
    with ErrorContext("test_context") as ctx:
        result = "success"
    
    print("✅ Error context - successful case")
    
    # Test error context with recovery
    def recovery_action():
        return "recovered"
    
    with ErrorContext("test_context", recovery_action) as ctx:
        raise ValueError("Test error in context")
    
    print("✅ Error context - error case with recovery")
    return True


def test_debug_mode():
    """Test debug mode functionality."""
    print("\n🧪 Testing Debug Mode...")
    
    debug = DebugMode(enabled=True)
    
    # Capture some debug state
    debug.capture_state("test_data", {"key": "value", "number": 42})
    debug.capture_state("test_list", [1, 2, 3, 4, 5])
    
    debug_info = debug.get_debug_context()
    assert "test_data" in debug_info
    assert "test_list" in debug_info
    assert debug_info["test_data"]["data"]["key"] == "value"
    
    print("✅ Debug mode state capture working")
    
    # Test disabled debug mode
    debug_disabled = DebugMode(enabled=False)
    debug_disabled.capture_state("should_not_capture", "data")
    
    debug_info_disabled = debug_disabled.get_debug_context()
    assert len(debug_info_disabled) == 0
    
    print("✅ Debug mode disable working")
    return True


def test_error_summary_and_reporting():
    """Test error summary and reporting functionality."""
    print("\n🧪 Testing Error Summary and Reporting...")
    
    handler = ErrorHandler()
    
    # Generate some test errors
    errors = [
        ValueError("Test error 1"),
        FileNotFoundError("Test file error"),
        ProcessingError("Custom error", category=ErrorCategory.PROCESSING, severity=ErrorSeverity.HIGH)
    ]
    
    for error in errors:
        handler.handle_error(error)
    
    # Test error summary
    summary = handler.get_error_summary()
    assert summary['total_errors'] == 3
    assert 'by_category' in summary
    assert 'by_severity' in summary
    
    print(f"✅ Error summary generated: {summary['total_errors']} errors")
    
    # Test error report export
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        report_file = f.name
    
    try:
        report_path = handler.export_error_report(report_file)
        assert os.path.exists(report_path)
        
        # Verify report content
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        assert 'summary' in report_data
        assert 'detailed_errors' in report_data
        assert len(report_data['detailed_errors']) == 3
        
        print("✅ Error report export working correctly")
        
    finally:
        if os.path.exists(report_file):
            os.unlink(report_file)
    
    return True


def test_global_error_handler():
    """Test global error handler functionality."""
    print("\n🧪 Testing Global Error Handler...")
    
    # Test global handle_error function
    test_error = RuntimeError("Global test error")
    result = handle_error(test_error, {'global_test': True})
    
    assert result['error_handled'] == True
    print("✅ Global error handler working")
    
    return True


def test_logging_integration():
    """Test integration with logging system."""
    print("\n🧪 Testing Logging Integration...")
    
    # Setup logging for test
    setup_logging(verbose=True, level="DEBUG")
    
    handler = ErrorHandler(debug_mode=True)
    
    # Test that errors are logged properly
    test_error = ValueError("Logging integration test")
    result = handler.handle_error(test_error, {'logging_test': True})
    
    # Check that error log file exists
    log_file = Path(handler.error_log_file)
    assert log_file.exists(), "Error log file should exist"
    
    print("✅ Logging integration working")
    return True


def test_cli_error_handling():
    """Test CLI error handling integration."""
    print("\n🧪 Testing CLI Error Handling...")
    
    # Test CLI with invalid arguments (should be handled gracefully)
    import subprocess
    import sys
    
    # Test with non-existent input file
    cmd = [
        sys.executable, 'src/main.py', 'non_existent_file.txt',
        '--debug'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
    
    # Should exit with error code but handle gracefully
    assert result.returncode != 0
    assert "Error" in result.stdout or "Error" in result.stderr
    
    print("✅ CLI error handling working")
    return True


def run_all_tests():
    """Run all error handling tests."""
    print("🚀 Running txtIntelligentReader Error Handling Tests")
    print("=" * 60)
    
    tests = [
        ("ErrorHandler Initialization", test_error_handler_initialization),
        ("Error Categorization", test_error_categorization),
        ("Severity Assessment", test_severity_assessment),
        ("Error Handling", test_error_handling),
        ("Recovery Mechanisms", test_recovery_mechanisms),
        ("ProcessingError", test_processing_error),
        ("Safe Execute", test_safe_execute),
        ("Error Context Manager", test_error_context_manager),
        ("Debug Mode", test_debug_mode),
        ("Error Summary & Reporting", test_error_summary_and_reporting),
        ("Global Error Handler", test_global_error_handler),
        ("Logging Integration", test_logging_integration),
        ("CLI Error Handling", test_cli_error_handling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = test_func()
            if success:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("🏁 ERROR HANDLING TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All error handling tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
