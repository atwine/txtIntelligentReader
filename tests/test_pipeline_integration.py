#!/usr/bin/env python3
"""
Integration tests for the txtIntelligentReader pipeline.

Tests the complete pipeline integration including TextProcessor,
FilterPipeline, and main CLI functionality.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from pipeline import TextProcessor, FilterPipeline
from main import TxtIntelligentReader
from config import load_config


def test_filter_pipeline():
    """Test the FilterPipeline class."""
    print("🧪 Testing FilterPipeline...")
    
    # Create test configuration
    config = {
        'health_threshold': 0.1,
        'completeness_threshold': 0.3,
        'quality_threshold': 0.4,
        'use_spacy': False
    }
    
    # Initialize pipeline
    pipeline = FilterPipeline(config=config)
    
    # Test sentences
    test_sentences = [
        "Patient shows signs of improvement after treatment.",
        "The medication dosage was adjusted by the doctor.",
        "Treatment was effective; patient recovered quickly.",
        "Random noise text @@@ ###",
        "This is a complete medical sentence about diagnosis.",
        "Incomplete fragment...",
        "The patient's vital signs are stable and improving."
    ]
    
    # Process sentences
    result = pipeline.process_sentences(test_sentences)
    
    print(f"✅ Pipeline processing: {result['success']}")
    print(f"   Input: {result['input_sentences']} sentences")
    print(f"   Output: {result['output_sentences']} sentences")
    print(f"   Retention: {result['overall_retention_rate']*100:.1f}%")
    print(f"   Layers: {', '.join(result['layers_applied'])}")
    
    # Test layer-specific processing
    quick_only = pipeline.process_sentences(test_sentences, layers=['quick'])
    print(f"✅ Quick filter only: {quick_only['output_sentences']} sentences")
    
    return result['success']


def test_text_processor():
    """Test the TextProcessor class."""
    print("\n🧪 Testing TextProcessor...")
    
    config = {
        'health_threshold': 0.1,
        'completeness_threshold': 0.3,
        'quality_threshold': 0.4
    }
    
    processor = TextProcessor(config=config)
    
    # Test direct text processing
    test_text = """
    Patient shows signs of improvement after treatment.
    The medication dosage was adjusted by the doctor.
    Treatment was effective; patient recovered quickly.
    Random noise text @@@ ###
    This is a complete medical sentence about diagnosis.
    """
    
    result = processor.process_text(test_text)
    
    print(f"✅ Text processing: {result['success']}")
    print(f"   Input: {result['input_sentences']} sentences")
    print(f"   Output: {result['output_sentences']} sentences")
    
    # Test file processing with temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_text)
        temp_file = f.name
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_file = f.name
        
        file_result = processor.process_file(temp_file, output_file)
        
        print(f"✅ File processing: {file_result['success']}")
        if file_result['success']:
            print(f"   Input: {file_result['statistics']['input_sentences']} sentences")
            print(f"   Output: {file_result['statistics']['output_sentences']} sentences")
        
        # Clean up
        os.unlink(output_file)
        
    finally:
        os.unlink(temp_file)
    
    return result['success'] and file_result['success']


def test_main_cli_integration():
    """Test the main CLI integration."""
    print("\n🧪 Testing Main CLI Integration...")
    
    config = load_config()
    reader = TxtIntelligentReader(config=config)
    
    # Create test file
    test_content = """
    Patient shows signs of improvement after treatment.
    The medication dosage was adjusted by the doctor.
    Treatment was effective; patient recovered quickly.
    Random noise text @@@ ###
    This is a complete medical sentence about diagnosis.
    The patient's vital signs are stable and improving.
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        input_file = f.name
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_file = f.name
        
        # Test with lenient thresholds
        reader.config.update({
            'health_threshold': 0.1,
            'completeness_threshold': 0.3,
            'quality_threshold': 0.4
        })
        reader.text_processor = TextProcessor(config=reader.config)
        
        result = reader.process_file(input_file, output_file, verbose=False)
        
        print(f"✅ CLI integration: {result['success']}")
        if result['success']:
            print(f"   Input: {result['statistics']['input_sentences']} sentences")
            print(f"   Output: {result['statistics']['output_sentences']} sentences")
        
        # Test JSON output
        json_output = output_file.replace('.txt', '.json')
        json_result = reader.process_file(input_file, json_output, output_format='json')
        
        print(f"✅ JSON output: {json_result['success']}")
        
        # Clean up
        for file_path in [output_file, json_output]:
            if os.path.exists(file_path):
                os.unlink(file_path)
        
    finally:
        os.unlink(input_file)
    
    return result['success']


def test_statistics_and_monitoring():
    """Test statistics collection and monitoring."""
    print("\n🧪 Testing Statistics and Monitoring...")
    
    config = {
        'health_threshold': 0.1,
        'completeness_threshold': 0.3,
        'quality_threshold': 0.4
    }
    
    processor = TextProcessor(config=config)
    
    # Process multiple texts to build statistics
    test_texts = [
        "Patient shows improvement after treatment.",
        "The medication was effective for the patient.",
        "Treatment resulted in complete recovery."
    ]
    
    for i, text in enumerate(test_texts):
        result = processor.process_text(text)
        print(f"   Processed text {i+1}: {result['output_sentences']} sentences")
    
    # Get comprehensive statistics
    stats = processor.get_processing_statistics()
    
    print(f"✅ Statistics collection:")
    print(f"   Files processed: {stats['processor_stats']['files_processed']}")
    print(f"   Total input sentences: {stats['processor_stats']['total_input_sentences']}")
    print(f"   Total output sentences: {stats['processor_stats']['total_output_sentences']}")
    
    # Test pipeline statistics
    pipeline_stats = stats['pipeline_stats']['pipeline_stats']
    print(f"   Pipeline runs: {pipeline_stats['total_runs']}")
    print(f"   Success rate: {pipeline_stats['successful_runs']}/{pipeline_stats['total_runs']}")
    
    return True


def test_configuration_validation():
    """Test configuration validation."""
    print("\n🧪 Testing Configuration Validation...")
    
    # Test valid configuration
    valid_config = {
        'health_threshold': 0.3,
        'completeness_threshold': 0.6,
        'quality_threshold': 0.7,
        'use_spacy': False
    }
    
    pipeline = FilterPipeline(config=valid_config)
    validation = pipeline.validate_configuration()
    
    print(f"✅ Valid config validation: {validation['valid']}")
    print(f"   Warnings: {len(validation['warnings'])}")
    print(f"   Errors: {len(validation['errors'])}")
    
    # Test invalid configuration
    invalid_config = {
        'health_threshold': 1.5,  # Invalid: > 1.0
        'completeness_threshold': -0.1,  # Invalid: < 0.0
        'quality_threshold': 0.95,  # Warning: very high
    }
    
    pipeline_invalid = FilterPipeline(config=invalid_config)
    invalid_validation = pipeline_invalid.validate_configuration()
    
    print(f"✅ Invalid config validation: {not invalid_validation['valid']}")
    print(f"   Errors detected: {len(invalid_validation['errors'])}")
    
    return validation['valid'] and not invalid_validation['valid']


def test_performance_estimation():
    """Test processing time estimation."""
    print("\n🧪 Testing Performance Estimation...")
    
    processor = TextProcessor()
    
    # Create a test file
    test_content = "This is a test sentence. " * 100  # 100 sentences
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        estimate = processor.estimate_processing_time(temp_file)
        
        print(f"✅ Time estimation:")
        print(f"   File size: {estimate.get('file_size_mb', 0):.3f} MB")
        print(f"   Estimated sentences: {estimate.get('estimated_sentences', 0)}")
        print(f"   Estimated time: {estimate.get('total_time_estimate', 0):.3f}s")
        
        # Test pipeline estimation
        pipeline = FilterPipeline()
        pipeline_estimate = pipeline.estimate_processing_time(100)
        
        print(f"   Pipeline estimate for 100 sentences: {pipeline_estimate:.3f}s")
        
    finally:
        os.unlink(temp_file)
    
    return True


def run_all_tests():
    """Run all integration tests."""
    print("🚀 Running txtIntelligentReader Pipeline Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Filter Pipeline", test_filter_pipeline),
        ("Text Processor", test_text_processor),
        ("Main CLI Integration", test_main_cli_integration),
        ("Statistics & Monitoring", test_statistics_and_monitoring),
        ("Configuration Validation", test_configuration_validation),
        ("Performance Estimation", test_performance_estimation)
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
    print("🏁 INTEGRATION TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All integration tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
