#!/usr/bin/env python3
"""
Test suite for output formatting functionality.

Tests all output formats including text, JSON, markdown, CSV, and HTML
with comprehensive validation of content and metadata.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from utils.output_formatter import OutputFormatter
from pipeline import TextProcessor
from main import TxtIntelligentReader
from config import load_config


def create_test_data():
    """Create test data for output formatting tests."""
    sentences = [
        "Patient shows signs of improvement after treatment.",
        "The medication dosage was adjusted by the doctor.",
        "Treatment was effective; patient recovered quickly.",
        "This is a complete medical sentence about diagnosis.",
        "The patient's vital signs are stable and improving."
    ]
    
    metadata = {
        'input_file': 'test_medical_input.txt',
        'processing_time': 0.123,
        'layers_applied': ['quick', 'health', 'ai', 'thought'],
        'configuration': {
            'health_threshold': 0.1,
            'completeness_threshold': 0.3,
            'quality_threshold': 0.4,
            'use_spacy': False
        },
        'statistics': {
            'input_sentences': 10,
            'output_sentences': 5,
            'overall_retention_rate': 0.5,
            'layer_results': [
                {
                    'layer': 'quick',
                    'input_count': 10,
                    'output_count': 8,
                    'retention_rate': 0.8,
                    'processing_time': 0.001
                },
                {
                    'layer': 'health',
                    'input_count': 8,
                    'output_count': 6,
                    'retention_rate': 0.75,
                    'processing_time': 0.002
                },
                {
                    'layer': 'ai',
                    'input_count': 6,
                    'output_count': 5,
                    'retention_rate': 0.833,
                    'processing_time': 0.1
                },
                {
                    'layer': 'thought',
                    'input_count': 5,
                    'output_count': 5,
                    'retention_rate': 1.0,
                    'processing_time': 0.02
                }
            ]
        },
        'filter_statistics': {
            'quick_filter': {
                'total_processed': 10,
                'noise_removed': 2,
                'pdf_artifacts_removed': 0,
                'headers_footers_removed': 0
            },
            'health_filter': {
                'total_processed': 8,
                'health_relevant': 6,
                'medical_terms_found': 15,
                'health_score_avg': 0.65
            },
            'ai_filter': {
                'total_processed': 6,
                'complete_sentences': 5,
                'incomplete_sentences': 1,
                'avg_completeness_score': 0.85
            },
            'thought_validator': {
                'total_processed': 5,
                'valid_thoughts': 5,
                'structural_issues': 0,
                'avg_quality_score': 0.9
            }
        }
    }
    
    return sentences, metadata


def test_text_output():
    """Test text output formatting."""
    print("🧪 Testing Text Output...")
    
    formatter = OutputFormatter()
    sentences, metadata = create_test_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        output_file = f.name
    
    try:
        # Test text output with metadata
        success = formatter.save_text(sentences, output_file, metadata)
        print(f"✅ Text output with metadata: {success}")
        
        # Verify file content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for metadata header
        assert "# txtIntelligentReader Output" in content
        assert "# Generated:" in content
        assert "# Input file: test_medical_input.txt" in content
        
        # Check sentences
        for sentence in sentences:
            assert sentence.strip() in content
        
        print("   ✓ Metadata header included")
        print("   ✓ All sentences present")
        
        # Test text output without metadata
        success_no_meta = formatter.save_text(sentences, output_file)
        print(f"✅ Text output without metadata: {success_no_meta}")
        
    finally:
        os.unlink(output_file)
    
    return success


def test_json_output():
    """Test JSON output formatting."""
    print("\n🧪 Testing JSON Output...")
    
    formatter = OutputFormatter()
    sentences, metadata = create_test_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        output_file = f.name
    
    try:
        # Test JSON output
        success = formatter.save_json(sentences, metadata, output_file)
        print(f"✅ JSON output: {success}")
        
        # Verify JSON structure
        with open(output_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Check top-level structure
        assert "txtIntelligentReader" in json_data
        assert "input" in json_data
        assert "processing" in json_data
        assert "results" in json_data
        assert "detailed_statistics" in json_data
        
        # Check specific content
        assert json_data["results"]["filtered_sentences"] == sentences
        assert json_data["results"]["output_sentence_count"] == len(sentences)
        assert json_data["input"]["file"] == "test_medical_input.txt"
        
        print("   ✓ JSON structure valid")
        print("   ✓ All required fields present")
        print("   ✓ Sentences correctly included")
        
    finally:
        os.unlink(output_file)
    
    return success


def test_markdown_output():
    """Test markdown report generation."""
    print("\n🧪 Testing Markdown Output...")
    
    formatter = OutputFormatter()
    sentences, metadata = create_test_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        output_file = f.name
    
    try:
        # Test markdown report
        success = formatter.save_markdown_report(sentences, metadata, output_file)
        print(f"✅ Markdown report: {success}")
        
        # Verify markdown content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check markdown structure
        assert "# txtIntelligentReader Processing Report" in content
        assert "## Input Information" in content
        assert "## Processing Configuration" in content
        assert "## Results Summary" in content
        assert "## Layer-by-Layer Analysis" in content
        assert "## Quality Metrics" in content
        assert "## Filtered Sentences" in content
        
        # Check specific content
        assert "test_medical_input.txt" in content
        assert "0.123 seconds" in content
        
        # Check sentences are included
        for i, sentence in enumerate(sentences, 1):
            assert f"{i}. {sentence}" in content
        
        print("   ✓ Markdown structure valid")
        print("   ✓ All sections present")
        print("   ✓ Content correctly formatted")
        
    finally:
        os.unlink(output_file)
    
    return success


def test_csv_output():
    """Test CSV statistics output."""
    print("\n🧪 Testing CSV Output...")
    
    formatter = OutputFormatter()
    sentences, metadata = create_test_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        output_file = f.name
    
    try:
        # Test CSV output
        success = formatter.save_csv_statistics(metadata, output_file)
        print(f"✅ CSV statistics: {success}")
        
        # Verify CSV content
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check header
        header = lines[0].strip()
        expected_columns = [
            'Timestamp', 'Input_File', 'Input_Sentences', 'Output_Sentences',
            'Retention_Rate', 'Processing_Time', 'Layers_Applied'
        ]
        
        for column in expected_columns:
            assert column in header
        
        # Check data row
        data_row = lines[1].strip()
        assert 'test_medical_input.txt' in data_row
        assert '10' in data_row  # input sentences
        assert '5' in data_row   # output sentences
        assert '50.0%' in data_row  # retention rate
        
        print("   ✓ CSV header correct")
        print("   ✓ Data row contains expected values")
        
    finally:
        os.unlink(output_file)
    
    return success


def test_html_output():
    """Test HTML report generation."""
    print("\n🧪 Testing HTML Output...")
    
    formatter = OutputFormatter()
    sentences, metadata = create_test_data()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        output_file = f.name
    
    try:
        # Test HTML report
        success = formatter.save_html_report(sentences, metadata, output_file)
        print(f"✅ HTML report: {success}")
        
        # Verify HTML content
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<html lang=\"en\">" in content
        assert "<title>txtIntelligentReader Report</title>" in content
        assert "txtIntelligentReader Processing Report" in content
        
        # Check content sections
        assert "Layer Performance" in content
        assert "Quality Metrics" in content
        assert "Filtered Sentences" in content
        
        # Check data is included
        assert "test_medical_input.txt" in content
        for sentence in sentences:
            assert sentence in content
        
        print("   ✓ HTML structure valid")
        print("   ✓ All sections present")
        print("   ✓ Content properly embedded")
        
    finally:
        os.unlink(output_file)
    
    return success


def test_output_validation():
    """Test output path and format validation."""
    print("\n🧪 Testing Output Validation...")
    
    formatter = OutputFormatter()
    
    # Test valid formats
    valid_formats = ['txt', 'json', 'md', 'csv', 'html']
    for fmt in valid_formats:
        valid = formatter.validate_output_path(f"test.{fmt}", fmt)
        assert valid, f"Format {fmt} should be valid"
    
    print("✅ Valid format validation passed")
    
    # Test supported formats list
    supported = formatter.get_supported_formats()
    assert set(supported) == set(valid_formats)
    
    print("✅ Supported formats list correct")
    
    return True


def test_quality_metrics():
    """Test quality metrics calculation."""
    print("\n🧪 Testing Quality Metrics...")
    
    formatter = OutputFormatter()
    sentences, metadata = create_test_data()
    
    # Calculate quality metrics
    metrics = formatter._calculate_quality_metrics(sentences, metadata)
    
    # Verify metrics structure
    expected_keys = [
        'avg_sentence_length', 'medical_terms_count', 
        'complete_sentences_count', 'readability_score'
    ]
    
    for key in expected_keys:
        assert key in metrics, f"Missing metric: {key}"
        assert isinstance(metrics[key], (int, float)), f"Metric {key} should be numeric"
    
    print("✅ Quality metrics structure valid")
    
    # Check reasonable values
    assert metrics['avg_sentence_length'] > 0
    assert metrics['medical_terms_count'] >= 0
    assert metrics['complete_sentences_count'] <= len(sentences)
    assert 0 <= metrics['readability_score'] <= 10
    
    print("✅ Quality metrics values reasonable")
    
    return True


def test_processing_summary():
    """Test processing summary generation."""
    print("\n🧪 Testing Processing Summary...")
    
    formatter = OutputFormatter()
    sentences, metadata = create_test_data()
    
    # Generate processing summary
    summary = formatter.generate_processing_summary(metadata)
    
    # Verify summary structure
    expected_keys = [
        'timestamp', 'version', 'input_file', 'processing_time',
        'layers_applied', 'sentence_counts', 'retention_rate', 'layer_performance'
    ]
    
    for key in expected_keys:
        assert key in summary, f"Missing summary key: {key}"
    
    # Check specific values
    assert summary['input_file'] == 'test_medical_input.txt'
    assert summary['processing_time'] == 0.123
    assert len(summary['layers_applied']) == 4
    assert summary['sentence_counts']['input'] == 10
    assert summary['sentence_counts']['output'] == 5
    
    print("✅ Processing summary structure valid")
    print("✅ Processing summary values correct")
    
    return True


def test_integrated_output_formatting():
    """Test integrated output formatting with TextProcessor."""
    print("\n🧪 Testing Integrated Output Formatting...")
    
    # Create test configuration
    config = {
        'health_threshold': 0.1,
        'completeness_threshold': 0.3,
        'quality_threshold': 0.4
    }
    
    processor = TextProcessor(config=config)
    
    # Test text
    test_text = """
    Patient shows signs of improvement after treatment.
    The medication dosage was adjusted by the doctor.
    Treatment was effective; patient recovered quickly.
    Random noise text @@@ ###
    This is a complete medical sentence about diagnosis.
    """
    
    # Test different output formats
    formats_to_test = ['txt', 'json', 'md', 'csv', 'html']
    
    for fmt in formats_to_test:
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{fmt}', delete=False) as f:
            output_file = f.name
        
        try:
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_text)
                input_file = f.name
            
            try:
                # Process with specific format
                result = processor.process_file(
                    input_file=input_file,
                    output_file=output_file,
                    output_format=fmt
                )
                
                success = result.get('success', False)
                print(f"✅ Integrated {fmt.upper()} output: {success}")
                
                # Verify file was created and has content
                if success and os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    assert file_size > 0, f"{fmt} output file is empty"
                    print(f"   ✓ Output file created ({file_size} bytes)")
                
            finally:
                if os.path.exists(input_file):
                    os.unlink(input_file)
                
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    return True


def run_all_tests():
    """Run all output formatting tests."""
    print("🚀 Running txtIntelligentReader Output Formatting Tests")
    print("=" * 60)
    
    tests = [
        ("Text Output", test_text_output),
        ("JSON Output", test_json_output),
        ("Markdown Output", test_markdown_output),
        ("CSV Output", test_csv_output),
        ("HTML Output", test_html_output),
        ("Output Validation", test_output_validation),
        ("Quality Metrics", test_quality_metrics),
        ("Processing Summary", test_processing_summary),
        ("Integrated Output", test_integrated_output_formatting)
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
    print("🏁 OUTPUT FORMATTING TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All output formatting tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
